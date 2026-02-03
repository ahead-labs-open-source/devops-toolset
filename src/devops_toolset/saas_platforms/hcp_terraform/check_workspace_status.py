#!/usr/bin/env python3
"""
HCP Terraform Workspace Status Checker

This script checks the status of workspaces and their latest runs.
"""

import argparse
import os
import sys
from typing import Dict, List, Optional
import requests
import time
from datetime import datetime


# Configuration
ORGANIZATION = "aheadlabs"
API_BASE_URL = "https://app.terraform.io/api/v2"


class TerraformCloudAPI:
    """HCP Terraform API client"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }
    
    def get_workspace(self, workspace_name: str) -> Optional[dict]:
        """Get workspace information"""
        url = f"{API_BASE_URL}/organizations/{ORGANIZATION}/workspaces/{workspace_name}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError:
            return None
    
    def get_run_status(self, run_id: str) -> dict:
        """Get run status and details"""
        url = f"{API_BASE_URL}/runs/{run_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["data"]
    
    def get_plan_logs(self, plan_id: str) -> str:
        """Get plan logs"""
        url = f"{API_BASE_URL}/plans/{plan_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        log_url = response.json()["data"]["attributes"]["log-read-url"]
        if log_url:
            log_response = requests.get(log_url)
            return log_response.text
        return "No logs available"
    
    def trigger_run(self, workspace_id: str, message: str = "Automated test run") -> str:
        """Trigger a new run in workspace"""
        url = f"{API_BASE_URL}/runs"
        payload = {
            "data": {
                "type": "runs",
                "attributes": {
                    "message": message
                },
                "relationships": {
                    "workspace": {
                        "data": {
                            "type": "workspaces",
                            "id": workspace_id
                        }
                    }
                }
            }
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["data"]["id"]


def check_workspaces(api: TerraformCloudAPI, workspace_names: List[str], verbose: bool = False):
    """Check status of multiple workspaces"""

    print(f"🔍 Checking {len(workspace_names)} workspace(s)...\n")

    for workspace_name in workspace_names:
        _print_workspace_header(workspace_name)

        workspace = api.get_workspace(workspace_name)
        if not workspace:
            _print_workspace_not_found()
            continue

        attrs = workspace["attributes"]
        _print_basic_workspace_info(attrs)
        _print_vcs_info(attrs)
        _print_latest_run_info(api, workspace, verbose)
        print()


def _print_workspace_header(workspace_name: str) -> None:
    print(f"📊 {workspace_name}")
    print("=" * (len(workspace_name) + 4))


def _print_workspace_not_found() -> None:
    print("   ❌ Workspace not found")
    print()


def _print_basic_workspace_info(attrs: Dict) -> None:
    print(f"   Status: {'🔒 Locked' if attrs['locked'] else '🔓 Unlocked'}")
    print(f"   Terraform: {attrs['terraform-version']}")
    print(f"   Working Dir: {attrs['working-directory']}")


def _print_vcs_info(attrs: Dict) -> None:
    vcs_repo = attrs.get("vcs-repo")
    if vcs_repo:
        print(f"   VCS: {vcs_repo['identifier']} (branch: {vcs_repo['branch']})")
        print(
            f"   Submodules: {'✅ Yes' if vcs_repo.get('ingress-submodules', False) else '❌ No'}"
        )
        return

    print("   VCS: ❌ Not connected")


def _print_latest_run_info(api: TerraformCloudAPI, workspace: dict, verbose: bool) -> None:
    current_run = workspace["relationships"].get("current-run", {}).get("data")
    if not current_run:
        print("   Latest Run: 📋 No runs")
        return

    run_id = current_run["id"]
    run_info = api.get_run_status(run_id)
    run_attrs = run_info["attributes"]

    status = run_attrs["status"]
    created_at = run_attrs["created-at"]
    message = run_attrs.get("message", "No message")

    print(f"   Latest Run: {_run_status_icon(status)} {status} ({run_id})")
    print(f"   Created: {created_at}")
    print(f"   Message: {message}")

    if verbose and status == "errored":
        _print_errored_run_logs(api, run_info)


def _run_status_icon(status: str) -> str:
    return {
        "planned": "📋",
        "planning": "⏳",
        "applied": "✅",
        "applying": "⚙️",
        "errored": "❌",
        "canceled": "⏹️",
        "pending": "⏸️",
    }.get(status, "❓")


def _print_errored_run_logs(api: TerraformCloudAPI, run_info: dict) -> None:
    plan_rel = run_info["relationships"].get("plan", {}).get("data")
    if not plan_rel:
        return

    plan_id = plan_rel["id"]
    print("   \n   📝 Error logs:")
    logs = api.get_plan_logs(plan_id)

    log_lines = logs.split("\n")[-10:]
    for line in log_lines:
        if line.strip():
            print(f"      {line}")


def trigger_test_runs(api: TerraformCloudAPI, workspace_names: List[str]):
    """Trigger test runs in workspaces"""

    print(f"🚀 Triggering test runs in {len(workspace_names)} workspace(s)...\n")
    run_ids = _trigger_runs_for_workspaces(api, workspace_names)

    if not run_ids:
        return

    print("\n⏳ Waiting for runs to complete...")
    _wait_for_runs_to_complete(api, run_ids)
    print("\n🎉 All runs completed!")


def _trigger_runs_for_workspaces(
    api: TerraformCloudAPI, workspace_names: List[str]
) -> Dict[str, str]:
    run_ids: Dict[str, str] = {}

    for workspace_name in workspace_names:
        workspace = api.get_workspace(workspace_name)
        if not workspace:
            print(f"   ❌ {workspace_name}: Workspace not found")
            continue

        workspace_id = workspace["id"]
        try:
            run_id = api.trigger_run(
                workspace_id,
                "Test run for workspace validation - "
                + datetime.now().strftime("%Y-%m-%d %H:%M"),
            )
            run_ids[workspace_name] = run_id
            print(f"   ✅ {workspace_name}: Run started ({run_id})")
        except Exception as e:
            print(f"   ❌ {workspace_name}: Failed to start run - {e}")

    return run_ids


def _wait_for_runs_to_complete(api: TerraformCloudAPI, run_ids: Dict[str, str]) -> None:
    while run_ids:
        time.sleep(10)
        completed = []

        for workspace_name, run_id in run_ids.items():
            run_info = api.get_run_status(run_id)
            status = run_info["attributes"]["status"]

            if not _is_terminal_run_status(status):
                continue

            print(f"   {_terminal_status_icon(status)} {workspace_name}: {status}")
            completed.append(workspace_name)

        for workspace_name in completed:
            del run_ids[workspace_name]


def _is_terminal_run_status(status: str) -> bool:
    return status in {"applied", "errored", "canceled", "discarded"}


def _terminal_status_icon(status: str) -> str:
    return {
        "applied": "✅",
        "errored": "❌",
        "canceled": "⏹️",
        "discarded": "🗑️",
    }.get(status, "❓")


def main():
    parser = argparse.ArgumentParser(
        description="Check HCP Terraform workspace status and run tests"
    )
    parser.add_argument(
        "--token",
        help="HCP Terraform API token (or set TFC_TOKEN env var)",
    )
    parser.add_argument(
        "--workspaces",
        nargs="+",
        default=[
            "aheadlabs-com-production",
            "aheadlabs-com-staging",
            "ai-assistant-production",
            "ai-assistant-staging",
            "apps-aheadlabs-com-production",
            "apps-aheadlabs-com-staging",
            "automations-production",
            "automations-staging",
            "campus-aheadlabs-com-production",
            "campus-aheadlabs-com-staging",
            "core-infrastructure-production",
            "core-infrastructure-shared",
            "core-infrastructure-staging",
            "ladichosa-es-production",
            "ladichosa-es-staging",
            "monitoring-production",
            "monitoring-staging",
            "services-aheadlabs-com-production",
            "services-aheadlabs-com-staging",
            "signatus-production",
            "signatus-staging"
        ],
        help="Workspace names to check",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed error logs",
    )
    parser.add_argument(
        "--trigger-runs",
        action="store_true",
        help="Trigger test runs in all workspaces",
    )
    
    args = parser.parse_args()
    
    # Get token
    token = args.token or os.environ.get("TFC_TOKEN")
    if not token:
        print("❌ Error: No API token provided")
        print("   Use --token YOUR_TOKEN or set TFC_TOKEN environment variable")
        sys.exit(1)
    
    # Initialize API client
    api = TerraformCloudAPI(token)
    
    try:
        if args.trigger_runs:
            trigger_test_runs(api, args.workspaces)
        else:
            check_workspaces(api, args.workspaces, args.verbose)
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
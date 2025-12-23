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
        print(f"📊 {workspace_name}")
        print("=" * (len(workspace_name) + 4))
        
        workspace = api.get_workspace(workspace_name)
        if not workspace:
            print("   ❌ Workspace not found")
            print()
            continue
        
        # Basic workspace info
        attrs = workspace["attributes"]
        print(f"   Status: {'🔒 Locked' if attrs['locked'] else '🔓 Unlocked'}")
        print(f"   Terraform: {attrs['terraform-version']}")
        print(f"   Working Dir: {attrs['working-directory']}")
        
        # VCS info
        vcs_repo = attrs.get("vcs-repo")
        if vcs_repo:
            print(f"   VCS: {vcs_repo['identifier']} (branch: {vcs_repo['branch']})")
            print(f"   Submodules: {'✅ Yes' if vcs_repo.get('ingress-submodules', False) else '❌ No'}")
        else:
            print("   VCS: ❌ Not connected")
        
        # Latest run info
        current_run = workspace["relationships"].get("current-run", {}).get("data")
        if current_run:
            run_id = current_run["id"]
            run_info = api.get_run_status(run_id)
            run_attrs = run_info["attributes"]
            
            status = run_attrs["status"]
            created_at = run_attrs["created-at"]
            message = run_attrs.get("message", "No message")
            
            status_icon = {
                "planned": "📋",
                "planning": "⏳",
                "applied": "✅",
                "applying": "⚙️",
                "errored": "❌",
                "canceled": "⏹️",
                "pending": "⏸️"
            }.get(status, "❓")
            
            print(f"   Latest Run: {status_icon} {status} ({run_id})")
            print(f"   Created: {created_at}")
            print(f"   Message: {message}")
            
            if verbose and status == "errored":
                # Get plan details for error
                plan_rel = run_info["relationships"].get("plan", {}).get("data")
                if plan_rel:
                    plan_id = plan_rel["id"]
                    print(f"   \n   📝 Error logs:")
                    logs = api.get_plan_logs(plan_id)
                    # Show last few lines of logs
                    log_lines = logs.split('\n')[-10:]
                    for line in log_lines:
                        if line.strip():
                            print(f"      {line}")
        else:
            print("   Latest Run: 📋 No runs")
        
        print()


def trigger_test_runs(api: TerraformCloudAPI, workspace_names: List[str]):
    """Trigger test runs in workspaces"""
    
    print(f"🚀 Triggering test runs in {len(workspace_names)} workspace(s)...\n")
    
    run_ids = {}
    
    for workspace_name in workspace_names:
        workspace = api.get_workspace(workspace_name)
        if not workspace:
            print(f"   ❌ {workspace_name}: Workspace not found")
            continue
        
        workspace_id = workspace["id"]
        try:
            run_id = api.trigger_run(workspace_id, f"Test run for workspace validation - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            run_ids[workspace_name] = run_id
            print(f"   ✅ {workspace_name}: Run started ({run_id})")
        except Exception as e:
            print(f"   ❌ {workspace_name}: Failed to start run - {e}")
    
    if run_ids:
        print(f"\n⏳ Waiting for runs to complete...")
        
        # Wait for completion
        while run_ids:
            time.sleep(10)
            completed = []
            
            for workspace_name, run_id in run_ids.items():
                run_info = api.get_run_status(run_id)
                status = run_info["attributes"]["status"]
                
                if status in ["applied", "errored", "canceled", "discarded"]:
                    status_icon = {
                        "applied": "✅",
                        "errored": "❌",
                        "canceled": "⏹️",
                        "discarded": "🗑️"
                    }.get(status, "❓")
                    
                    print(f"   {status_icon} {workspace_name}: {status}")
                    completed.append(workspace_name)
            
            for workspace_name in completed:
                del run_ids[workspace_name]
        
        print("\n🎉 All runs completed!")


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
#!/usr/bin/env python3
"""
Trigger runs in all HCP Terraform workspaces.

This script triggers plan/apply runs across all workspaces in the organization,
providing a similar experience to `terragrunt run-all apply` but compatible
with HCP Terraform cloud workspaces.

Usage:
    python trigger-all-runs.py [--apply] [--filter PATTERN] [--dry-run]

Options:
    --apply     Auto-apply runs (default: plan only)
    --filter    Filter workspaces by name pattern (e.g., "production", "staging")
    --dry-run   Show what would be triggered without actually triggering
    --confirm   Skip confirmation prompt
"""

import json
import os
import sys
import time
import argparse
import urllib.request
from urllib.parse import quote, urlencode, urljoin, urlparse
from datetime import datetime


API_BASE_URL = "https://app.terraform.io/api/v2/"
UI_BASE_URL = "https://app.terraform.io/"


def _build_api_url(endpoint: str) -> str:
    endpoint = str(endpoint or "").strip()
    if not endpoint:
        raise ValueError("endpoint is required")

    url = urljoin(API_BASE_URL, endpoint.lstrip("/"))
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "app.terraform.io":
        raise ValueError("Invalid API endpoint")
    if not parsed.path.startswith("/api/v2/"):
        raise ValueError("Invalid API endpoint")
    return url


def _quote_path_segment(value: str) -> str:
    return quote(str(value), safe="")


def _org_workspaces_endpoint(org: str, page: int, page_size: int = 50) -> str:
    org_segment = _quote_path_segment(org)
    query = urlencode({"page[number]": page, "page[size]": page_size})
    return f"/organizations/{org_segment}/workspaces?{query}"


def _runs_endpoint(run_id: str) -> str:
    return f"/runs/{_quote_path_segment(run_id)}"


def _ui_run_url(org: str, workspace_name: str, run_id: str) -> str:
    org_segment = _quote_path_segment(org)
    workspace_segment = _quote_path_segment(workspace_name)
    run_segment = _quote_path_segment(run_id)
    return f"{UI_BASE_URL}app/{org_segment}/workspaces/{workspace_segment}/runs/{run_segment}"


def get_token():
    """Get HCP Terraform token from credentials file."""
    creds_file = os.path.expanduser("~/.terraform.d/credentials.tfrc.json")
    if not os.path.exists(creds_file):
        print("❌ Error: No credentials file found at ~/.terraform.d/credentials.tfrc.json")
        sys.exit(1)
    
    with open(creds_file) as f:
        creds = json.load(f)
    
    return creds["credentials"]["app.terraform.io"]["token"]


def api_request(endpoint, token, method="GET", data=None):
    """Make an API request to HCP Terraform."""
    url = _build_api_url(endpoint)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json"
    }
    
    req = urllib.request.Request(url, headers=headers, method=method)
    
    if data:
        req.data = json.dumps(data).encode("utf-8")
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"❌ API Error: {e.code} - {error_body}")
        return None


def get_all_workspaces(token, org="aheadlabs"):
    """Get all workspaces in the organization."""
    workspaces = []
    page = 1
    
    while True:
        endpoint = _org_workspaces_endpoint(org, page=page, page_size=50)
        result = api_request(endpoint, token)
        
        if not result:
            break
        
        workspaces.extend(result["data"])
        
        # Check for more pages
        if result.get("meta", {}).get("pagination", {}).get("next-page"):
            page += 1
        else:
            break
    
    return workspaces


def trigger_run(token, workspace_id, auto_apply=False, message=None):
    """Trigger a run in a workspace."""
    if message is None:
        message = f"Triggered by trigger-all-runs.py at {datetime.now().isoformat()}"
    
    data = {
        "data": {
            "attributes": {
                "message": message,
                "auto-apply": auto_apply
            },
            "relationships": {
                "workspace": {
                    "data": {
                        "type": "workspaces",
                        "id": workspace_id
                    }
                }
            },
            "type": "runs"
        }
    }
    
    result = api_request("/runs", token, method="POST", data=data)
    
    if result:
        run_id = result["data"]["id"]
        return run_id
    return None


def get_run_status(token, run_id):
    """Get the status of a run."""
    result = api_request(_runs_endpoint(run_id), token)
    if result:
        return result["data"]["attributes"]["status"]
    return None


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Trigger runs in all HCP Terraform workspaces"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Auto-apply runs (default: plan only)"
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Filter workspaces by name pattern"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be triggered without actually triggering"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for all runs to complete"
    )
    parser.add_argument(
        "--exclude",
        type=str,
        help="Exclude workspaces matching pattern"
    )
    return parser.parse_args()


def _print_header():
    print("=" * 60)
    print("🚀 HCP Terraform - Trigger All Runs")
    print("=" * 60)


def _filter_and_sort_workspaces(workspaces, include_pattern=None, exclude_pattern=None):
    if include_pattern:
        include_lower = include_pattern.lower()
        workspaces = [
            w for w in workspaces
            if include_lower in w["attributes"]["name"].lower()
        ]

    if exclude_pattern:
        exclude_lower = exclude_pattern.lower()
        workspaces = [
            w for w in workspaces
            if exclude_lower not in w["attributes"]["name"].lower()
        ]

    return sorted(workspaces, key=lambda w: w["attributes"]["name"])


def _print_workspace_list(workspaces):
    print(f"\n📋 Found {len(workspaces)} workspaces")
    print("-" * 60)

    for ws in workspaces:
        name = ws["attributes"]["name"]
        vcs = "VCS" if ws["attributes"].get("vcs-repo") else "CLI"
        print(f"   • {name} ({vcs})")

    print("-" * 60)


def _print_mode(auto_apply):
    mode = "🔴 AUTO-APPLY" if auto_apply else "🟡 PLAN ONLY"
    print(f"\n⚙️  Mode: {mode}")


def _confirm_or_abort(run_count, skip_confirmation):
    if skip_confirmation:
        return True

    print(f"\n⚠️  This will trigger {run_count} runs.")
    response = input("Continue? [y/N]: ")
    if response.lower() != "y":
        print("❌ Aborted")
        return False
    return True


def _trigger_runs(token, workspaces, auto_apply):
    print("\n🚀 Triggering runs...")
    print("-" * 60)

    triggered_runs = []

    for ws in workspaces:
        ws_id = ws["id"]
        ws_name = ws["attributes"]["name"]

        run_id = trigger_run(token, ws_id, auto_apply=auto_apply)

        if run_id:
            print(f"   ✅ {ws_name}: {run_id}")
            triggered_runs.append({"name": ws_name, "run_id": run_id})
        else:
            print(f"   ❌ {ws_name}: Failed to trigger")

    print("-" * 60)
    print(f"\n✅ Triggered {len(triggered_runs)}/{len(workspaces)} runs")
    return triggered_runs


def _wait_for_runs_to_complete(token, triggered_runs, org):
    if not triggered_runs:
        return

    print("\n⏳ Waiting for runs to complete...")
    print("-" * 60)

    pending = list(triggered_runs)
    completed = []
    failed = []

    while pending:
        time.sleep(10)  # Poll every 10 seconds

        still_pending = []
        for run in pending:
            status = get_run_status(token, run["run_id"])

            if status in ["planned", "applied", "planned_and_finished"]:
                completed.append(run)
                print(f"   ✅ {run['name']}: {status}")
            elif status in ["errored", "canceled", "force_canceled", "discarded"]:
                failed.append(run)
                print(f"   ❌ {run['name']}: {status}")
            else:
                still_pending.append(run)

        pending = still_pending

        if pending:
            print(f"   ⏳ {len(pending)} runs still in progress...")

    print("-" * 60)
    print("\n📊 Results:")
    print(f"   ✅ Completed: {len(completed)}")
    print(f"   ❌ Failed: {len(failed)}")

    if failed:
        print("\n❌ Failed runs:")
        for run in failed:
            print(f"   • {run['name']}: {_ui_run_url(org, run['name'], run['run_id'])}")


def _print_run_urls(triggered_runs, org):
    print("\n🔗 Run URLs:")
    for run in triggered_runs:
        print(f"   {_ui_run_url(org, run['name'], run['run_id'])}")


def main():
    org = "aheadlabs"
    args = _parse_args()

    _print_header()

    token = get_token()
    workspaces = get_all_workspaces(token, org=org)
    workspaces = _filter_and_sort_workspaces(
        workspaces,
        include_pattern=args.filter,
        exclude_pattern=args.exclude,
    )

    _print_workspace_list(workspaces)
    _print_mode(args.apply)

    if args.dry_run:
        print("\n🔍 DRY RUN - No runs will be triggered")
        return

    if not _confirm_or_abort(len(workspaces), skip_confirmation=args.confirm):
        return

    triggered_runs = _trigger_runs(token, workspaces, auto_apply=args.apply)
    if args.wait:
        _wait_for_runs_to_complete(token, triggered_runs, org=org)

    _print_run_urls(triggered_runs, org=org)


if __name__ == "__main__":
    main()

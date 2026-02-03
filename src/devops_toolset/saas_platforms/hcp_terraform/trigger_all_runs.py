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
from urllib.parse import urljoin, urlparse
from datetime import datetime


API_BASE_URL = "https://app.terraform.io/api/v2/"


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
        endpoint = f"/organizations/{org}/workspaces?page%5Bnumber%5D={page}&page%5Bsize%5D=50"
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


def trigger_run(token, workspace_id, workspace_name, auto_apply=False, message=None):
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
    result = api_request(f"/runs/{run_id}", token)
    if result:
        return result["data"]["attributes"]["status"]
    return None


def main():
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
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 HCP Terraform - Trigger All Runs")
    print("=" * 60)
    
    token = get_token()
    workspaces = get_all_workspaces(token)
    
    # Filter workspaces
    if args.filter:
        workspaces = [w for w in workspaces if args.filter.lower() in w["attributes"]["name"].lower()]
    
    if args.exclude:
        workspaces = [w for w in workspaces if args.exclude.lower() not in w["attributes"]["name"].lower()]
    
    # Sort by name
    workspaces = sorted(workspaces, key=lambda w: w["attributes"]["name"])
    
    print(f"\n📋 Found {len(workspaces)} workspaces")
    print("-" * 60)
    
    for ws in workspaces:
        name = ws["attributes"]["name"]
        vcs = "VCS" if ws["attributes"].get("vcs-repo") else "CLI"
        print(f"   • {name} ({vcs})")
    
    print("-" * 60)
    
    mode = "🔴 AUTO-APPLY" if args.apply else "🟡 PLAN ONLY"
    print(f"\n⚙️  Mode: {mode}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No runs will be triggered")
        return
    
    # Confirmation
    if not args.confirm:
        print(f"\n⚠️  This will trigger {len(workspaces)} runs.")
        response = input("Continue? [y/N]: ")
        if response.lower() != "y":
            print("❌ Aborted")
            return
    
    # Trigger runs
    print("\n🚀 Triggering runs...")
    print("-" * 60)
    
    triggered_runs = []
    
    for ws in workspaces:
        ws_id = ws["id"]
        ws_name = ws["attributes"]["name"]
        
        run_id = trigger_run(token, ws_id, ws_name, auto_apply=args.apply)
        
        if run_id:
            print(f"   ✅ {ws_name}: {run_id}")
            triggered_runs.append({"name": ws_name, "run_id": run_id})
        else:
            print(f"   ❌ {ws_name}: Failed to trigger")
    
    print("-" * 60)
    print(f"\n✅ Triggered {len(triggered_runs)}/{len(workspaces)} runs")
    
    # Wait for completion if requested
    if args.wait and triggered_runs:
        print("\n⏳ Waiting for runs to complete...")
        print("-" * 60)
        
        pending = triggered_runs.copy()
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
        print(f"\n📊 Results:")
        print(f"   ✅ Completed: {len(completed)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        if failed:
            print("\n❌ Failed runs:")
            for run in failed:
                print(f"   • {run['name']}: https://app.terraform.io/app/aheadlabs/workspaces/{run['name']}/runs/{run['run_id']}")
    
    # Print URLs
    print("\n🔗 Run URLs:")
    for run in triggered_runs:
        print(f"   https://app.terraform.io/app/aheadlabs/workspaces/{run['name']}/runs/{run['run_id']}")


if __name__ == "__main__":
    main()

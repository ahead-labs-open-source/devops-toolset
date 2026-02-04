#!/usr/bin/env python3
"""
Enable Git submodules for HCP Terraform workspaces.

This script enables the "Include submodules on clone" setting for workspaces
that use the iac-toolset submodule. This is required for workspaces to access
shared Terraform modules.

Requirements:
    pip install requests

Usage:
    python enable-submodules.py --token <HCP_TOKEN>
    python enable-submodules.py --token <HCP_TOKEN> --dry-run
    python enable-submodules.py --token $(cat ../../terraform.token)
    python enable-submodules.py --token-file ../../terraform.token --workspace core-infrastructure-staging
"""

import argparse
import json
import sys
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)


class HCPTerraformClient:
    """Client for HCP Terraform API operations."""
    
    def __init__(self, token: str, organization: str = "aheadlabs"):
        self.token = token
        self.organization = organization
        self.base_url = "https://app.terraform.io/api/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json"
        }
    
    def list_workspaces(self) -> List[Dict]:
        """List all workspaces in the organization."""
        url = f"{self.base_url}/organizations/{self.organization}/workspaces"
        workspaces = []
        
        while url:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            workspaces.extend(data.get("data", []))
            
            # Handle pagination
            next_url = data.get("links", {}).get("next")
            url = f"{self.base_url}{next_url}" if next_url else None
        
        return workspaces
    
    def get_workspace(self, workspace_name: str) -> Optional[Dict]:
        """Get a specific workspace."""
        url = f"{self.base_url}/organizations/{self.organization}/workspaces/{workspace_name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return response.json().get("data")
    
    def enable_submodules(self, workspace_name: str) -> bool:
        """Enable submodules for a workspace."""
        # Get workspace ID first
        workspace = self.get_workspace(workspace_name)
        if not workspace:
            raise ValueError(f"Workspace '{workspace_name}' not found")
        
        workspace_id = workspace["id"]
        
        # Update workspace to enable submodules
        payload = {
            "data": {
                "type": "workspaces",
                "attributes": {
                    "vcs-repo": {
                        **workspace["attributes"].get("vcs-repo", {}),
                        "ingress-submodules": True
                    }
                }
            }
        }
        
        url = f"{self.base_url}/workspaces/{workspace_id}"
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return True


def _load_token_from_file(token_file: str) -> str:
    with open(token_file, "r", encoding="utf-8") as f:
        return f.read().strip()


def _get_token(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    if args.token_file:
        try:
            return _load_token_from_file(args.token_file)
        except FileNotFoundError:
            print(f"Error: Token file '{args.token_file}' not found")
            raise SystemExit(1)
    if args.token:
        return args.token

    print("Error: Either --token or --token-file is required")
    parser.print_help()
    raise SystemExit(1)


def _get_workspaces_to_process(client: HCPTerraformClient, args: argparse.Namespace) -> List[Dict]:
    if args.workspace:
        workspace_data = client.get_workspace(args.workspace)
        if not workspace_data:
            print(f"Error: Workspace '{args.workspace}' not found")
            raise SystemExit(1)
        return [workspace_data]

    print("Fetching workspaces...")
    workspaces = client.list_workspaces()
    print(f"Found {len(workspaces)} workspaces")
    print()
    return workspaces


def _init_results() -> Dict[str, List]:
    return {
        "enabled": [],
        "already_enabled": [],
        "no_vcs": [],
        "errors": [],
    }


def _handle_workspace(
    *,
    client: HCPTerraformClient,
    workspace: Dict,
    verify_only: bool,
    dry_run: bool,
    results: Dict[str, List],
) -> None:
    name = workspace["attributes"]["name"]
    vcs_repo = workspace["attributes"].get("vcs-repo")

    if not vcs_repo:
        results["no_vcs"].append(name)
        print(f"⚠️  {name}: No VCS connection (skipped)")
        return

    submodules_enabled = bool(vcs_repo.get("ingress-submodules", False))
    if submodules_enabled:
        results["already_enabled"].append(name)
        print(f"✅ {name}: Submodules already enabled")
        return

    if verify_only:
        results["enabled"].append(name)
        print(f"❌ {name}: Submodules NOT enabled")
        return

    if dry_run:
        results["enabled"].append(name)
        print(f"🔄 {name}: Would enable submodules (dry run)")
        return

    try:
        client.enable_submodules(name)
        results["enabled"].append(name)
        print(f"✅ {name}: Submodules enabled")
    except Exception as e:
        results["errors"].append({"workspace": name, "error": str(e)})
        print(f"❌ {name}: Error - {e}")


def _print_summary(results: Dict[str, List], *, dry_run: bool, verify_only: bool) -> None:
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Already enabled: {len(results['already_enabled'])}")
    enabled_label = "Would enable" if dry_run or verify_only else "Enabled"
    print(f"{enabled_label}: {len(results['enabled'])}")
    print(f"No VCS connection: {len(results['no_vcs'])}")
    print(f"Errors: {len(results['errors'])}")

    if results["enabled"] and not verify_only:
        print()
        print(f"{enabled_label} submodules for:")
        for name in results["enabled"]:
            print(f"  • {name}")

    if results["errors"]:
        print()
        print("Errors occurred:")
        for error in results["errors"]:
            print(f"  • {error['workspace']}: {error['error']}")

    if dry_run:
        print()
        print("This was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply changes.")
    elif verify_only:
        print()
        print("Verification complete. No changes were made.")
    else:
        print()
        print("✅ Configuration complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Enable Git submodules for HCP Terraform workspaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be changed
  %(prog)s --token <token> --dry-run
  
  # Enable submodules for all workspaces
  %(prog)s --token <token>
  
  # Enable for specific workspace only
  %(prog)s --token <token> --workspace core-infrastructure-staging
  
  # Use token from file
  %(prog)s --token-file ../../terraform.token
        """
    )
    
    parser.add_argument(
        "--token",
        help="HCP Terraform API token"
    )
    parser.add_argument(
        "--token-file",
        help="File containing HCP Terraform API token"
    )
    parser.add_argument(
        "--organization",
        default="aheadlabs",
        help="HCP Terraform organization (default: aheadlabs)"
    )
    parser.add_argument(
        "--workspace",
        help="Specific workspace to update (default: all workspaces)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify current submodule settings, don't make changes"
    )
    
    args = parser.parse_args()
    
    token = _get_token(args, parser)
    
    # Initialize client
    client = HCPTerraformClient(token, args.organization)
    
    print("=" * 60)
    print("HCP Terraform Submodules Configuration")
    print("=" * 60)
    print(f"Organization: {args.organization}")

    if args.dry_run:
        mode = "DRY RUN"
    elif args.verify_only:
        mode = "VERIFY ONLY"
    else:
        mode = "APPLY CHANGES"
    print(f"Mode: {mode}")
    print()
    
    try:
        workspaces = _get_workspaces_to_process(client, args)
        
        # Process workspaces
        results = _init_results()
        
        for workspace in workspaces:
            _handle_workspace(
                client=client,
                workspace=workspace,
                verify_only=args.verify_only,
                dry_run=args.dry_run,
                results=results,
            )

        _print_summary(results, dry_run=args.dry_run, verify_only=args.verify_only)
        
        # Exit code based on results
        if results["errors"]:
            raise SystemExit(1)
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response.status_code == 401:
            print("Authentication failed. Check your API token.")
        raise SystemExit(1)
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

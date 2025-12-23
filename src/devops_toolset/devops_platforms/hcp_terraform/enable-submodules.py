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
        url = f"{self.base_url}/workspaces/{workspace_name}"
        
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
    
    # Get token
    if args.token_file:
        try:
            with open(args.token_file, 'r') as f:
                token = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Token file '{args.token_file}' not found")
            sys.exit(1)
    elif args.token:
        token = args.token
    else:
        print("Error: Either --token or --token-file is required")
        parser.print_help()
        sys.exit(1)
    
    # Initialize client
    client = HCPTerraformClient(token, args.organization)
    
    print("=" * 60)
    print("HCP Terraform Submodules Configuration")
    print("=" * 60)
    print(f"Organization: {args.organization}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'VERIFY ONLY' if args.verify_only else 'APPLY CHANGES'}")
    print()
    
    try:
        # Get workspaces to process
        if args.workspace:
            workspace_data = client.get_workspace(args.workspace)
            if not workspace_data:
                print(f"Error: Workspace '{args.workspace}' not found")
                sys.exit(1)
            workspaces = [workspace_data]
        else:
            print("Fetching workspaces...")
            workspaces = client.list_workspaces()
            print(f"Found {len(workspaces)} workspaces")
            print()
        
        # Process workspaces
        results = {
            "enabled": [],
            "already_enabled": [],
            "no_vcs": [],
            "errors": []
        }
        
        for workspace in workspaces:
            name = workspace["attributes"]["name"]
            vcs_repo = workspace["attributes"].get("vcs-repo")
            
            # Skip workspaces without VCS connection
            if not vcs_repo:
                results["no_vcs"].append(name)
                print(f"⚠️  {name}: No VCS connection (skipped)")
                continue
            
            submodules_enabled = vcs_repo.get("ingress-submodules", False)
            
            if submodules_enabled:
                results["already_enabled"].append(name)
                print(f"✅ {name}: Submodules already enabled")
            else:
                if args.verify_only:
                    results["enabled"].append(name)
                    print(f"❌ {name}: Submodules NOT enabled")
                elif args.dry_run:
                    results["enabled"].append(name)
                    print(f"🔄 {name}: Would enable submodules (dry run)")
                else:
                    try:
                        client.enable_submodules(name)
                        results["enabled"].append(name)
                        print(f"✅ {name}: Submodules enabled")
                    except Exception as e:
                        results["errors"].append({"workspace": name, "error": str(e)})
                        print(f"❌ {name}: Error - {e}")
        
        # Summary
        print()
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Already enabled: {len(results['already_enabled'])}")
        print(f"{'Would enable' if args.dry_run or args.verify_only else 'Enabled'}: {len(results['enabled'])}")
        print(f"No VCS connection: {len(results['no_vcs'])}")
        print(f"Errors: {len(results['errors'])}")
        
        if results["enabled"] and not args.verify_only:
            print()
            print(f"{'Would enable' if args.dry_run else 'Enabled'} submodules for:")
            for name in results["enabled"]:
                print(f"  • {name}")
        
        if results["errors"]:
            print()
            print("Errors occurred:")
            for error in results["errors"]:
                print(f"  • {error['workspace']}: {error['error']}")
        
        if args.dry_run:
            print()
            print("This was a DRY RUN. No changes were made.")
            print("Run without --dry-run to apply changes.")
        elif args.verify_only:
            print()
            print("Verification complete. No changes were made.")
        else:
            print()
            print("✅ Configuration complete!")
        
        # Exit code based on results
        if results["errors"]:
            sys.exit(1)
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response.status_code == 401:
            print("Authentication failed. Check your API token.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

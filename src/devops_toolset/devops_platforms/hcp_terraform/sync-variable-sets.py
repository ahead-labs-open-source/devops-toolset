#!/usr/bin/env python3
"""
HCP Terraform Variable Set Association Manager

This script manages the association of variable sets to workspaces in HCP Terraform,
following the principle of least privilege.

Usage:
    python sync-variable-sets.py --token YOUR_TOKEN [--dry-run]
    python sync-variable-sets.py --verify-only
    
Environment Variables:
    TFC_TOKEN - HCP Terraform API token (alternative to --token)
"""

import argparse
import os
import sys
from typing import Dict, List, Set
import requests


# Configuration
ORGANIZATION = "aheadlabs"
API_BASE_URL = "https://app.terraform.io/api/v2"

# Workspace to cloud provider mapping
WORKSPACE_CONFIG = {
    # Core infrastructure - uses both Azure and AWS
    "core-infrastructure-staging": {"azure", "azure-db", "aws"},
    "core-infrastructure-production": {"azure", "azure-db", "aws"},
    "core-infrastructure-shared": {"azure", "azure-db"},
    
    # Monitoring - Azure only (no DB needed)
    "monitoring-staging": {"azure"},
    "monitoring-production": {"azure"},
    
    # Automations - Azure only (no DB needed)
    "automations-staging": {"azure"},
    "automations-production": {"azure"},
    
    # AI Assistant - Azure only (may need DB in future)
    "ai-assistant-staging": {"azure", "azure-db"},
    "ai-assistant-production": {"azure", "azure-db"},
    
    # Signatus - Azure only (needs DB access)
    "signatus-staging": {"azure", "azure-db"},
    "signatus-production": {"azure", "azure-db"},
    
    # Campus - Azure only (needs DB access)
    "campus-aheadlabs-com-staging": {"azure", "azure-db"},
    "campus-aheadlabs-com-production": {"azure", "azure-db"},
    
    # Ahead Labs website - Azure + AWS (temporary, needs DB access)
    "aheadlabs-com-staging": {"azure", "azure-db", "aws"},
    "aheadlabs-com-production": {"azure", "azure-db", "aws"},
    
    # Ladichosa website - Azure + AWS (temporary, needs DB access)
    "ladichosa-es-staging": {"azure", "azure-db", "aws"},
    "ladichosa-es-production": {"azure", "azure-db", "aws"},
    
    # Corporate Apps - Azure only (needs DB access)
    "apps-aheadlabs-com-staging": {"azure", "azure-db"},
    "apps-aheadlabs-com-production": {"azure", "azure-db"},
    
    # Commercial Services - Azure only (needs DB access)
    "services-aheadlabs-com-staging": {"azure", "azure-db"},
    "services-aheadlabs-com-production": {"azure", "azure-db"},
}

# Variable set name mapping
VARIABLE_SETS = {
    "azure": "Azure credentials",
    "azure-db": "Azure database credentials",
    "aws": "AWS credentials",
}


class TerraformCloudAPI:
    """HCP Terraform API client"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }
    
    def get_workspaces(self) -> Dict[str, str]:
        """Get all workspaces in the organization"""
        url = f"{API_BASE_URL}/organizations/{ORGANIZATION}/workspaces"
        workspaces = {}
        
        while url:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            for workspace in data["data"]:
                workspaces[workspace["attributes"]["name"]] = workspace["id"]
            
            # Handle pagination
            url = data.get("links", {}).get("next")
        
        return workspaces
    
    def get_variable_sets(self) -> Dict[str, dict]:
        """Get all variable sets in the organization with their metadata"""
        url = f"{API_BASE_URL}/organizations/{ORGANIZATION}/varsets"
        varsets = {}
        
        while url:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            for varset in data["data"]:
                varsets[varset["attributes"]["name"]] = {
                    "id": varset["id"],
                    "global": varset["attributes"].get("global", False),
                }
            
            url = data.get("links", {}).get("next")
        
        return varsets
    
    def get_varset_workspaces(self, varset_id: str) -> Set[str]:
        """Get workspaces associated with a variable set"""
        # Get variable set details with workspace relationships included
        url = f"{API_BASE_URL}/varsets/{varset_id}?include=workspaces"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            print(f"⚠️  Variable set {varset_id} not found")
            return set()
        
        response.raise_for_status()
        data = response.json()
        
        # Extract workspace IDs from relationships
        workspace_ids = set()
        if "data" in data and "relationships" in data["data"]:
            workspaces_rel = data["data"]["relationships"].get("workspaces", {})
            if "data" in workspaces_rel and workspaces_rel["data"]:
                workspace_ids = {ws["id"] for ws in workspaces_rel["data"]}
        
        return workspace_ids
    
    def associate_workspace(self, varset_id: str, workspace_id: str):
        """Associate a workspace with a variable set"""
        url = f"{API_BASE_URL}/varsets/{varset_id}/relationships/workspaces"
        payload = {
            "data": [{"id": workspace_id, "type": "workspaces"}]
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
    
    def disassociate_workspace(self, varset_id: str, workspace_id: str):
        """Disassociate a workspace from a variable set"""
        url = f"{API_BASE_URL}/varsets/{varset_id}/relationships/workspaces"
        payload = {
            "data": [{"id": workspace_id, "type": "workspaces"}]
        }
        response = requests.delete(url, headers=self.headers, json=payload)
        response.raise_for_status()
    
    def set_global_scope(self, varset_id: str, global_scope: bool):
        """Set or unset global scope for a variable set"""
        url = f"{API_BASE_URL}/varsets/{varset_id}"
        payload = {
            "data": {
                "id": varset_id,
                "type": "varsets",
                "attributes": {
                    "global": global_scope
                }
            }
        }
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()


def calculate_changes(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varsets: Dict[str, dict]
) -> Dict[str, Dict[str, List[str]]]:
    """Calculate required changes to variable set associations"""
    
    # Dynamically create changes dict for all providers
    changes = {
        provider: {"add": [], "remove": []}
        for provider in VARIABLE_SETS.keys()
    }
    
    for provider, varset_name in VARIABLE_SETS.items():
        if varset_name not in varsets:
            print(f"⚠️  Variable set '{varset_name}' not found!")
            continue
        
        varset_info = varsets[varset_name]
        varset_id = varset_info["id"]
        
        # If variable set is global, we can't check individual associations
        # All workspaces already have access
        if varset_info["global"]:
            continue
        
        current_associations = api.get_varset_workspaces(varset_id)
        
        for workspace_name, workspace_id in workspaces.items():
            if workspace_name not in WORKSPACE_CONFIG:
                continue
            
            should_have = provider in WORKSPACE_CONFIG[workspace_name]
            currently_has = workspace_id in current_associations
            
            if should_have and not currently_has:
                changes[provider]["add"].append(workspace_name)
            elif not should_have and currently_has:
                changes[provider]["remove"].append(workspace_name)
    
    return changes


def apply_changes(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varsets: Dict[str, dict],
    changes: Dict[str, Dict[str, List[str]]],
    dry_run: bool = False
):
    """Apply the calculated changes"""
    
    total_changes = sum(
        len(changes[p]["add"]) + len(changes[p]["remove"])
        for p in changes
    )
    
    if total_changes == 0:
        print("✅ No changes needed - all associations are correct!")
        return
    
    print(f"\n{'DRY RUN - ' if dry_run else ''}Applying {total_changes} changes:\n")
    
    for provider, varset_name in VARIABLE_SETS.items():
        if varset_name not in varsets:
            continue
        
        varset_info = varsets[varset_name]
        varset_id = varset_info["id"]
        
        # Add associations
        for workspace_name in changes[provider]["add"]:
            workspace_id = workspaces[workspace_name]
            print(f"  ➕ Adding {varset_name} to {workspace_name}")
            if not dry_run:
                api.associate_workspace(varset_id, workspace_id)
        
        # Remove associations
        for workspace_name in changes[provider]["remove"]:
            workspace_id = workspaces[workspace_name]
            print(f"  ➖ Removing {varset_name} from {workspace_name}")
            if not dry_run:
                api.disassociate_workspace(varset_id, workspace_id)
    
    if dry_run:
        print("\n⚠️  This was a dry run. Use without --dry-run to apply changes.")
    else:
        print("\n✅ All changes applied successfully!")


def verify_configuration(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varsets: Dict[str, dict]
):
    """Verify current configuration and report status"""
    
    print(f"\n📋 Configuration Report for Organization: {ORGANIZATION}\n")
    print("=" * 80)
    
    # Check for global variable sets
    global_varsets = [name for name, info in varsets.items() if info["global"]]
    if global_varsets:
        print("\n🌍 Global Variable Sets (applied to ALL workspaces):")
        for vs in sorted(global_varsets):
            print(f"  - {vs}")
        print("\n⚠️  Global variable sets violate the principle of least privilege!")
        print("   Consider using --convert-to-workspace-specific to change this.")
    
    # Check for missing workspaces
    missing_workspaces = set(WORKSPACE_CONFIG.keys()) - set(workspaces.keys())
    if missing_workspaces:
        print("\n⚠️  Missing Workspaces (not found in HCP Terraform):")
        for ws in sorted(missing_workspaces):
            print(f"  - {ws}")
    
    # Check for missing variable sets
    missing_varsets = set(VARIABLE_SETS.values()) - set(varsets.keys())
    if missing_varsets:
        print("\n⚠️  Missing Variable Sets (not found in HCP Terraform):")
        for vs in sorted(missing_varsets):
            print(f"  - {vs}")
    
    # Show current associations
    print("\n📊 Current Variable Set Associations:\n")
    
    for provider, varset_name in VARIABLE_SETS.items():
        if varset_name not in varsets:
            continue
        
        print(f"\n{varset_name}:")
        print("-" * 40)
        
        varset_info = varsets[varset_name]
        varset_id = varset_info["id"]
        
        if varset_info["global"]:
            print("  🌍 GLOBAL - All workspaces have access")
            continue
        
        current_associations = api.get_varset_workspaces(varset_id)
        
        for workspace_name in sorted(WORKSPACE_CONFIG.keys()):
            if workspace_name not in workspaces:
                continue
            
            workspace_id = workspaces[workspace_name]
            should_have = provider in WORKSPACE_CONFIG[workspace_name]
            currently_has = workspace_id in current_associations
            
            if should_have and currently_has:
                status = "✅"
            elif should_have and not currently_has:
                status = "❌ MISSING"
            elif not should_have and currently_has:
                status = "⚠️  EXTRA"
            else:
                status = "⚪"
            
            if should_have or currently_has:
                print(f"  {status} {workspace_name}")
    
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Manage HCP Terraform variable set associations"
    )
    parser.add_argument(
        "--token",
        help="HCP Terraform API token (or set TFC_TOKEN env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify current configuration, don't make changes",
    )
    parser.add_argument(
        "--convert-to-workspace-specific",
        action="store_true",
        help="Convert global variable sets to workspace-specific associations",
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
        # Fetch current state
        print("🔍 Fetching workspaces and variable sets...")
        workspaces = api.get_workspaces()
        varsets = api.get_variable_sets()
        
        print(f"   Found {len(workspaces)} workspaces")
        print(f"   Found {len(varsets)} variable sets")
        
        # Handle global to workspace-specific conversion
        if args.convert_to_workspace_specific:
            global_varsets = [
                (name, info) for name, info in varsets.items() 
                if info["global"] and name in VARIABLE_SETS.values()
            ]
            
            if not global_varsets:
                print("\n✅ No global variable sets to convert!")
                return
            
            print(f"\n{'DRY RUN - ' if args.dry_run else ''}Converting {len(global_varsets)} variable sets from global to workspace-specific:\n")
            
            for varset_name, varset_info in global_varsets:
                print(f"  🔄 Converting '{varset_name}' to workspace-specific")
                if not args.dry_run:
                    api.set_global_scope(varset_info["id"], False)
                    
                    # Add associations for appropriate workspaces
                    provider = [p for p, vs in VARIABLE_SETS.items() if vs == varset_name][0]
                    for workspace_name, workspace_id in workspaces.items():
                        if workspace_name in WORKSPACE_CONFIG and provider in WORKSPACE_CONFIG[workspace_name]:
                            print(f"     ➕ Adding {workspace_name}")
                            if not args.dry_run:
                                api.associate_workspace(varset_info["id"], workspace_id)
            
            if args.dry_run:
                print("\n⚠️  This was a dry run. Use without --dry-run to apply changes.")
            else:
                print("\n✅ Conversion completed successfully!")
                print("   Run --verify-only to see the new configuration.")
            return
        
        if args.verify_only:
            verify_configuration(api, workspaces, varsets)
        else:
            # Calculate changes
            changes = calculate_changes(api, workspaces, varsets)
            
            # Apply changes
            apply_changes(api, workspaces, varsets, changes, dry_run=args.dry_run)
    
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        print(f"   Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

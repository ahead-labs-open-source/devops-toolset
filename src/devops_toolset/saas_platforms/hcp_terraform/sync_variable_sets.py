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
from typing import Dict, List, Optional, Set
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

    changes = _init_provider_changes()

    configured_workspaces = {
        workspace_name: workspace_id
        for workspace_name, workspace_id in workspaces.items()
        if workspace_name in WORKSPACE_CONFIG
    }

    for provider, varset_name in VARIABLE_SETS.items():
        varset_info = _get_varset_info_or_warn(varsets, varset_name)
        if varset_info is None:
            continue

        if varset_info.get("global"):
            continue

        varset_id = str(varset_info["id"])
        current_associations = api.get_varset_workspaces(varset_id)
        _update_provider_changes(
            provider,
            configured_workspaces,
            current_associations,
            changes,
        )

    return changes


def _init_provider_changes() -> Dict[str, Dict[str, List[str]]]:
    return {provider: {"add": [], "remove": []} for provider in VARIABLE_SETS.keys()}


def _get_varset_info_or_warn(varsets: Dict[str, dict], varset_name: str) -> Optional[dict]:
    if varset_name not in varsets:
        print(f"⚠️  Variable set '{varset_name}' not found!")
        return None
    return varsets[varset_name]


def _update_provider_changes(
    provider: str,
    configured_workspaces: Dict[str, str],
    current_associations: Set[str],
    changes: Dict[str, Dict[str, List[str]]],
) -> None:
    for workspace_name, workspace_id in configured_workspaces.items():
        required_providers = WORKSPACE_CONFIG.get(workspace_name, set())
        should_have = provider in required_providers
        currently_has = workspace_id in current_associations

        if should_have and not currently_has:
            changes[provider]["add"].append(workspace_name)
        elif not should_have and currently_has:
            changes[provider]["remove"].append(workspace_name)


def apply_changes(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varsets: Dict[str, dict],
    changes: Dict[str, Dict[str, List[str]]],
    dry_run: bool = False
):
    """Apply the calculated changes"""

    total_changes = _count_total_changes(changes)
    if total_changes == 0:
        print("✅ No changes needed - all associations are correct!")
        return

    prefix = "DRY RUN - " if dry_run else ""
    print(f"\n{prefix}Applying {total_changes} changes:\n")

    for provider, varset_name in VARIABLE_SETS.items():
        varset_info = varsets.get(varset_name)
        if not varset_info:
            continue

        _apply_provider_changes(api, workspaces, provider, varset_name, varset_info, changes, dry_run)

    _print_apply_summary(dry_run)


def _count_total_changes(changes: Dict[str, Dict[str, List[str]]]) -> int:
    return sum(len(entry["add"]) + len(entry["remove"]) for entry in changes.values())


def _apply_provider_changes(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    provider: str,
    varset_name: str,
    varset_info: dict,
    changes: Dict[str, Dict[str, List[str]]],
    dry_run: bool,
) -> None:
    varset_id = varset_info["id"]

    for workspace_name in changes[provider]["add"]:
        workspace_id = workspaces[workspace_name]
        print(f"  ➕ Adding {varset_name} to {workspace_name}")
        if not dry_run:
            api.associate_workspace(varset_id, workspace_id)

    for workspace_name in changes[provider]["remove"]:
        workspace_id = workspaces[workspace_name]
        print(f"  ➖ Removing {varset_name} from {workspace_name}")
        if not dry_run:
            api.disassociate_workspace(varset_id, workspace_id)


def _print_apply_summary(dry_run: bool) -> None:
    if dry_run:
        print("\n⚠️  This was a dry run. Use without --dry-run to apply changes.")
        return
    print("\n✅ All changes applied successfully!")


def verify_configuration(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varsets: Dict[str, dict]
):
    """Verify current configuration and report status"""

    print(f"\n📋 Configuration Report for Organization: {ORGANIZATION}\n")
    print("=" * 80)

    _print_global_varsets(varsets)
    _print_missing_workspaces(workspaces)
    _print_missing_varsets(varsets)

    print("\n📊 Current Variable Set Associations:\n")

    configured_workspaces = {
        workspace_name: workspace_id
        for workspace_name, workspace_id in workspaces.items()
        if workspace_name in WORKSPACE_CONFIG
    }
    configured_workspace_names = sorted(configured_workspaces.keys())

    for provider, varset_name in VARIABLE_SETS.items():
        varset_info = varsets.get(varset_name)
        if not varset_info:
            continue

        _print_provider_associations(
            api,
            provider,
            varset_name,
            varset_info,
            configured_workspaces,
            configured_workspace_names,
        )

    print("\n" + "=" * 80)


def _print_global_varsets(varsets: Dict[str, dict]) -> None:
    global_varsets = [name for name, info in varsets.items() if info.get("global")]
    if not global_varsets:
        return

    print("\n🌍 Global Variable Sets (applied to ALL workspaces):")
    for varset_name in sorted(global_varsets):
        print(f"  - {varset_name}")
    print("\n⚠️  Global variable sets violate the principle of least privilege!")
    print("   Consider using --convert-to-workspace-specific to change this.")


def _print_missing_workspaces(workspaces: Dict[str, str]) -> None:
    missing_workspaces = set(WORKSPACE_CONFIG.keys()) - set(workspaces.keys())
    if not missing_workspaces:
        return

    print("\n⚠️  Missing Workspaces (not found in HCP Terraform):")
    for workspace_name in sorted(missing_workspaces):
        print(f"  - {workspace_name}")


def _print_missing_varsets(varsets: Dict[str, dict]) -> None:
    missing_varsets = set(VARIABLE_SETS.values()) - set(varsets.keys())
    if not missing_varsets:
        return

    print("\n⚠️  Missing Variable Sets (not found in HCP Terraform):")
    for varset_name in sorted(missing_varsets):
        print(f"  - {varset_name}")


def _print_provider_associations(
    api: TerraformCloudAPI,
    provider: str,
    varset_name: str,
    varset_info: dict,
    configured_workspaces: Dict[str, str],
    configured_workspace_names: List[str],
) -> None:
    print(f"\n{varset_name}:")
    print("-" * 40)

    if varset_info.get("global"):
        print("  🌍 GLOBAL - All workspaces have access")
        return

    varset_id = varset_info["id"]
    current_associations = api.get_varset_workspaces(varset_id)

    for workspace_name in configured_workspace_names:
        workspace_id = configured_workspaces[workspace_name]
        should_have = provider in WORKSPACE_CONFIG[workspace_name]
        currently_has = workspace_id in current_associations
        status = _association_status(should_have, currently_has)
        if status is not None:
            print(f"  {status} {workspace_name}")


def _association_status(should_have: bool, currently_has: bool) -> Optional[str]:
    if not (should_have or currently_has):
        return None
    if should_have:
        return "✅" if currently_has else "❌ MISSING"
    return "⚠️  EXTRA"


def _parse_args() -> argparse.Namespace:
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
    return parser.parse_args()


def _get_token_or_exit(args: argparse.Namespace) -> str:
    token = args.token or os.environ.get("TFC_TOKEN")
    if token:
        return token

    print("❌ Error: No API token provided")
    print("   Use --token YOUR_TOKEN or set TFC_TOKEN environment variable")
    sys.exit(1)


def _fetch_state(api: TerraformCloudAPI) -> tuple[Dict[str, str], Dict[str, dict]]:
    print("🔍 Fetching workspaces and variable sets...")
    workspaces = api.get_workspaces()
    varsets = api.get_variable_sets()

    print(f"   Found {len(workspaces)} workspaces")
    print(f"   Found {len(varsets)} variable sets")
    return workspaces, varsets


def _convert_global_varsets_to_workspace_specific(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varsets: Dict[str, dict],
    dry_run: bool,
) -> None:
    global_varsets = _global_varsets_to_convert(varsets)
    if not global_varsets:
        print("\n✅ No global variable sets to convert!")
        return

    _print_convert_header(global_varsets, dry_run)

    for varset_name, varset_info in global_varsets:
        _convert_single_varset(api, workspaces, varset_name, varset_info, dry_run)

    _print_convert_summary(dry_run)


def _global_varsets_to_convert(varsets: Dict[str, dict]) -> List[tuple[str, dict]]:
    return [
        (name, info)
        for name, info in varsets.items()
        if info.get("global") and name in VARIABLE_SETS.values()
    ]


def _print_convert_header(global_varsets: List[tuple[str, dict]], dry_run: bool) -> None:
    prefix = "DRY RUN - " if dry_run else ""
    print(
        f"\n{prefix}Converting {len(global_varsets)} variable sets from global to workspace-specific:\n"
    )


def _provider_for_varset_name(varset_name: str) -> Optional[str]:
    for provider, mapped_name in VARIABLE_SETS.items():
        if mapped_name == varset_name:
            return provider
    return None


def _convert_single_varset(
    api: TerraformCloudAPI,
    workspaces: Dict[str, str],
    varset_name: str,
    varset_info: dict,
    dry_run: bool,
) -> None:
    print(f"  🔄 Converting '{varset_name}' to workspace-specific")
    varset_id = varset_info["id"]
    if not dry_run:
        api.set_global_scope(varset_id, False)

    provider = _provider_for_varset_name(varset_name)
    if provider is None:
        return

    for workspace_name, workspace_id in workspaces.items():
        required_providers = WORKSPACE_CONFIG.get(workspace_name)
        if not required_providers or provider not in required_providers:
            continue

        print(f"     ➕ Adding {workspace_name}")
        if not dry_run:
            api.associate_workspace(varset_id, workspace_id)


def _print_convert_summary(dry_run: bool) -> None:
    if dry_run:
        print("\n⚠️  This was a dry run. Use without --dry-run to apply changes.")
        return
    print("\n✅ Conversion completed successfully!")
    print("   Run --verify-only to see the new configuration.")


def main():
    args = _parse_args()
    token = _get_token_or_exit(args)
    api = TerraformCloudAPI(token)

    try:
        workspaces, varsets = _fetch_state(api)
        if args.convert_to_workspace_specific:
            _convert_global_varsets_to_workspace_specific(
                api,
                workspaces,
                varsets,
                dry_run=args.dry_run,
            )
            return

        if args.verify_only:
            verify_configuration(api, workspaces, varsets)
            return

        changes = calculate_changes(api, workspaces, varsets)
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

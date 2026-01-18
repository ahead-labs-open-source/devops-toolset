"""Delete Postman collections and environments from a workspace by x-api-id.

This script deletes all collections and environments that match a specific x-api-id
from a Postman workspace using the Postman REST API.

Authentication:
- Provide an API key via --api-key or the POSTMAN_API_KEY environment variable.

Examples:
  python -m devops_toolset.project_types.postman.delete_from_workspace \
    --workspace-id <workspaceId> --x-api-id "my-api" --dry-run

  POSTMAN_API_KEY=... python -m devops_toolset.project_types.postman.delete_from_workspace \
    --workspace-id <workspaceId> --x-api-id "my-api"
"""

from __future__ import annotations

import argparse
import os
from typing import Any, cast

try:
    # Normal package import
    from devops_toolset.project_types.postman.deploy_to_workspace import (
        _request_json,
        get_workspace_assets,
        DEFAULT_API_BASE_URL,
        DEFAULT_TIMEOUT_SECONDS,
    )
except ImportError:  # pragma: no cover
    # Allow running this file directly
    from deploy_to_workspace import (  # type: ignore
        _request_json,
        get_workspace_assets,
        DEFAULT_API_BASE_URL,
        DEFAULT_TIMEOUT_SECONDS,
    )


def delete_by_api_id(
    base_url: str,
    api_key: str,
    workspace_id: str,
    x_api_id: str,
    dry_run: bool = False,
) -> tuple[list[str], list[str]]:
    """
    Delete all collections and environments matching x-api-id from workspace.
    
    Since Postman API doesn't preserve x-api-id in info, we match by name pattern instead.
    We'll match collections/environments whose name (without version) matches the slug.
    
    Args:
        base_url: Postman API base URL
        api_key: Postman API key
        workspace_id: Target workspace ID
        x_api_id: The x-api-id to match (we'll derive pattern from this)
        dry_run: If True, only report what would be deleted without actually deleting
        
    Returns:
        Tuple of (deleted_collection_uids, deleted_environment_uids)
    """
    import re
    
    assets = get_workspace_assets(base_url, api_key, workspace_id)
    
    deleted_collections: list[str] = []
    deleted_environments: list[str] = []
    
    # Convert x-api-id slug to name pattern (e.g., "ai-personal-assistant-api" -> "AI Personal Assistant API")
    # This is a best-effort conversion since the original casing is lost in the slug
    # We'll uppercase common acronyms
    words = x_api_id.split('-')
    name_words = []
    acronyms = {'api', 'ai', 'ui', 'id', 'url', 'http', 'https', 'rest', 'json', 'xml'}
    for word in words:
        if word.lower() in acronyms:
            name_words.append(word.upper())
        else:
            name_words.append(word.capitalize())
    name_pattern = ' '.join(name_words)
    
    print(f"Searching for collections/environments matching: '{name_pattern}'")
    print("=" * 70)
    
    # Find and delete collections with matching name (ignoring version suffix)
    for name, uid in assets.collections_by_name.items():
        # Remove version suffixes like " v1-rev0", " v1.0.0", " v1-rev0 v1.0.0" from name for comparison
        # Matches patterns like: v1, v1.0, v1.0.0, v1-rev0, v2-rev1, etc. (with or without version number after)
        base_name = re.sub(r'\s+v\d+([-.]\w+)*(\s+v?\d+(\.\d+)*)?$', '', name, flags=re.IGNORECASE).strip()
        if base_name == name_pattern:
            if dry_run:
                print(f"🔍 [DRY-RUN] Would delete collection: {name} ({uid})")
            else:
                try:
                    _request_json("DELETE", base_url, f"/collections/{uid}", api_key)
                    print(f"✅ Deleted collection: {name} ({uid})")
                    deleted_collections.append(uid)
                except Exception as e:
                    print(f"❌ Failed to delete collection {name}: {e}")
    
    # Find and delete environments with matching name pattern
    for name, uid in assets.environments_by_name.items():
        # Match pattern like "Test API v1-rev0 v1.0.0 - Staging"
        # Remove both " v1-rev0 v1.0.0" and " - Staging" parts
        base_name = re.sub(r'\s+v\d+([-.]\w+)*(\s+v?\d+(\.\d+)*)?(\s+-\s+\w+)?$', '', name, flags=re.IGNORECASE).strip()
        if base_name == name_pattern:
            if dry_run:
                print(f"🔍 [DRY-RUN] Would delete environment: {name} ({uid})")
            else:
                try:
                    _request_json("DELETE", base_url, f"/environments/{uid}", api_key)
                    print(f"✅ Deleted environment: {name} ({uid})")
                    deleted_environments.append(uid)
                except Exception as e:
                    print(f"❌ Failed to delete environment {name}: {e}")
    
    if not deleted_collections and not deleted_environments and not dry_run:
        print(f"ℹ️  No collections or environments found matching: {name_pattern}")
    
    return (deleted_collections, deleted_environments)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete Postman collections and environments from a workspace by x-api-id."
    )
    parser.add_argument(
        "--workspace-id",
        required=True,
        help="Target Postman workspace ID"
    )
    parser.add_argument(
        "--x-api-id",
        required=True,
        help="The x-api-id to match for deletion"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Postman API key. If omitted, uses POSTMAN_API_KEY env var.",
    )
    parser.add_argument(
        "--api-base-url",
        default=DEFAULT_API_BASE_URL,
        help=f"Postman API base URL (default: {DEFAULT_API_BASE_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"HTTP timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )

    args = parser.parse_args(argv)

    api_key = str(args.api_key or os.getenv("POSTMAN_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("Missing API key. Provide --api-key or set POSTMAN_API_KEY.")

    base_url = str(args.api_base_url)
    workspace_id = str(args.workspace_id)
    x_api_id = str(args.x_api_id)
    dry_run = bool(args.dry_run)

    print("=" * 70)
    print("Delete Postman Assets by x-api-id")
    print("=" * 70)
    print(f"Workspace ID: {workspace_id}")
    print(f"x-api-id: {x_api_id}")
    if dry_run:
        print("⚠️  DRY-RUN MODE: Nothing will be deleted")
    print("=" * 70)
    
    print("Fetching workspace assets...")
    assets = get_workspace_assets(base_url, api_key, workspace_id)
    print(f"Found {len(assets.collections_by_name)} collections by name")
    if assets.collections_by_name:
        for name in assets.collections_by_name.keys():
            print(f"  - {name}")
    print(f"Found {len(assets.collections_by_api_id)} collections by x-api-id")
    print(f"Found {len(assets.environments_by_name)} environments by name")
    if assets.environments_by_name:
        for name in assets.environments_by_name.keys():
            print(f"  - {name}")
    print(f"Found {len(assets.environments_by_api_id)} environments by x-api-id")
    if assets.collections_by_api_id:
        print(f"x-api-id values found in collections: {list(assets.collections_by_api_id.keys())}")
    if assets.environments_by_api_id:
        print(f"x-api-id values found in environments: {list(assets.environments_by_api_id.keys())}")
    print("=" * 70)

    deleted_colls, deleted_envs = delete_by_api_id(
        base_url,
        api_key,
        workspace_id,
        x_api_id,
        dry_run=dry_run,
    )

    print("=" * 70)
    if dry_run:
        print("🔍 DRY-RUN SUMMARY")
    else:
        print("✅ DELETION SUMMARY")
    print(f"Collections: {len(deleted_colls)}")
    print(f"Environments: {len(deleted_envs)}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

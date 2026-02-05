"""Delete Postman collections and environments from a workspace by x-api-id.

This script deletes all collections and environments that match a specific x-api-id
from a Postman workspace using the Postman REST API.

Authentication:
- Provide an API key via --api-key or the POSTMAN_API_KEY environment variable.

Examples:
  python -m devops_toolset.saas_platforms.postman.delete_from_workspace \
    --workspace-id <workspaceId> --x-api-id "my-api" --dry-run

  POSTMAN_API_KEY=... python -m devops_toolset.saas_platforms.postman.delete_from_workspace \
    --workspace-id <workspaceId> --x-api-id "my-api"
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Iterable

try:
    # Normal package import
    from devops_toolset.saas_platforms.postman.deploy_to_workspace import (
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


try:
    from devops_toolset.saas_platforms.postman.utils import strip_version_suffix
except ImportError:  # pragma: no cover
    from utils import strip_version_suffix  # type: ignore


_ACRONYMS = {"api", "ai", "ui", "id", "url", "http", "https", "rest", "json", "xml"}


def _name_pattern_from_x_api_id(x_api_id: str) -> str:
    words = [w for w in str(x_api_id or "").split("-") if w]
    if not words:
        return ""

    name_words: list[str] = []
    for word in words:
        if word.lower() in _ACRONYMS:
            name_words.append(word.upper())
        else:
            name_words.append(word.capitalize())
    return " ".join(name_words)


def _iter_assets_matching_name_pattern(
    assets_by_name: dict[str, str],
    name_pattern: str,
    *,
    strip_dash_suffix: bool,
) -> Iterable[tuple[str, str]]:
    for name, uid in assets_by_name.items():
        if strip_version_suffix(name, strip_dash_suffix=strip_dash_suffix) == name_pattern:
            yield name, uid


def _delete_single_asset(
    base_url: str,
    api_key: str,
    *,
    asset_kind: str,
    api_path: str,
    name: str,
    uid: str,
    dry_run: bool,
) -> bool:
    if dry_run:
        print(f"🔍 [DRY-RUN] Would delete {asset_kind}: {name} ({uid})")
        return False

    try:
        _request_json("DELETE", base_url, f"{api_path}{uid}", api_key)
    except Exception as exc:
        print(f"❌ Failed to delete {asset_kind} {name}: {exc}")
        return False

    print(f"✅ Deleted {asset_kind}: {name} ({uid})")
    return True


def _delete_assets_matching_name_pattern(
    base_url: str,
    api_key: str,
    *,
    asset_kind: str,
    api_path: str,
    assets_by_name: dict[str, str],
    name_pattern: str,
    dry_run: bool,
    strip_dash_suffix: bool,
) -> list[str]:
    deleted: list[str] = []
    for name, uid in _iter_assets_matching_name_pattern(
        assets_by_name, name_pattern, strip_dash_suffix=strip_dash_suffix
    ):
        deleted_now = _delete_single_asset(
            base_url,
            api_key,
            asset_kind=asset_kind,
            api_path=api_path,
            name=name,
            uid=uid,
            dry_run=dry_run,
        )
        if deleted_now:
            deleted.append(uid)
    return deleted


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
    assets = get_workspace_assets(base_url, api_key, workspace_id)

    # Convert x-api-id slug to name pattern (e.g., "ai-personal-assistant-api" -> "AI Personal Assistant API")
    # This is a best-effort conversion since the original casing is lost in the slug.
    name_pattern = _name_pattern_from_x_api_id(x_api_id)
    
    print(f"Searching for collections/environments matching: '{name_pattern}'")
    print("=" * 70)

    deleted_collections = _delete_assets_matching_name_pattern(
        base_url,
        api_key,
        asset_kind="collection",
        api_path="/collections/",
        assets_by_name=assets.collections_by_name,
        name_pattern=name_pattern,
        dry_run=dry_run,
        strip_dash_suffix=False,
    )

    deleted_environments = _delete_assets_matching_name_pattern(
        base_url,
        api_key,
        asset_kind="environment",
        api_path="/environments/",
        assets_by_name=assets.environments_by_name,
        name_pattern=name_pattern,
        dry_run=dry_run,
        strip_dash_suffix=True,
    )
    
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

"""Deploy Postman collections and environments to a Postman workspace.

This script takes:
- A Postman collection JSON file (v2.1 export or generated)
- Zero or more Postman environment JSON files (exported or generated)

And deploys them to a target Postman workspace using the Postman REST API.
If the collection / environments already exist in the workspace (matched by name),
they are updated (overwritten).

Authentication:
- Provide an API key via --api-key or the POSTMAN_API_KEY environment variable.

Examples:
  python -m devops_toolset.project_types.postman.deploy_to_workspace \
    ./collection.json --workspace-id <workspaceId> \
    --environments ./staging.env.json ./prod.env.json

  POSTMAN_API_KEY=... python -m devops_toolset.project_types.postman.deploy_to_workspace \
    ./collection.json --workspace-id <workspaceId>
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

import requests


DEFAULT_API_BASE_URL = "https://api.postman.com"
DEFAULT_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class PostmanWorkspaceAssets:
    collections_by_name: dict[str, str]
    collections_by_api_id: dict[str, str]
    environments_by_name: dict[str, str]
    environments_by_api_id: dict[str, str]


class PostmanApiError(RuntimeError):
    pass


def _load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return cast(dict[str, Any], raw)


def _strip_id_fields(obj: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy without common id fields.

    Postman exports often include 'id'/'uid'. API update calls generally don't
    require these fields in the payload and they may conflict.
    """
    cleaned = dict(obj)
    cleaned.pop("id", None)
    cleaned.pop("uid", None)
    return cleaned


def _collection_name_from_export(collection_export: dict[str, Any]) -> str:
    info_raw: Any = collection_export.get("info", {})
    info = cast(dict[str, Any], info_raw) if isinstance(info_raw, dict) else {}
    name = str(info.get("name", "")).strip()
    if not name:
        raise ValueError("Collection export is missing info.name")
    return name


def _collection_api_id_from_export(collection_export: dict[str, Any]) -> str:
    """Extract x-api-id from collection, fallback to name if not present."""
    info_raw: Any = collection_export.get("info", {})
    info = cast(dict[str, Any], info_raw) if isinstance(info_raw, dict) else {}
    api_id = str(info.get("x-api-id", "")).strip()
    if api_id:
        return api_id
    # Fallback to name for backward compatibility
    return _collection_name_from_export(collection_export)


def _environment_name_from_export(env_export: dict[str, Any]) -> str:
    # Accept either {"environment": {...}} (API format) or export format {...}
    if "environment" in env_export and isinstance(env_export.get("environment"), dict):
        env_obj = cast(dict[str, Any], env_export["environment"])
    else:
        env_obj = env_export

    name = str(env_obj.get("name", "")).strip()
    if not name:
        raise ValueError("Environment export is missing name")
    return name


def _environment_api_id_from_export(env_export: dict[str, Any]) -> str:
    """Extract x-api-id from environment, fallback to name if not present."""
    # Accept either {"environment": {...}} (API format) or export format {...}
    if "environment" in env_export and isinstance(env_export.get("environment"), dict):
        env_obj = cast(dict[str, Any], env_export["environment"])
    else:
        env_obj = env_export

    api_id = str(env_obj.get("x-api-id", "")).strip()
    if not api_id:
        # Fallback to name if no x-api-id
        api_id = str(env_obj.get("name", "")).strip()
    return api_id


def _strip_version_from_name(name: str) -> str:
    """
    Strip version patterns from resource names.
    Examples:
        "Test API v1-rev0" -> "Test API"
        "Test API v1-rev0 v1.0.0" -> "Test API"
        "Test API v2-rev1 v2.5.0 - Development" -> "Test API - Development"
    """
    import re
    # Remove patterns like " v1-rev0", " v1.0.0", " v1-rev0 v1.0.0"
    stripped = re.sub(r'\s+v\d+([-.]\w+)*(\s+v?\d+(\.\d+)*)?', '', name, flags=re.IGNORECASE)
    return stripped.strip()


def _find_uid_by_base_name(
    name_to_find: str,
    assets_by_name: dict[str, str]
) -> str | None:
    """
    Find a resource UID by comparing base names (without version suffixes).
    Returns the UID of the first match, or None if no match found.
    """
    base_name_to_find = _strip_version_from_name(name_to_find)
    
    for existing_name, uid in assets_by_name.items():
        base_existing_name = _strip_version_from_name(existing_name)
        if base_existing_name == base_name_to_find:
            return uid
    
    return None



    if "environment" in env_export and isinstance(env_export.get("environment"), dict):
        env_obj = cast(dict[str, Any], env_export["environment"])
    else:
        env_obj = env_export
    
    api_id = str(env_obj.get("x-api-id", "")).strip()
    if api_id:
        return api_id
    # Fallback to name for backward compatibility
    return _environment_name_from_export(env_export)


def _wrap_collection_for_api(collection_export: dict[str, Any]) -> dict[str, Any]:
    return {"collection": _strip_id_fields(collection_export)}


def _wrap_environment_for_api(env_export: dict[str, Any]) -> dict[str, Any]:
    if "environment" in env_export and isinstance(env_export.get("environment"), dict):
        env_obj = cast(dict[str, Any], env_export["environment"])
    else:
        env_obj = env_export
    return {"environment": _strip_id_fields(env_obj)}


def _raise_for_postman_error(resp: requests.Response) -> None:
    if resp.ok:
        return

    body_text = ""
    try:
        body_text = json.dumps(resp.json(), indent=2, ensure_ascii=False)
    except Exception:
        body_text = (resp.text or "").strip()

    raise PostmanApiError(f"Postman API error {resp.status_code}: {body_text}")


def _request_json(
    method: str,
    base_url: str,
    path: str,
    api_key: str,
    *,
    params: Optional[dict[str, str]] = None,
    payload: Optional[dict[str, Any]] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + path
    headers = {
        "X-Api-Key": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    resp = requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=payload,
        timeout=timeout_seconds,
    )
    _raise_for_postman_error(resp)

    if resp.status_code == 204:
        return {}

    data: Any = resp.json()
    if not isinstance(data, dict):
        raise PostmanApiError(f"Unexpected response shape from {method} {path}")
    return cast(dict[str, Any], data)


def get_workspace_assets(base_url: str, api_key: str, workspace_id: str) -> PostmanWorkspaceAssets:
    # Workspaces API returns collection/env identifiers that are in that workspace.
    data = _request_json("GET", base_url, f"/workspaces/{workspace_id}", api_key)
    workspace_raw: Any = data.get("workspace", {})
    workspace = cast(dict[str, Any], workspace_raw) if isinstance(workspace_raw, dict) else {}

    collections_by_name: dict[str, str] = {}
    collections_by_api_id: dict[str, str] = {}
    envs_by_name: dict[str, str] = {}
    envs_by_api_id: dict[str, str] = {}

    collections_raw: Any = workspace.get("collections", [])
    if isinstance(collections_raw, list):
        collections_list = cast(list[Any], collections_raw)
        for c_raw in collections_list:
            if not isinstance(c_raw, dict):
                continue
            c = cast(dict[str, Any], c_raw)
            name = str(c.get("name", "")).strip()
            uid = str(c.get("uid", "")).strip() or str(c.get("id", "")).strip()
            if name and uid:
                collections_by_name[name] = uid
                # Fetch full collection to get x-api-id
                try:
                    coll_data = _request_json("GET", base_url, f"/collections/{uid}", api_key)
                    coll_obj_raw: Any = coll_data.get("collection", {})
                    coll_obj = cast(dict[str, Any], coll_obj_raw) if isinstance(coll_obj_raw, dict) else {}
                    info_raw: Any = coll_obj.get("info", {})
                    info = cast(dict[str, Any], info_raw) if isinstance(info_raw, dict) else {}
                    api_id = str(info.get("x-api-id", "")).strip()
                    if api_id:
                        collections_by_api_id[api_id] = uid
                except Exception:
                    # Silently ignore errors fetching individual collections
                    pass

    envs_raw: Any = workspace.get("environments", [])
    if isinstance(envs_raw, list):
        envs_list = cast(list[Any], envs_raw)
        for e_raw in envs_list:
            if not isinstance(e_raw, dict):
                continue
            e = cast(dict[str, Any], e_raw)
            name = str(e.get("name", "")).strip()
            uid = str(e.get("uid", "")).strip() or str(e.get("id", "")).strip()
            if name and uid:
                envs_by_name[name] = uid
                # Fetch full environment to get x-api-id
                try:
                    env_data = _request_json("GET", base_url, f"/environments/{uid}", api_key)
                    env_obj_raw: Any = env_data.get("environment", {})
                    env_obj = cast(dict[str, Any], env_obj_raw) if isinstance(env_obj_raw, dict) else {}
                    api_id = str(env_obj.get("x-api-id", "")).strip()
                    if api_id:
                        envs_by_api_id[api_id] = uid
                except Exception:
                    # Silently ignore errors fetching individual environments
                    pass

    return PostmanWorkspaceAssets(
        collections_by_name=collections_by_name,
        collections_by_api_id=collections_by_api_id,
        environments_by_name=envs_by_name,
        environments_by_api_id=envs_by_api_id
    )


def upsert_collection(
    base_url: str,
    api_key: str,
    workspace_id: str,
    collection_export: dict[str, Any],
) -> tuple[str, str]:
    api_id = _collection_api_id_from_export(collection_export)
    name = _collection_name_from_export(collection_export)
    assets = get_workspace_assets(base_url, api_key, workspace_id)

    # Try to find existing collection by:
    # 1. x-api-id (exact match)
    # 2. Exact name match
    # 3. Base name match (name without version suffix)
    existing_uid = (
        assets.collections_by_api_id.get(api_id) or 
        assets.collections_by_name.get(name) or
        _find_uid_by_base_name(name, assets.collections_by_name)
    )
    payload = _wrap_collection_for_api(collection_export)

    if existing_uid:
        _request_json("PUT", base_url, f"/collections/{existing_uid}", api_key, payload=payload)
        return ("updated", existing_uid)

    created = _request_json(
        "POST",
        base_url,
        "/collections",
        api_key,
        params={"workspace": workspace_id},
        payload=payload,
    )
    collection_obj_raw: Any = created.get("collection", {})
    collection_obj = cast(dict[str, Any], collection_obj_raw) if isinstance(collection_obj_raw, dict) else {}
    uid = str(collection_obj.get("uid", "")).strip() or str(collection_obj.get("id", "")).strip()
    return ("created", uid or "")


def upsert_environment(
    base_url: str,
    api_key: str,
    workspace_id: str,
    env_export: dict[str, Any],
) -> tuple[str, str, str]:
    api_id = _environment_api_id_from_export(env_export)
    name = _environment_name_from_export(env_export)
    assets = get_workspace_assets(base_url, api_key, workspace_id)

    # Try to find existing environment by:
    # 1. x-api-id (exact match)
    # 2. Exact name match
    # 3. Base name match (name without version suffix)
    existing_uid = (
        assets.environments_by_api_id.get(api_id) or 
        assets.environments_by_name.get(name) or
        _find_uid_by_base_name(name, assets.environments_by_name)
    )
    payload = _wrap_environment_for_api(env_export)

    if existing_uid:
        _request_json("PUT", base_url, f"/environments/{existing_uid}", api_key, payload=payload)
        return ("updated", name, existing_uid)

    created = _request_json(
        "POST",
        base_url,
        "/environments",
        api_key,
        params={"workspace": workspace_id},
        payload=payload,
    )
    env_obj_raw: Any = created.get("environment", {})
    env_obj = cast(dict[str, Any], env_obj_raw) if isinstance(env_obj_raw, dict) else {}
    uid = str(env_obj.get("uid", "")).strip() or str(env_obj.get("id", "")).strip()
    return ("created", name, uid or "")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deploy a Postman collection and environments to a Postman workspace (create or overwrite)."
    )
    parser.add_argument("collection", type=str, help="Path to Postman collection JSON (v2.1 export)")
    parser.add_argument(
        "--environments",
        nargs="*",
        default=[],
        type=str,
        help="Paths to Postman environment JSON files",
    )
    parser.add_argument("--workspace-id", required=True, help="Target Postman workspace ID")
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

    args = parser.parse_args(argv)

    api_key = str(args.api_key or os.getenv("POSTMAN_API_KEY") or "").strip()
    if not api_key:
        raise SystemExit("Missing API key. Provide --api-key or set POSTMAN_API_KEY.")

    collection_path = Path(str(args.collection)).expanduser().resolve()
    if not collection_path.exists():
        raise SystemExit(f"Collection file not found: {collection_path}")

    env_paths = [Path(p).expanduser().resolve() for p in cast(list[str], (args.environments or []))]
    for p in env_paths:
        if not p.exists():
            raise SystemExit(f"Environment file not found: {p}")

    base_url = str(args.api_base_url)
    workspace_id = str(args.workspace_id)

    # Collection
    collection_export = _load_json_file(collection_path)
    action, uid = upsert_collection(base_url, api_key, workspace_id, collection_export)
    print(f"✅ Collection {action}: {collection_path.name} ({uid})")

    # Environments
    for env_path in env_paths:
        env_export = _load_json_file(env_path)
        env_action, env_name, env_uid = upsert_environment(base_url, api_key, workspace_id, env_export)
        print(f"✅ Environment {env_action}: {env_name} ({env_uid})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

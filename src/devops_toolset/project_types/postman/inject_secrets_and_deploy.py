"""
Inject secrets into Postman environment and deploy to workspace.

This module combines secret injection and Postman deployment into a single operation.
It reads a Postman environment JSON file, injects secrets (like API keys, credentials),
and then deploys both the collection and updated environment to a Postman workspace.

This replaces inline Bash scripts in CI/CD workflows with testable, maintainable Python code.

Usage:
    python -m devops_toolset.project_types.postman.inject_secrets_and_deploy \\
        --collection ./collection.json \\
        --environment ./environment.json \\
        --workspace-id <workspace-id> \\
        --apim-api-key <secret> \\
        --tenant-id <value> \\
        --client-id <value> \\
        --client-secret <secret> \\
        [--mask-secrets]

Requirements:
- Postman API key (via --api-key or POSTMAN_API_KEY env var)
- Collection and environment JSON files (generated from OpenAPI spec)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from devops_toolset.project_types.postman.deploy_to_workspace import (
        upsert_collection,
        upsert_environment,
        _load_json_file,
        PostmanApiError,
        DEFAULT_API_BASE_URL,
    )
except ImportError:  # pragma: no cover
    from deploy_to_workspace import (  # type: ignore
        upsert_collection,
        upsert_environment,
        _load_json_file,
        PostmanApiError,
        DEFAULT_API_BASE_URL,
    )


def mask_secret_for_github(secret: str) -> None:
    """
    Emit GitHub Actions workflow command to mask a secret in logs.
    
    Args:
        secret: Secret value to mask
    """
    if secret:
        print(f"::add-mask::{secret}", flush=True)


def inject_secrets_into_environment(
    env_json: Dict[str, Any],
    secrets: Dict[str, tuple[str, str]]
) -> Dict[str, Any]:
    """
    Inject secrets into Postman environment JSON.
    
    Upserts key-value pairs into the environment's 'values' array.
    If a key already exists, updates its value and type.
    If a key doesn't exist, adds a new entry.
    
    Args:
        env_json: Postman environment JSON document
        secrets: Dictionary mapping key names to (value, type) tuples
                type should be 'secret' or 'default'
    
    Returns:
        Modified environment JSON
    """
    # Ensure values array exists
    if "values" not in env_json:
        env_json["values"] = []
    
    values = env_json["values"]
    
    for key, (value, var_type) in secrets.items():
        # Find existing entry
        found = False
        for item in values:
            if isinstance(item, dict) and item.get("key") == key:
                item["value"] = value
                item["type"] = var_type
                item["enabled"] = True
                found = True
                break
        
        # Add new entry if not found
        if not found:
            values.append({
                "key": key,
                "value": value,
                "type": var_type,
                "enabled": True
            })
    
    return env_json


def validate_secrets(
    apim_api_key: Optional[str],
    client_secret: Optional[str]
) -> None:
    """
    Validate that required secrets are present and non-empty.
    
    Args:
        apim_api_key: APIM API key
        client_secret: ARM client secret
        
    Raises:
        ValueError: If any required secret is missing or empty
    """
    if not apim_api_key:
        raise ValueError("APIM_API_KEY is required but was not provided or is empty")
    
    if not client_secret:
        raise ValueError("ARM_CLIENT_SECRET is required but was not provided or is empty")


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for inject and deploy script.
    
    Returns:
        Exit code: 0 if successful, 1 if error
    """
    parser = argparse.ArgumentParser(
        description="Inject secrets into Postman environment and deploy to workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m devops_toolset.project_types.postman.inject_secrets_and_deploy \\
    --collection ./collection.json \\
    --environment ./staging_environment.json \\
    --workspace-id abc123 \\
    --apim-api-key "secret1" \\
    --tenant-id "tenant-guid" \\
    --client-id "client-guid" \\
    --client-secret "secret2"

  # With secret masking for GitHub Actions
  python -m devops_toolset.project_types.postman.inject_secrets_and_deploy \\
    --collection ./collection.json \\
    --environment ./staging_environment.json \\
    --workspace-id abc123 \\
    --apim-api-key "$APIM_API_KEY" \\
    --tenant-id "$TENANT_ID" \\
    --client-id "$CLIENT_ID" \\
    --client-secret "$CLIENT_SECRET" \\
    --mask-secrets

Requirements:
- Postman API key must be set via --api-key or POSTMAN_API_KEY environment variable
        """
    )
    
    parser.add_argument(
        "--collection",
        type=Path,
        required=True,
        help="Path to Postman collection JSON file"
    )
    
    parser.add_argument(
        "--environment",
        type=Path,
        required=True,
        help="Path to Postman environment JSON file"
    )
    
    parser.add_argument(
        "--workspace-id",
        required=True,
        help="Target Postman workspace ID"
    )
    
    parser.add_argument(
        "--apim-api-key",
        help="APIM API subscription key (secret)"
    )
    
    parser.add_argument(
        "--tenant-id",
        help="Azure tenant ID"
    )
    
    parser.add_argument(
        "--client-id",
        help="Azure client ID"
    )
    
    parser.add_argument(
        "--client-secret",
        help="Azure client secret"
    )
    
    parser.add_argument(
        "--api-key",
        default=None,
        help="Postman API key (can also use POSTMAN_API_KEY env var)"
    )
    
    parser.add_argument(
        "--api-base-url",
        default=DEFAULT_API_BASE_URL,
        help=f"Postman API base URL (default: {DEFAULT_API_BASE_URL})"
    )
    
    parser.add_argument(
        "--mask-secrets",
        action="store_true",
        help="Emit GitHub Actions ::add-mask:: commands for secrets"
    )
    
    args = parser.parse_args(argv)
    
    try:
        # Get Postman API key
        api_key = str(args.api_key or os.getenv("POSTMAN_API_KEY") or "").strip()
        if not api_key:
            raise ValueError(
                "Missing Postman API key. "
                "Provide --api-key or set POSTMAN_API_KEY environment variable."
            )
        
        # Validate secrets
        validate_secrets(args.apim_api_key, args.client_secret)
        
        # Mask secrets if requested (GitHub Actions)
        if args.mask_secrets:
            if args.apim_api_key:
                mask_secret_for_github(args.apim_api_key)
            if args.client_secret:
                mask_secret_for_github(args.client_secret)
        
        # Load collection
        print(f"Loading collection: {args.collection}", file=sys.stderr)
        if not args.collection.exists():
            raise FileNotFoundError(f"Collection file not found: {args.collection}")
        
        collection_json = _load_json_file(args.collection)
        
        # Load environment
        print(f"Loading environment: {args.environment}", file=sys.stderr)
        if not args.environment.exists():
            raise FileNotFoundError(f"Environment file not found: {args.environment}")
        
        env_json = _load_json_file(args.environment)
        
        # Inject secrets into environment
        print("Injecting secrets into environment...", file=sys.stderr)
        secrets_to_inject: Dict[str, tuple[str, str]] = {}
        
        if args.apim_api_key:
            secrets_to_inject["ocpApimSubscriptionKey"] = (args.apim_api_key, "secret")
        
        if args.tenant_id:
            secrets_to_inject["tenantId"] = (args.tenant_id, "default")
        
        if args.client_id:
            secrets_to_inject["clientId"] = (args.client_id, "default")
        
        if args.client_secret:
            secrets_to_inject["clientSecret"] = (args.client_secret, "secret")
        
        env_json = inject_secrets_into_environment(env_json, secrets_to_inject)
        
        # Deploy collection
        print(f"Deploying collection to workspace {args.workspace_id}...", file=sys.stderr)
        action, uid = upsert_collection(
            args.api_base_url,
            api_key,
            args.workspace_id,
            collection_json
        )
        print(f"✅ Collection {action}: {args.collection.name} (UID: {uid})", file=sys.stderr)
        
        # Deploy environment
        print(f"Deploying environment to workspace {args.workspace_id}...", file=sys.stderr)
        env_action, env_name, env_uid = upsert_environment(
            args.api_base_url,
            api_key,
            args.workspace_id,
            env_json
        )
        print(f"✅ Environment {env_action}: {env_name} (UID: {env_uid})", file=sys.stderr)
        
        print("\n✅ Deployment completed successfully", file=sys.stderr)
        return 0
        
    except (ValueError, FileNotFoundError, PostmanApiError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

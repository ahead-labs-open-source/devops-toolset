#!/usr/bin/env python3
"""
Extract Azure credentials from a JSONC template file.

This script reads a secrets-and-variables.jsonc template and extracts the Azure
credentials needed for OIDC authentication. It outputs the credentials to 
GITHUB_OUTPUT for use in subsequent workflow steps.

Usage:
    python extract_azure_credentials.py <template_path>

Environment Variables:
    GITHUB_OUTPUT - Path to GitHub Actions output file (required in workflow)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Import from the same package
from .inject_secrets_and_variables import strip_jsonc_comments


def extract_azure_credentials(template_path: str) -> Dict[str, str]:
    """
    Extract Azure credentials from a JSONC template.
    
    Args:
        template_path: Path to the secrets-and-variables.jsonc file
        
    Returns:
        Dictionary with client-id, tenant-id, and subscription-id
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        ValueError: If required credentials are missing
        json.JSONDecodeError: If JSON parsing fails
    """
    # Read template file
    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_file, 'r', encoding='utf-8') as f:
        jsonc_content = f.read()
    
    # Strip comments and parse
    json_content = strip_jsonc_comments(jsonc_content)
    data = json.loads(json_content)
    
    # Extract credentials
    arm_subscription_id = data.get('repository', {}).get('variables', {}).get('ARM_SUBSCRIPTION_ID', '')
    arm_tenant_id = data.get('repository', {}).get('variables', {}).get('ARM_TENANT_ID', '')
    
    # ARM_CLIENT_ID might be in repository variables or environment variables
    arm_client_id = (
        data.get('repository', {}).get('variables', {}).get('ARM_CLIENT_ID') or
        data.get('environments', {}).get('staging', {}).get('variables', {}).get('ARM_CLIENT_ID', '')
    )
    
    # Validate required credentials
    if not all([arm_subscription_id, arm_tenant_id, arm_client_id]):
        missing = []
        if not arm_subscription_id:
            missing.append('ARM_SUBSCRIPTION_ID')
        if not arm_tenant_id:
            missing.append('ARM_TENANT_ID')
        if not arm_client_id:
            missing.append('ARM_CLIENT_ID')
        raise ValueError(
            f"Missing required Azure credentials: {', '.join(missing)}\n"
            f"Template file: {template_path}"
        )
    
    return {
        'client-id': arm_client_id,
        'tenant-id': arm_tenant_id,
        'subscription-id': arm_subscription_id
    }


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Extract Azure credentials from JSONC template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'template_path',
        help='Path to secrets-and-variables.jsonc template file'
    )
    parser.add_argument(
        '--output-format',
        choices=['github-actions', 'json', 'env'],
        default='github-actions',
        help='Output format (default: github-actions)'
    )
    
    args = parser.parse_args()
    
    try:
        # Extract credentials
        credentials = extract_azure_credentials(args.template_path)
        
        # Output in requested format
        if args.output_format == 'github-actions':
            # Write to GITHUB_OUTPUT for use in workflow
            github_output = os.environ.get('GITHUB_OUTPUT')
            if not github_output:
                print("Error: GITHUB_OUTPUT environment variable not set", file=sys.stderr)
                sys.exit(1)
            
            with open(github_output, 'a') as f:
                for key, value in credentials.items():
                    f.write(f"{key}={value}\n")
            
            print("✅ Successfully extracted Azure credentials from template")
            
        elif args.output_format == 'json':
            print(json.dumps(credentials, indent=2))
            
        elif args.output_format == 'env':
            for key, value in credentials.items():
                # Convert to uppercase environment variable format
                env_key = key.upper().replace('-', '_')
                print(f"{env_key}={value}")
        
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in template file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

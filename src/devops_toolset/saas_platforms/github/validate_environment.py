"""
GitHub Actions Environment Validator

This module validates that required environment variables and secrets are present in a GitHub Actions job.

IMPORTANT: This script validates that variables/secrets **arrived correctly to the job environment**,
NOT that they exist directly in GitHub Settings.

Validation Flow:
1. User configures vars.ARM_SUBSCRIPTION_ID in GitHub Settings → Secrets and variables
2. Workflow declares: ARM_SUBSCRIPTION_ID: ${{ vars.ARM_SUBSCRIPTION_ID }}
3. GitHub Actions passes the value to job environment (or empty string if not found)
4. This script reads os.environ["ARM_SUBSCRIPTION_ID"] and validates it's non-empty

Limitation:
Cannot distinguish between "doesn't exist in GitHub" vs "exists but is empty".
Both cases result in an empty value in the environment.

Practical Result:
If validation passes, you know:
- ✅ Variable/secret exists in GitHub
- ✅ Has a non-empty value
- ✅ Was passed correctly to the job
"""

import argparse
import os
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class RequiredItem:
    """Represents a required environment variable or secret."""
    
    name: str
    item_type: str  # 'variable' or 'secret'
    scope: str      # 'repo' or 'env'

    @classmethod
    def from_string(cls, spec: str) -> "RequiredItem":
        """
        Parse a requirement specification string.
        
        Format: VARIABLE_NAME:type:scope
        Example: ARM_SUBSCRIPTION_ID:variable:repo
        
        Args:
            spec: Specification string
            
        Returns:
            RequiredItem instance
            
        Raises:
            ValueError: If format is invalid
        """
        parts = spec.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid requirement format: '{spec}'. "
                f"Expected format: VARIABLE_NAME:type:scope"
            )
        
        name, item_type, scope = parts
        
        if item_type not in ("variable", "secret"):
            raise ValueError(
                f"Invalid type '{item_type}' for {name}. "
                f"Must be 'variable' or 'secret'"
            )
        
        if scope not in ("repo", "env"):
            raise ValueError(
                f"Invalid scope '{scope}' for {name}. "
                f"Must be 'repo' or 'env'"
            )
        
        return cls(name=name, item_type=item_type, scope=scope)


def print_github_context(environment: str = None) -> None:
    """
    Print GitHub Actions context information to stderr.
    
    Displays: repository, ref, ref_name, workflow, run_id
    
    Args:
        environment: Optional environment name for display (e.g., 'staging', 'production')
    """
    env_label = f" ({environment})" if environment else ""
    
    print(f"GitHub context{env_label}:", file=sys.stderr)
    print(f" - repository: {os.environ.get('GITHUB_REPOSITORY', '')}", file=sys.stderr)
    print(f" - ref: {os.environ.get('GITHUB_REF', '')}", file=sys.stderr)
    print(f" - ref_name: {os.environ.get('GITHUB_REF_NAME', '')}", file=sys.stderr)
    print(f" - workflow: {os.environ.get('GITHUB_WORKFLOW', '')}", file=sys.stderr)
    print(f" - run_id: {os.environ.get('GITHUB_RUN_ID', '')}", file=sys.stderr)


def validate_environment(required_items: List[RequiredItem]) -> List[RequiredItem]:
    """
    Validate that all required items are present and non-empty in the environment.
    
    Reads from os.environ and checks for non-empty values.
    
    Args:
        required_items: List of RequiredItem to validate
        
    Returns:
        List of missing RequiredItem (empty list if all present)
    """
    missing = []
    
    for item in required_items:
        # Read from environment
        value = os.environ.get(item.name, "")
        
        # Check if empty (missing or empty string)
        if not value:
            missing.append(item)
    
    return missing


def report_missing_items(
    missing: List[RequiredItem],
    environment: str = None,
    template_path: str = None
) -> None:
    """
    Report missing environment variables/secrets to stderr.
    
    Args:
        missing: List of missing RequiredItem
        environment: Optional environment name for display
        template_path: Optional documentation reference path
    """
    env_label = f" for environment '{environment}'" if environment else ""
    
    print(f"Missing required variables/secrets{env_label}:", file=sys.stderr)
    
    for item in missing:
        print(f" - {item.name} ({item.item_type})", file=sys.stderr)
    
    if template_path:
        print(f"Template: {template_path}", file=sys.stderr)


def main() -> int:
    """
    Main entry point for the validation script.
    
    Returns:
        Exit code: 0 if all required items present, 1 if any missing
    """
    parser = argparse.ArgumentParser(
        description="Validate GitHub Actions environment variables and secrets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python -m devops_toolset.saas_platforms.github.validate_environment \\
    --required ARM_SUBSCRIPTION_ID:variable:repo \\
    --required POSTMAN_API_KEY:secret:repo

  # With environment and template reference
  python -m devops_toolset.saas_platforms.github.validate_environment \\
    --required ARM_SUBSCRIPTION_ID:variable:repo \\
    --required ARM_CLIENT_ID:variable:env \\
    --required ARM_CLIENT_SECRET:secret:env \\
    --environment staging \\
    --template-path .github/workflows/secrets-and-variables.jsonc
        """
    )
    
    parser.add_argument(
        "--required",
        action="append",
        required=True,
        metavar="VARIABLE_NAME:type:scope",
        help="Required variable or secret in format VARIABLE_NAME:type:scope. "
             "type: 'variable' or 'secret'. "
             "scope: 'repo' (repository-level) or 'env' (environment-level). "
             "Can be specified multiple times."
    )
    
    parser.add_argument(
        "--environment",
        help="Environment name for logging/messages (e.g., 'staging', 'production'). "
             "Optional, cosmetic only."
    )
    
    parser.add_argument(
        "--template-path",
        help="Documentation reference path to show in error messages. "
             "Optional, informational only."
    )
    
    args = parser.parse_args()
    
    # Parse required items
    try:
        required_items = [RequiredItem.from_string(spec) for spec in args.required]
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Print GitHub context
    print_github_context(args.environment)
    print(file=sys.stderr)  # Empty line for readability
    
    # Validate environment
    missing = validate_environment(required_items)
    
    # Report results
    if missing:
        report_missing_items(missing, args.environment, args.template_path)
        return 1
    
    # Success - all required items present
    return 0


if __name__ == "__main__":
    sys.exit(main())

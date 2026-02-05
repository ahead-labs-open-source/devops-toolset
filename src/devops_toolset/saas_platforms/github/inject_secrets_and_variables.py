"""
GitHub Secrets and Variables Injector

This module injects repository and environment-level variables and secrets into GitHub
using the GitHub CLI (gh) or REST API.

It reads a template file (JSONC format) that defines:
- Repository-level variables and secrets
- Environment-level variables and secrets (per environment: staging, production, etc.)

For secrets, the script can either:
1. Read plain text values directly from the template (for testing/dev)
2. Fetch values from Azure Key Vault using secret URLs (recommended for production)

Usage:
    python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \\
        --template path/to/secrets-and-variables.jsonc \\
        --repo owner/repo-name \\
        [--fetch-from-keyvault] \\
        [--dry-run]

Requirements:
- GitHub CLI (gh) installed and authenticated
- Azure CLI (az) installed and authenticated (if using --fetch-from-keyvault)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# Pattern to detect Azure Key Vault secret URLs
KEYVAULT_URL_PATTERN = re.compile(
    r"https://([^.]+)\.vault\.azure\.net/secrets/([^/]+)(/([^?]+))?",
    re.IGNORECASE
)


@dataclass
class Variable:
    """Represents a GitHub variable."""
    name: str
    value: str
    scope: str  # 'repository' or environment name


@dataclass
class Secret:
    """Represents a GitHub secret."""
    name: str
    value: str  # Can be plain text or Key Vault URL
    scope: str  # 'repository' or environment name


def strip_jsonc_comments(content: str) -> str:
    """
    Remove comments from JSONC content.
    
    Supports:
    - Line comments: // comment
    - Block comments: /* comment */
    
    Args:
        content: JSONC file content
        
    Returns:
        JSON content without comments
    """
    # Remove block comments /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove line comments // ...
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    
    return content


def load_template(template_path: Path) -> Dict[str, Any]:
    """
    Load and parse secrets/variables template file (JSONC).
    
    Args:
        template_path: Path to template file
        
    Returns:
        Parsed template dictionary
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        json.JSONDecodeError: If template is invalid JSON
    """
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    content = template_path.read_text(encoding='utf-8')
    content_no_comments = strip_jsonc_comments(content)
    
    try:
        return json.loads(content_no_comments)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in template file: {e}") from e


def is_keyvault_url(value: str) -> bool:
    """
    Check if a value is an Azure Key Vault secret URL.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is a Key Vault URL, False otherwise
    """
    return bool(KEYVAULT_URL_PATTERN.match(value))


def fetch_keyvault_secret(secret_url: str) -> str:
    """
    Fetch secret value from Azure Key Vault using Azure CLI.
    
    Args:
        secret_url: Azure Key Vault secret URL
        
    Returns:
        Secret value
        
    Raises:
        RuntimeError: If Azure CLI command fails
    """
    match = KEYVAULT_URL_PATTERN.match(secret_url)
    if not match:
        raise ValueError(f"Invalid Key Vault URL: {secret_url}")
    
    vault_name = match.group(1)
    secret_name = match.group(2)
    version = match.group(4)  # Optional
    
    cmd = ["az", "keyvault", "secret", "show", "--vault-name", vault_name, "--name", secret_name]
    
    if version:
        cmd.extend(["--version", version])
    
    cmd.extend(["--query", "value", "-o", "tsv"])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Timed out fetching secret from Key Vault: {secret_url}"
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to fetch secret from Key Vault: {secret_url}\n"
            f"Error: {e.stderr}"
        ) from e


def parse_template(
    template: Dict[str, Any],
    fetch_from_keyvault: bool = False
) -> tuple[List[Variable], List[Secret]]:
    """
    Parse template and extract variables and secrets.
    
    Args:
        template: Parsed template dictionary
        fetch_from_keyvault: If True, fetch secret values from Key Vault
        
    Returns:
        Tuple of (variables, secrets) lists
    """
    variables: List[Variable] = []
    secrets: List[Secret] = []
    
    # Repository-level
    repo_data = template.get("repository", {})
    
    for name, value in repo_data.get("variables", {}).items():
        variables.append(Variable(name=name, value=str(value), scope="repository"))
    
    for name, value in repo_data.get("secrets", {}).items():
        secret_value = value
        
        # Fetch from Key Vault if requested and value is a KV URL
        if fetch_from_keyvault and is_keyvault_url(value):
            print(f"Fetching secret {name} from Key Vault...", file=sys.stderr)
            secret_value = fetch_keyvault_secret(value)
        
        secrets.append(Secret(name=name, value=secret_value, scope="repository"))
    
    # Environment-level
    environments = template.get("environments", {})
    
    for env_name, env_data in environments.items():
        for name, value in env_data.get("variables", {}).items():
            variables.append(Variable(name=name, value=str(value), scope=env_name))
        
        for name, value in env_data.get("secrets", {}).items():
            secret_value = value
            
            # Fetch from Key Vault if requested and value is a KV URL
            if fetch_from_keyvault and is_keyvault_url(value):
                print(f"Fetching secret {name} for env {env_name} from Key Vault...", file=sys.stderr)
                secret_value = fetch_keyvault_secret(value)
            
            secrets.append(Secret(name=name, value=secret_value, scope=env_name))
    
    return variables, secrets


def set_repository_variable(repo: str, name: str, value: str, dry_run: bool = False) -> None:
    """
    Set a repository-level variable using GitHub CLI.
    
    Args:
        repo: Repository in format owner/repo-name
        name: Variable name
        value: Variable value
        dry_run: If True, only print command without executing
    """
    cmd = ["gh", "variable", "set", name, "--repo", repo, "--body", value]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}", file=sys.stderr)
        return
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
        print(f"✅ Set repository variable: {name}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set repository variable {name}: {e.stderr}", file=sys.stderr)
        raise


def set_repository_secret(repo: str, name: str, value: str, dry_run: bool = False) -> None:
    """
    Set a repository-level secret using GitHub CLI.
    
    Args:
        repo: Repository in format owner/repo-name
        name: Secret name
        value: Secret value
        dry_run: If True, only print command without executing
    """
    cmd = ["gh", "secret", "set", name, "--repo", repo, "--body-file", "-"]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: gh secret set {name} --repo {repo} --body ***", file=sys.stderr)
        return
    
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            input=value,
            timeout=60,
        )
        print(f"✅ Set repository secret: {name}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set repository secret {name}: {e.stderr}", file=sys.stderr)
        raise


def set_environment_variable(repo: str, env: str, name: str, value: str, dry_run: bool = False) -> None:
    """
    Set an environment-level variable using GitHub CLI.
    
    Args:
        repo: Repository in format owner/repo-name
        env: Environment name
        name: Variable name
        value: Variable value
        dry_run: If True, only print command without executing
    """
    cmd = ["gh", "variable", "set", name, "--repo", repo, "--env", env, "--body", value]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}", file=sys.stderr)
        return
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
        print(f"✅ Set environment variable: {name} (env: {env})", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set environment variable {name} for {env}: {e.stderr}", file=sys.stderr)
        raise


def set_environment_secret(repo: str, env: str, name: str, value: str, dry_run: bool = False) -> None:
    """
    Set an environment-level secret using GitHub CLI.
    
    Args:
        repo: Repository in format owner/repo-name
        env: Environment name
        name: Secret name
        value: Secret value
        dry_run: If True, only print command without executing
    """
    cmd = ["gh", "secret", "set", name, "--repo", repo, "--env", env, "--body-file", "-"]
    
    if dry_run:
        print(f"[DRY-RUN] Would execute: gh secret set {name} --repo {repo} --env {env} --body ***", file=sys.stderr)
        return
    
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            input=value,
            timeout=60,
        )
        print(f"✅ Set environment secret: {name} (env: {env})", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set environment secret {name} for {env}: {e.stderr}", file=sys.stderr)
        raise


def inject_variables_and_secrets(
    repo: str,
    variables: List[Variable],
    secrets: List[Secret],
    dry_run: bool = False
) -> None:
    """
    Inject all variables and secrets into GitHub repository.
    
    Args:
        repo: Repository in format owner/repo-name
        variables: List of variables to inject
        secrets: List of secrets to inject
        dry_run: If True, only print what would be done
    """
    print(f"Injecting variables and secrets into {repo}...", file=sys.stderr)
    print(file=sys.stderr)
    
    # Inject variables
    for var in variables:
        if var.scope == "repository":
            set_repository_variable(repo, var.name, var.value, dry_run)
        else:
            set_environment_variable(repo, var.scope, var.name, var.value, dry_run)
    
    # Inject secrets
    for secret in secrets:
        if secret.scope == "repository":
            set_repository_secret(repo, secret.name, secret.value, dry_run)
        else:
            set_environment_secret(repo, secret.scope, secret.name, secret.value, dry_run)
    
    print(file=sys.stderr)
    print("✅ All variables and secrets injected successfully", file=sys.stderr)


def main() -> int:
    """
    Main entry point for the injection script.
    
    Returns:
        Exit code: 0 if successful, 1 if error
    """
    parser = argparse.ArgumentParser(
        description="Inject GitHub repository and environment variables/secrets from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Inject using template (secrets as plain text in template)
  python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \\
    --template .github/workflows/secrets-and-variables.jsonc \\
    --repo myorg/myrepo

  # Inject with Key Vault fetch (recommended for production)
  python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \\
    --template .github/workflows/secrets-and-variables.jsonc \\
    --repo myorg/myrepo \\
    --fetch-from-keyvault

  # Dry run (see what would be done without executing)
  python -m devops_toolset.saas_platforms.github.inject_secrets_and_variables \\
    --template .github/workflows/secrets-and-variables.jsonc \\
    --repo myorg/myrepo \\
    --dry-run

Requirements:
- GitHub CLI (gh) must be installed and authenticated
- Azure CLI (az) required if using --fetch-from-keyvault
        """
    )
    
    parser.add_argument(
        "--template",
        type=Path,
        required=True,
        help="Path to secrets and variables template file (JSONC format)"
    )
    
    parser.add_argument(
        "--repo",
        required=True,
        help="Target GitHub repository in format owner/repo-name"
    )
    
    parser.add_argument(
        "--fetch-from-keyvault",
        action="store_true",
        help="Fetch secret values from Azure Key Vault (requires Azure CLI authenticated)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without executing commands"
    )
    
    args = parser.parse_args()
    
    try:
        # Load template
        print(f"Loading template: {args.template}", file=sys.stderr)
        template = load_template(args.template)
        
        # Parse template
        print("Parsing template...", file=sys.stderr)
        variables, secrets = parse_template(template, args.fetch_from_keyvault)
        
        print(f"Found {len(variables)} variables and {len(secrets)} secrets", file=sys.stderr)
        print(file=sys.stderr)
        
        # Inject
        inject_variables_and_secrets(args.repo, variables, secrets, args.dry_run)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

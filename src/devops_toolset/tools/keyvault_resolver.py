"""Resolve Azure Key Vault secret URLs into values for GitHub Actions.

This module is intended to be executed inside GitHub Actions.

It reads one or more *input* environment variables, and for each one:
- if the value is an Azure Key Vault secret URL, it fetches the secret value via Azure CLI
- otherwise it uses the value as-is

The resolved values are:
- masked via the GitHub Actions masking command
- exported to subsequent steps by appending to $GITHUB_ENV

Example:
  python -m devops_toolset.tools.keyvault_resolver \
    --map POSTMAN_API_KEY_INPUT=POSTMAN_API_KEY \
    --map ARM_CLIENT_SECRET_INPUT=ARM_CLIENT_SECRET

Requirements:
- Azure CLI (az) available
- Azure login already performed (e.g., azure/login with OIDC)
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from uuid import uuid4

_KEYVAULT_URL_PATTERN = re.compile(
    r"https://([^.]+)\.vault\.azure\.net/secrets/([^/]+)(/([^?]+))?",
    re.IGNORECASE,
)

_ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_]\w*$", re.ASCII)


@dataclass(frozen=True)
class MappingPair:
    input_name: str
    output_name: str


def _add_mask(value: str) -> None:
    if value:
        print(f"::add-mask::{value}")


def _append_github_env(name: str, value: str) -> None:
    github_env = os.environ.get("GITHUB_ENV")
    if not github_env:
        raise RuntimeError("GITHUB_ENV is not set")

    if not _ENV_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid output env var name: {name!r}. "
            "Expected [A-Za-z_][A-Za-z0-9_]*"
        )

    with open(github_env, "a", encoding="utf-8") as f:
        delimiter = f"KEYVAULT_RESOLVER_{uuid4().hex}"
        f.write(f"{name}<<{delimiter}\n")
        f.write(f"{value}\n")
        f.write(f"{delimiter}\n")


def _resolve(value: str, timeout_seconds: int) -> str:
    if value and _KEYVAULT_URL_PATTERN.match(value):
        return _fetch_keyvault_secret(value, timeout_seconds=timeout_seconds)
    return value


def _fetch_keyvault_secret(secret_url: str, timeout_seconds: int) -> str:
    match = _KEYVAULT_URL_PATTERN.match(secret_url)
    if not match:
        raise ValueError(f"Invalid Key Vault URL: {secret_url}")

    vault_name = match.group(1)
    secret_name = match.group(2)
    version = match.group(4)  # Optional

    cmd: list[str] = [
        "az",
        "keyvault",
        "secret",
        "show",
        "--vault-name",
        vault_name,
        "--name",
        secret_name,
    ]
    if version:
        cmd.extend(["--version", version])
    cmd.extend(["--query", "value", "-o", "tsv"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as e:
        raise RuntimeError("Azure CLI ('az') not found on PATH") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Timed out after {timeout_seconds}s fetching Key Vault secret: {secret_url}"
        ) from e
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise RuntimeError(
            f"Failed to fetch secret from Key Vault: {secret_url}\n"
            f"Error: {stderr}"
        )
    return (result.stdout or "").strip()


def _parse_mapping(value: str) -> MappingPair:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "Invalid --map value. Expected format INPUT_ENV=OUTPUT_ENV"
        )

    input_name, output_name = value.split("=", 1)
    input_name = input_name.strip()
    output_name = output_name.strip()

    if not input_name or not output_name:
        raise argparse.ArgumentTypeError(
            "Invalid --map value. INPUT_ENV and OUTPUT_ENV must be non-empty"
        )

    if not _ENV_NAME_PATTERN.match(input_name):
        raise argparse.ArgumentTypeError(
            f"Invalid input env var name: {input_name!r}. "
            "Expected [A-Za-z_][A-Za-z0-9_]*"
        )

    if not _ENV_NAME_PATTERN.match(output_name):
        raise argparse.ArgumentTypeError(
            f"Invalid output env var name: {output_name!r}. "
            "Expected [A-Za-z_][A-Za-z0-9_]*"
        )

    return MappingPair(input_name=input_name, output_name=output_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve Azure Key Vault secret URLs from env vars and export to GITHUB_ENV",
    )

    parser.add_argument(
        "--map",
        action="append",
        type=_parse_mapping,
        required=True,
        help="Map INPUT_ENV=OUTPUT_ENV (repeatable)",
    )

    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow resolved values to be empty (default: fail if empty)",
    )

    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=60,
        help="Timeout in seconds for Azure CLI calls (default: 60)",
    )

    args = parser.parse_args(argv)

    mappings: list[MappingPair] = args.map
    allow_empty: bool = args.allow_empty
    timeout_seconds: int = args.timeout_seconds

    if timeout_seconds <= 0:
        raise ValueError("--timeout-seconds must be > 0")

    for mapping in mappings:
        raw_value = os.environ.get(mapping.input_name, "")
        resolved_value = _resolve(raw_value, timeout_seconds=timeout_seconds)

        if not allow_empty and not resolved_value:
            raise RuntimeError(
                f"Resolved value for '{mapping.input_name}' is empty; "
                f"cannot export '{mapping.output_name}'."
            )

        _add_mask(resolved_value)
        _append_github_env(mapping.output_name, resolved_value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

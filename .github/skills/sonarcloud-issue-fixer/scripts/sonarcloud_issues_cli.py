#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SonarCloud Issues CLI - Tool for extracting unresolved code quality issues

This command-line tool retrieves all unresolved issues from a SonarCloud project
and branch using the SonarCloud REST API. It supports pagination to handle large
result sets and can optionally fetch detailed information about the violated rules.

Main features:
- Fetches all unresolved issues from a specific project and branch
- Automatic pagination handling (500 issues per page)
- Optional rule details extraction for deeper analysis
- JSON output (file or stdout) with timestamp and metadata
- Bearer token authentication via CLI argument or SONARQUBE_TOKEN environment variable

Usage examples:
    # Basic usage - fetch issues and output to stdout
    python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issues_cli.py --organization ahead-labs-software --project signatus-surface

    # Fetch issues with rule details and save to file
    python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issues_cli.py --organization ahead-labs-software --project signatus-surface \
        --branch feature/my-feature --rules --out issues.json

    # Using environment variable for token
    export SONARQUBE_TOKEN="your_token_here"
    python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issues_cli.py --organization ahead-labs-software --project signatus-surface

Dependencies:
    - requests: HTTP client for SonarCloud API calls
    - Standard library: argparse, json, os, sys, time, datetime, typing, urllib

Output format:
    {
        "timestamp": "ISO 8601 timestamp",
        "organization": "organization key",
        "project": "project key",
        "branch": "branch name",
        "total_issues": number of issues,
        "issues": [ array of issue objects ],
        "rules": [ optional array of rule details ]
    }

Author: Ahead Labs Software
License: GNU General Public License v3.0 (GPL-3.0)
Repository: https://github.com/ahead-labs-open-source/devops-toolset

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

import requests
from urllib.parse import quote


BASE_URL = "https://sonarcloud.io"


def http_get(path: str, token: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Perform an HTTP GET request with Bearer auth and return parsed JSON."""
    url = f"{BASE_URL.rstrip('/')}{path}"
    r = requests.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def get_issues_unresolved(
    organization: str,
    project: str,
    branch: str,
    token: str,
    pull_request: Optional[str] = None,
) -> Dict[str, Any]:
    """Paginate through /api/issues/search and return ALL unresolved issues.

    componentKeys are built as <organization>_<project>.
    """

    component_keys = f"{organization}_{project}"

    # Normalize branch: default to main; URL-encode for visibility.
    branch = branch or "main"
    encoded_branch = quote(branch, safe="")

    issues_all: List[Dict[str, Any]] = []
    p = 1
    ps = 500
    total = None

    while True:
        params = {
            "componentKeys": component_keys,
            "resolved": "false",
            "p": p,
            "ps": ps,
        }
        if pull_request:
            params["pullRequest"] = str(pull_request)
        else:
            params["branch"] = branch
        data = http_get("/api/issues/search", token, params)
        page_issues = data.get("issues", [])
        issues_all.extend(page_issues)

        paging = data.get("paging", {})
        total = paging.get("total", total)
        if not page_issues or (total is not None and len(issues_all) >= int(total)):
            break

        p += 1
        time.sleep(0.15)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organization": organization,
        "project": project,
        "branch": branch,
        "pull_request": str(pull_request) if pull_request else "",
        "branch_web": encoded_branch,
        "componentKeys": component_keys,
        "total_issues": len(issues_all) if total is None else int(total),
        "issues": issues_all,
    }


def fetch_rules_details(organization: str, token: str, rule_keys: Set[str]) -> List[Dict[str, Any]]:
    """Fetch rule details for each unique rule key using /api/rules/show."""

    rules: List[Dict[str, Any]] = []
    for rk in sorted(rule_keys):
        try:
            data = http_get("/api/rules/show", token, {"organization": organization, "key": rk})
            rule_obj = data.get("rule")
            if rule_obj:
                rules.append(rule_obj)
        except requests.HTTPError as e:
            sys.stderr.write(f"[warn] Could not fetch rule '{rk}': {e}\n")
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[warn] Error for rule '{rk}': {e}\n")
        time.sleep(0.05)
    return rules


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch all unresolved issues from a project/branch in SonarCloud. "
            "Optionally add unique rule details."
        )
    )
    parser.add_argument("--organization", required=True, help="SonarCloud organization key (e.g. ahead-labs-software)")
    parser.add_argument("--project", required=True, help="Project key (e.g. signatus-surface)")
    parser.add_argument("--branch", default="main", help="Branch name; defaults to 'main'")
    parser.add_argument(
        "--pull-request",
        default="",
        help="Pull request key/number (for PR analysis). If set, overrides --branch.",
    )
    parser.add_argument("--token", help="SonarCloud token (Bearer). If not provided, uses SONARQUBE_TOKEN env var")
    parser.add_argument("--rules", action="store_true", help="If set, add 'rules' with unique rule details")
    parser.add_argument("--out", default="", help="Path to output JSON file (stdout if not set)")
    args = parser.parse_args()

    token = args.token or os.getenv("SONARQUBE_TOKEN")
    if not token:
        sys.stderr.write("Error: no token provided and SONARQUBE_TOKEN env var is not set.\n")
        raise SystemExit(1)

    pr = args.pull_request.strip() or None
    result = get_issues_unresolved(args.organization, args.project, args.branch, token, pull_request=pr)

    if args.rules:
        rule_keys: Set[str] = {it.get("rule") for it in result.get("issues", []) if it.get("rule")}
        result["rules"] = fetch_rules_details(args.organization, token, rule_keys)

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Written JSON to {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        sys.stderr.write(f"HTTP error: {e.response.status_code} {e.response.text}\n")
        raise SystemExit(2)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        raise SystemExit(1)

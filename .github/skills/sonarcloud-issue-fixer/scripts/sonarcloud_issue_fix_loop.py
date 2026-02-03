#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SonarCloud Issue Fix Loop

This script is intended to be used by an AI agent and humans.

It builds on the existing SonarCloud issues fetcher:
- `.github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issues_cli.py`

Capabilities:
- Infer Sonar org/project/branch from the current git repo (overridable)
- Fetch unresolved issues from SonarCloud
- Sort them by priority
- Provide an iterative "next issue" loop via a small local state file

Notes:
- SonarCloud issues clear only after a new analysis runs in CI.
- This tool tracks local progress (mark done/skip) to drive a stable loop.

Examples:
  python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issue_fix_loop.py plan --format md --out sonarcloud-fix-plan.md
  python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issue_fix_loop.py next --format json
  python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issue_fix_loop.py mark-done AX2bcdEfghIjkLmNoP

Auth:
- Use SONARQUBE_TOKEN or pass --token
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[4]
SONAR_ISSUES_CLI_PATH = (
    REPO_ROOT
    / ".github"
    / "skills"
    / "sonarcloud-issue-fixer"
    / "scripts"
    / "sonarcloud_issues_cli.py"
)
DEFAULT_STATE_PATH = REPO_ROOT / ".github" / "skills" / "sonarcloud-issue-fixer" / ".local" / "state.json"


SEVERITY_WEIGHT: dict[str, int] = {
    "BLOCKER": 50,
    "CRITICAL": 40,
    "MAJOR": 30,
    "MINOR": 20,
    "INFO": 10,
}

TYPE_WEIGHT: dict[str, int] = {
    "VULNERABILITY": 30,
    "BUG": 20,
    "CODE_SMELL": 10,
}


class CommandError(RuntimeError):
    pass


def _run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        shell=False,
    )
    if completed.returncode != 0:
        raise CommandError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _infer_owner_repo_from_remote(remote_url: str) -> Optional[Tuple[str, str]]:
    """Parse GitHub remote URLs and return (owner, repo)."""

    # https://github.com/OWNER/REPO.git
    m = re.match(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", remote_url)
    if m:
        return m.group("owner"), m.group("repo")

    # git@github.com:OWNER/REPO.git
    m = re.match(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", remote_url)
    if m:
        return m.group("owner"), m.group("repo")

    # ssh://git@github.com/OWNER/REPO.git
    m = re.match(r"^ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", remote_url)
    if m:
        return m.group("owner"), m.group("repo")

    return None


def infer_repo_identity() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Infer (owner, repo, branch) from git, best-effort."""

    owner = None
    repo = None

    try:
        remote = _run_git(["remote", "get-url", "origin"])
        parsed = _infer_owner_repo_from_remote(remote)
        if parsed:
            owner, repo = parsed
    except Exception:
        pass

    branch = None
    for env_key in ("GITHUB_REF_NAME", "BRANCH_NAME"):
        if os.getenv(env_key):
            branch = os.getenv(env_key)
            break

    if not branch:
        try:
            branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        except Exception:
            branch = None

    return owner, repo, branch


def load_sonar_issues_cli_module():
    if not SONAR_ISSUES_CLI_PATH.exists():
        raise FileNotFoundError(f"Missing dependency: {SONAR_ISSUES_CLI_PATH}")

    spec = importlib.util.spec_from_file_location("sonarcloud_issues_cli", str(SONAR_ISSUES_CLI_PATH))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {SONAR_ISSUES_CLI_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _parse_debt_to_minutes(debt: Optional[str]) -> int:
    """Parse Sonar 'debt' strings like '5min', '2h', '3d' into minutes."""

    if not debt:
        return 0

    m = re.match(r"^(?P<num>\d+)(?P<unit>min|h|d)$", debt.strip())
    if not m:
        return 0

    num = int(m.group("num"))
    unit = m.group("unit")

    if unit == "min":
        return num
    if unit == "h":
        return num * 60
    if unit == "d":
        return num * 60 * 8

    return 0


def _issue_sort_key(issue: dict[str, Any]) -> tuple:
    severity = (issue.get("severity") or "").upper()
    issue_type = (issue.get("type") or "").upper()

    severity_w = SEVERITY_WEIGHT.get(severity, 0)
    type_w = TYPE_WEIGHT.get(issue_type, 0)

    debt_minutes = _parse_debt_to_minutes(issue.get("debt"))

    created = issue.get("creationDate") or "9999-12-31T00:00:00+0000"

    # Descending severity/type/debt, then oldest first.
    return (-severity_w, -type_w, -debt_minutes, created)


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"done": [], "skipped": [], "updatedAt": None}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"done": [], "skipped": [], "updatedAt": None}
        data.setdefault("done", [])
        data.setdefault("skipped", [])
        return data
    except Exception:
        return {"done": [], "skipped": [], "updatedAt": None}


def _save_state(path: Path, state: dict[str, Any]) -> None:
    state["updatedAt"] = datetime.now(timezone.utc).isoformat()
    _ensure_parent_dir(path)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _select_remaining_issues(issues: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    done = set(state.get("done", []))
    skipped = set(state.get("skipped", []))

    remaining = []
    for it in issues:
        key = it.get("key")
        if not key:
            continue
        if key in done or key in skipped:
            continue
        remaining.append(it)

    remaining.sort(key=_issue_sort_key)
    return remaining


def _render_issue_md(issue: dict[str, Any]) -> str:
    key = issue.get("key", "")
    severity = issue.get("severity", "")
    issue_type = issue.get("type", "")
    component = issue.get("component", "")
    line = issue.get("line")
    msg = issue.get("message", "")
    rule = issue.get("rule", "")
    debt = issue.get("debt", "")

    loc = component
    if line:
        loc = f"{component}:{line}"

    return "\n".join(
        [
            f"- **{key}** [{severity}/{issue_type}] {loc}",
            f"  - Rule: `{rule}`" if rule else "  - Rule: (n/a)",
            f"  - Debt: {debt or '(n/a)'}",
            f"  - Message: {msg}",
        ]
    )


def _infer_defaults() -> tuple[str, str, str, str]:
    owner, repo, branch = infer_repo_identity()

    organization = os.getenv("SONARCLOUD_ORG") or (owner or "")
    project = os.getenv("SONARCLOUD_PROJECT") or (repo or "")
    branch_name = os.getenv("SONARCLOUD_BRANCH") or (branch or "main")

    token = os.getenv("SONARQUBE_TOKEN") or ""

    return organization, project, branch_name, token


@dataclass(frozen=True)
class LoopContext:
    organization: str
    project: str
    branch: str
    token: str
    pull_request: str
    state_path: Path
    format: str
    out: str


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch, prioritize, and iterate SonarCloud issues.")
    parser.add_argument("--organization", default="", help="SonarCloud organization")
    parser.add_argument("--project", default="", help="SonarCloud project key")
    parser.add_argument("--branch", default="", help="Branch name")
    parser.add_argument(
        "--pull-request",
        default="",
        help="Pull request key/number (for PR analysis). If set, overrides --branch.",
    )
    parser.add_argument("--token", default="", help="SonarCloud token (Bearer). Prefer SONARQUBE_TOKEN env var")
    parser.add_argument("--state", default="", help="Local state file path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_p = subparsers.add_parser("plan", help="Generate an ordered fix plan")
    plan_p.add_argument("--format", default="md", choices=["md", "json"], help="Output format")
    plan_p.add_argument("--out", default="", help="Write output to a file")

    next_p = subparsers.add_parser("next", help="Print the next issue (highest priority)")
    next_p.add_argument("--format", default="json", choices=["json", "md"], help="Output format")

    mark_p = subparsers.add_parser("mark-done", help="Mark an issue as done in local state")
    mark_p.add_argument("issue_key")

    skip_p = subparsers.add_parser("skip", help="Skip an issue in local state")
    skip_p.add_argument("issue_key")

    subparsers.add_parser("reset", help="Reset local progress state")

    return parser.parse_args(argv)


def _build_context(args: argparse.Namespace) -> LoopContext:
    org0, project0, branch0, token0 = _infer_defaults()

    org = args.organization or org0
    project = args.project or project0
    branch = args.branch or branch0
    token = args.token or token0

    pr = (args.pull_request or "").strip()

    if not org or not project:
        raise ValueError("Could not infer Sonar org/project. Pass --organization and --project.")
    if not token:
        raise ValueError("Missing token. Set SONARQUBE_TOKEN or pass --token.")

    state_path = Path(args.state) if args.state else DEFAULT_STATE_PATH

    fmt = getattr(args, "format", "") or "json"
    out = getattr(args, "out", "") or ""

    return LoopContext(
        organization=org,
        project=project,
        branch=branch,
        token=token,
        pull_request=pr,
        state_path=state_path,
        format=fmt,
        out=out,
    )


def _fetch_issues(ctx: LoopContext) -> list[dict[str, Any]]:
    cli = load_sonar_issues_cli_module()

    result = cli.get_issues_unresolved(
        organization=ctx.organization,
        project=ctx.project,
        branch=ctx.branch,
        token=ctx.token,
        pull_request=ctx.pull_request or None,
    )
    issues = result.get("issues", [])
    if not isinstance(issues, list):
        return []
    return issues


def _write_output(text: str, out_path: str) -> None:
    if not out_path:
        print(text)
        return

    path = Path(out_path)
    _ensure_parent_dir(path)
    path.write_text(text, encoding="utf-8")
    print(f"Wrote output to {path}")


def cmd_plan(ctx: LoopContext) -> int:
    issues = _fetch_issues(ctx)
    state = _load_state(ctx.state_path)

    remaining = _select_remaining_issues(issues, state)
    if ctx.format == "json":
        payload = {
            "remaining": len(remaining),
            "issues": remaining,
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        _write_output(text, ctx.out)
        return 0

    lines: list[str] = []
    lines.append(f"# SonarCloud fix plan")
    lines.append("")
    lines.append(f"- Organization: `{ctx.organization}`")
    lines.append(f"- Project: `{ctx.project}`")
    if ctx.pull_request:
        lines.append(f"- Pull request: `{ctx.pull_request}`")
    else:
        lines.append(f"- Branch: `{ctx.branch}`")
    lines.append(f"- Generated at: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append(f"## Remaining: {len(remaining)}")
    lines.append("")
    for it in remaining:
        lines.append(_render_issue_md(it))
    text = "\n".join(lines)
    _write_output(text, ctx.out)
    return 0


def cmd_next(ctx: LoopContext) -> int:
    issues = _fetch_issues(ctx)
    state = _load_state(ctx.state_path)
    remaining = _select_remaining_issues(issues, state)

    if not remaining:
        print(json.dumps({"remaining": 0, "next": None}, indent=2))
        return 0

    nxt = remaining[0]
    if ctx.format == "md":
        print(_render_issue_md(nxt))
        return 0

    print(json.dumps({"remaining": len(remaining), "next": nxt}, indent=2, ensure_ascii=False))
    return 0


def _update_state_list(state: dict[str, Any], key: str, list_name: str) -> None:
    items = state.get(list_name, [])
    if not isinstance(items, list):
        items = []
    if key not in items:
        items.append(key)
    state[list_name] = items


def cmd_mark_done(ctx: LoopContext, issue_key: str) -> int:
    state = _load_state(ctx.state_path)
    _update_state_list(state, issue_key, "done")
    _save_state(ctx.state_path, state)
    print(f"Marked {issue_key} as done in {ctx.state_path}")
    return 0


def cmd_skip(ctx: LoopContext, issue_key: str) -> int:
    state = _load_state(ctx.state_path)
    _update_state_list(state, issue_key, "skipped")
    _save_state(ctx.state_path, state)
    print(f"Skipped {issue_key} in {ctx.state_path}")
    return 0


def cmd_reset(ctx: LoopContext) -> int:
    state = {"done": [], "skipped": [], "updatedAt": None}
    _save_state(ctx.state_path, state)
    print(f"Reset state in {ctx.state_path}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    ctx = _build_context(args)

    if args.command == "plan":
        return cmd_plan(ctx)
    if args.command == "next":
        return cmd_next(ctx)
    if args.command == "mark-done":
        return cmd_mark_done(ctx, args.issue_key)
    if args.command == "skip":
        return cmd_skip(ctx, args.issue_key)
    if args.command == "reset":
        return cmd_reset(ctx)

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)

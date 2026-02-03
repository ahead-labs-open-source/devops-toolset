---
name: sonarcloud-issue-fixer
description: Fetch unresolved SonarCloud issues for the current repo, prioritize them, and drive an iterative fix loop (one issue at a time) until the backlog is cleared.
license: GPL-3.0
metadata:
  author: Ahead Labs Software
---

# SonarCloud Issue Fixer

## Goal

- Fetch all **unresolved** SonarCloud issues for the *current repository* and *current branch*.
- Sort them by **priority** (severity first, then type).
- Fix them **one by one** in small, reviewable changes, until the list is empty (after the next Sonar analysis run).

This skill is designed for an AI agent + human workflow: the agent performs the code changes, and SonarCloud clears the issues after CI runs a new analysis.

## Required configuration

### Authentication

- Set `SONARQUBE_TOKEN` (recommended) or pass `--token`.

### Project auto-detection (defaults)

The helper script tries to infer defaults from the Git remote:

- SonarCloud `organization` defaults to GitHub owner
- SonarCloud `project` defaults to repo name
- `branch` defaults to current git branch

Override anytime via env vars or CLI:

- `SONARCLOUD_ORG`
- `SONARCLOUD_PROJECT`
- `SONARCLOUD_BRANCH`

## Core workflow

### 1) Generate a prioritized plan

- `python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issue_fix_loop.py plan --format md --out sonarcloud-fix-plan.md`

This produces an ordered list with the most important issues first.

### 2) Take the next issue

- `python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issue_fix_loop.py next --format json`

Then:

- Open the referenced file/line.
- Apply the smallest safe fix.
- Run the most relevant validation for this repo (format/lint/tests if applicable).
- Commit with a clear message.

### 3) Mark progress and continue

- `python .github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issue_fix_loop.py mark-done <issueKey>`
- Repeat `next` until there are no remaining issues.

## Prioritization rules

See [.github/skills/sonarcloud-issue-fixer/references/prioritization.md](.github/skills/sonarcloud-issue-fixer/references/prioritization.md).

## Definition of done

- `plan` reports `0` remaining unresolved issues (after CI Sonar analysis runs).
- No new issues introduced by the changes.

## Safety rules

- Prefer minimal diffs; avoid refactors unless required.
- Don’t silence issues (e.g., `//NOSONAR`) unless explicitly justified.
- Keep fixes scoped: 1–3 issues per commit is ideal.

## Related tool

The underlying SonarCloud issue fetcher lives at:

- [.github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issues_cli.py](.github/skills/sonarcloud-issue-fixer/scripts/sonarcloud_issues_cli.py)

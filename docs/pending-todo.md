# Pending TODO (public)

This document lists pending tasks for the repository.

Constraints:

- Public-safe only: do not include secrets, internal URLs, customer names, or logs containing credentials.
- English-only: keep all documentation in English.

## README

- [ ] Fix README badges: identify broken ones and update URLs/paths (CI, coverage, PyPI, license, etc.) so they render correctly on GitHub.
  - [ ] List which badges are currently broken and why (repo/branch/workflow renamed, outdated paths, etc.).
  - [ ] Update badges for `main` and/or `feature/*` as appropriate.
  - [ ] Verify workflows exist and publish the expected artifacts (e.g., coverage reports).

## Packaging / Poetry / Project layout

- [ ] Review whether the `src/devops_toolset` layout is consistent with Poetry and Python packaging best practices.
  - [ ] Confirm whether Poetry is already being used for dependency and version management.
    - Current observation (to validate): `pyproject.toml` exists but appears focused on a `setuptools` build-system; `setup.py` and `requirements.txt` also exist.
  - [ ] Decide whether the repo should migrate fully to Poetry or stay on `setuptools`.
  - [ ] If migrating to Poetry:
    - [ ] Define `tool.poetry` (name/version/deps) and move dependencies from `requirements.txt`.
    - [ ] Define a versioning strategy (e.g., `project.xml` vs git tags/semver vs Poetry-managed version).
    - [ ] Update CI to install via Poetry and run tests.
  - [ ] Evaluate whether `setup.py` still makes sense:
    - [ ] If kept: document why (compatibility, classic packaging workflows).
    - [ ] If removed: ensure full replacement (build, publish, editable install) and update docs/CI.

## Tooling (SonarCloud)

- [ ] Bring `sonarcloud_issues_cli.py` into this repository (do not copy blindly):

  - Source: https://github.com/ahead-labs-software/signatus-surface/blob/main/.github/tools/sonarcloud_issues_cli.py

  - [ ] Decide the appropriate location (proposal: `.github/tools/` or `src/devops_toolset/tools/sonarcloud_issues_cli.py`, depending on how it will be executed).
  - [ ] Verify license/attribution/compatibility before copying any code (keep compliance).
  - [ ] Integrate into CI if applicable (e.g., a job to list issues and fail on a threshold).
  - [ ] Add usage documentation (args, examples) and local run instructions.

- [ ] Run an initial SonarCloud analysis on the default branch `main` (it used to be `master`).
  - [ ] Verify SonarCloud project settings reference `main` as the main branch.
  - [ ] Update any pipeline/workflow configuration that still assumes `master`.
  - [ ] Ensure README links/badges (coverage/quality gate) reflect the `main` branch.

## CI/CD (Azure Pipelines -> GitHub Actions)

- [ ] Migrate CI/CD from Azure DevOps Pipelines to GitHub Actions.
  - [ ] Inventory current Azure Pipelines definitions/templates (e.g., under `src/devops_toolset/.devops/`) and document what each job does.
  - [ ] Decide the target workflows to create (minimum viable):
    - [ ] Unit tests (pytest) on PRs and pushes.
    - [ ] Lint/static checks if applicable.
    - [ ] SonarCloud analysis (if still required for this repo).
    - [ ] Build/package verification (sdist/wheel) and optional publish.
  - [ ] Create `.github/workflows/*` equivalents and verify they run on PRs.
  - [ ] Port secrets/variables from Azure DevOps to GitHub Actions secrets (no secrets in repo).
  - [ ] Update README badges to reflect the new GitHub Actions workflows.
  - [ ] Deprecate/remove Azure Pipelines config only after parity is confirmed.

## Maintenance

- [ ] If docs grow, add a minimal `docs/README.md` describing what belongs in `docs/` and how to keep it up to date.

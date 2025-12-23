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

## Maintenance

- [ ] If docs grow, add a minimal `docs/README.md` describing what belongs in `docs/` and how to keep it up to date.

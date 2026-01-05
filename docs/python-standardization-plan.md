# Python Standardization Plan: Poetry Migration and PyPI Publishing

**Date:** January 4, 2026  
**Branch:** develop  
**Status:** Planning

## Executive Summary

This document presents a comprehensive analysis of the `devops-toolset` repository and provides a migration plan to standardize it as a modern Python package using Poetry, ready for public publication on PyPI with CI/CD via GitHub Actions.

**Current State:** The repository uses setuptools with a basic pyproject.toml (PEP 517/518) but does NOT use Poetry. It has functional Azure Pipelines but lacks GitHub Actions.

**Goal:** Fully migrate to Poetry, implement GitHub Actions, add standard documentation, and resolve critical inconsistencies.

---

## 1. Current State Analysis

### 1.1 Package Structure

#### Current Configuration

**pyproject.toml:**
- ✅ Exists but is minimal
- ❌ NOT using Poetry (uses `build-backend = "setuptools.build_meta"`)
- ❌ Missing `[tool.poetry]` section
- Only defines build-system with dependencies

**setup.py:**
- ✅ Present and is the primary packaging mechanism
- ⚠️ Imports from package (`from devops_toolset.filesystem.parsers import ProjectParser`) - circular dependency risk
- Reads version from `project.xml` (non-standard)
- Uses `find_namespace_packages("src")`

**requirements.txt:**
- ✅ Present
- ❌ **Version conflicts** with pyproject.toml:
  - setuptools: 57.0.0 (pyproject) vs 65.5.1 (requirements)
  - requests: >=2.25.1 (pyproject) vs >=2.31.0 (requirements)
- ⚠️ Mixes runtime and test dependencies (pytest, pytest-cov)

#### Directory Structure

```
/
├── devops_toolset/          ← ❌ ONLY __pycache__/ (artifacts)
│   ├── core/__pycache__/
│   ├── filesystem/__pycache__/
│   ├── i18n/__pycache__/
│   └── project_types/__pycache__/
│
└── src/
    └── devops_toolset/      ← ✅ ACTUAL SOURCE CODE
```

**Critical Finding:** The root `devops_toolset/` folder only contains `__pycache__/` - should be removed.

### 1.2 Version Management

**Current Method:** `project.xml` (custom XML)

```xml
<project>
    <name>devops-toolset</name>
    <version>2.18.0</version>
    <organization>Ahead Labs</organization>
</project>
```

**Issues:**
- ❌ Not Python standard
- ❌ Requires custom parser
- ❌ No `__version__` in `__init__.py`
- ⚠️ Difficult to automate with standard tools

### 1.3 Package Metadata

**`__init__.py` files:**
- ❌ `src/devops_toolset/__init__.py` is empty
- ❌ Does not define `__version__`
- ❌ Does not define `__all__` (public API)
- ⚠️ Only some submodules have docstrings

### 1.4 Testing and CI/CD

#### Testing
- ✅ **Excellent test structure** reflecting source code
- ✅ pytest.ini configured
- ✅ Complete .coveragerc
- ✅ conftest.py at all levels

#### CI/CD
**Azure Pipelines:**
- ✅ Fully configured in `.azure-pipelines/`
- ✅ Main pipeline: `pipeline-build-devopstoolset-ci.yml`
- ✅ Multiple reusable templates
- ✅ SonarCloud integration
- ✅ Builds and publishes to PyPI

**GitHub Actions:**
- ❌ **DOES NOT EXIST** `.github/workflows/`
- ❌ README.md references badges for `ci.yml` and `cd.yml` that don't exist
- ❌ Broken badges (documented in docs/pending-todo.md)

### 1.5 Documentation

**Existing:**
- ✅ Detailed README.md (but with broken badges)
- ✅ LICENSE (GNU GPL v3.0)
- ✅ docs/pending-todo.md (lists known issues)

**Missing:**
- ❌ CONTRIBUTING.md
- ❌ CHANGELOG.md
- ❌ CODE_OF_CONDUCT.md
- ❌ SECURITY.md
- ❌ API documentation
- ❌ Development guides
- ⚠️ docs/ has only 1 file

### 1.6 Code Quality Tools

**Configured:**
- ✅ .pylintrc (411 lines)
- ✅ .gitignore
- ✅ sonar-project.properties (SonarCloud)

**Missing:**
- ❌ .flake8
- ❌ mypy.ini or mypy configuration
- ❌ .pre-commit-config.yaml
- ❌ tox.ini
- ❌ black configuration
- ❌ isort configuration
- ❌ ruff configuration

### 1.7 Distribution Readiness

**Status:**
- ✅ Already published on PyPI: https://pypi.org/project/devops-toolset/
- ⚠️ No MANIFEST.in (relies on auto-discovery)
- ⚠️ `.devops/` folder may not be included in distribution
- ✅ `package_data` configured in setup.py
- ✅ `include_package_data=True`

### 1.8 Critical Issues Identified

#### 🔴 Critical

1. **Inconsistent License:**
   - LICENSE file: GNU GPL v3.0
   - pyproject.toml: MIT
   - **ACTION REQUIRED:** Decide on final license

2. **setup.py imports from package:**
   ```python
   from devops_toolset.filesystem.parsers import ProjectParser
   ```
   - Risk of circular dependency during installation

3. **Version Conflicts:**
   - setuptools: 57.0.0 vs 65.5.1
   - requests: >=2.25.1 vs >=2.31.0

#### 🟡 Moderate

4. Root `devops_toolset/` folder only has __pycache__
5. Non-standard versioning (project.xml)
6. No accessible `__version__`
7. requirements.txt mixes dev/runtime deps
8. GitHub Actions missing
9. Minimal documentation

#### 🟢 Minor

10. Missing standard documentation (CONTRIBUTING, CHANGELOG, etc.)
11. Limited quality tools
12. No CLI entry points
13. `.devops/` folder in source tree

---

## 2. Poetry Migration Plan

### 2.1 Phase 1: Poetry Configuration

#### Step 1.1: Create Complete pyproject.toml

**File:** `pyproject.toml`

**New Content:**

```toml
[tool.poetry]
name = "devops-toolset"
version = "2.18.0"
description = "DevOps Toolset - A comprehensive Python package for DevOps automation"
authors = ["Ahead Labs <info@aheadlabs.com>"]
license = "GPL-3.0-or-later"  # Or "MIT" based on decision
readme = "README.md"
homepage = "https://github.com/ahead-labs-open-source/devops-toolset"
repository = "https://github.com/ahead-labs-open-source/devops-toolset"
documentation = "https://github.com/ahead-labs-open-source/devops-toolset/blob/main/README.md"
keywords = ["devops", "automation", "ci-cd", "azure", "aws"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Systems Administration",
]
packages = [{include = "devops_toolset", from = "src"}]
include = [
    "src/devops_toolset/core/*.json",
    "src/devops_toolset/locales/**/*.mo",
    "src/devops_toolset/json-schemas/**/*.json",
]

[tool.poetry.dependencies]
python = "^3.9"
requests = ">=2.31.0"
colorama = ">=0.4.4"
clint = ">=0.5.1"
pyfiglet = ">=0.8"
boto3 = "^1.24.92"
botocore = "^1.27.92"
pyyaml = ">=6.0.1"

[tool.poetry.group.dev.dependencies]
pytest = "^7.1.3"
pytest-cov = ">=2.11.1"
black = "^23.0.0"
isort = "^5.12.0"
mypy = "^1.0.0"
ruff = "^0.1.0"
pre-commit = "^3.0.0"

[tool.poetry.scripts]
# Define CLI commands if needed
# devops-toolset = "devops_toolset.cli:main"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

# Tool Configuration
[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
follow_imports = "normal"
ignore_missing_imports = true

[tool.ruff]
target-version = "py39"
line-length = 100
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.pytest.ini_options]
addopts = "--strict-markers --cov=devops_toolset --cov-report=html --cov-report=xml"
testpaths = ["tests"]
markers = [
    "slow: Run tests that use sample data from file",
]
junit_family = "xunit2"

[tool.coverage.run]
branch = true
source = ["src/devops_toolset"]
omit = [
    "**/__init__.py",
    "**/__pycache__/*",
    "**/tests/*",
    "tests/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if False:",
]
skip_covered = true
show_missing = true

[tool.coverage.html]
directory = "tests/.pytest/htmlcov/"
```

#### Step 1.2: Implement __version__ in Package

**File:** `src/devops_toolset/__init__.py`

```python
"""DevOps Toolset - A comprehensive Python package for DevOps automation.

This package provides tools and utilities for DevOps workflows including:
- CI/CD automation
- Cloud platform integration (Azure, AWS)
- Project type management
- Build and deployment utilities
"""

__version__ = "2.18.0"
__author__ = "Ahead Labs"
__email__ = "info@aheadlabs.com"

__all__ = [
    "__version__",
    "__author__",
    "__email__",
]
```

#### Step 1.3: Create Version Sync Script

**File:** `scripts/sync_version.py`

```python
#!/usr/bin/env python3
"""Sync version between pyproject.toml and __init__.py"""

import re
from pathlib import Path


def get_version_from_pyproject() -> str:
    """Extract version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    return match.group(1)


def update_init_version(version: str) -> None:
    """Update version in __init__.py"""
    init_path = Path(__file__).parent.parent / "src" / "devops_toolset" / "__init__.py"
    content = init_path.read_text()
    new_content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{version}"',
        content
    )
    init_path.write_text(new_content)
    print(f"✅ Updated __version__ to {version} in {init_path}")


def main():
    version = get_version_from_pyproject()
    print(f"Version in pyproject.toml: {version}")
    update_init_version(version)


if __name__ == "__main__":
    main()
```

#### Step 1.4: Remove Obsolete Files

**Actions:**
1. ✅ Remove `setup.py`
2. ✅ Remove `requirements.txt`
3. ⚠️ Keep `project.xml` temporarily (pending decision)
4. ✅ Remove root `devops_toolset/` folder (only __pycache__)

### 2.2 Phase 2: License and Structure Fixes

#### Step 2.1: Resolve License Inconsistency

**DECISION REQUIRED:**

**Option A: Keep GPL v3.0 (Recommended if GPL code exists)**
- ✅ Already have LICENSE file
- Update pyproject.toml: `license = "GPL-3.0-or-later"`
- Classifier: `"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"`
- More restrictive (copyleft)

**Option B: Change to MIT**
- Replace LICENSE file
- Update pyproject.toml: `license = "MIT"`
- Classifier: `"License :: OSI Approved :: MIT License"`
- More permissive
- Requires verifying all code is compatible

#### Step 2.2: Create MANIFEST.in

**File:** `MANIFEST.in`

```
include README.md
include LICENSE
include pyproject.toml
include pytest.ini

recursive-include src/devops_toolset/json-schemas *.json
recursive-include src/devops_toolset/locales *.mo
recursive-include src/devops_toolset/core *.json

exclude project.xml
exclude setup.py
exclude requirements.txt
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
recursive-exclude .azure-pipelines *
```

#### Step 2.3: Reorganize .devops/

**Option A:** Move outside src/

```bash
mv src/devops_toolset/.devops .azure-pipelines/legacy/
```

**Option B:** Keep but exclude from distribution

Update MANIFEST.in:
```
recursive-exclude src/devops_toolset/.devops *
```

#### Step 2.4: Clean Root Folder

```bash
rm -rf devops_toolset/
```

Verify in .gitignore:
```
devops_toolset/
```

### 2.3 Phase 3: GitHub Actions CI/CD

#### Step 3.1: Create CI Workflow

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true
    
    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
    
    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: poetry install --no-interaction --no-root
    
    - name: Install project
      run: poetry install --no-interaction
    
    - name: Run tests
      run: |
        poetry run pytest --cov --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
    
    - name: Install dependencies
      run: poetry install --with dev
    
    - name: Run black
      run: poetry run black --check src tests
    
    - name: Run isort
      run: poetry run isort --check-only src tests
    
    - name: Run ruff
      run: poetry run ruff check src tests
    
    - name: Run mypy
      run: poetry run mypy src
      continue-on-error: true
```

#### Step 3.2: Create CD Workflow (Deploy)

**File:** `.github/workflows/cd.yml`

```yaml
name: CD

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install Poetry
      uses: snok/install-poetry@v1
    
    - name: Build package
      run: poetry build
    
    - name: Store distribution packages
      uses: actions/upload-artifact@v3
      with:
        name: python-package-distributions
        path: dist/

  publish-to-pypi:
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/devops-toolset
    permissions:
      id-token: write

    steps:
    - name: Download distributions
      uses: actions/download-artifact@v3
      with:
        name: python-package-distributions
        path: dist/
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1

  github-release:
    name: Upload to GitHub Release
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
    - name: Download distributions
      uses: actions/download-artifact@v3
      with:
        name: python-package-distributions
        path: dist/
    
    - name: Upload to Release
      env:
        GITHUB_TOKEN: ${{ github.token }}
      run: |
        gh release upload '${{ github.ref_name }}' dist/** --repo '${{ github.repository }}'
```

#### Step 3.3: Update README.md with New Badges

```markdown
# DevOps Toolset

[![CI](https://github.com/ahead-labs-open-source/devops-toolset/workflows/CI/badge.svg)](https://github.com/ahead-labs-open-source/devops-toolset/actions/workflows/ci.yml)
[![CD](https://github.com/ahead-labs-open-source/devops-toolset/workflows/CD/badge.svg)](https://github.com/ahead-labs-open-source/devops-toolset/actions/workflows/cd.yml)
[![codecov](https://codecov.io/gh/ahead-labs-open-source/devops-toolset/branch/main/graph/badge.svg)](https://codecov.io/gh/ahead-labs-open-source/devops-toolset)
[![PyPI version](https://badge.fury.io/py/devops-toolset.svg)](https://badge.fury.io/py/devops-toolset)
[![Python Versions](https://img.shields.io/pypi/pyversions/devops-toolset.svg)](https://pypi.org/project/devops-toolset/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=devops-toolset&metric=alert_status)](https://sonarcloud.io/dashboard?id=devops-toolset)
```

### 2.4 Phase 4: Standard Documentation

#### Step 4.1: CONTRIBUTING.md

**File:** `CONTRIBUTING.md`

```markdown
# Contributing to DevOps Toolset

We love your input! We want to make contributing to DevOps Toolset as easy and transparent as possible.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/devops-toolset.git`
3. Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
4. Install dependencies: `poetry install --with dev`
5. Install pre-commit hooks: `poetry run pre-commit install`

## Development Process

1. Create a branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Run tests: `poetry run pytest`
4. Run linting: `poetry run ruff check .`
5. Format code: `poetry run black .`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## Code Quality Standards

- All tests must pass
- Code coverage should not decrease
- Follow PEP 8 style guidelines
- Add docstrings to all public functions/classes
- Update documentation as needed

## Testing

Run the full test suite:
```bash
poetry run pytest
```

Run with coverage:
```bash
poetry run pytest --cov --cov-report=html
```

## Reporting Bugs

Report bugs via [GitHub Issues](https://github.com/ahead-labs-open-source/devops-toolset/issues).

**Great Bug Reports** include:
- Quick summary
- Steps to reproduce
- What you expected
- What actually happens
- Notes (possible fixes, etc.)

## License

By contributing, you agree that your contributions will be licensed under the GNU GPL v3.0.
```

#### Step 4.2: CHANGELOG.md

**File:** `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Poetry configuration for dependency management
- GitHub Actions CI/CD workflows
- Pre-commit hooks configuration
- Comprehensive code quality tools (black, isort, mypy, ruff)
- Standard documentation (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)
- `__version__` in package `__init__.py`

### Changed
- Migrated from setuptools to Poetry
- Standardized project structure
- Updated dependency versions
- Improved testing configuration

### Removed
- Deprecated `setup.py`
- Removed `requirements.txt` (replaced by Poetry)
- Cleaned up `devops_toolset/` root folder artifacts

### Fixed
- License inconsistency (GPL v3 vs MIT)
- Version conflicts between configuration files
- Circular import in setup.py

## [2.18.0] - 2024-XX-XX

### Previous Releases
See [GitHub Releases](https://github.com/ahead-labs-open-source/devops-toolset/releases) for earlier versions.

[Unreleased]: https://github.com/ahead-labs-open-source/devops-toolset/compare/v2.18.0...HEAD
[2.18.0]: https://github.com/ahead-labs-open-source/devops-toolset/releases/tag/v2.18.0
```

#### Step 4.3: CODE_OF_CONDUCT.md

**File:** `CODE_OF_CONDUCT.md`

```markdown
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior:

* The use of sexualized language or imagery
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information without permission
* Other conduct which could reasonably be considered inappropriate

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the project team at info@aheadlabs.com. All complaints will be
reviewed and investigated promptly and fairly.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

[homepage]: https://www.contributor-covenant.org
```

#### Step 4.4: SECURITY.md

**File:** `SECURITY.md`

```markdown
# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.18.x  | :white_check_mark: |
| < 2.18  | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@aheadlabs.com**

You should receive a response within 48 hours. If for some reason you do not,
please follow up via email to ensure we received your original message.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported releases
4. Release patches as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a
pull request.
```

### 2.5 Phase 5: Code Quality Tools

#### Step 5.1: Create .pre-commit-config.yaml

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        name: isort (python)

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

#### Step 5.2: Update .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Poetry
poetry.lock

# Virtual environments
venv/
ENV/
env/
.venv/

# IDEs
.vscode/
.idea/
.vs/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
tests/.pytest/

# Localization
*.pot
*.mo
*.po

# Logs
*.log
logs/

# Config files
*.json*

# DevOps Toolset specific
devops_toolset/  # Root level artifacts only
project.xml      # If decided to remove

# OS
.DS_Store
Thumbs.db
```

### 2.6 Phase 6: Entry Points and Accessible Version

#### Step 6.1: Define CLI Entry Points (if applicable)

If the package should expose CLI commands, add to `pyproject.toml`:

```toml
[tool.poetry.scripts]
devops-toolset = "devops_toolset.cli:main"
devops-tool = "devops_toolset.tools.cli:main"
# Add other commands as needed
```

And create corresponding modules:

**File:** `src/devops_toolset/cli.py`

```python
#!/usr/bin/env python3
"""Main CLI entry point for devops-toolset."""

import sys
from devops_toolset.core.app import main as app_main


def main():
    """Execute the main application."""
    return app_main()


if __name__ == "__main__":
    sys.exit(main())
```

#### Step 6.2: Make Version Programmatically Accessible

Users can import version:

```python
from devops_toolset import __version__
print(__version__)  # "2.18.0"
```

#### Step 6.3: Update docs/pending-todo.md

Mark as resolved:
- ✅ Poetry vs setuptools decision
- ✅ Version conflicts
- ✅ GitHub Actions badges
- ✅ License inconsistency

---

## 3. Pending Decisions

### 3.1 License (CRITICAL)

**Must be resolved BEFORE publishing:**

- [ ] **Option A:** Keep GPL v3.0 (current LICENSE file)
  - More restrictive
  - Copyleft - derivatives must be GPL
  - Appropriate if GPL dependencies exist
  
- [ ] **Option B:** Change to MIT
  - More permissive
  - Allows proprietary derivatives
  - Requires verifying compatibility with all dependencies

**Recommendation:** Review dependencies and expected usage before deciding.

### 3.2 project.xml

**Options:**

- [ ] **Option A:** Remove completely
  - Use only `pyproject.toml` and `__version__`
  - More standard
  
- [ ] **Option B:** Keep but read from `__version__`
  - Invert dependency
  - Script that updates XML from Python
  
- [ ] **Option C:** Keep temporarily
  - Gradual migration plan
  - Document deprecation

**Recommendation:** Option A (remove) for simplicity.

### 3.3 CI/CD

**Migration Strategy:**

- [ ] **Option A:** Keep both (Azure + GitHub) temporarily
  - Gradual transition
  - More costly to maintain
  
- [ ] **Option B:** Immediate migration to GitHub Actions
  - Cleaner
  - Requires configuring secrets in GitHub
  
- [ ] **Option C:** GitHub Actions only
  - Deprecate Azure Pipelines
  - Document migration

**Recommendation:** Option B (full migration) with documentation.

### 3.4 .devops/ in Source Tree

- [ ] **Option A:** Move to `.azure-pipelines/legacy/`
- [ ] **Option B:** Keep but exclude from distribution
- [ ] **Option C:** Remove if no longer used

**Recommendation:** Option A (move) if templates still needed.

---

## 4. Implementation Checklist

### Phase 1: Poetry Setup ✅ PRIORITY

- [ ] Create complete `pyproject.toml` with Poetry
- [ ] Implement `__version__` in `src/devops_toolset/__init__.py`
- [ ] Create `scripts/sync_version.py`
- [ ] Generate `poetry.lock`: `poetry lock`
- [ ] Install dependencies: `poetry install`
- [ ] Verify build: `poetry build`
- [ ] **DECISION:** License (GPL v3 or MIT)
- [ ] Update license in pyproject.toml
- [ ] Remove `setup.py`
- [ ] Remove `requirements.txt`
- [ ] Commit: "feat: migrate to Poetry for dependency management"

### Phase 2: Structure and Cleanup 🧹

- [ ] Remove root `devops_toolset/` folder
- [ ] Create `MANIFEST.in`
- [ ] **DECISION:** What to do with `.devops/`?
- [ ] Move/remove `.devops/` based on decision
- [ ] **DECISION:** Keep `project.xml`?
- [ ] Remove/mark deprecated `project.xml` based on decision
- [ ] Update `.gitignore`
- [ ] Commit: "chore: clean up project structure"

### Phase 3: GitHub Actions 🚀

- [ ] Create `.github/workflows/ci.yml`
- [ ] Create `.github/workflows/cd.yml`
- [ ] Configure GitHub secrets:
  - `PYPI_TOKEN`
  - `SONAR_TOKEN` (optional)
  - `CODECOV_TOKEN` (optional)
- [ ] Update badges in `README.md`
- [ ] Test workflows with push to develop
- [ ] Commit: "ci: implement GitHub Actions workflows"

### Phase 4: Documentation 📚

- [ ] Create `CONTRIBUTING.md`
- [ ] Create `CHANGELOG.md`
- [ ] Create `CODE_OF_CONDUCT.md`
- [ ] Create `SECURITY.md`
- [ ] Update `README.md` with new instructions
- [ ] Expand `docs/` with additional guides
- [ ] Update/close issues in `docs/pending-todo.md`
- [ ] Commit: "docs: add standard project documentation"

### Phase 5: Code Quality Tools 🔧

- [ ] Create `.pre-commit-config.yaml`
- [ ] Install hooks: `poetry run pre-commit install`
- [ ] Run on all files: `poetry run pre-commit run --all-files`
- [ ] Format code: `poetry run black src tests`
- [ ] Sort imports: `poetry run isort src tests`
- [ ] Fix linting: `poetry run ruff check --fix src tests`
- [ ] Commit: "style: format code with black and isort"
- [ ] Commit: "chore: add pre-commit hooks and code quality tools"

### Phase 6: Entry Points and Testing 🎯

- [ ] **DECISION:** Expose CLI commands?
- [ ] Define entry points in `pyproject.toml` if applicable
- [ ] Create CLI modules if needed
- [ ] Update tests if structure changes
- [ ] Run full suite: `poetry run pytest`
- [ ] Verify coverage: `poetry run pytest --cov`
- [ ] Commit: "feat: add CLI entry points" (if applicable)

### Phase 7: Final Validation ✔️

- [ ] Verify all tests pass
- [ ] Verify local build: `poetry build`
- [ ] Install locally: `pip install dist/*.whl`
- [ ] Test import: `python -c "import devops_toolset; print(devops_toolset.__version__)"`
- [ ] Verify GitHub Actions passes
- [ ] Review coverage report
- [ ] Update version in `pyproject.toml` (e.g., 2.19.0)
- [ ] Run `poetry run python scripts/sync_version.py`
- [ ] Commit: "chore: bump version to 2.19.0"
- [ ] Tag: `git tag -a v2.19.0 -m "Release v2.19.0 - Poetry migration"`
- [ ] Push: `git push origin develop --tags`

### Phase 8: Release 🎉

- [ ] Merge develop → main
- [ ] Create GitHub Release from tag
- [ ] Verify CD workflow publishes to PyPI
- [ ] Verify on PyPI: https://pypi.org/project/devops-toolset/
- [ ] Announce changes in README/CHANGELOG
- [ ] **DECISION:** Deprecate Azure Pipelines?
- [ ] Document migration for users

---

## 5. Useful Commands

### Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Initialize project (if new)
poetry init

# Install dependencies
poetry install

# Install with dev dependencies
poetry install --with dev

# Add dependency
poetry add requests

# Add dev dependency
poetry add --group dev pytest

# Update dependencies
poetry update

# Show dependencies
poetry show --tree

# Build
poetry build

# Publish (requires PyPI token configuration)
poetry publish

# Run command
poetry run pytest
poetry run black .
```

### Pre-commit

```bash
# Install hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files

# Update hooks
poetry run pre-commit autoupdate
```

### Testing

```bash
# Basic tests
poetry run pytest

# With coverage
poetry run pytest --cov --cov-report=html

# Only slow tests
poetry run pytest -m slow

# Specific tests
poetry run pytest tests/core/app_test.py

# Verbose mode
poetry run pytest -v
```

### Linting and Formatting

```bash
# Black (format)
poetry run black src tests

# Black (check only)
poetry run black --check src tests

# isort (sort imports)
poetry run isort src tests

# Ruff (linting)
poetry run ruff check src tests

# Ruff (auto fix)
poetry run ruff check --fix src tests

# Mypy (type checking)
poetry run mypy src
```

---

## 6. Risks and Mitigations

### Risk 1: Breaking Changes for Users

**Mitigation:**
- Document changes in CHANGELOG.md
- Bump major version (2.x → 3.0) if incompatible changes
- Keep installation instructions simple

### Risk 2: Incompatible Dependencies

**Mitigation:**
- Test on multiple Python versions (3.9-3.12)
- Use matrix in GitHub Actions
- Verify poetry.lock generates correctly

### Risk 3: CI/CD Failures

**Mitigation:**
- Test workflows in feature branch first
- Configure secrets correctly
- Keep Azure Pipelines temporarily as backup

### Risk 4: Loss of Azure Pipelines Features

**Mitigation:**
- Inventory all features used
- Replicate in GitHub Actions
- Document differences

### Risk 5: License Legal Issues

**Mitigation:**
- **Consult with legal/IP team before changing license**
- Audit dependencies with tools (liccheck, pip-licenses)
- Document reasons for change

---

## 7. Estimated Timeline

| Phase | Duration | Priority |
|------|----------|-----------|
| 1. Poetry Setup | 2-4 hours | 🔴 CRITICAL |
| 2. Structure and Cleanup | 1-2 hours | 🟡 HIGH |
| 3. GitHub Actions | 3-4 hours | 🟡 HIGH |
| 4. Documentation | 2-3 hours | 🟢 MEDIUM |
| 5. Code Quality Tools | 2-3 hours | 🟢 MEDIUM |
| 6. Entry Points | 1-2 hours | 🔵 LOW |
| 7. Final Validation | 2-3 hours | 🟡 HIGH |
| 8. Release | 1 hour | 🟡 HIGH |

**Total Estimated:** 14-22 hours of work

---

## 8. Resources and References

### Poetry

- [Official Documentation](https://python-poetry.org/docs/)
- [Dependency Management](https://python-poetry.org/docs/dependency-specification/)
- [Publishing](https://python-poetry.org/docs/repositories/)

### GitHub Actions

- [Python Workflows](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [Publishing to PyPI](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

### Python Packaging

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 517](https://peps.python.org/pep-0517/) - Build System
- [PEP 518](https://peps.python.org/pep-0518/) - pyproject.toml
- [PEP 621](https://peps.python.org/pep-0621/) - Project Metadata

### Code Quality

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pre-commit Documentation](https://pre-commit.com/)

---

## Appendix A: Migration Commands Summary

```bash
# 1. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Create pyproject.toml (manually or from template)
# 3. Remove old files
rm setup.py requirements.txt
rm -rf devops_toolset/

# 4. Initialize Poetry
poetry lock
poetry install --with dev

# 5. Test build
poetry build

# 6. Install pre-commit hooks
poetry run pre-commit install
poetry run pre-commit run --all-files

# 7. Format code
poetry run black src tests
poetry run isort src tests

# 8. Run tests
poetry run pytest --cov

# 9. Commit changes
git add .
git commit -m "feat: migrate to Poetry"
git push
```

---

## Appendix B: Configuration File Comparison

### Before (setuptools)

**setup.py:**
- Manual configuration
- Imports from package (risky)
- Custom version reading

**requirements.txt:**
- Flat file
- Version conflicts possible
- No dev/prod separation

### After (Poetry)

**pyproject.toml:**
- Declarative configuration
- Built-in dependency resolution
- Dev dependencies grouped
- Standard format (PEP 621)

**poetry.lock:**
- Deterministic builds
- Exact versions locked
- Platform-specific

---

**Document Version:** 1.0  
**Last Updated:** January 4, 2026  
**Author:** DevOps Team  
**Status:** Planning - Awaiting Decisions

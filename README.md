# DevOps Toolset
[![GitHub last commit](https://img.shields.io/github/last-commit/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset/commits/)
[![GitHub tag](https://img.shields.io/github/v/tag/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset/tags)

[![GitHub license](https://img.shields.io/github/license/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset/blob/main/LICENSE)
[![GitHub repo size](https://img.shields.io/github/repo-size/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset)
[![GitHub top language](https://img.shields.io/github/languages/top/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset)

[![GitHub Actions CI](https://img.shields.io/github/actions/workflow/status/ahead-labs-open-source/devops-toolset/ci.yml?branch=main)](https://github.com/ahead-labs-open-source/devops-toolset/actions/workflows/ci.yml?query=branch%3Amain)
[![GitHub Actions CD](https://img.shields.io/github/actions/workflow/status/ahead-labs-open-source/devops-toolset/cd.yml?branch=main)](https://github.com/ahead-labs-open-source/devops-toolset/actions/workflows/cd.yml?query=branch%3Amain)
[![Sonar quality gate (branch)](https://img.shields.io/sonar/quality_gate/ahead-labs-open-source_devops-toolset/main?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/dashboard?id=ahead-labs-open-source_devops-toolset&branch=main)
[![Sonar tech debt (branch)](https://img.shields.io/sonar/tech_debt/ahead-labs-open-source_devops-toolset/main?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/dashboard?id=ahead-labs-open-source_devops-toolset&branch=main)
[![Sonar violations (branch)](https://img.shields.io/sonar/violations/ahead-labs-open-source_devops-toolset/main?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/dashboard?id=ahead-labs-open-source_devops-toolset&branch=main)
[![Sonar coverage (branch)](https://img.shields.io/sonar/coverage/ahead-labs-open-source_devops-toolset/main?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/dashboard?id=ahead-labs-open-source_devops-toolset&branch=main)

Everything than can be automated, must be automated!<br><br>
![Logo](.media/devops-toolset-logo-216x100px.png)

# Getting Started

## Description

This project contains general purpose, DevOps-related, scripts and tools.

## Prerequisites

- You need Python 3.8.2+ installed on your machine. Please follow the instructions on the [Python web site](https://www.python.org/downloads/).
- You also need to have [pip package manager](https://pypi.org/project/pip/) installed.

## How to use

1. Install from the [PyPI package index](https://pypi.org/project/devops-toolset/) using the following command:
   ```pip install devops-toolset```
2. Reference the package in your pipeline to have these tools available.

## Running the tests

### Unit tests

To run the unit tests you need to install [pytest from PyPI](https://pypi.org/project/pytest/). You can do so by executing the following command:

```
pip install pytest
```

Then, run the tests using the following command at the project's root path:
```
pytest
```

# File structure
| Directory / file | Description |
| -- | -- |
| /.devops | Contains pipeline definitions for the project |
| /core | Core settings for devops-toolset |
| /.devops-platforms | Contains platform-specific code |
| /filesystem | File system related tools |
| /i18n | Internationalization related tools |
| /json-schemas | Json schemas that support needed JSON document structures |
| /project types | Contains scripts and tools related to specific project types like Angular, AWS, .NET, Linux, Maven, NodeJS, PHP os WordPress |
| /tools | Contains helpers and tools used in scripts |
| /toolset | Script that downloads "manually" this toolset to a directory (deprecated) |
| /project.xml | Project description and project version |

# WordPress tools
This repository relies on WP CLI for WordPress automation. Please refer to [WP-CLI handbook](https://make.wordpress.org/cli/handbook/) for more information and installation instructions.

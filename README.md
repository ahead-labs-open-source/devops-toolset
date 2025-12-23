# DevOps Toolset
[![Last commit](https://img.shields.io/github/last-commit/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset/commits/)
[![Build status](https://img.shields.io/azure-devops/build/aheadlabs/DevOps-toolset/6)](https://dev.azure.com/aheadlabs/DevOps-toolset/_build?definitionId=6&_a=summary)
[![Release](https://img.shields.io/azure-devops/release/aheadlabs/1485b494-712b-4941-9b9a-d177484d1727/1/1)](https://dev.azure.com/aheadlabs/DevOps-toolset/_release?_a=releases&view=mine&definitionId=1)  
[![Sonar quality gate](https://img.shields.io/sonar/quality_gate/devops-toolset?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/dashboard?id=devops-toolset)
[![Sonar coverage](https://img.shields.io/sonar/coverage/devops-toolset?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/component_measures?id=devops-toolset&metric=coverage&view=list)
[![Sonar tech debt](https://img.shields.io/sonar/tech_debt/devops-toolset?server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/component_measures?id=devops-toolset&metric=sqale_index&view=list)
[![Sonar violations](https://img.shields.io/sonar/violations/devops-toolset?format=long&server=https%3A%2F%2Fsonarcloud.io)](https://sonarcloud.io/dashboard?id=devops-toolset)<!--[![Sonar documented API density](https://img.shields.io/sonar/public_documented_api_density/devops-toolset?server=https%3A%2F%2Fsonarcloud.io)]()-->  
[![GitHub SemVer tag](https://img.shields.io/github/v/tag/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset/tags)
[![Repo size](https://img.shields.io/github/repo-size/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset)
[![Top language](https://img.shields.io/github/languages/top/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset)
[![License](https://img.shields.io/github/license/ahead-labs-open-source/devops-toolset)](https://github.com/ahead-labs-open-source/devops-toolset/blob/main/LICENSE)  
[![Liberapay](https://img.shields.io/liberapay/receives/ahead-labs?logo=liberapay)](https://es.liberapay.com/ahead-labs/)
[![Donate Liberapay](https://img.shields.io/badge/donate-Liberapay-yellow)](https://liberapay.com/ahead-labs/donate)
[![Donate PayPal](https://img.shields.io/badge/donate-PayPal-yellow.svg)](https://www.paypal.me/aheadlabs)  

Everything than can be automated, must be automated!<br><br>
![Logo](.media/devops-toolset-logo-216x100px.png)

# Getting Started

## Description

This project contains general purpose, DevOps-related, scripts and tools.

## Prerequisites

- You need Python 3.8.2+ installed on your machine. Please follow the instructions on the [Python web site](https://www.python.org/downloads/).
- You also need to have pip package manager installed.

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

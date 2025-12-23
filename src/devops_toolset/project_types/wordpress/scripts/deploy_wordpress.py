"""Deploys a WordPress site based on its build artifacts"""

import argparse

import devops_toolset.tools.cli as cli
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.core.app import App
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals

app: App = App()
literals = LiteralsCore([WordpressLiterals])


def main():
    """Deploys a WordPress site based on its build artifacts"""

    # TODO(anyone) Activate maintenance page
    # TODO(anyone) Deploy files artifact
    # TODO(anyone) Deploy SQL artifact
    # TODO(anyone) Deactivate maintenance page

    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args, args_unknown = parser.parse_known_args()
    kwargs = {}
    for kwarg in args_unknown:
        splited = str(kwarg).split("=")
        kwargs[splited[0]] = splited[1]

    cli.print_title(literals.get("wp_title_deploy_wordpress"))
    main()

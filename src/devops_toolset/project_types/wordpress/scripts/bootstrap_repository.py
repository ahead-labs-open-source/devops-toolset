"""Generates a WordPress Git repository for local development.

Git repositories should not contain downloadable or third-party files, but you need them for your site to work.
These are the type of files that won't be pushed to the repository and we will download/generate here:
  - WordPress core files
  - This toolset's
  - WordPress themes (parent themes)

Args:
    --project-path: Path to the WordPress installation.
    --environment-path: Path to the environment JSON file.
    --environment-name: Environment name.
    --db-user-password: Password for the database user.
    --db-admin-password: Password for the WordPress admin user.
"""

import argparse
import os
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.core.app import App
from devops_toolset.project_types.wordpress.scripts import generate_wordpress
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from devops_toolset.tools import git

app: App = App()
literals = LiteralsCore([WordpressLiterals])


def main(project_path: str, db_user_password: str, db_admin_password: str, wp_admin_password: str,
         environment: str, additional_environments: list, additional_environment_db_user_passwords: list,
         create_db: bool, skip_partial_dumps: bool, skip_git: bool, **kwnargs):
    """Generates a WordPress Git repository for local development."""

    # Change the working directory
    os.chdir(project_path)

    # Initialize a local Git repository?
    git.git_init(project_path, skip_git)

    # Generate wordpress with the required data
    generate_wordpress.main(project_path, db_user_password, db_admin_password, wp_admin_password, environment,
                            additional_environments, additional_environment_db_user_passwords, create_db,
                            skip_partial_dumps, **kwnargs)

    # Move initial required files to .devops
    # TODO(ivan.sainz) Move initial required files to .devops

    # Commit git repository
    git.git_commit(skip_git)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project-path", action=tools.argument_validators.PathValidator)
    parser.add_argument("--additional-environments", default="")
    parser.add_argument("--additional-environment-db-user-passwords", default="")
    parser.add_argument("--create-db", action="store_true", default=False)
    parser.add_argument("--db-user-password", required=True)
    parser.add_argument("--db-admin-password", required=True)
    parser.add_argument("--environment", default="localhost")
    parser.add_argument("--skip-git", action="store_true", default=False)
    parser.add_argument("--skip-partial-dumps", action="store_true", default=False)
    parser.add_argument("--wp-admin-password", required=True)
    kwargs = {}
    args, args_unknown = parser.parse_known_args()
    for kwarg in args_unknown:
        splitted = str(kwarg).split("=")
        kwargs[splitted[0]] = splitted[1]
    tools.cli.print_title(literals.get("wp_title_generate_wordpress"))
    main(args.project_path, args.db_user_password, args.db_admin_password, args.wp_admin_password,
         args.environment,
         args.additional_environments.split(","),
         args.additional_environment_db_user_passwords.split(","),
         args.create_db, args.skip_partial_dumps, args.skip_git, **kwargs)

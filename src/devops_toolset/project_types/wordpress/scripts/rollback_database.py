"""Rollbacks a database using a dump, removing first all existing tables."""

import argparse
from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.tools.commands import Commands as ToolsCommands
from devops_toolset.tools.Literals import Literals as ToolsLiterals
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from devops_toolset.project_types.wordpress import wp_cli

app: App = App()
literals = LiteralsCore([WordpressLiterals, ToolsLiterals])
commands = CommandsCore([ToolsCommands])


def main(wordpress_path: str, database_dump_path: str, quiet: bool):
    """Rollbacks a database using a dump, dropping and re-creating the database

    Args:
        wordpress_path: Path to WordPress directory.
        database_dump_path: Path to the database dump file to be restored.
        quiet: If True, no questions are asked and defaults are assumed.
    """

    # Drop the database and create an empty one
    wp_cli.reset_database(wordpress_path, quiet)

    # Imports a dump in the newly created database
    wp_cli.import_database(wordpress_path, database_dump_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wordpress-path", action=tools.argument_validators.PathValidator)
    parser.add_argument("database-dump-path", action=tools.argument_validators.PathValidator)
    parser.add_argument("--quiet", action="store_true", default=False)
    args, args_unknown = parser.parse_known_args()

    tools.cli.print_title(literals.get("wp_title_wordpress_rollback_db"))
    main(args.wordpress_path, args.database_dump_path, args.quiet)

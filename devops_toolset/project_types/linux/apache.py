"""Contains Apache utilities"""

import pathlib
from devops_toolset.core.app import App
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.linux.Literals import Literals as LinuxLiterals
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.project_types.linux.commands import Commands as LinuxCommands

app: App = App()
literals = LiteralsCore([LinuxLiterals])
commands = CommandsCore([LinuxCommands])


def generate_htaccess_file_based_basic_auth_file_for_user(realm_name: str, passwords_file_path: str, user_name: str,
                                                         htaccess_path: str):
    """Generates an .htacess file that claims for file-based basic
    authentication for a specific user.

    More info at: https://httpd.apache.org/docs/2.4/howto/auth.html

    Args:
        realm_name: Name for the authentication realm.
        passwords_file_path: Path to the password's file.
        user_name: user that will have access after authenticating.
        htaccess_path: Path to the directory where the .htaccess file will be
            generated.
    """

    htaccess_file_path: str = pathlib.Path.joinpath(pathlib.Path(htaccess_path), ".htaccess")
    lines: list = [
        "AuthType Basic\n",
        f"AuthName {realm_name}\n",
        "AuthBasicProvider file\n",
        f"AuthUserFile {passwords_file_path}\n",
        f"Require user {user_name}\n"
    ]

    with open(htaccess_file_path, "w") as file:
        file.writelines(lines)


if __name__ == "__main__":
    help(__name__)

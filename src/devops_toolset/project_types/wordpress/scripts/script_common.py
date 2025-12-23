""" Here we must place the common methods that are used in more than one script """

from clint.textui import prompt
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.core.app import App
import devops_toolset.core.log_tools as log_tools
import requests
import devops_toolset.filesystem.paths as paths
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
import logging
import pathlib

app: App = App()
literals = LiteralsCore([WordpressLiterals])


def check_required_files(required_files_pattern_suffixes: list, root_path: str, required_files_urls: dict[str, str]):
    """ Checks required files present in the root path. Also prompts the user in case of files not present, for default
    files downloading

    Args:
        required_files_pattern_suffixes: A list of file suffixes to match.
        root_path: Path where the files will be looked for.
        required_files_urls: A list of urls to match the default files to download.
    """
    required_files_not_present: list[str] = paths.files_exist_filtered(
        root_path, False, required_files_pattern_suffixes)

    if len(required_files_not_present) <= 0:
        return

    log_tools.log_indented_list(literals.get("wp_required_files_not_found_detail")
                                .format(path=root_path),
                                required_files_not_present,
                                log_tools.LogLevel.warning)

    # Ask to use defaults
    use_defaults: bool = prompt.yn(literals.get("wp_use_default_files"))

    # If not using defaults, exit
    if not use_defaults:
        logging.critical(literals.get("wp_required_files_mandatory"))
        raise ValueError(literals.get("wp_required_files_not_found").format(path=root_path))

    # Download defaults from GitHub
    for file in required_files_not_present:
        url = required_files_urls[file]
        file_name = paths.get_file_name_from_url(url)
        file_path = pathlib.Path.joinpath(pathlib.Path(root_path), file_name)

        logging.info(literals.get("wp_downloading_default_file").format(file=file, url=url))
        response: requests.Response = requests.get(url)
        with open(file_path, "wb") as fw:
            fw.write(response.content)

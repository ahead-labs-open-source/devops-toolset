"""Helper functions for Git-related task automation."""

# ! python

import devops_toolset.core.app
import devops_toolset.filesystem.paths
import devops_toolset.filesystem.paths as path_tools
import devops_toolset.tools.cli
import devops_toolset.tools.git_flow as gitflow
import logging
import os
import pathlib
import re
from clint.textui import prompt

from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.filesystem.constants import FileNames, Directions
from devops_toolset.tools.commands import Commands as ToolsCommands
from devops_toolset.tools.Literals import Literals as ToolsLiterals

app: devops_toolset.core.app.App = devops_toolset.core.app.App()
literals = LiteralsCore([ToolsLiterals])
commands = CommandsCore([ToolsCommands])
platform_specific = app.load_platform_specific("environment")


def add_gitignore_exclusion(path: str, exclusion: str):
    """Adds an exclusion in a .gitignore file.

    It adds the exclusion at the end of the file.

    Args:
        path: Path to the .gitignore file.
        exclusion: Exclusion to be added (whole line must be passed).
    """

    with open(path, "a") as _gitignore:
        _gitignore.write(f"{exclusion}\n")


def find_gitignore_exclusion(path: str, exclusion: str) -> bool:
    """Finds if an exclusion exists in a .gitignore file.

    It tries to find the exclusion.

    Args:
        path: Path to the .gitignore file.
        exclusion: Exclusion to find (whole line must be passed not including
            newline).

    Returns:
        True if the exclusion is found, False otherwise.
    """

    with open(path, "r") as _gitignore:
        index = _gitignore.read().find(f"{exclusion}\n")

    return index > -1


def get_current_branch_simplified(branch: str, environment_variable_name: str = "DT_CURRENT_BRANCH_SIMPLIFIED") -> str:
    """Creates an environment variable from a branch name (simplified)

    Args:
        branch: Git branch name to be simplified and stored in an environment
            variable
        environment_variable_name: Name of the environment variable to be
            created. Defaults to "DT_CURRENT_BRANCH_SIMPLIFIED".

    Returns:
        Branch name simplified.
    """

    simplified_branch_name = simplify_branch_name(branch)
    platform_specific.create_environment_variables({environment_variable_name: simplified_branch_name})

    return simplified_branch_name


def get_gitignore_path(path: str = None, direction: Directions = Directions.ASCENDING) -> str:
    """Gets the path to the .gitignore file.

    If no path parameter is passed to the function it returns the path to the
    .gitignore file in the project root.
    If a path is passed it returns the path to the .gitignore file that is
    closer to the given path in the specified direction.

    Args:
        path: Optional path to start looking for a .gitignore file.
        direction: The direction of the seek (ascending by default).

    Returns:
        The path to the closest/root .gitignore file
    """
    if path is None:
        gitignore_path = pathlib.Path.joinpath(
            pathlib.Path(devops_toolset.filesystem.paths.get_project_root()), FileNames.GITIGNORE_FILE)
        if not pathlib.Path(gitignore_path).exists():
            raise FileNotFoundError
        return gitignore_path

    return str(devops_toolset.filesystem.paths.get_filepath_in_tree(FileNames.GITIGNORE_FILE, direction))


def git_commit(skip: bool):
    """Add modified files to .git repository and commit

    Args:
        skip: Boolean that determines if the user want or don't want to create the .git repository.
    """
    if not skip:
        devops_toolset.tools.cli.call_subprocess(commands.get("git_add"),
                                                 log_before_process=[literals.get(
                                                     "git_before_adding_project_structure_files_to_stage")],
                                                 log_after_err=[
                                                     literals.get("git_err_adding_project_structure_files_to_stage")])
        devops_toolset.tools.cli.call_subprocess(commands.get("git_commit_m").format(
            message=literals.get("git_add_project_structure_message")),
            log_before_process=[literals.get("git_before_project_structure_commit")],
            log_after_err=[literals.get("git_err_commit_project_structure")],
            log_after_out=[literals.get("git_after_project_structure_commit")])


def git_init(path: str, skip: bool, prompt_user: bool = False):
    """Initialize .git repository

    Args:
        path: Path where it creates the .git repository.
        skip: Boolean that determines if the user want or don't want to create the .git repository.
        prompt_user: Boolean that determines if the user wants or not to create the
            .git repository.
    """

    if not skip:
        init_git = prompt.yn(literals.get("git_init_repo")) if prompt_user is True else True
        if init_git:
            devops_toolset.tools.cli.call_subprocess(commands.get("git_init").format(path=path),
                                                     log_before_process=[literals.get("git_repo_to_be_created")],
                                                     log_after_err=[literals.get("git_err_create_repo")],
                                                     log_after_out=[literals.get("git_repo_created")])


def git_tag(commit_name: str, tag_name: str, branch: str, auth_header: str, overwrite_tag: bool = True):
    """ Does a git tag over a checkout branch's commit
        Args:
            commit_name: Name of the commit.
            Git will need the checksum name, or part of it.
            F.I: If the commit name is 9fceb02d0ae598e95dc970b74767f19372d61af8, the checksum will be 9fceb02.
            tag_name: Name of the tag to be added.
            branch: The simplified name of the git branch.
            auth_header: Includes an auth header into the git command (needed for elevated privilege operations).
            Normally, it will be ["basic <BASIC_AUTH_TOKEN>"] or "bearer <BEARER_TOKEN>"]
            overwrite_tag: Tag will be moved to the <commit_name> if exists. False will maintain the current tag.
            Default behaviour is True -> move tag if exist on remote
    """
    if gitflow.is_branch_suitable_for_tagging(branch):
        if git_tag_exist(tag_name, auth_header):
            logging.warning(literals.get("git_tag_exists").format(tag_name=tag_name))
            # Tag exists. Depending on the overwrite_tag behaviour we'll move the tag or not
            if overwrite_tag:
                logging.warning(literals.get("git_existing_tag_move").format(tag_name=tag_name,
                                                                             commit_name=commit_name))
                # Delete current tag on origin
                git_tag_delete(tag_name, True, auth_header)
            else:
                # No action taken. Skip tag and return
                logging.warning(literals.get("git_existing_tag_keep").format(tag_name=tag_name))
                return
        logging.info(literals.get("git_tag")
                     .format(tag_name=tag_name, commit_name=commit_name, branch_name=branch))
        git_tag_add(tag_name, commit_name, auth_header=auth_header)


def git_tag_add(tag_name: str, commit_name: str, push_to_origin: bool = True, auth_header: str = ''):
    """ Adds a tag to a git commit

     Args:
        tag_name: Name of the tag to be added
        commit_name: Name of the commit.
            Git will need the checksum name, or part of it.
            F.I: If the commit name is 9fceb02d0ae598e95dc970b74767f19372d61af8, the checksum will be 9fceb02
        push_to_origin: If True, will push the tag to origin
        auth_header: Includes an auth header into the git command (needed for elevated privilege operations).
        Normally, it will be ["basic <BASIC_AUTH_TOKEN>"] or ["bearer <BEARER_TOKEN>"]


    """
    devops_toolset.tools.cli.call_subprocess(
        commands.get("git_tag_add").format(tag_name=tag_name, commit_name=commit_name),
        log_before_process=[literals.get("git_tag_add_init").format(tag_name=tag_name, commit_name=commit_name)],
        log_after_err=[literals.get("git_tag_add_err")])

    if push_to_origin:
        devops_toolset.tools.cli.call_subprocess(commands.get("git_push_tag").format(
            tag_name=tag_name,
            auth=commands.get("git_auth").format(auth_header=auth_header)
        ),
            log_before_process=[literals.get("git_push_tag_init").format(tag_name=tag_name)],
            log_after_err=[literals.get("git_push_tag_err")])


def git_tag_delete(tag_name: str, push_to_origin: bool = True, auth_header: str = ''):
    """ Deletes a tag from git
    Args:
        tag_name: Name of the tag to be deleted
        push_to_origin: If True, will push the tag deletion to origin
        auth_header: Includes an auth header into the git command (needed for elevated privilege operations).
        Normally, it will be ["basic <BASIC_AUTH_TOKEN>"] or "bearer <BEARER_TOKEN>"]
    """
    devops_toolset.tools.cli.call_subprocess(commands.get("git_tag_delete").format(
        tag_name=tag_name
    ),
        log_before_process=[literals.get("git_tag_delete_init").format(tag_name=tag_name)],
        log_after_err=[literals.get("git_tag_delete_err").format(tag_name=tag_name)])
    if push_to_origin:
        devops_toolset.tools.cli.call_subprocess(commands.get("git_push_tag_delete").format(
            tag_name=tag_name,
            auth=commands.get("git_auth").format(auth_header=auth_header)
        ),
            log_before_process=[literals.get("git_push_tag_delete_init").format(tag_name=tag_name)],
            log_after_err=[literals.get("git_push_tag_delete_err")])


def git_tag_exist(tag_name: str, auth_header: str = '', remote_name: str = 'origin') -> bool:
    """ Returns True if the tag name already exists on checkout branch's origin. False otherwise
        Args:
            :param tag_name: Name of the tag to be checked
            :param auth_header: Includes an auth header into the git command (needed for elevated privilege operations).
        Normally, it will be ["basic <BASIC_AUTH_TOKEN>"] or "bearer <BEARER_TOKEN>"]
            :param remote_name: Name of the remote. <origin> by default.
        """
    result: str = devops_toolset.tools.cli.call_subprocess_with_result(commands.get("git_tag_check").format(
        remote_name=remote_name,
        auth=commands.get("git_auth").format(auth_header=auth_header),
        tag_name=tag_name
    ))

    return result is not None


def purge_gitkeep(path: str = None):
    """Deletes .gitkeep file if exists and there are more files in the path."""

    if not devops_toolset.filesystem.paths.is_valid_path(path, True):
        raise ValueError(literals.get("git_non_valid_dir_path"))

    path_object = pathlib.Path(path)
    guess_gitkeep_file = pathlib.Path(pathlib.Path.joinpath(path_object, ".gitkeep"))
    if not path_tools.is_empty_dir(path) and guess_gitkeep_file.exists():
        logging.info(literals.get("git_purging_gitkeep").format(path=path))
        os.remove(guess_gitkeep_file)


def simplify_branch_name(branch: str):
    """Simplifies a branch name.

    e.g:
        refs/heads/master => master
        refs/heads/feature/name => feature/name
        refs/pull/1/merge => pull/1

    If none of these cases the original branch name is returned.

    Args:
        branch: Long name of the branch to be simplified
    """

    if branch.startswith("refs/heads/"):
        return branch.replace("refs/heads/", "")

    if branch.startswith("refs/pull/"):
        return branch.replace("refs/", "").replace("/merge", "")

    return branch


def update_gitignore_exclusion(path: str, regex: str, value: str):
    """Updates an existing exclusion in a .gitignore file.

    It updates the exclusion in the .gitignore file replacing the passed value using the RegEx.

    Args:
        path: Path to the .gitignore file.
        regex: RegEx with only 1 capturing group, whose content will be replaced.
        value: String that will replace the RegEx capture group.
    Raises:
        ValueError: When regex has no capture groups or more than one
    """

    compiled_regex = re.compile(regex)

    if compiled_regex.groups != 1:
        raise ValueError(literals.get("git_regex1cg"))

    with open(path, "r+") as _gitignore:
        content = _gitignore.read()

    from_index = 0
    iterations = len(compiled_regex.findall(content))
    while iterations > 0:
        match = compiled_regex.search(content, from_index)
        content = content[:match.regs[1][0]] + value + content[match.regs[1][1]:]
        from_index = match.regs[1][1]
        iterations -= 1

    with open(path, "w") as _gitignore:
        _gitignore.write(content)


if __name__ == "__main__":
    help(__name__)

"""Unit tests for the tools/git module"""

import io
import pathlib
import pytest
import devops_toolset.tools.git as sut
import devops_toolset.filesystem.paths as path_tools
from unittest.mock import patch, mock_open, call, ANY
from devops_toolset.filesystem.constants import Directions, FileNames
from tests.tools.conftest import GitignoreData
from tests.tools.conftest import BranchesData
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.tools.commands import Commands as ToolsCommands
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.tools.Literals import Literals as ToolsLiterals

commands = CommandsCore([ToolsCommands])
literals = LiteralsCore([ToolsLiterals])


# region add_gitignore_exclusion()


def test_add_gitignore_exclusion_given_path_when_file_opens_then_appends_exclusion(filenames, tmp_path):
    """Given a path, when the file opens, the exclusion is appended"""

    # Arrange
    test_gitignore_path = pathlib.Path.joinpath(tmp_path, FileNames.GITIGNORE_FILE)
    with open(test_gitignore_path, "w") as test_gitignore:
        test_gitignore.write(".pytest/")
    exclusion = "exclusion/"
    expected_gitignore = io.StringIO(f".pytest/{exclusion}\n")

    # Act
    sut.add_gitignore_exclusion(test_gitignore_path, exclusion)

    # Assert
    with open(test_gitignore_path, "r") as test_gitignore:
        content = test_gitignore.read()
        assert content == expected_gitignore.read()


# endregion

# region find_gitignore_exclusion()


def test_find_gitignore_exclusion_given_path_when_exclusion_exists_then_returns_true(filenames, tmp_path):
    """Given a path, when the exclusion is found on it, then returns True"""

    # Arrange
    test_gitignore_path = pathlib.Path.joinpath(tmp_path, FileNames.GITIGNORE_FILE)
    with open(test_gitignore_path, "w") as test_gitignore:
        test_gitignore.write(".idea\n.vscode\n.vs\n.pytest/")
    exclusion = ".vs"

    # Act
    result = sut.find_gitignore_exclusion(test_gitignore_path, exclusion)

    # Assert
    assert result == True


def test_find_gitignore_exclusion_given_path_when_exclusion_exists_then_returns_false(filenames, tmp_path):
    """Given a path, when the exclusion is not found, then returns False"""

    # Arrange
    test_gitignore_path = pathlib.Path.joinpath(tmp_path, FileNames.GITIGNORE_FILE)
    with open(test_gitignore_path, "w") as test_gitignore:
        test_gitignore.write(".idea\n.vscode\n.vs\n.pytest/")
    exclusion = "notpresent"

    # Act
    result = sut.find_gitignore_exclusion(test_gitignore_path, exclusion)

    # Assert
    assert result == False


# endregion

# region get_gitignore_path()


@patch("devops_toolset.filesystem.paths.get_project_root")
def test_get_gitignore_path_given_none_when_exists_then_returns_root_gitignore_path(target, filenames):
    """Given no file, when it exists, should return path to root .gitignore"""

    # Arrange
    target.return_value = pathlib.Path(f"{filenames.path}")
    with patch.object(pathlib.Path, "exists") as exits:
        exits.return_value = True

        # Act
        result = sut.get_gitignore_path()

    # Assert
    assert result == pathlib.Path(f"{filenames.path}/{FileNames.GITIGNORE_FILE}")


@patch("devops_toolset.filesystem.paths.get_project_root")
def test_get_gitignore_path_given_none_when_not_exist_then_raises_filenotfounderror(target, filenames):
    """Given no file, when it doesn't exist, should raise FileNotFoundError"""

    # Arrange
    target.return_value = pathlib.Path(f"{filenames.path}")
    with patch.object(pathlib.Path, "exists") as exits:
        exits.return_value = False

        # Act
        with pytest.raises(FileNotFoundError):
            # Assert
            sut.get_gitignore_path()


@patch("devops_toolset.filesystem.paths.get_filepath_in_tree")
def test_get_gitignore_path_given_file_then_calls_get_filepath_in_tree(target, filenames):
    """Given a file, should call get_filepath_in_tree(FileNames.GITIGNORE_FILE, direction)"""

    # Arrange

    # Act
    sut.get_gitignore_path(filenames.file, Directions.ASCENDING)

    # Assert
    target.assert_called_with(filenames.file, Directions.ASCENDING)


# endregion

# region git_commit()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_git_commit_when_skip_do_nothing(call_subprocess):
    """Given arguments, when skip is true, then do nothing"""

    # Arrange
    skip = True

    # Act
    sut.git_commit(skip)

    # Assert
    call_subprocess.assert_not_called()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_git_commit_when_not_skip_then_call_subprocess(call_subprocess):
    """Given arguments, when skip is false, then call subprocess"""

    # Arrange
    skip = False
    expected_command_1 = commands.get("git_add")
    expected_command_2 = commands.get("git_commit_m").format(message=literals.get("git_add_project_structure_message"))

    # Act
    sut.git_commit(skip)

    # Assert
    calls = [call(expected_command_1, log_before_process=ANY, log_after_err=ANY),
             call(expected_command_2, log_before_process=ANY, log_after_err=ANY, log_after_out=ANY)]
    call_subprocess.assert_has_calls(calls, any_order=False)


# endregion

# region git_init()


@patch("clint.textui.prompt.yn")
def test_git_init_when_skip_do_nothing(prompt_yn):
    """Given arguments, when skip is true, then do nothing"""

    # Arrange
    skip = True
    path = ""

    # Act
    sut.git_init(path, skip)

    # Assert
    prompt_yn.assert_not_called()


@patch("devops_toolset.tools.cli.call_subprocess")
@patch("clint.textui.prompt.yn")
@pytest.mark.parametrize("prompt_user, prompt_return_value, times_called", [
    (True, True, 1),
    (True, False, 0),
    (False, True, 1)
])
def test_git_init_when_not_skip_and_not_init_git_then_call_subprocess(
        prompt_mock, call_subprocess, prompt_user, prompt_return_value, times_called):
    """Given arguments, when skip is false and init_git is false, then don't
    call_subprocess"""

    # Arrange
    skip = False
    path = ""
    prompt_mock.return_value = prompt_return_value

    # Act
    sut.git_init(path, skip, prompt_user)

    # Assert
    assert call_subprocess.call_count == times_called


# endregion

# region git_tag()


@patch("logging.info")
@patch("devops_toolset.tools.git_flow.is_branch_suitable_for_tagging")
@patch("devops_toolset.tools.git.git_tag_add")
@patch("devops_toolset.tools.git.git_tag_exist")
def test_git_tag_calls_git_tools_tag_add(
        git_tag_exist_mock, git_tag_add_mock, git_flow_suitable_branch_mock, _, gitdata):
    """ Given a commit name, tag name and branch name, calls git.git_tag_add() """
    # Arrange
    branch = gitdata.branch
    commit = gitdata.commit
    tag = gitdata.tag
    auth_header = gitdata.auth_header
    git_flow_suitable_branch_mock.return_value = True
    git_tag_exist_mock.return_value = False

    # Act
    sut.git_tag(commit, tag, branch, auth_header)

    # Assert
    git_tag_add_mock.assert_called_with(tag, commit, auth_header=auth_header)


@patch("logging.info")
@patch("devops_toolset.tools.git_flow.is_branch_suitable_for_tagging")
@patch("devops_toolset.tools.git.git_tag_add")
@patch("devops_toolset.tools.git.git_tag_exist")
def test_git_tag_not_calls_git_tools_tag_add(
        git_tag_exist_mock, git_tag_add_mock, git_flow_suitable_branch_mock, _, gitdata):
    """ Given a commit name, tag name and branch name, calls git.git_tag_add() """
    # Arrange
    branch = gitdata.branch
    commit = gitdata.commit
    tag = gitdata.tag
    auth_header = gitdata.auth_header
    git_flow_suitable_branch_mock.return_value = False
    git_tag_exist_mock.return_value = False

    # Act
    sut.git_tag(commit, tag, branch, auth_header)

    # Assert
    git_tag_add_mock.assert_not_called()


@patch("logging.info")
@patch("logging.warning")
@patch("devops_toolset.tools.git_flow.is_branch_suitable_for_tagging")
@patch("devops_toolset.tools.git.git_tag_add")
@patch("devops_toolset.tools.git.git_tag_exist")
@patch("devops_toolset.tools.git.git_tag_delete")
def test_git_tag_calls_git_tools_tag_delete_when_tag_exists_and_overwrite_tag \
                (git_tag_delete_mock, git_tag_exist_mock, git_tag_add_mock, git_flow_suitable_branch_mock,
                 logging_warning_mock, _, gitdata):
    """ Given a commit name, tag name, branch name and overwrite_tag, calls git.git_tag_delete() """
    # Arrange
    branch = gitdata.branch
    commit = gitdata.commit
    tag = gitdata.tag
    auth_header = gitdata.auth_header
    git_flow_suitable_branch_mock.return_value = True
    git_tag_exist_mock.return_value = True

    # Act
    sut.git_tag(commit, tag, branch, auth_header)

    # Assert
    git_tag_delete_mock.assert_called_with(tag, True, auth_header)


@patch("logging.info")
@patch("logging.warning")
@patch("devops_toolset.tools.git_flow.is_branch_suitable_for_tagging")
@patch("devops_toolset.tools.git.git_tag_add")
@patch("devops_toolset.tools.git.git_tag_exist")
@patch("devops_toolset.tools.git.git_tag_delete")
def test_git_tag_warns_when_tag_exists_and_not_overwrite_tag\
                (git_tag_delete_mock, git_tag_exist_mock, git_tag_add_mock, git_flow_suitable_branch_mock,
                 logging_warning_mock, _, gitdata):
    """ Given a commit name, tag name, branch name and not overwrite_tag, then not tag anything """
    # Arrange
    branch = gitdata.branch
    commit = gitdata.commit
    tag = gitdata.tag
    auth_header = gitdata.auth_header
    git_flow_suitable_branch_mock.return_value = True
    git_tag_exist_mock.return_value = True

    # Act
    sut.git_tag(commit, tag, branch, auth_header, False)

    # Assert
    git_tag_add_mock.assert_not_called()

# endregion git_tag()

# region git_tag_add()

@patch("devops_toolset.tools.cli.call_subprocess")
def test_git_tag_add_calls_git_tag_add_command(call_subprocess):
    """ Calls git_tag_add command with necessary parameters """
    # Arrange
    tag_name = 'test'
    commit_name = 'bnd6f45'
    expected_command = commands.get("git_tag_add").format(tag_name=tag_name, commit_name=commit_name)

    # Act
    sut.git_tag_add(tag_name, commit_name, False)

    # Assert
    call_subprocess.assert_called_with(expected_command, log_before_process=ANY, log_after_err=ANY)


@patch("devops_toolset.tools.cli.call_subprocess")
def test_git_tag_add_calls_git_push_tag_command(call_subprocess, clidata):
    """ Calls git_tag_add command and git_push_tag command with necessary parameters """
    # Arrange
    tag_name = 'test'
    commit_name = 'bnd6f45'
    auth_header = clidata.auth_header
    auth_part = commands.get("git_auth").format(auth_header=auth_header)
    expected_command_1 = commands.get("git_tag_add").format(tag_name=tag_name, commit_name=commit_name)
    expected_command_2 = commands.get("git_push_tag").format(tag_name=tag_name, auth=auth_part)

    # Act
    sut.git_tag_add(tag_name, commit_name, True, auth_header)

    # Assert
    calls = [call(expected_command_1, log_before_process=ANY, log_after_err=ANY),
             call(expected_command_2, log_before_process=ANY, log_after_err=ANY)]
    call_subprocess.assert_has_calls(calls, any_order=False)


# endregion git_tag_add()

# region git_tag_delete()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_git_tag_delete_calls_git_tag_add_command(call_subprocess):
    """ Calls git_tag_delete command with necessary parameters """
    # Arrange
    tag_name = 'test'
    commit_name = 'bnd6f45'
    expected_command = commands.get("git_tag_delete").format(tag_name=tag_name, commit_name=commit_name)

    # Act
    sut.git_tag_delete(tag_name, False)

    # Assert
    call_subprocess.assert_called_with(expected_command, log_before_process=ANY, log_after_err=ANY)


@patch("devops_toolset.tools.cli.call_subprocess")
def test_git_tag_delete_calls_git_push_tag_command(call_subprocess, clidata):
    """ Calls git_tag_delete and git_push_tag_delete commands with necessary parameters """
    # Arrange
    tag_name = 'test'
    auth_header = clidata.auth_header
    auth_part = commands.get("git_auth").format(auth_header=auth_header)
    expected_command_1 = commands.get("git_tag_delete").format(tag_name=tag_name)
    expected_command_2 = commands.get("git_push_tag_delete").format(tag_name=tag_name, auth=auth_part)

    # Act
    sut.git_tag_delete(tag_name, True, auth_header)

    # Assert
    calls = [call(expected_command_1, log_before_process=ANY, log_after_err=ANY),
             call(expected_command_2, log_before_process=ANY, log_after_err=ANY)]
    call_subprocess.assert_has_calls(calls, any_order=False)


# endregion git_tag_delete()

# region git_tag_exist()


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
def test_git_tag_exist_calls_git_tag_check_command(call_subprocess, clidata):
    """ Calls git_tag_check command with necessary parameters """
    # Arrange
    tag_name = 'test'
    auth_header = commands.get("git_auth").format(auth_header=clidata.auth_header)
    remote_name = 'origin'
    expected_command = commands.get("git_tag_check").format(
        remote_name=remote_name, auth=auth_header, tag_name=tag_name)

    # Act
    sut.git_tag_exist(tag_name, clidata.auth_header)

    # Assert
    call_subprocess.assert_called_with(expected_command)


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
def test_git_tag_exist_returns_true_when_result_is_not_none(call_subprocess, clidata):
    """ Calls git_tag_check command with necessary parameters """
    # Arrange
    tag_name = '0.0.1'
    auth_header = clidata.auth_header
    call_subprocess.return_value = 'fdsasadfdfdsd1237843 refs/tags/0.0.1'

    # Act
    result = sut.git_tag_exist(tag_name, auth_header)

    # Assert
    assert result


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
def test_git_tag_exist_returns_false_when_result_is_none(call_subprocess, clidata):
    """ Calls git_tag_check command with necessary parameters """
    # Arrange
    tag_name = '0.0.1'
    auth_header = clidata.auth_header
    call_subprocess.return_value = None

    # Act
    result = sut.git_tag_exist(tag_name, auth_header)

    # Assert
    assert not result


# endregion git_tag_exist()

# region get_current_branch_simplified()


def test_get_current_branch_simplified_given_branch_and_environment_variable_creates_environment_variable(branchesdata):
    """Given a branch name and a environment variable, calls platform_specific's create_
    environment_variables method"""

    # Arrange
    branch = branchesdata.other_branch
    environment_variable_name = branchesdata.environment_variable_name

    # Act
    with patch.object(sut, "platform_specific") as platform_specific_mock:
        with patch.object(platform_specific_mock, "create_environment_variables") as create_env_vars_mock:
            sut.get_current_branch_simplified(branch, environment_variable_name)
            # Assert
            create_env_vars_mock.assert_called_once_with({environment_variable_name: branch})


# endregion

# region simplify_branch_name()


@pytest.mark.parametrize("long_branch, expected", [
    (BranchesData.long_master_branch, BranchesData.simple_master_branch),
    (BranchesData.long_pr_branch, BranchesData.simple_pr_branch)])
def test_simplify_branch_name_given_branch_when_root_then_returns_simplified(long_branch, expected):
    """Given a branch name, when it is a root branch, then it is returned
    simplified"""

    # Arrange

    # Act
    result = sut.simplify_branch_name(long_branch)

    # Assert
    assert result == expected


def test_simplify_branch_name_given_branch_when_feature_then_returns_simplified(branchesdata):
    """Given a branch name, when it is a feature branch, then it is returned
    simplified"""

    # Arrange
    long_branch = branchesdata.long_feature_branch
    expected = branchesdata.simple_feature_branch

    # Act
    result = sut.simplify_branch_name(long_branch)

    # Assert
    assert result == expected


def test_simplify_branch_name_given_branch_when_other_then_returns_original(branchesdata):
    """Given a branch name, when it is non-defined branch, then it is returned
    simplified"""

    # Arrange
    long_branch = branchesdata.other_branch
    expected = branchesdata.other_branch

    # Act
    result = sut.simplify_branch_name(long_branch)

    # Assert
    assert result == expected


# endregion

# region update_gitignore_exclusion()


def test_update_gitignore_exclusion_given_regex_when_more_than_1_capture_group_raises_valueerror():
    """Given a RegEx, when it has more than 1 capture group, then raises
    ValueError"""

    # Arrange
    path = "/pathto"
    regex = "(a-z)(a-z)"
    value = "mytheme"

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.update_gitignore_exclusion(path, regex, value)


@patch("builtins.open", new_callable=mock_open, read_data=GitignoreData.file_contents)
def test_update_gitignore_exclusion_given_regex_when_1_capture_group_reads_gitignore(mocked_open, filenames):
    """Given a RegEx, when it has 1 capture group, it reads the .gitignore file
    passed in path"""

    # Arrange
    regex = GitignoreData.regex
    value = GitignoreData.replace_value

    # Act
    sut.update_gitignore_exclusion(filenames.path, regex, value)

    # Assert
    mocked_open.assert_any_call(filenames.path, "r+")


@patch("builtins.open", new_callable=mock_open, read_data=GitignoreData.file_contents)
def test_update_gitignore_exclusion_given_regex_when_1_capture_group_writes_gitignore(mocked_open, filenames):
    """Given a RegEx, when it has 1 capture group, it writes the .gitignore
    file after editing it"""

    # Arrange
    regex = GitignoreData.regex
    value = GitignoreData.replace_value

    # Act
    sut.update_gitignore_exclusion(filenames.path, regex, value)

    # Assert
    mocked_open.assert_any_call(filenames.path, "w")


# endregion

# region purge_gitkeep()


def test_purge_gitkeep_when_invalid_path_raises_valueerror(paths):
    """Given an invalid path, raises ValueError"""

    # Arrange
    path = paths.invalid_path

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.purge_gitkeep(path)


@patch("logging.info")
@patch("os.remove")
@patch.object(path_tools, "is_empty_dir", return_value=True)
def test_purge_gitkeep_when_no_additional_files_remove_not_called(is_empty_dir_mock,
                                                                  os_remove,
                                                                  logging_info,
                                                                  tmp_path):
    """Given a directory with a .gitkeep file, when directory is empty, do
    nothing"""

    # Arrange
    guess_gitkeep_file = pathlib.Path.joinpath(tmp_path, ".gitkeep")
    with open(str(guess_gitkeep_file), "w") as gitkeep:
        gitkeep.write("")

    # Act
    sut.purge_gitkeep(str(tmp_path))

    # Assert
    os_remove.assert_not_called()


@patch("logging.info")
@patch("os.remove")
def test_purge_gitkeep_when_directory_not_empty_remove_called(os_remove, logging_info, tmp_path):
    """Given a directory with a .gitkeep file, when directory not empty, call
    os.remove()"""

    # Arrange
    guess_gitkeep_file = pathlib.Path.joinpath(tmp_path, ".gitkeep")
    other_file = pathlib.Path.joinpath(tmp_path, "other_file.txt")
    with open(str(guess_gitkeep_file), "w") as gitkeep:
        gitkeep.write("")
    with open(str(other_file), "w") as file:
        file.write("hello world!")

    # Act
    sut.purge_gitkeep(str(tmp_path))

    # Assert
    os_remove.assert_called_once_with(guess_gitkeep_file)

# endregion

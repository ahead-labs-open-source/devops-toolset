"""Unit core for the i18n/utils.py file"""

import unittest.mock as mock
from unittest.mock import call

import devops_toolset as sut
import devops_toolset as tools_cli
import argparse
import pathlib
import os
from devops_toolset.core import App
import shutil

# region get_files()

app: App = App(True)


@mock.patch.object(pathlib.Path, "rglob")
def test_get_files_given_starting_path_and_glob_should_return_list_pathlib_rglob(rglob_mock, filenames):
    """ Given a starting_path and a glob, should call pathlib.rglob with arguments and return a list"""
    # Arrange
    starting_path = filenames.path
    test_glob = "*.*"
    expected_result = filenames.paths
    rglob_mock.return_value = expected_result
    # Act
    result = sut.get_files(starting_path, test_glob)
    # Assert
    assert expected_result == result


# endregion get_files()

# region compile_po_files()


@mock.patch.object(tools_cli, "call_subprocess")
def test_compile_po_files_given_path_then_calls_get_files(filenames):
    """Given a locale path, it should call get_file_paths_in_tree() to get the
    paths"""

    # Arrange
    with mock.patch.object(sut, "get_files") as file_paths:
        file_paths.return_value = filenames.paths

    # Act
        sut.compile_po_files()

    # Assert
    file_paths.assert_called()


@mock.patch.object(tools_cli, "call_subprocess")
def test_compile_po_files_given_path_when_args_contain_py_then_calls_subprocess_with_dot_py(subprocess_mock):
    """ Given a locale path, when args contain the py arg, then compounds the command
        with msgfmt.py and files and calls it """

    # Arrange
    expected_files = ["foo1.po"]
    expected_command = "msgfmt.py -o foo1.mo foo1.po"

    with mock.patch.object(sut, "args") as sut_args_mock:
        sut_args_mock.return_value = argparse.Namespace(py=True)
        with mock.patch.object(sut, "get_files") as file_paths:
            file_paths.return_value = expected_files

            # Act
            sut.compile_po_files()

    # Assert
    subprocess_mock.assert_called_once_with(expected_command)


@mock.patch.object(tools_cli, "call_subprocess")
def test_compile_po_files_given_path_when_args_not_contain_py_then_calls_subprocess_without_dot_py(subprocess_mock):
    """ Given a locale path, when args contain the py arg, then compounds the command
        with msgfmt and po/mo files and calls it """

    # Arrange
    expected_files = ["foo2.po"]
    expected_command = "msgfmt -o foo2.mo foo2.po"

    with mock.patch.object(sut, "get_files") as file_paths:
        file_paths.return_value = expected_files

        # Act
        sut.compile_po_files()

    # Assert
    subprocess_mock.assert_called_once_with(expected_command)


@mock.patch.object(os, "remove")
def test_compile_po_files_given_path_when_mo_file_exist_then_calls_os_remove(os_remove_mock):
    """ Given a locale path, when a mo file already exists, should remove it first """

    # Arrange
    expected_files = ["foo3.po"]
    expected_mo_deleted_file = "foo3.mo"

    with mock.patch.object(tools_cli, "call_subprocess"):
        with mock.patch.object(sut, "get_files") as file_paths:
            file_paths.return_value = expected_files
            with mock.patch.object(pathlib.Path, "exists") as path_exists_mock:
                path_exists_mock.return_value = True

                # Act
                sut.compile_po_files()

                # Assert
                os_remove_mock.assert_called_once_with(pathlib.PurePath(expected_mo_deleted_file))

# endregion

# region generate_pot_file()


@mock.patch("devops_toolset.i18n.utils.distribute_pot")
@mock.patch.object(tools_cli, "call_subprocess")
def test_generate_pot_file_given_path_then_calls_get_files(call_subprocess_mock, distribute_pot_mock, filenames):
    """Given a locale path, it should call get_file_paths_in_tree() to get the
    paths"""

    # Arrange
    with mock.patch.object(sut, "get_files") as file_paths:
        file_paths.return_value = filenames.paths

    # Act
        sut.generate_pot_file()

    # Assert
    file_paths.assert_called()


@mock.patch("devops_toolset.i18n.utils.distribute_pot")
@mock.patch.object(tools_cli, "call_subprocess")
def test_generate_pot_file_given_path_when_args_contain_py_then_calls_popen_with_pygettext(subprocess_mock,
                                                                                           distribute_pot_mock,
                                                                                           filenames):
    """ Given a pot file path, when args contain the py arg, then compounds the command
        with pygettext.py and all py files and calls it """
    # Arrange
    expected_pot_file = filenames.test_pot_file
    expected_path_list = [pathlib.PurePath(filenames.test_file), pathlib.PurePath(filenames.test_file)]
    expected_command = f"pygettext.py -d base -o {expected_pot_file} {' '.join(map(str, expected_path_list))}"

    with mock.patch.object(sut, "args") as sut_args_mock:
        sut_args_mock.return_value = argparse.Namespace(py=True)
        with mock.patch.object(sut, "get_files") as file_paths:
            file_paths.return_value = expected_path_list
            with mock.patch.object(pathlib.Path, "joinpath") as joinpath_mock:
                joinpath_mock.return_value = pathlib.PurePath(expected_pot_file)

                # Act
                sut.generate_pot_file()

    # Assert
    subprocess_mock.assert_called_once_with(expected_command)


@mock.patch("devops_toolset.i18n.utils.distribute_pot")
@mock.patch.object(tools_cli, "call_subprocess")
def test_generate_pot_file_given_path_when_args_not_py_then_calls_popen_with_xgettext(subprocess_mock,
                                                                                      distribute_pot_mock,
                                                                                      filenames):
    """ Given a locale path, when args not contain the py arg, then iterates on files and compounds the command
        with xgettext and all py files and calls it """

    # Arrange
    expected_pot_file = filenames.test_pot_file
    expected_path_list = [pathlib.PurePath(filenames.test_file), pathlib.PurePath(filenames.test_file2)]
    expected_command = f"xgettext --from-code=utf-8 -d base -o {expected_pot_file} " \
                       f"{' '.join(map(str, expected_path_list))}"

    with mock.patch.object(sut, "get_files") as file_paths:
        file_paths.return_value = expected_path_list
        with mock.patch.object(pathlib.Path, "joinpath") as joinpath_mock:
            joinpath_mock.return_value = pathlib.PurePath(expected_pot_file)

            # Act
            sut.generate_pot_file()

    # Assert
    subprocess_mock.assert_called_once_with(expected_command)


@mock.patch.object(os, "remove")
@mock.patch("devops_toolset.i18n.utils.distribute_pot")
def test_generate_pot_file_given_path_when_mo_file_exist_then_calls_os_remove(distribute_pot_mock, os_remove_mock,
                                                                              filenames):
    """ Given a locale path, when a pot file already exists, should remove it first """

    # Arrange
    expected_pot_deleted_file = filenames.test_pot_file
    expected_path_list = [pathlib.PurePath(filenames.test_file), pathlib.PurePath(filenames.test_file2)]

    with mock.patch.object(tools_cli, "call_subprocess"):
        with mock.patch.object(pathlib.Path, "joinpath") as joinpath_mock:
            joinpath_mock.return_value = pathlib.PurePath(expected_pot_deleted_file)
            with mock.patch.object(sut, "get_files") as file_paths:
                file_paths.return_value = expected_path_list
                with mock.patch.object(pathlib.Path, "exists") as path_exists_mock:
                    path_exists_mock.return_value = True

                    # Act
                    sut.generate_pot_file()

    # Assert
    os_remove_mock.assert_called_once_with(expected_pot_deleted_file)


# endregion

# region distribute_pot()


@mock.patch("os.walk")
@mock.patch("pathlib.Path.exists")
def test_distribute_pot_when_pot_file_not_exist_then_return(exists_mock, walk_mock):
    """ Given pot_file path, when doesn't exist, then should return """
    # Arrange
    exists_mock.return_value = False
    # Act
    sut.distribute_pot()
    # Assert
    walk_mock.assert_not_called()


@mock.patch("os.remove")
@mock.patch.object(shutil, "copy")
@mock.patch("pathlib.Path.exists")
def test_distribute_pot_when_pot_file_exist_and_po_file_exist_then_remove_po_file(exists_mock, shutil_mock,
                                                                                  remove_mock):
    """ Given pot_file path, when exists and the correspondent po file exist, then should call os.remove """
    # Arrange
    exists_mock.return_value = True
    destination_path = pathlib.Path.joinpath(app.settings.locales_path, pathlib.Path("en"),
                                                 "LC_MESSAGES", "base.po")
    # Act
    sut.distribute_pot()
    calls = [call(destination_path)]
    # Assert
    remove_mock.assert_has_calls(calls)


@mock.patch("os.remove")
@mock.patch.object(shutil, "copy")
@mock.patch("pathlib.Path.exists")
def test_distribute_pot_when_pot_file_exist_then_copy_to_inmediate_subdirectories(exists_mock, shutil_mock,
                                                                                  remove_mock):
    """ Given pot_file path, when exists, then should walk into subdirectories and call shutil.copy to them """
    # Arrange
    exists_mock.return_value = True
    pot_file = pathlib.Path.joinpath(app.settings.locales_path, "base.pot")
    destination_path = pathlib.Path.joinpath(app.settings.locales_path, pathlib.Path("en"),
                                             "LC_MESSAGES", "base.po")
    # Act
    sut.distribute_pot()
    calls = [call(pot_file, destination_path)]

    # Assert
    shutil_mock.assert_has_calls(calls)

# endregion

# region merge_pot_file()


@mock.patch.object(tools_cli, "call_subprocess")
def test_merge_pot_file_given_pot_file_should_call_msgmerge_command(subprocess_mock, filenames):
    """ Given a pot file and a locale path, should call an str command """
    # Arrange
    expected_pot_file = filenames.test_pot_file
    expected_po_files_list = [pathlib.PurePath(filenames.test_file)]
    expected_command = f"msgmerge -U {expected_po_files_list[0]} {expected_pot_file}"
    with mock.patch.object(pathlib.Path, "joinpath") as joinpath_mock:
        joinpath_mock.return_value = pathlib.PurePath(expected_pot_file)
        with mock.patch.object(sut, "get_files") as file_paths:
            file_paths.return_value = expected_po_files_list
            with mock.patch.object(pathlib.Path, "exists") as path_exists_mock:
                path_exists_mock.return_value = True

                # Act
                sut.merge_pot_file()

    subprocess_mock.assert_called_once_with(expected_command)


@mock.patch.object(sut, "generate_pot_file")
@mock.patch.object(pathlib.Path, "exists")
def test_merge_pot_file_given_pot_file_when_not_exist_should_call_generate_pot_file(path_exists_mock, sut_mock):
    """ Given a pot file and a locale path, if pot_file doesn't exist,
    should call generate_pot_file """
    # Arrange
    path_exists_mock.return_value = False
    with mock.patch.object(tools_cli, "call_subprocess"):
        # Act
        sut.merge_pot_file()
        # Assert
    sut_mock.assert_called_once()
# endregion


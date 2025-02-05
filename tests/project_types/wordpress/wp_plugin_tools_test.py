"""Unit tests for the wp_plugin_tools file"""
import json
import pathlib

import pytest
from unittest.mock import patch

import devops_toolset as sut
from devops_toolset import BasicStructureStarter


# region create_plugin


@patch("logging.error")
@patch("os.path.exists")
def test_create_plugin_logs_error_when_plugin_destination_paths_does_not_exist(exists_mock, logging_mock, pluginsdata):
    """ Given root path, when not exist, then logs error and returns """
    # Arrange
    exists_mock.return_value = False
    # Act
    sut.create_plugin(json.loads(pluginsdata.plugin_config), json.loads(pluginsdata.plugin_structure),
                      pluginsdata.plugin_root_path)
    # Assert
    logging_mock.assert_called_once()


@patch("os.path.exists")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch.object(BasicStructureStarter, "add_item")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.parse_plugin_config_in_plugin_file")
def test_create_plugin_calls_purge_gitkeep_when_path_exists(parse_plugin_config_mock, add_item_mock,
                                                            purge_gitkeep_mock, exists_mock, pluginsdata):
    """ Given root path, when exist, then calls purge_gitkeep """
    # Arrange
    exists_mock.return_value = True
    # Act
    sut.create_plugin(json.loads(pluginsdata.plugin_config), json.loads(pluginsdata.plugin_structure),
                      pluginsdata.plugin_root_path)
    # Assert
    purge_gitkeep_mock.assert_called_once_with(pathlib.Path(pluginsdata.plugin_root_path).as_posix())


@patch("os.path.exists")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch.object(BasicStructureStarter, "add_item")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.parse_plugin_config_in_plugin_file")
def test_create_plugin_calls_add_item_when_path_exists(parse_plugin_config_mock, add_item_mock,
                                                                purge_gitkeep_mock, exists_mock, pluginsdata):
    """ Given root path, when exists, then calls add_item method """
    # Arrange
    exists_mock.return_value = True
    # Act
    sut.create_plugin(json.loads(pluginsdata.plugin_config), json.loads(pluginsdata.plugin_structure),
                          pluginsdata.plugin_root_path)
    # Assert
    add_item_mock.assert_called()


@patch("os.path.exists")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch.object(BasicStructureStarter, "add_item")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.parse_plugin_config_in_plugin_file")
def test_create_plugin_does_not_call_add_item_when_path_exists(parse_plugin_config_mock, add_item_mock,
                                                                purge_gitkeep_mock, exists_mock, pluginsdata):
    """ Given root path, when exists and no items found, then doesn't call add_item method """
    # Arrange
    exists_mock.return_value = True
    # Act
    sut.create_plugin(json.loads(pluginsdata.plugin_config), json.loads(pluginsdata.empty_plugin_structure),
                          pluginsdata.plugin_root_path)
    # Assert
    add_item_mock.assert_not_called()

# endregion create_plugin


# region create_release_tag


@patch("logging.exception")
def test_create_release_tag_logs_exception_when_exception_raised(logging_mock, pluginsdata):
    """ Given root path, when not exists, should catch exception and log exception"""
    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    tag_name = pluginsdata.tag_name

    # Act
    sut.create_release_tag(plugin_root_path, tag_name, False)

    # Assert
    logging_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("pathlib.Path.mkdir")
@patch("logging.info")
def test_create_release_tag_creates_structure_when_path_not_already_exist(
        logging_mock, mkdir_mock, _, pluginsdata):
    """ Given root path, when exists, then creates tag directory structure"""

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    tag_name = pluginsdata.tag_name
    plugin_tag_path = pathlib.Path(plugin_root_path).joinpath('tags', tag_name)

    # Act
    sut.create_release_tag(plugin_root_path, tag_name, False)

    # Assert
    mkdir_mock.assert_called_once_with(plugin_tag_path)


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.exists")
@patch("logging.warning")
def test_create_release_tag_warns_when_path_already_exist(
        logging_mock, exists_mock, mkdir_mock, check_plugin_path_exists_mock, pluginsdata):
    """ Given root path, when exists, then creates tag directory structure """

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    tag_name = pluginsdata.tag_name
    exists_mock.return_value = True

    # Act
    sut.create_release_tag(plugin_root_path, tag_name, False)

    # Assert
    logging_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.exists")
@patch("shutil.copytree")
@patch("logging.info")
def test_create_release_tag_copies_trunk_when_copy_trunk_is_true(
        logging_mock, shutil_copy_mock, exists_mock, mkdir_mock, check_plugin_path_exists_mock, pluginsdata):
    """ Given root path, when exists and copy_trunk is true, then creates tag directory and copies trunk data"""

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    tag_name = pluginsdata.tag_name
    exists_mock.return_value = False
    plugin_trunk_path: str = str(pathlib.Path(plugin_root_path).joinpath('trunk'))
    plugin_tag_path: str = str(pathlib.Path(plugin_root_path).joinpath('tags', tag_name))

    # Act
    sut.create_release_tag(plugin_root_path, tag_name, True)

    # Assert
    shutil_copy_mock.assert_called_once_with(plugin_trunk_path, plugin_tag_path, dirs_exist_ok=True)


# endregion create_release_tag

# region deploy_current_trunk


@patch("logging.exception")
def test_deploy_current_trunk_logs_exception_when_exception_raised(logging_mock, pluginsdata):
    """ Given root path, when not exists then logs an exception """

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password

    # Act
    sut.deploy_current_trunk(plugin_root_path, commit_message, username, password)

    # Assert
    logging_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_parameters")
@patch("devops_toolset.tools.svn.svn_add")
@patch("devops_toolset.tools.svn.svn_checkin")
@patch("logging.info")
def test_deploy_current_trunk_calls_svn_add(
        logging_mock, svn_checkin_mock, svn_add_mock, check_parameters_mock, check_plugin_path_exists_mock,
        pluginsdata):
    """ Given arguments, when valid, then calls svn add"""

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    plugin_trunk_path: str = str(pathlib.Path(plugin_root_path).joinpath('trunk'))
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password

    # Act
    sut.deploy_current_trunk(plugin_root_path, commit_message, username, password)

    # Assert
    svn_add_mock.assert_called_once_with(f'{plugin_trunk_path}/*')


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_parameters")
@patch("devops_toolset.tools.svn.svn_add")
@patch("devops_toolset.tools.svn.svn_checkin")
@patch("logging.info")
def test_deploy_current_trunk_calls_svn_checkin(
        logging_mock, svn_checkin_mock, svn_add_mock, check_parameters_mock, check_plugin_path_exists_mock,
        pluginsdata):
    """ Given arguments, when valid, then calls svn checkin"""

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password

    # Act
    sut.deploy_current_trunk(plugin_root_path, commit_message, username, password)

    # Assert
    svn_checkin_mock.assert_called_once_with(commit_message, username, password)


# endregion deploy_current_trunk

# region deploy_release_tag


@patch("logging.exception")
def test_deploy_release_tag_logs_exception_when_exception_raised(logging_mock, pluginsdata):
    """ Given root path, when not exists then logs an exception """

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password
    tag_name = pluginsdata.tag_name

    # Act
    sut.deploy_release_tag(plugin_root_path, tag_name, commit_message, username, password)

    # Assert
    logging_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_parameters")
@patch("devops_toolset.tools.svn.svn_add")
@patch("devops_toolset.tools.svn.svn_checkin")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.create_release_tag")
@patch("logging.info")
def test_deploy_release_tag_calls_create_release_tag(
        logging_mock, create_release_tag_mock, svn_checkin_mock, svn_add_mock, check_parameters_mock,
        check_plugin_path_exists_mock, pluginsdata):
    """ Given arguments, when valid, then calls create_release_tag """

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password
    tag_name = pluginsdata.tag_name

    # Act
    sut.deploy_release_tag(plugin_root_path, tag_name, commit_message, username, password)

    # Assert
    create_release_tag_mock.assert_called_once_with(plugin_root_path, tag_name)


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_parameters")
@patch("devops_toolset.tools.svn.svn_add")
@patch("devops_toolset.tools.svn.svn_checkin")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.create_release_tag")
@patch("logging.info")
def test_deploy_release_tag_calls_svn_add(
        logging_mock, create_release_tag_mock, svn_checkin_mock, svn_add_mock, check_parameters_mock,
        check_plugin_path_exists_mock, pluginsdata):
    """ Given arguments, when valid, then calls svn add"""

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password
    tag_name = pluginsdata.tag_name
    plugin_tag_path = pathlib.Path(plugin_root_path).joinpath('tags', tag_name)

    # Act
    sut.deploy_release_tag(plugin_root_path, tag_name, commit_message, username, password)

    # Assert
    svn_add_mock.assert_called_once_with(f'{plugin_tag_path}/*')


@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_plugin_path_exists")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.__check_parameters")
@patch("devops_toolset.tools.svn.svn_add")
@patch("devops_toolset.tools.svn.svn_checkin")
@patch("devops_toolset.project_types.wordpress.wp_plugin_tools.create_release_tag")
@patch("logging.info")
def test_deploy_release_tag_calls_svn_checkin(
        logging_mock, create_release_tag_mock, svn_checkin_mock, svn_add_mock, check_parameters_mock,
        check_plugin_path_exists_mock, pluginsdata):
    """ Given arguments, when valid, then calls svn checkin"""

    # Arrange
    plugin_root_path = pluginsdata.plugin_root_path
    commit_message = pluginsdata.commit_message
    username = pluginsdata.username
    password = pluginsdata.password
    tag_name = pluginsdata.tag_name

    # Act
    sut.deploy_release_tag(plugin_root_path, tag_name, commit_message, username, password)

    # Assert
    svn_checkin_mock.assert_called_once_with(commit_message, username, password)


# endregion deploy_release_tag

# region __check_parameters

@pytest.mark.parametrize("commit_message, username, password", [('', 'username', 'password'),
                                                                ('commit_message', None, 'password'),
                                                                ('commit_message', 'username', '')])
def test__check_parameters_raises_error_when_commit_message_is_none(commit_message, username, password):
    """ Given parameters, when not valid, then raises ValueError """

    # Arrange
    # Act
    with pytest.raises(ValueError) as error:
        sut.__check_parameters(commit_message, username, password)
        # Assert
        assert error is not None


# endregion __check_parameters

# region __check_plugin_path_exists

@patch("pathlib.Path.exists")
def test__check_plugin_path_exists_raises_error_when_path_not_exists(exists_path_mock, pluginsdata):
    """ Given plugin path, when not exist, then raises FileNotFoundError """
    # Arrange
    exists_path_mock.return_value = False

    # Act
    with pytest.raises(FileNotFoundError) as error:
        sut.__check_plugin_path_exists(pluginsdata.plugin_root_path)
        # Assert
        assert error is not None


@patch("pathlib.Path.exists")
def test__check_plugin_path_returns_when_path_exists(exists_path_mock, pluginsdata):
    """ Given plugin path, when exist, then do not raise FileNotFoundError """

    # Arrange
    exists_path_mock.return_value = True

    # Act
    sut.__check_plugin_path_exists(pluginsdata.plugin_root_path)

    # Assert (reaching this line implies no exception raised, to test passed successfully)
    assert True

# endregion __check_plugin_path_exists

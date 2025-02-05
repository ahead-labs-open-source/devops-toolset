""" Unit core for the generate_wordpress script """

import json
import pathlib
import devops_toolset as constants
import devops_toolset as sut
from unittest.mock import patch, ANY

# region main


@patch("devops_toolset.project_types.wordpress.wptools.import_content_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.filesystem.paths.move_files")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.delete_sample_wp_config_file")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.generate_additional_wpconfig_files")
@patch("logging.info")
@patch("devops_toolset.core.log_tools.log_indented_list")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.build_theme")
@patch("devops_toolset.project_types.wordpress.wptools.install_plugins_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.install_themes_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_site")
@patch("devops_toolset.project_types.wordpress.wptools.set_wordpress_config_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.download_wordpress")
@patch("devops_toolset.project_types.wordpress.wptools.scaffold_wordpress_basic_project_structure")
@patch("devops_toolset.project_types.wordpress.wptools.get_wordpress_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("devops_toolset.project_types.wordpress.wptools.get_required_file_paths")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_themes_path_from_root_path")
@patch("devops_toolset.filesystem.paths.files_exist_filtered")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wptools.get_environment")
@patch("devops_toolset.project_types.wordpress.wptools.add_wp_options")
@patch("devops_toolset.project_types.wordpress.wptools.create_users")
def test_main_given_required_files_when_present_then_calls_wptools_get_required_file_paths(
        create_users_mock, add_wp_options_mock, get_environment_mock, constants_mock, files_exist_mock,
        get_themes_path_mock, get_required_files_mock, get_site_config_mock, get_wordpress_path,
        scaffold_basic_structure_mock, download_wordpress_mock, set_wordpress_config_mock,
        install_wordpress_site_mock, install_theme_mock, install_plugins_mock, build_theme_mock, log_indented_mock,
        logging_mock, generate_environments_mock, delete_sample_mock, export_database_mock, purge_gitkeep_mock,
        move_files_mock, convert_wp_config_token_mock,  import_content_mock, wordpressdata):
    """ Given root_path, when required files present in root_path, then calls get_required_file_paths"""

    # Arrange
    required_files = []
    files_exist_mock.return_value = required_files
    environment = "any"
    root_path = wordpressdata.root_path
    required_files_pattern_suffixes = list(
        map(lambda x: f"*{x[1]}", constants.FileNames.REQUIRED_FILE_SUFFIXES.items())
    )

    # Act
    sut.main(root_path, "root", "root", "root", environment, [''], {}, False, True, False, False, False)

    # Assert
    get_required_files_mock.assert_called_with(root_path, required_files_pattern_suffixes)


@patch("devops_toolset.project_types.wordpress.wptools.import_content_from_configuration_file")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.delete_sample_wp_config_file")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.generate_additional_wpconfig_files")
@patch("logging.info")
@patch("devops_toolset.core.log_tools.log_indented_list")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.build_theme")
@patch("devops_toolset.project_types.wordpress.wptools.install_plugins_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.install_themes_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.setup_database")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_site")
@patch("devops_toolset.project_types.wordpress.wptools.set_wordpress_config_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.download_wordpress")
@patch("devops_toolset.project_types.wordpress.wptools.scaffold_wordpress_basic_project_structure")
@patch("devops_toolset.project_types.wordpress.wptools.get_wordpress_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("devops_toolset.project_types.wordpress.wptools.get_required_file_paths")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_themes_path_from_root_path")
@patch("devops_toolset.filesystem.paths.files_exist_filtered")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wptools.get_environment")
@patch("devops_toolset.project_types.wordpress.wptools.add_wp_options")
@patch("devops_toolset.project_types.wordpress.wptools.create_users")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.filesystem.paths.move_files")
def test_main_given_required_files_when_present_and_create_db_then_calls_setup_database(
        move_files_mock, convert_wp_config_token_mock, create_users_mock, add_wp_options_mock, get_environment_mock,
        constants_mock, files_exist_mock, get_themes_path_mock, get_required_files_mock,  get_site_config_mock,
        get_wordpress_path, scaffold_basic_structure_mock, download_wordpress_mock,
        set_wordpress_config_mock, install_wordpress_site_mock, setup_database_mock, install_theme_mock,
        install_plugins_mock, build_theme_mock, log_indented_mock, logging_mock, generate_environments_mock,
        delete_sample_mock, export_database_mock, purge_gitkeep_mock, import_content_mock, wordpressdata):
    """ Given root_path, when required files present in root_path, then calls setup_database"""

    # Arrange
    required_files = []
    files_exist_mock.return_value = required_files
    environment = "any"
    root_path = wordpressdata.root_path
    environment_config = json.loads(wordpressdata.site_config_content)["environments"][0]
    get_environment_mock.return_value = environment_config
    get_wordpress_path.return_value = wordpressdata.wordpress_path
    create_db = True

    # Act
    sut.main(root_path, "root", "root", "root", environment, [''], {}, create_db, True, False, False, False)

    # Assert
    setup_database_mock.assert_called_with(environment_config, wordpressdata.wordpress_path, "root", "root")


@patch("devops_toolset.project_types.wordpress.wptools.import_content_from_configuration_file")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.delete_sample_wp_config_file")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.generate_additional_wpconfig_files")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.build_theme")
@patch("devops_toolset.project_types.wordpress.wptools.install_plugins_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.install_themes_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_site")
@patch("devops_toolset.project_types.wordpress.wptools.set_wordpress_config_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.download_wordpress")
@patch("devops_toolset.project_types.wordpress.wptools.scaffold_wordpress_basic_project_structure")
@patch("devops_toolset.project_types.wordpress.wptools.get_wordpress_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("devops_toolset.project_types.wordpress.wptools.get_required_file_paths")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_themes_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wptools.get_environment")
@patch("devops_toolset.project_types.wordpress.wptools.add_wp_options")
@patch("devops_toolset.project_types.wordpress.wptools.create_users")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.filesystem.paths.move_files")
@patch("devops_toolset.project_types.wordpress.scripts.script_common.check_required_files")
def test_main_given_required_files_calls_common_check_required_files(
        check_required_files_mock, move_files_mock, convert_wp_config_token_mock, create_users_mock,
        add_wp_options_mock, get_environment_mock, constants_mock, get_themes_path_mock, get_required_files_mock,
        get_site_config_mock, get_wordpress_path, scaffold_basic_structure_mock,
        download_wordpress_mock, set_wordpress_config_mock, install_wordpress_site_mock, install_theme_mock,
        install_plugins_mock, build_theme_mock, generate_environments_mock,
        delete_sample_mock, export_database_mock, purge_gitkeep_mock, import_content_mock, wordpressdata, mocks):
    """ Given root_path, when required files present in root_path, then calls get_required_file_paths"""

    # Arrange
    required_files = list(map(lambda x: f"*{x[1]}", constants.FileNames.REQUIRED_FILE_SUFFIXES.items()))
    environment = "any"
    root_path = wordpressdata.root_path
    wordpress_files_urls = constants.Urls.BOOTSTRAP_REQUIRED_FILES

    # Act
    sut.main(root_path, "root", "root", "root", environment, [''], {}, False, True, False, False, False)

    # Assert
    check_required_files_mock.assert_called_with(required_files, root_path, wordpress_files_urls)


@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.delete_sample_wp_config_file")
@patch("devops_toolset.project_types.wordpress.scripts.generate_wordpress.generate_additional_wpconfig_files")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.build_theme")
@patch("devops_toolset.project_types.wordpress.wptools.install_plugins_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.install_themes_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_site")
@patch("devops_toolset.project_types.wordpress.wptools.set_wordpress_config_from_configuration_file")
@patch("devops_toolset.project_types.wordpress.wptools.download_wordpress")
@patch("devops_toolset.project_types.wordpress.wptools.scaffold_wordpress_basic_project_structure")
@patch("devops_toolset.project_types.wordpress.wptools.get_wordpress_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("devops_toolset.project_types.wordpress.wptools.get_required_file_paths")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_themes_path_from_root_path")
@patch("devops_toolset.filesystem.paths.files_exist_filtered")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.create_development_theme")
@patch("devops_toolset.project_types.wordpress.wptools.get_environment")
@patch("devops_toolset.project_types.wordpress.wptools.add_wp_options")
@patch("devops_toolset.project_types.wordpress.wptools.create_users")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.filesystem.paths.move_files")
def test_main_given_required_files_when_create_development_theme_then_calls_create_development_theme(
        move_files_mock, convert_wp_config_token_mock, create_users_mock, add_wp_options_mock, get_environment_mock,
        create_dev_theme_mock, constants_mock, files_exist_mock, get_themes_path_mock, get_required_files_mock,
        get_site_config_mock, get_wordpress_path, scaffold_basic_structure_mock,
        download_wordpress_mock, set_wordpress_config_mock, install_wordpress_site_mock, install_theme_mock,
        install_plugins_mock, build_theme_mock, generate_environments_mock, delete_sample_mock, export_database_mock,
        purge_gitkeep_mock, wordpressdata, mocks):
    """ Given root_path, when required files present in root_path, then calls get_required_file_paths"""

    # Arrange
    required_files = []
    files_exist_mock.return_value = required_files
    environment = "any"
    root_path = wordpressdata.root_path
    constants_mock.return_value = json.loads(wordpressdata.constants_file_content)
    constants_data = json.loads(wordpressdata.constants_file_content)

    # Act
    sut.main(root_path, "root", "root", "root", environment, [''], {}, False, True, True, True, False)

    # Assert
    create_dev_theme_mock.assert_called_once_with(ANY, root_path, constants_data)

# endregion main

# region delete_sample_wp_config_file


@patch("pathlib.Path.exists")
@patch("os.remove")
def test_delete_sample_wp_config_file_when_file_not_exist_then_remove(remove_mock, path_exists_mock, wordpressdata):
    """ Given wordpress_path, when config-sample.php exist, then calls os.remove """
    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    file_path = pathlib.Path.joinpath(pathlib.Path(wordpress_path), "wp-config-sample.php")
    path_exists_mock.return_value = True
    # Act
    sut.delete_sample_wp_config_file(wordpress_path)
    # Assert
    remove_mock.assert_called_once_with((str(file_path)))


@patch("pathlib.Path.exists")
@patch("os.remove")
def test_delete_sample_wp_config_file_when_file_exist_then_remove(remove_mock, path_exists_mock, wordpressdata):
    """ Given wordpress_path, when config-sample.php exist, then calls os.remove """
    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    path_exists_mock.return_value = False
    # Act
    sut.delete_sample_wp_config_file(wordpress_path)
    # Assert
    remove_mock.assert_not_called()


# endregion delete_sample_wp_config_file

# region get_basic_paths


@patch("os.path.realpath")
def test_get_basic_paths_returns_tuple(realpath_mock):
    """ Returns tuple with several basic paths """

    # Arrange
    script_path = "pathto/wordpress/scripts/generate_wordpress.py"
    realpath_mock.return_value = script_path

    # Act
    result = sut.get_basic_paths()

    # Assert
    assert type(result) is tuple


# endregion

# region generate_additional_wpconfig_files

@patch("devops_toolset.filesystem.paths.is_valid_path")
@patch("shutil.move")
def test_generate_additional_wpconfig_files_moves_file_if_is_valid_path(shutil_move_mock, is_valid_path_mock,
                                                                        wordpressdata):
    """ Given site_config and wordpress path, when its valid, should call shutils's move """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    wordpress_path = wordpressdata.wordpress_path
    # Act
    sut.generate_additional_wpconfig_files(site_config, {}, [], {}, wordpress_path)
    # Assert
    shutil_move_mock.assert_called()


# TODO (alberto.carbonell) Finish generate_additional_wpconfig_files tests
# endregion

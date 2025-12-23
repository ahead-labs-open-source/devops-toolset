"""Unit core for the wp_theme_tools file"""
import json
import pathlib

from devops_toolset.devops_platforms import constants as devops_platforms_constants
import devops_toolset.project_types.wordpress.wp_theme_tools as sut
import pytest
import devops_toolset.project_types.wordpress.constants as wp_constants
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
from tests.project_types.wordpress.conftest import WordPressData, ThemesData
from unittest.mock import patch, call, mock_open, ANY, Mock

literals = LiteralsCore([WordpressLiterals])


# region build_theme


@patch("logging.info")
def test_build_theme_given_site_config_when_no_src_themes_then_logs(logging_mock, wordpressdata,
                                                                    themesdata):
    """ Given site configuration, when no src themes present, then logs info """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    literal1 = literals.get("wp_looking_for_src_themes")
    literal2 = literals.get("wp_no_src_themes")
    src_theme: dict = {}

    # Act
    sut.build_theme(src_theme, theme_path, root_path)
    # Assert
    calls = [call(literal1), call(literal2)]
    logging_mock.assert_has_calls(calls)


@patch("logging.info")
def test_build_theme_given_site_config_when_no_build_in_src_themes_then_logs(logging_mock, wordpressdata, themesdata):
    """ Given site configuration, when no build is present on src themes, then logs info """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    no_src_theme_config = json.loads(themesdata.theme_single_no_src)
    literal1 = literals.get("wp_looking_for_src_themes")
    literal2 = literals.get("wp_theme_src_will_not_be_built")

    # Act
    sut.build_theme(no_src_theme_config, theme_path, root_path)
    # Assert
    calls = [call(literal1), call(literal2)]
    logging_mock.assert_has_calls(calls)


@patch("logging.info")
@patch("os.path.exists")
@patch("os.chdir")
@patch("devops_toolset.project_types.node.npm.install")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("devops_toolset.filesystem.zip.zip_directory")
@patch("devops_toolset.filesystem.parsers.parse_json_file")
@patch("devops_toolset.filesystem.tools.update_xml_file_entity_text")
def test_build_theme_given_site_config_when_src_themes_then_calls_npm_install(
        update_xml_mock, parse_json_mock, zip_directory_mock, subprocess_mock, npm_install_mock, chdir_mock,
        path_exists_mock, logging_mock, wordpressdata, themesdata):
    """ Given site configuration, when src theme present, then calls npm install wrapper """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    path_exists_mock.return_value = True
    src_theme_config = json.loads(themesdata.theme_single_src)[0]
    # Act
    sut.build_theme(src_theme_config, theme_path, root_path)
    # Assert
    npm_install_mock.assert_called_once()


@patch("logging.info")
@patch("os.path.exists")
@patch("os.chdir")
@patch("devops_toolset.project_types.node.npm.install")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("devops_toolset.filesystem.zip.zip_directory")
@patch("devops_toolset.filesystem.parsers.parse_json_file")
@patch("devops_toolset.filesystem.tools.update_xml_file_entity_text")
def test_build_theme_given_site_config_when_src_themes_then_chdir_to_source(
        update_xml_mock, parse_json_mock, zip_directory_mock, subprocess_mock, npm_install_mock,
        chdir_mock, path_exists_mock, logging_mock, wordpressdata, themesdata):
    """ Given site configuration, when src theme present, then calls npm install wrapper """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    path_exists_mock.return_value = True
    src_theme_config = json.loads(themesdata.theme_single_src)[0]
    src_theme_path = pathlib.Path.joinpath(pathlib.Path(theme_path), src_theme_config["source"])
    # Act
    sut.build_theme(src_theme_config, theme_path, root_path)
    # Assert
    chdir_mock.assert_called_once_with(src_theme_path)


@patch("logging.info")
@patch("os.path.exists")
@patch("os.chdir")
@patch("devops_toolset.project_types.node.npm.install")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("devops_toolset.filesystem.zip.zip_directory")
@patch("devops_toolset.filesystem.parsers.parse_json_file")
@patch("devops_toolset.filesystem.tools.update_xml_file_entity_text")
def test_build_theme_given_site_config_when_src_themes_then_calls_subprocess_with_build_command(
        update_xml_mock, parse_json_mock, zip_directory_mock, subprocess_mock, npm_install_mock,
        chdir_mock, path_exists_mock, logging_mock, wordpressdata, themesdata):
    """ Given site configuration, when src theme present, then calls subprocess with gulp_build command """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    path_exists_mock.return_value = True
    src_theme_config = json.loads(themesdata.theme_single_src)[0]
    theme_slug = src_theme_config["name"]
    theme_path_src = pathlib.Path.joinpath(pathlib.Path(theme_path), src_theme_config["source"])
    theme_path_dist = pathlib.Path.joinpath(theme_path_src, "dist")
    command = sut.commands.get("wp_theme_src_build_production").format(
        theme_slug=theme_slug,
        path=theme_path_dist)
    literal_before = literals.get("wp_webpack_build_before").format(theme_slug=theme_slug)
    literal_after = literals.get("wp_webpack_build_after").format(theme_slug=theme_slug)
    literal_error = literals.get("wp_webpack_build_error").format(theme_slug=theme_slug)
    # Act
    sut.build_theme(src_theme_config, theme_path, root_path)
    # Assert
    subprocess_mock.assert_called_once_with(command,
                                            log_before_out=[literal_before],
                                            log_after_out=[literal_after],
                                            log_after_err=[literal_error])


@patch("logging.info")
@patch("os.path.exists")
@patch("os.chdir")
@patch("devops_toolset.project_types.node.npm.install")
@patch("devops_toolset.tools.cli.call_subprocess")
@patch("devops_toolset.filesystem.zip.zip_directory")
@patch("devops_toolset.filesystem.parsers.parse_json_file")
@patch("devops_toolset.filesystem.tools.update_xml_file_entity_text")
def test_build_theme_given_site_config_when_src_themes_then_zips_dist(
        update_xml_mock, parse_json_mock, zip_directory_mock, subprocess_mock, npm_install_mock,
        chdir_mock, path_exists_mock, logging_mock, wordpressdata, themesdata):
    """ Given site configuration, when src theme present, then calls zip_directory """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    path_exists_mock.return_value = True
    src_theme_config = json.loads(themesdata.theme_single_src)[0]
    src_theme_path_obj = pathlib.Path.joinpath(pathlib.Path(theme_path), src_theme_config["source"])
    theme_slug = src_theme_config['name']
    theme_path_dist = pathlib.Path.joinpath(src_theme_path_obj, "dist")
    theme_path_zip = pathlib.Path.joinpath(pathlib.Path(theme_path), f"{theme_slug}.zip")
    # Act
    sut.build_theme(src_theme_config, theme_path, root_path)
    # Assert
    zip_directory_mock.assert_called_once_with(
        theme_path_dist.as_posix(), theme_path_zip.as_posix())


@patch("logging.info")
@patch("os.path.exists")
@patch("logging.error")
def test_build_theme_given_site_config_when_no_path_themes_src_then_logs_error(
        logging_error_mock, path_exists_mock, logging_info_mock, wordpressdata, themesdata):
    """ Given site configuration, when theme path src not exists, then logs error """
    # Arrange
    root_path = wordpressdata.root_path
    theme_path = wordpressdata.theme_path
    path_exists_mock.return_value = False
    src_theme_config = json.loads(themesdata.theme_single_src)[0]
    theme_path_src = pathlib.Path.joinpath(pathlib.Path(theme_path), src_theme_config["source"])
    # Act
    sut.build_theme(src_theme_config, theme_path, root_path)
    # Assert
    logging_error_mock.assert_called_once_with(literals.get("wp_file_not_found").format(file=theme_path_src))


# endregion

# region check_themes_configuration()

@patch("logging.warning")
@patch("logging.error")
@pytest.mark.parametrize("themes, expected",
                         [("[]", False),
                          (ThemesData.themes_content_with_three_themes_no_activate, False)])
def test_check_themes_configuration_given_themes_when_wrong_number_of_themes_then_return_false(
        error_mock, warning_mock, themes, expected):
    """ Given themes dict, when wrong number of themes, then return False """
    # Arrange
    themes_dict_content = json.loads(themes)
    # Act
    result = sut.check_themes_activation_configuration(themes_dict_content)
    # Assert
    assert result == expected


@patch("logging.warning")
@patch("logging.error")
@pytest.mark.parametrize("themes, expected",
                         [(ThemesData.themes_content_with_two_activated_themes, False),
                          (ThemesData.themes_content_with_two_themes_none_activated, False)])
def test_check_themes_configuration_given_themes_when_wrong_number_of_activated_themes_then_return_false(
        error_mock, warning_mock, themes, expected):
    """ Given themes dict, when wrong number of activated themes, then return False """
    # Arrange
    themes_dict_content = json.loads(themes)
    # Act
    result = sut.check_themes_activation_configuration(themes_dict_content)
    # Assert
    assert result == expected


@patch("logging.warning")
@patch("logging.error")
def test_check_themes_configuration_given_themes_when_correct_then_return_true(error_mock, warning_mock):
    """ Given themes dict, when correct setup of the themes, then return True """
    # Arrange
    themes_dict_content = json.loads(ThemesData.themes_content_with_two_themes_one_activated)
    expected = True
    # Act
    result = sut.check_themes_activation_configuration(themes_dict_content)
    # Assert
    assert result == expected


# endregion

# region check_theme_configuration()


@patch("logging.warning")
@patch("logging.error")
@pytest.mark.parametrize("theme, expected",
                         [(ThemesData.theme_single_content_with_wrong_feed, False),
                          (ThemesData.theme_single_content_with_correct_feed, True)])
def test_check_theme_configuration_given_theme_when_feed_expected_and_not_source_type_feed_then_returns_false(
        error_mock, warning_mock, theme, expected):
    """ Given single theme dict, when source_type = feed and no feed node, then returns False """
    # Arrange
    theme_dict_content = json.loads(theme)
    # Act
    result = sut.check_theme_configuration(theme_dict_content)
    # Assert
    assert result == expected


# endregion

# region create_development_theme()

@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_themes_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
@patch("logging.warning")
def test_create_development_theme_given_theme_config_when_no_src_theme_then_should_log_warning(
        log_warn_mock, get_src_theme, get_themes_from_root_path_mock, themesdata, wordpressdata):
    """ Given theme config, when there is no source_typed src themes, then should log a warning message """
    # Arrange
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    themes_path = wordpressdata.theme_path
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["environments"][0]["type"] = "production"
    get_src_theme.return_value = None
    get_themes_from_root_path_mock.return_value = pathlib.Path.joinpath(pathlib.Path(root_path), themes_path)
    # Act
    sut.create_development_theme(site_config, root_path, constants)
    # Assert
    log_warn_mock.assert_called()


@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_themes_path_from_root_path")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.scaffold_basic_theme_structure")
def test_create_development_theme_given_theme_config_when_src_theme_then_should_start_basic_theme_structure(
        scaffold_structure_mock, get_src_theme_mock, get_themes_from_root_path_mock, wordpressdata, themesdata):
    """ Given theme config, when there is a source_typed src theme, then should call the start_basic_theme_structure """

    # Arrange
    constants = json.loads(wordpressdata.constants_file_content)
    themes_content = json.loads(themesdata.theme_single_src)
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["environments"][0]["type"] = "production"
    site_config["settings"]["themes"] = themes_content
    get_src_theme_mock.return_value = themes_content[0]
    theme_slug = themes_content[0]["source"]
    root_path = pathlib.Path(wordpressdata.root_path)
    structure_file_name = f'{theme_slug}-wordpress-theme-structure.json'
    structure_file_path = pathlib.Path.joinpath(pathlib.Path(root_path), structure_file_name)
    themes_path = wordpressdata.theme_path
    get_themes_from_root_path_mock.return_value = pathlib.Path.joinpath(pathlib.Path(root_path), themes_path)
    destination_path = pathlib.Path.joinpath(pathlib.Path(root_path), themes_path)

    # Act
    sut.create_development_theme(site_config, wordpressdata.root_path, constants)

    # Assert
    scaffold_structure_mock.assert_called_once_with(destination_path, site_config, str(structure_file_path))


# endregion create_development_theme()

# region download_wordpress_theme()


@patch("devops_toolset.filesystem.zip.extract_file_from_zip")
@patch("os.remove")
def test_download_wordpress_theme_given_theme_config_when_source_type_is_feed_then_calls_get_last_artifact(
        os_remove_mock, extract_file_from_zip_mock, themesdata):
    """ Given theme config, when source type is feed, then should call get_last_artifact"""
    # Arrange
    theme_config = json.loads(themesdata.theme_single_content_with_correct_feed)
    destination_path = "path/to/destination"
    azdevops_user = "user"
    azdevops_token = "my_token"
    feed_config = theme_config["feed"]
    # Act
    with patch.object(sut, "platform_specific_restapi") as platform_specific_mock:
        with patch.object(platform_specific_mock, "get_last_artifact") as get_last_artifact_mock:
            get_last_artifact_mock.return_value = ("file_name", "file_path")
            sut.download_wordpress_theme(theme_config, destination_path,
                                         azdevops_user=azdevops_user,
                                         azdevops_token=azdevops_token)
            # Assert
            get_last_artifact_mock.assert_called_once_with(
                "organization",
                feed_config["name"],
                feed_config["package"],
                destination_path,
                azdevops_user,
                azdevops_token,
            )


@patch("logging.warning")
def test_download_wordpress_theme_given_theme_config_when_source_type_is_feed_and_not_kwargs_then_warns(
        log_warning_mock, themesdata):
    """ Given theme config, when source type is feed, then should call get_last_artifact"""
    # Arrange
    theme_config = json.loads(themesdata.theme_single_content_with_correct_feed)
    destination_path = "path/to/destination"
    # Act
    sut.download_wordpress_theme(theme_config, destination_path)
    # Assert
    log_warning_mock.assert_called()


@patch("devops_toolset.filesystem.paths.download_file")
def test_download_wordpress_theme_given_theme_config_when_source_type_is_url_then_calls_paths_download_file(
        download_file_mock, themesdata):
    """ Given theme config, when source type is url, then downloads content to the destination path"""
    # Arrange
    theme_config = json.loads(themesdata.theme_single_content_with_url)
    destination_path = "path/to/destination/"
    # Act
    sut.download_wordpress_theme(theme_config, destination_path)
    # Assert
    download_file_mock.assert_called_once_with(theme_config["source"], destination_path, f"{theme_config['name']}.zip")


# endregion

# region install_themes_from_configuration_file()


@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wp_cli.install_theme")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.check_themes_activation_configuration")
def test_install_theme_given_configuration_file_when_wrong_themes_configuration_then_return(
        check_themes_mock, install_theme_mock, logging_mock, wordpressdata, themesdata):
    """ Given the configuration values, when wrong configuration of themes given, then no installation calls
     should be made """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["themes"] = json.loads(themesdata.themes_content_with_three_themes_no_activate)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    check_themes_mock.return_value = False
    # Act
    sut.install_themes_from_configuration_file(site_config, environment_config, constants, root_path, True)
    # Assert
    install_theme_mock.assert_not_called()


@patch("devops_toolset.project_types.wordpress.wp_theme_tools.check_themes_activation_configuration")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.check_theme_configuration")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.download_wordpress_theme")
@patch("devops_toolset.filesystem.zip.read_text_file_in_zip")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.triage_themes")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wp_cli.install_theme")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.parse_theme_metadata")
@patch("devops_toolset.project_types.wordpress.wp_cli.theme_list_count")
def test_install_theme_given_configuration_file_theme_already_installed_then_skip(
        theme_list_count_mock, parse_metadata_mock, install_theme_mock, logging_mock, export_database_mock,
        convert_token_mock, triage_themes_mock, read_text_file_mock, download_wordpress_mock, check_theme_mock,
        check_themes_mock, wordpressdata, themesdata):
    """ Given the configuration values, when wrong single theme configuration found, then the theme is skipped """

    # Arrange
    theme_list_count_mock.return_value = 1
    check_themes_mock.return_value = True
    check_theme_mock.return_value = True
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["themes"] = json.loads(themesdata.theme_single_src)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    triage_themes_mock.return_value = None, json.loads(themesdata.themes_content_with_child_activated)[0]

    # Act
    sut.install_themes_from_configuration_file(site_config, environment_config, constants, root_path, True)

    # Assert
    install_theme_mock.assert_called()



@patch("devops_toolset.project_types.wordpress.wp_theme_tools.check_themes_activation_configuration")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.check_theme_configuration")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.download_wordpress_theme")
@patch("devops_toolset.filesystem.zip.read_text_file_in_zip")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.triage_themes")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wp_cli.install_theme")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.parse_theme_metadata")
@patch("devops_toolset.project_types.wordpress.wp_cli.theme_list_count")
def test_install_theme_given_configuration_file_when_no_parent_theme_then_install_once(
        theme_list_count_mock, parse_metadata_mock, install_theme_mock, logging_mock, export_database_mock,
        convert_token_mock, triage_themes_mock, read_text_file_mock, download_wordpress_mock, check_theme_mock,
        check_themes_mock, wordpressdata, themesdata):
    """ Given the configuration values, when wrong single theme configuration found, then the theme is skipped """

    # Arrange
    theme_list_count_mock.return_value = 0
    check_themes_mock.return_value = True
    check_theme_mock.return_value = True
    constants = json.loads(wordpressdata.constants_file_content)
    wordpress_path = pathlib.Path.joinpath(
        pathlib.Path(wordpressdata.root_path, constants["paths"]["wordpress"]))
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["themes"] = json.loads(themesdata.themes_content_with_child_activated)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    triage_themes_mock.return_value = None, json.loads(themesdata.themes_content_with_child_activated)[0]

    # Act
    sut.install_themes_from_configuration_file(site_config, environment_config, constants, root_path, True)

    # Assert
    install_theme_mock.assert_called_once_with(str(wordpress_path), themesdata.child_url_source, True,
                                               environment_config["wp_cli_debug"], themesdata.child_name)


# endregion

# region parse_theme_metadata()

@patch("logging.info")
@patch("logging.warning")
def test_parse_theme_metadata_returns_default_metadata_when_no_css_content_to_parse(logging_warning_mock,
                                                                                    logging_info_mock):
    """ Given metadata dict, when no css content, then returns default_metadata """
    # Arrange
    css_content: str = ''
    expected_result = wp_constants.DefaultValues.WORDPRESS_METADATA_EMPTY

    # Act
    result = sut.parse_theme_metadata(css_content)

    # Assert
    assert result == expected_result


@patch("logging.info")
@patch("logging.warning")
def test_parse_theme_metadata_returns_metadata(logging_warning_mock, logging_info_mock, themesdata):
    """ Given metadata dict, when css content present, then returns metadata parsed """
    # Arrange
    css_content: str = themesdata.default_scss_file_example
    expected_result = wp_constants.DefaultValues.WORDPRESS_METADATA_EMPTY

    # Act
    result = sut.parse_theme_metadata(css_content)

    # Assert
    assert result == expected_result


@patch("logging.info")
@patch("logging.warning")
def test_parse_theme_metadata_creates_environment_variables_when_flag_is_on(logging_warning_mock, logging_info_mock,
                                                                            themesdata):
    """ Given metadata dict, when css content present and add_environment_variables is True, then
     creates environment variables """
    # Arrange
    css_content: str = themesdata.default_scss_file_example

    # Act
    with patch.object(sut, "platform_specific_environment") as platform_specific_mock:
        with patch.object(platform_specific_mock, "create_environment_variables") as create_environment_variables_mock:
            sut.parse_theme_metadata(css_content, True)

            # Assert
            create_environment_variables_mock.assert_called()
# endregion

# region replace_theme_meta_data_in_package_file()

@patch("builtins.open", new_callable=mock_open, read_data=WordPressData.package_json_example_content)
@patch("json.dump")
def test_replace_theme_meta_data_in_package_file_given_src_theme_then_replace_data_in_file_path(jsondump_mock,
                                                                                                fileopen_mock,
                                                                                                themesdata,
                                                                                                wordpressdata):
    """ Given src theme config, then open json file and replace data based on src theme """
    # Arrange
    theme_config = json.loads(themesdata.theme_single_src_with_metadata)
    expected_json_content = json.loads(wordpressdata.package_json_expected_content)
    file_path = wordpressdata.path
    # Act
    sut.replace_theme_meta_data_in_package_file(file_path, theme_config)
    # Assert
    jsondump_mock.assert_called_once_with(expected_json_content, ANY, indent=2)


# endregion replace_theme_meta_data_in_package_file()

# region replace_theme_meta_data_in_scss_file()


@patch("devops_toolset.project_types.wordpress.wp_theme_tools.replace_theme_meta_data")
def test_replace_theme_meta_data_in_scss_file_given_src_theme_then_replace_data_in_file_path(
        replace_theme_metadata_mock, themesdata, wordpressdata):
    """ Given src theme config, then open the style.scss file and replace data based on src theme """
    # Arrange
    theme_config = json.loads(themesdata.theme_single_src_with_metadata)
    file_path = wordpressdata.path
    replacements = json.loads(themesdata.replacements_on_scss_file)
    # Act
    sut.replace_theme_meta_data_in_scss_file(file_path, theme_config)
    # Assert
    replace_theme_metadata_mock.assert_called_once_with(file_path, replacements, ANY)


# endregion replace_theme_meta_data_in_scss_file()

# region replace_theme_slug_in_functions_php()


def test_replace_theme_slug_in_functions_php_given_src_theme_then_replace_data_in_core_functions_php(
        themesdata, wordpressdata):
    """ Given src theme config, then open the core/functions.php file and replaces data based on src theme """
    # Arrange
    theme_config = json.loads(themesdata.theme_single_src_with_metadata)
    theme_config["source"] = "mytheme_replaced"
    file_path = wordpressdata.path
    expected_content = themesdata.default_functions_core_php_example_expected
    # Act
    with patch(wordpressdata.builtins_open, new_callable=mock_open,
               read_data=themesdata.default_functions_core_php_example) as m:
        sut.replace_theme_slug_in_functions_php(file_path, theme_config)
        # Assert
        handler = m()
        handler.write.assert_called_once_with(expected_content)


# endregion replace_theme_slug_in_functions_php()

# region replace_theme_meta_data()


def test_replace_theme_meta_data_given_path_and_replacements_then_replaces_file_matches_with_regex(
        themesdata, wordpressdata):
    """ Given a path file and replacements dict, should iterate for the replacements and replace with regex """
    # Arrange
    file_path = wordpressdata.path
    replacements = json.loads(themesdata.replacements_on_scss_file)
    regex = wp_constants.Expressions.WORDPRESS_REGEX_THEME_METADATA_PARSE
    expected_content = themesdata.default_scss_file_expected
    # Act
    with patch(wordpressdata.builtins_open, new_callable=mock_open,
               read_data=themesdata.default_scss_file_example) as m:
        sut.replace_theme_meta_data(file_path, replacements, regex)
        # Assert
        handler = m()
        handler.write.assert_called_once_with(expected_content)


# endregion replace_theme_meta_data()

# region start_basic_theme_structure()


@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("pathlib.Path.exists")
@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_environment_by_type")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
def test_start_basic_theme_structure_given_structure_file_path_when_exists_then_gets_site_configuration(
        get_src_theme_mock, get_environment_mock, purge_gitkeep_mock, path_exists_mock,
        get_site_configuration_mock, logging_mock, wordpressdata, themesdata):
    """ Given structure file, when file exists, should call wptools.get_site_configuration """
    # Arrange
    destination_path = wordpressdata.path
    path_exists_mock.return_value = True
    site_config = json.loads(wordpressdata.site_config_content)
    themes_content = json.loads(themesdata.theme_single_src_with_metadata)
    get_src_theme_mock.return_value = themes_content
    site_config["environments"][0]["type"] = "production"
    site_config["settings"]["themes"] = [themes_content]
    get_environment_mock.return_value = site_config["environments"][0]
    structure_file_path = wordpressdata.project_structure_path
    # Act
    sut.scaffold_basic_theme_structure(destination_path, site_config, structure_file_path)
    # Assert
    get_site_configuration_mock.assert_called_once_with(str(structure_file_path))


@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_environment_by_type")
@patch("devops_toolset.project_types.wordpress.wptools.get_default_project_structure")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
@patch("pathlib.Path.exists")
@patch("devops_toolset.tools.git.purge_gitkeep")
def test_start_basic_theme_structure_given_structure_file_path_when_not_exists_then_gets_project_structure(
        purge_gitkeep_mock, path_exists_mock, get_src_theme_mock, get_project_structure_mock, logging_mock,
        get_environment_mock, wordpressdata, themesdata):
    """ Given structure file, when file exists, should call wptools.get_default_project_structure """
    # Arrange
    destination_path = wordpressdata.path
    site_config = json.loads(wordpressdata.site_config_content)
    theme_config = json.loads(themesdata.theme_single_src_with_metadata)
    get_src_theme_mock.return_value = theme_config
    site_config["environments"][0]["type"] = "production"
    site_config["settings"]["themes"] = [theme_config]
    path_exists_mock.return_value = False
    get_environment_mock.return_value = site_config["environments"][0]
    structure_file_path = wordpressdata.project_structure_path
    expected_replacement = {'mytheme': 'theme'}
    # Act
    sut.scaffold_basic_theme_structure(destination_path, site_config, structure_file_path)
    # Assert
    get_project_structure_mock.assert_called_once_with(wp_constants.ProjectStructureType.THEME, expected_replacement)

# endregion start_basic_theme_structure()

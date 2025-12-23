"""Unit core for the wordpress.wptools file"""
import os
import re
import stat
import pytest
import json
import pathlib
import devops_toolset.project_types.wordpress.basic_structure_starter
import devops_toolset.project_types.wordpress.wptools as sut
from devops_toolset.filesystem import paths
from devops_toolset.project_types.wordpress.basic_structure_starter import BasicStructureStarter
from devops_toolset.devops_platforms import constants as devops_platform_constants
import devops_toolset.project_types.wordpress.constants as wp_constants
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.wordpress.Literals import Literals as WordpressLiterals
from unittest.mock import patch, mock_open, call
from tests.project_types.wordpress.conftest import WordPressData, mocked_requests_get, \
    mocked_requests_get_json_content, PluginsData

literals = LiteralsCore([WordpressLiterals])
# TODO(alberto.carbonell) Refactor / split wptools.py in order to decrease the lines of this file (max allowed is 1000)
# region add_cloudfront_forwarded_proto_to_config


@patch("pathlib.Path.joinpath")
def test_add_cloudfront_forwarded_proto_returns_then_no_config_is_present(joinpath_mock, wordpressdata):
    """ Given environment_config, when no aws_cloudfront on it, then returns """
    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    config = {"settings": {"aws_cloudfront": False}}
    # Act
    sut.add_cloudfront_forwarded_proto_to_config(config, wordpress_path)
    # Assert
    joinpath_mock.assert_not_called()

@patch("pathlib.Path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="data")
def test_add_cloudfront_forwarded_proto_snippet_when_wpconfig_not_exists(
        builtins_open, path_exists_mock, wordpressdata):
    """Given path to wordpress installation, when wp-config.php not exists, then
    ends function."""
    # Arrange
    environment_config: dict = wordpressdata.environment_config_aws_cloudfront_true
    wordpress_path: str = wordpressdata.wordpress_path
    path_exists_mock.return_value = False
    # Act
    sut.add_cloudfront_forwarded_proto_to_config(environment_config, wordpress_path)
    # Assert
    builtins_open.assert_not_called()


@patch("pathlib.Path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="data")
@patch("re.search")
def test_add_cloudfront_forwarded_proto_snippet_when_wpconfig_exists_calls_re_search_with_pattern(
        search_mock, builtins_open, path_exists_mock, wordpressdata):
    """Given path to wordpress installation, when wp-config.php exists, then
    searches for specific pattern."""
    # Arrange
    environment_config: dict = wordpressdata.environment_config_aws_cloudfront_true
    wordpress_path: str = wordpressdata.wordpress_path
    path_exists_mock.return_value = True
    # Act
    sut.add_cloudfront_forwarded_proto_to_config(environment_config, wordpress_path)
    # Assert
    search_mock.assert_called_once_with(r'/\*\*.*\nrequire_once.*', "data")


@patch("pathlib.Path.exists")
@patch("re.search")
def test_add_cloudfront_forwarded_proto_snippet_when_no_match_pattern(
        search_mock, path_exists_mock, wordpressdata):
    """Given path to wordpress installation, when no match specific pattern in
     wp-config content ends function."""
    # Arrange
    environment_config: dict = wordpressdata.environment_config_aws_cloudfront_true
    wordpress_path: str = wordpressdata.wordpress_path
    path_exists_mock.return_value = True
    search_mock.return_value = None
    m = mock_open()
    # Act
    with patch(wordpressdata.builtins_open, m, create=True):
        sut.add_cloudfront_forwarded_proto_to_config(environment_config, wordpress_path)

        # Assert
        handler = m()
        handler.write.assert_not_called()


@patch("pathlib.Path.exists")
@patch("re.search")
@patch("re.sub")
def test_add_cloudfront_forwarded_proto_snippet_when_match_pattern(
        sub_mock, search_mock, path_exists_mock, tmp_path, wordpressdata):
    """Given path to wordpress installation, when match specific pattern in
     wp-config overwrites content with match substitution."""
    # Arrange
    environment_config: dict = wordpressdata.environment_config_aws_cloudfront_true
    wordpress_path: str = str(tmp_path)
    path_exists_mock.return_value = True
    sub_mock.return_value = "new content"
    search_mock.return_value = re.search("data", "data")
    expected_content = sub_mock.return_value
    m = mock_open()
    # Act
    with patch(wordpressdata.builtins_open, m, create=True):
        sut.add_cloudfront_forwarded_proto_to_config(environment_config, wordpress_path)
        # Assert
        handler = m()
        handler.write.assert_called_once_with(expected_content)

# endregion

# region add_wp_options


@patch("devops_toolset.project_types.wordpress.wp_cli.add_update_option")
def test_add_wp_options_given_options_then_calls_wp_cli_add_update_option(add_update_option_mock, wordpressdata):
    """ Given options dict, then calls wp_cli_add_update_option for every option """
    # Arrange
    options = json.loads(wordpressdata.site_config_content)["settings"]["options"]
    wordpress_path = wordpressdata.wordpress_path
    # Act
    sut.add_wp_options(options, wordpress_path)
    # Assert
    calls = []
    for option in options:
        calls.append(call(option, wordpress_path, False))
    add_update_option_mock.assert_has_calls(calls)


# endregion add_wp_options

# region check_wordpress_files_locale


@patch("devops_toolset.filesystem.tools.search_regex_in_text_file")
@patch("logging.warning")
def test_check_wordpress_files_locale_should_warn_when_locale_found_and_not_ok(logging_warning_mock,
                                                                               search_regex_mock, wordpressdata):
    """ Given locale, when found and not ok, when warns """
    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    locale_found = True
    locale = 'es_ES'
    locale_match = re.search(wp_constants.Expressions.WORDPRESS_REGEX_VERSION_LOCAL_PACKAGE,
                             wordpressdata.wp_locale_data)
    search_regex_mock.return_value = (locale_found, locale_match)
    # Act
    sut.check_wordpress_files_locale(wordpress_path, locale)
    # Assert
    logging_warning_mock.assert_called()


@patch("devops_toolset.filesystem.tools.search_regex_in_text_file")
@patch("logging.warning")
def test_check_wordpress_files_locale_should_warn_when_not_locale_found_and_not_default(logging_warning_mock,
                                                                                        search_regex_mock,
                                                                                        wordpressdata):
    """ Given locale, when found and not ok, when warns """
    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    locale_found = False
    locale = 'es_ES'
    locale_match = re.search(wp_constants.Expressions.WORDPRESS_REGEX_VERSION_LOCAL_PACKAGE, "")
    search_regex_mock.return_value = (locale_found, locale_match)
    # Act
    sut.check_wordpress_files_locale(wordpress_path, locale)
    # Assert
    logging_warning_mock.assert_called()

# endregion

# region check_wordpress_zip_file_format


@patch("os.path.basename")
@patch("logging.info")
def test_check_wordpress_zip_file_format_should_return_version_when_file_name_matches(logging_info_mock,
                                                                                       path_basename_mock,
                                                                                       wordpressdata):
    """ Given zip_file_path, when name matches regex, then returns True and version """
    # Arrange
    expected_version = "6.0.2"
    wrodpress_zip_file_name = f'wordpress-{expected_version}.zip'
    path_basename_mock.return_value = wrodpress_zip_file_name
    # Act
    found, version = sut.check_wordpress_zip_file_format(wrodpress_zip_file_name)
    # Assert
    assert found and version == expected_version


@patch("os.path.basename")
@patch("logging.error")
def test_check_wordpress_zip_file_format_should_return_none_when_file_name_matches(logging_error_mock,
                                                                                       path_basename_mock,
                                                                                       wordpressdata):
    """ Given zip_file_path, when name matches regex, then returns True and version """
    # Arrange
    expected_version = "6.0.2"
    wrodpress_zip_file_name = f'wordpress-incorrect_file-{expected_version}.zip'
    path_basename_mock.return_value = wrodpress_zip_file_name
    # Act
    found, version = sut.check_wordpress_zip_file_format(wrodpress_zip_file_name)
    # Assert
    assert not found and version is None


# endregion

# region convert_wp_config_token


def test_convert_wp_config_token_given_token_when_no_match_then_return_bare_token(wordpressdata):
    """Given token, when no matches, then returns bare token without changes"""
    # Arrange
    token = "no_matching_token"
    wordpress_path = wordpressdata.wordpress_path
    # Act
    result = sut.convert_wp_config_token(token, wordpress_path)
    # Assert
    assert result == token


@patch("devops_toolset.project_types.wordpress.wp_cli.eval_code")
def test_convert_wp_config_token_given_token_when_date_match_then_calls_wp_cli_eval_code(
        eval_code_mock, wordpressdata):
    """Given token, when match "date|", then parses and calls wp_cli.eval_code with necessary data"""
    # Arrange
    token = "some-data-[date|Y.m.d-Hisve]"
    date_formatted = "some-formatted-date"
    eval_code_mock.return_value = date_formatted
    expected_result = f"some-data-{date_formatted}"
    wordpress_path = wordpressdata.wordpress_path
    # Act
    result = sut.convert_wp_config_token(token, wordpress_path)
    # Assert
    assert result == expected_result

# endregion

# region create_wp_cli_bat_file()


def test_create_wp_cli_bat_file_given_phar_path_creates_bat_file_with_specific_content(tmp_path):
    """Given a .phar path, then creates a .bat file with specific content"""

    # Arrange
    phar_path = str(pathlib.Path.joinpath(tmp_path, "wp-cli.phar"))
    bat_path = str(pathlib.Path.joinpath(tmp_path, "wp.bat"))
    expected_content = f"@ECHO OFF\nphp \"{phar_path}\" %*"

    # Act
    sut.create_wp_cli_bat_file(phar_path)

    # Assert
    with open(bat_path, "r") as bat:
        file_content = bat.read()
    assert file_content == expected_content


# endregion

# region create_configuration_file()


@patch("devops_toolset.project_types.wordpress.wp_cli.create_configuration_file")
def test_create_configuration_file_then_calls_wp_cli_create_configuration_with_database_parameters(
        create_conf_file_mock, wordpressdata):
    """ Given database parameters, calls wp.cli.create_configuration_file """
    # Arrange
    environment_config = json.loads(wordpressdata.site_config_content)["environments"][0]
    wordpress_path = wordpressdata.wordpress_path
    database_user_pass = "my-password"
    # Act
    sut.create_configuration_file(environment_config, wordpress_path, database_user_pass)
    # Assert
    create_conf_file_mock.assert_called_once_with(
        wordpress_path=wordpress_path,
        db_host=environment_config["database"]["host"],
        db_name=environment_config["database"]["db_name"],
        db_user=environment_config["database"]["db_user"],
        db_pass=database_user_pass,
        db_prefix=environment_config["database"]["table_prefix"],
        db_charset=environment_config["database"]["charset"],
        db_collate=environment_config["database"]["collate"],
        skip_check=environment_config["database"]["skip_check"],
        debug=environment_config["wp_cli_debug"])


# endregion

# region create_users

@patch("devops_toolset.project_types.wordpress.wp_cli.create_user")
@patch("devops_toolset.project_types.wordpress.wp_cli.user_exists")
def test_create_users_when_user_does_not_exist_then_create_user(user_exists_mock, create_user_mock, wordpressdata):
    """ Given users data, when it not exist, then create it  """
    # Arrange
    user_exists_mock.return_value = False
    user = {"user_login": "test_user"}
    users = [user]
    wordpress_path = wordpressdata.wordpress_path
    debug = False
    # Act
    sut.create_users(users, wordpress_path, debug)
    # Assert
    create_user_mock.assert_called_with(user, wordpress_path, debug)


@patch("logging.warning")
@patch("devops_toolset.project_types.wordpress.wp_cli.user_exists")
def test_create_users_when_user_does_exist_then_warns(user_exists_mock, logging_warning_mock, wordpressdata):
    """ Given users data, when it not exist, then create it  """
    # Arrange
    user_exists_mock.return_value = True
    wordpress_path = wordpressdata.wordpress_path
    user = {"user_login": "test_user"}
    users = [user]
    debug = False
    # Act
    sut.create_users(users, wordpress_path, debug)
    # Assert
    logging_warning_mock.assert_called()

# endregion create_users

# region download_wordpress()


@patch("devops_toolset.project_types.wordpress.wp_cli.download_wordpress")
def test_download_wordpress_given_invalid_path_raises_valueerror(download_wordpress_mock, wordpressdata):
    """Given an invalid path, raises ValueError"""

    # Arrange
    site_configuration = json.loads(wordpressdata.site_config_content)
    path = wordpressdata.wordpress_path_err

    # Act
    with pytest.raises(ValueError):
        # Assert
        sut.download_wordpress(site_configuration, path)


@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wp_cli.download_wordpress")
def test_download_wordpress_given_valid_arguments_calls_subprocess(
        download_wordpress_mock, purge_gitkeep, wordpressdata):
    """Given valid arguments, calls subprocess"""

    # Arrange
    site_configuration = json.loads(wordpressdata.site_config_content)
    path = wordpressdata.wordpress_path

    # Act
    sut.download_wordpress(site_configuration, path)

    # Assert
    download_wordpress_mock.assert_called_once()
    purge_gitkeep.assert_called_once()


# endregion

# region export_database()

@patch("devops_toolset.project_types.wordpress.wp_cli.export_database")
def test_export_database_calls_wp_cli_export_database(export_database_mock, wordpressdata):
    """Given site configuration, should call wp_cli.export_database"""
    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    dump_file_path = wordpressdata.dump_file_path
    # Act
    sut.export_database(environment_config, wordpress_path, dump_file_path)
    # Assert
    export_database_mock.assert_called_once_with(wordpress_path, dump_file_path, environment_config["wp_cli_debug"])

# endregion

# region get_constants()


@patch("builtins.open", new_callable=mock_open, read_data=WordPressData.empty_dict)
def test_get_constants_reads_file(open_file_mock):
    """Reads the constants file and returns dict"""
    # Act
    result = sut.get_constants()
    # Assert
    open_file_mock.assert_called_once()
    assert type(result) is dict

# endregion

# region get_environment()


def test_get_environment_given_env_name_when_not_match_then_raises_value_error(wordpressdata):
    """ Given environment name, when no matches found in site_config, then raises ValueError """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_name = "non_existing_environment"
    expected_error_message = literals.get('wp_env_x_not_found').format(environment=environment_name)
    # Act
    with pytest.raises(ValueError) as value_error:
        sut.get_environment(site_config, environment_name)
        # Assert
        assert value_error == expected_error_message


@patch("devops_toolset.tools.dicts.filter_keys")
@patch("logging.warning")
def test_get_environment_given_env_name_when_multiple_match_then_warns(log_warning_mock, filter_keys_mock,
                                                                       wordpressdata):
    """ Given environment name, when multiples matches found in site_config, then warns with message"""
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment = site_config["environments"][0]
    environment_name = environment["name"]
    site_config["environments"].append(environment)
    expected_message = literals.get('wp_environment_x_found_multiple').format(environment=environment_name)
    filter_keys_mock.return_value = []
    # Act
    sut.get_environment(site_config, environment_name)
    # Assert
    log_warning_mock.assert_called_once_with(expected_message)


@patch("devops_toolset.tools.dicts.filter_keys")
def test_get_environment_given_site_config_then_update_url_constants(filter_keys_mock, wordpressdata):
    """ Given site_config, then updates url constants """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    url_keys = ["content_url"]
    environment = site_config["environments"][0]
    environment_name = environment["name"]
    filter_keys_mock.return_value = url_keys
    expected_content_url_value = environment["base_url"] + environment["wp_config"][url_keys[0]]["value"]
    # Act
    result = sut.get_environment(site_config, environment_name)
    # Assert
    assert result["wp_config"]["content_url"]["value"] == expected_content_url_value

# endregion get_environment()

# region get_default_project_structure()


def test_get_project_structure_given_resource_reads_and_parses_content(wordpressdata, mocks):
    """Given a path, reads the file obtained from the resource and parses the JSON content."""
    # Arrange
    mocks.requests_get_mock.side_effect = mocked_requests_get_json_content
    # Act
    result = sut.get_default_project_structure(wp_constants.ProjectStructureType.WORDPRESS)
    # Assert
    assert result is not None


# endregion

# region get_required_file_paths()


@patch("devops_toolset.filesystem.paths.get_file_path_from_pattern")
def test_get_required_file_paths(get_file_path_from_pattern, wordpressdata):
    """Given, when, then"""
    # Arrange
    path = wordpressdata.path
    required_file_patterns = ["*site.json"]
    get_file_path_from_pattern.return_value = wordpressdata.site_config_path
    # Act
    result = sut.get_required_file_paths(path, required_file_patterns)
    # Assert
    assert result == (wordpressdata.site_config_path,)

# endregion

# region get_site_configuration()


@patch("builtins.open", new_callable=mock_open, read_data=WordPressData.site_config_content)
def test_get_site_configuration_reads_json(builtins_open, wordpressdata):
    """Given a JSON file path, returns dict with JSON content"""
    # Arrange
    path = wordpressdata.site_config_path
    # Act
    result = sut.get_site_configuration(path)
    # Assert
    assert result == json.loads(wordpressdata.site_config_content)

# endregion

# region get_snippet_cloudfront


@patch("logging.error")
@patch("pathlib.Path.exists")
def test_get_snippet_cloudfront_default_snippet_cloudfront_file_not_exists(path_exists_mock, logging_mock):
    """When default_snippet_cloudfront file not exits logs error."""
    # Arrange
    path_exists_mock.return_value = False
    # Act
    sut.get_snippet_cloudfront()
    # Assert
    logging_mock.assert_called_once()

@patch("builtins.open", new_callable=mock_open, read_data="data")
@patch("pathlib.Path.exists")
def test_get_snippet_cloudfront_default_snippet_cloudfront_file_exists(path_exists_mock, builtins_open):
    """When default_snippet_cloudfront file exits returns its content."""
    # Arrange
    path_exists_mock.return_value = True
    # Act
    result = sut.get_snippet_cloudfront()
    # Assert
    assert result == "data"

# endregion

# region get_wordpress_path_from_root_path


@patch("logging.info")
def test_get_wordpress_path_from_root_path_from_constants(logging_info_mock, wordpressdata):
    """ Given root path and consts, then gets the WordPress path"""
    # Arrange
    root_path = wordpressdata.root_path
    constants = json.loads(wordpressdata.constants_file_content)
    wordpress_relative_path = constants["paths"]["wordpress"]
    expected_wordpress_path = pathlib.Path.joinpath(pathlib.Path(root_path), wordpress_relative_path).as_posix()
    # Act
    wordpress_path = sut.get_wordpress_path_from_root_path(root_path, constants)
    # Assert
    assert expected_wordpress_path == wordpress_path


@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
def test_get_wordpress_path_from_root_path_from_default_constants(get_constants_mock, logging_info_mock, wordpressdata):
    """ Given root path and consts, then gets the WordPress path from default constants"""
    # Arrange
    root_path = wordpressdata.root_path
    constants = json.loads(wordpressdata.constants_file_content)
    get_constants_mock.return_value = constants
    wordpress_relative_path = constants["paths"]["wordpress"]
    expected_wordpress_path = pathlib.Path.joinpath(pathlib.Path(root_path), wordpress_relative_path).as_posix()
    # Act
    wordpress_path = sut.get_wordpress_path_from_root_path(root_path)
    # Assert
    assert expected_wordpress_path == wordpress_path
# endregion

# region import_content_from_configuration_file()


@patch("devops_toolset.project_types.wordpress.wp_cli.import_wxr_content")
@patch("devops_toolset.project_types.wordpress.wp_cli.delete_post_type_content")
def test_import_content_from_configuration_file_given_args_then_call_delete_post_type_content(delete_content_mock,
                                                                                              import_wxr_content,
                                                                                              wordpressdata):
    """ Given args, for every content type present, should call delete_post_type_content with required data """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    wordpress_path = pathlib.Path.joinpath(pathlib.Path(root_path), constants["paths"]["wordpress"])
    expected_content_imported = ["page", "nav_menu_item"]
    site_config["content"] = json.loads(wordpressdata.import_content_skip_author)
    # Act
    sut.import_content_from_configuration_file(site_config, environment_config, root_path, constants)
    expected_calls = [call(str(wordpress_path), expected_content_imported[0], False),
                      call(str(wordpress_path), expected_content_imported[1], False)]
    # Assert
    delete_content_mock.assert_has_calls(expected_calls)


@patch("devops_toolset.project_types.wordpress.wp_cli.import_wxr_content")
@patch("devops_toolset.project_types.wordpress.wp_cli.delete_post_type_content")
@pytest.mark.parametrize("authors_value", ["create", "skip", "mapping.csv"])
def test_import_content_from_configuration_file_given_args_then_call_import_wxr_content(delete_content_mock,
                                                                                        import_wxr_content,
                                                                                        authors_value, wordpressdata):
    """ Given args, for every content type present, should call delete_post_type_content with required data """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    wordpress_path = pathlib.Path.joinpath(pathlib.Path(root_path), constants["paths"]["wordpress"])
    wxr_path = pathlib.Path.joinpath(pathlib.Path(root_path), constants["paths"]["content"]["wxr"])
    expected_content_imported = ["page", "nav_menu_item"]
    site_config["content"] = json.loads(wordpressdata.import_content_skip_author)
    site_config["authors_handling"] = authors_value
    # Act
    sut.import_content_from_configuration_file(site_config, environment_config, root_path, constants)
    expected_calls = []
    for content_type in expected_content_imported:
        content_path = pathlib.Path.joinpath(wxr_path, f"{content_type}.xml")
        expected_calls.append(call(str(wordpress_path), str(content_path), "skip", environment_config["wp_cli_debug"]))
    # Assert
    import_wxr_content.assert_has_calls(expected_calls)


@patch("devops_toolset.project_types.wordpress.wp_cli.import_wxr_content")
def test_import_content_from_configuration_file_given_args_when_no_content_then_return_without_import(
        import_wxr_content, wordpressdata):
    """ Given args, when no content present, then return without importing anything """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    site_config.pop("content", None)
    environment_config = {}
    root_path = wordpressdata.root_path
    constants = {}
    # Act
    sut.import_content_from_configuration_file(site_config, environment_config, root_path, constants)
    # Assert
    import_wxr_content.assert_not_called()


@patch("devops_toolset.project_types.wordpress.wp_cli.import_wxr_content")
def test_import_content_from_configuration_file_given_args_when_empty_content_then_no_import(
        import_wxr_content, wordpressdata):
    """ Given args, when no content present, then return without importing anything """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["content"] = {}
    site_config["content"]["author_handling"] = {}
    site_config["content"]["sources"] = {}
    environment_config = site_config["environments"][0]
    root_path = wordpressdata.root_path
    constants = json.loads(wordpressdata.constants_file_content)
    # Act
    sut.import_content_from_configuration_file(site_config, environment_config, root_path, constants)
    # Assert
    import_wxr_content.assert_not_called()

# endregion import_content_from_configuration_file

# region install_plugins_from_configuration_file()


@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wp_cli.install_plugin")
@patch("logging.warning")
def test_install_plugins_given_configuration_file_when_no_plugins_then_no_install(
        logging_warning_mock, install_plugin_mock, purge_gitkeep_mock, wordpressdata):
    """ Given the configuration values, when no plugins present, then no installation calls
     should be made """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["settings"]["plugins"] = {}
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    # Act
    sut.install_plugins_from_configuration_file(site_config, environment_config, constants, root_path, True, True)
    # Assert
    install_plugin_mock.assert_not_called()


@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("logging.warning")
@patch("logging.info")
@patch("devops_toolset.project_types.wordpress.wp_cli.install_plugin")
@patch("devops_toolset.project_types.wordpress.wptools.download_wordpress_plugin")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@pytest.mark.parametrize(
    "plugins_content", [json.loads(PluginsData.plugins_content_single_url_source),
                        json.loads(PluginsData.plugins_content_single_zip_source),
                        json.loads(PluginsData.plugins_content_two_plugins_with_url_and_zip_sources)])
def test_install_plugins_given_configuration_file_when_plugins_present_then_install_plugins(
        export_mock, convert_token_mock, download_wordpress_plugin_mock, install_plugin_mock,
        logging_mock, logging_warn_mock, purge_gitkeep_mock, plugins_content, wordpressdata, pluginsdata):
    """ Given the configuration values, when url plugin present, then calls download_wordpress_plugin"""
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    site_config["settings"]["plugins"] = plugins_content
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = pathlib.Path(wordpressdata.root_path)
    wordpress_path = pathlib.Path.joinpath(root_path, constants["paths"]["wordpress"])
    plugins_path = pathlib.Path.joinpath(root_path, constants["paths"]["content"]["plugins"])
    # Act
    sut.install_plugins_from_configuration_file(site_config, environment_config, constants, str(root_path), True, True)
    # Assert
    calls = []
    for plugin in site_config["settings"]["plugins"]:
        plugin_path = paths.get_file_path_from_pattern(str(plugins_path), f"{plugin['name']}*.zip")
        plugin_call = call(plugin["name"],
                           str(wordpress_path),
                           plugin["activate"],
                           plugin["force"],
                           plugin_path,
                           environment_config["wp_cli_debug"])
        calls.append(plugin_call)
    install_plugin_mock.assert_has_calls(calls)


# endregion

# region install_wp_cli()


@patch("pathlib.Path")
def test_install_wp_cli_given_path_when_not_dir_then_raise_value_error(pathlib_mock, wordpressdata):
    """Given a file path, raises ValueError when install_path is not a dir."""
    # Arrange
    install_path = wordpressdata.wp_cli_install_path
    pathlib_mock.return_value = install_path
    expected_exception_message = literals.get("wp_not_dir")
    with patch.object(pathlib.Path, "is_dir", return_value=False):
        # Act
        with pytest.raises(ValueError) as exceptionInfo:
            sut.install_wp_cli(install_path)
        # Assert
        assert expected_exception_message == str(exceptionInfo.value)


@patch("pathlib.Path")
@patch("devops_toolset.project_types.wordpress.wptools.create_wp_cli_bat_file")
@patch("devops_toolset.project_types.wordpress.wp_cli.wp_cli_info")
@patch("logging.info")
def test_install_wp_cli_given_path_when_is_dir_then_downloads_from_request_resource(
        log_info_mock, wp_cli_info, create_wp_cli_bat_file, pathlib_mock, wordpressdata, mocks):
    """ Given a file path, when path is a dir, then downloads from download url """
    # Arrange
    install_path = wordpressdata.wp_cli_install_path
    pathlib_mock.return_value = install_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    wp_cli_phar = "wp-cli.phar"
    wp_cli_download_url = f"https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/{wp_cli_phar}"
    with patch(wordpressdata.builtins_open, mock_open()):
        with patch.object(os, "stat"):
            with patch.object(os, "chmod"):
                # Act
                sut.install_wp_cli(install_path)
                # Assert
                calls = [call(wp_cli_download_url)]
                mocks.requests_get_mock.assert_has_calls(calls, any_order=True)


@patch("pathlib.Path")
@patch("devops_toolset.project_types.wordpress.wptools.create_wp_cli_bat_file")
@patch("devops_toolset.project_types.wordpress.wp_cli.wp_cli_info")
@patch("logging.info")
def test_install_wp_cli_given_path_when_is_dir_then_writes_response_content(
        log_info_mock, wp_cli_info, create_wp_cli_bat_file, pathlib_mock, wordpressdata, mocks):
    """ Given a file path, when path is a dir, then writes response content to
    file_path """
    # Arrange
    install_path = wordpressdata.wp_cli_install_path
    pathlib_mock.return_value = install_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    expected_content = b"sample response in bytes"
    m = mock_open()
    with patch(wordpressdata.builtins_open, m, create=True):
        with patch.object(os, "stat"):
            with patch.object(os, "chmod"):
                # Act
                sut.install_wp_cli(install_path)
                # Assert
                handler = m()
                handler.write.assert_called_once_with(expected_content)


@patch("devops_toolset.project_types.wordpress.wp_cli.wp_cli_info")
def test_install_wp_cli_given_path_when_is_dir_then_chmods_written_file_path(wp_cli_info, wordpressdata, mocks):
    """ Given a file path, when path is a dir, then does chmod with S_IEXEC """
    # Arrange
    install_path = wordpressdata.wp_cli_install_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    with patch.object(pathlib.Path, "is_dir", return_value=True):
        with patch(wordpressdata.builtins_open, mock_open()):
            with patch.object(os, "stat") as file_stat_mock:
                file_stat_mock.return_value = os.stat(install_path)
                with patch.object(os, "chmod") as chmod_mock:
                    # Act
                    sut.install_wp_cli(install_path)
                    # Assert
                    chmod_mock.assert_called_once_with(str(wordpressdata.wp_cli_file_path),
                                                       file_stat_mock.return_value.st_mode | stat.S_IEXEC)


@patch("devops_toolset.project_types.wordpress.wp_cli.wp_cli_info")
def test_install_wp_cli_given_path_when_is_dir_then_calls_subprocess_wpcli_info_command(
        wp_cli_info, wordpressdata, mocks):
    """ Given a file path, when path is a dir, then calls wp_cli_info() from wp_cli module """
    # Arrange
    install_path = wordpressdata.wp_cli_install_path
    mocks.requests_get_mock.side_effect = mocked_requests_get
    with patch.object(pathlib.Path, "is_dir", return_value=True):
        with patch(wordpressdata.builtins_open, mock_open()):
            with patch.object(os, "stat") as file_stat_mock:
                file_stat_mock.return_value = os.stat(install_path)
                with patch.object(os, "chmod"):
                    # Act
                    sut.install_wp_cli(install_path)
                    # Assert
                    wp_cli_info.assert_called_once()

# endregion

# region install_wordpress_core()


@patch("devops_toolset.project_types.wordpress.wp_cli.install_wordpress_core")
def test_install_wordpress_core_then_calls_cli_install_wordpress_core(install_wordpress_mock, wordpressdata):
    """ Given configuration file, then calls install_wordpress_core from cli """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    wordpress_path = wordpressdata.wordpress_path
    admin_pass = "root"
    # Act
    sut.install_wordpress_core(site_config, environment_config, wordpress_path, admin_pass)
    # Assert
    install_wordpress_mock.assert_called_once()

# endregion

# region install_wordpress_site()

@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wp_cli.reset_database")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_core")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("pathlib.Path.as_posix")
def test_install_wordpress_site_then_calls_install_wordpress_core(
        path_mock, convert_wp_config_token, export_database, install_wordpress_core,
        update_database, reset_database_mock, get_constants_mock, purge_gitkeep_mock, wordpressdata):
    """ Given site_configuration, then calls install_wordpress_core """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    path_mock.return_value = root_path
    admin_pass = "root"
    # Act
    sut.install_wordpress_site(site_config, environment_config, constants, root_path, admin_pass)
    # Assert
    install_wordpress_core.assert_called_with(site_config, environment_config, root_path, admin_pass)


@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wp_cli.reset_database")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_core")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("pathlib.Path.as_posix")
def test_install_wordpress_site_then_calls_cli_update_option(
        path_mock, convert_wp_config_token, export_database, install_wordpress_core,
        update_database, reset_database_mock, get_constants_mock, purge_gitkeep_mock, wordpressdata):
    """ Given site_configuration, then calls cli's update database  option """
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    path_mock.return_value = str(root_path)
    admin_pass = "root"
    # Act
    sut.install_wordpress_site(site_config, environment_config, constants, root_path, admin_pass)
    # Assert
    update_database.assert_called_with("blogdescription", site_config["settings"]["description"],
                                       root_path, environment_config["wp_cli_debug"])


@patch("devops_toolset.tools.git.purge_gitkeep")
@patch("devops_toolset.project_types.wordpress.wptools.get_constants")
@patch("devops_toolset.project_types.wordpress.wp_cli.reset_database")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wptools.install_wordpress_core")
@patch("devops_toolset.project_types.wordpress.wptools.export_database")
@patch("devops_toolset.project_types.wordpress.wptools.convert_wp_config_token")
@patch("pathlib.Path.as_posix")
def test_install_wordpress_site_then_calls_cli_export_database(
        path_mock, convert_wp_config_token, export_database, install_wordpress_core,
        update_database, reset_database_mock, get_constants_mock, purge_gitkeep_mock, wordpressdata):
    """ Given site_configuration, then calls cli's export_database"""
    # Arrange
    site_config = json.loads(wordpressdata.site_config_content)
    environment_config = site_config["environments"][0]
    constants = json.loads(wordpressdata.constants_file_content)
    root_path = wordpressdata.root_path
    path_mock.return_value = root_path
    admin_pass = "root"
    # Act
    sut.install_wordpress_site(site_config, environment_config, constants, root_path, admin_pass)
    # Assert
    export_database.assert_called_with(environment_config, root_path, root_path)

# endregion

# region scaffold_wordpress_basic_project_structure


@patch("devops_toolset.project_types.wordpress.wptools.get_default_project_structure")
@patch("logging.info")
@patch("logging.warning")
@patch("pathlib.Path.exists")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
def test_scaffold_wordpress_given_parameters_when_path_not_exists_must_call_get_default_project_structure(
        get_src_theme_mock, path_exists_mock, logging_warn_mock, logging_info_mock,
        get_project_structure_mock, wordpressdata):
    """Given arguments, must call get_default_project_structure with passed project_path"""
    # Arrange
    expected_default_project_structure = wp_constants.ProjectStructureType.WORDPRESS
    path_exists_mock.return_value = False
    site_config = json.loads(wordpressdata.site_config_content)
    root_path = wordpressdata.wordpress_path
    get_project_structure_mock.return_value = {"items": {}}
    # Act
    sut.scaffold_wordpress_basic_project_structure(root_path, site_config)
    # Assert
    get_project_structure_mock.assert_called_once_with(expected_default_project_structure)


@patch("logging.info")
@patch("logging.warning")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.joinpath")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
def test_scaffold_wordpress_given_parameters_when_path_exists_must_call_get_site_configuration(
        get_src_theme_mock, path_joinpath_mock, path_exists_mock, get_site_configuration_mock, logging_warn_mock,
        logging_info_mock, wordpressdata):
    """Given arguments, must call get_default_project_structure with passed project_path"""
    # Arrange
    path_joinpath_mock.return_value = wordpressdata.project_structure_path
    path_exists_mock.return_value = True
    site_config = json.loads(wordpressdata.site_config_content)
    root_path = wordpressdata.wordpress_path
    # Act
    sut.scaffold_wordpress_basic_project_structure(root_path, site_config)
    # Assert
    get_site_configuration_mock.assert_called_once_with(wordpressdata.project_structure_path)


@patch("logging.info")
@patch("logging.warning")
@patch("devops_toolset.project_types.wordpress.wptools.get_site_configuration")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.joinpath")
@patch("devops_toolset.project_types.wordpress.wp_theme_tools.get_src_theme")
def test_scaffold_wordpress_given_parameters_when_path_exists_must_add_items(
        get_src_theme_mock, path_joinpath_mock, path_exists_mock, get_site_configuration_mock,
        logging_warn_mock, logging_info_mock, wordpressdata):
    """Given arguments, must call get_default_project_structure with passed project_path"""
    # Arrange
    items: dict = {'items': [{'item1': 'value1'}]}
    path_joinpath_mock.return_value = wordpressdata.project_structure_path
    path_exists_mock.return_value = True
    site_config = json.loads(wordpressdata.site_config_content)
    get_site_configuration_mock.return_value = items
    root_path = wordpressdata.wordpress_path
    # Act
    with patch.object(devops_toolset.project_types.wordpress.basic_structure_starter.BasicStructureStarter,
                      "add_item") as add_item_mock:
        sut.scaffold_wordpress_basic_project_structure(root_path, site_config)
        # Assert
        add_item_mock.assert_called_once_with(items["items"][0], root_path)

# endregion scaffold_wordpress_basic_project_structure

# region set_wordpress_config_from_configuration_file


@patch("devops_toolset.project_types.wordpress.wptools.add_cloudfront_forwarded_proto_to_config")
@patch("devops_toolset.project_types.wordpress.wptools.create_configuration_file")
@patch("devops_toolset.project_types.wordpress.wp_cli.set_configuration_value")
@pytest.mark.parametrize("aws_cloudfront", [True, False])
def test_set_wordpress_config_from_configuration_file(set_configuration_value_mock, create_configuration_file_mock,
                                                      add_cloudfront_mock, wordpressdata, aws_cloudfront):
    """Given site_configuration, then calls
    add_cloudfront_forwarded_proto_to_config."""
    # Arrange
    environment_config = wordpressdata.environment_config_aws_cloudfront_true \
        if aws_cloudfront else wordpressdata.environment_config_aws_cloudfront_false
    wordpress_path = wordpressdata.wordpress_path
    database_user_pass = "my-password"
    # Act
    sut.set_wordpress_config_from_configuration_file(
        environment_config, wordpress_path, database_user_pass)
    # Assert
    add_cloudfront_mock.assert_called_once()

# endregion set_wordpress_config_from_configuration_file

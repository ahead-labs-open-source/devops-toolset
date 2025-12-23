"""Test configuration file for wordpress module.

Add here whatever you want to pass as a fixture in your texts."""
import pathlib
import pytest


class PluginsData:
    """Class used to create the pluginsdata fixture"""
    plugins_content_single_url_source = \
        "[{\"name\":\"plugin-name\",\"source_type\":\"url\",\"source\":\"https://plugin1.zip\",\"force\":true," \
        "\"activate\":true}]"
    plugins_content_single_zip_source = \
        "[{\"name\":\"plugin-name\",\"source_type\":\"zip\",\"source\":\"plugin1.zip\",\"force\":true," \
        "\"activate\":true}]"
    plugins_content_two_plugins_with_url_and_zip_sources = \
        "[{\"name\":\"plugin-name1\",\"source_type\":\"url\",\"source\":\"https://plugin1.zip\",\"force\":true," \
        "\"activate\":true},{\"name\":\"plugin-name2\",\"source_type\":\"zip\",\"source\":\"plugin1.zip\"," \
        "\"force\":true,\"activate\":true}]"
    commit_message = "Test commit message"
    tag_name = "v1.0"
    username = "username"
    password = "password"
    plugin_root_path = "/non/existent/path"
    plugin_config = "{\"$schema\":\"http://dev.aheadlabs.com/schemas/json/wordpress-plugin-config-schema.json\"," \
                    "\"name\":\"Plugin Name\",\"slug\":\"plugin-name\"," \
                    "\"uri\":\"https://github.com/my-repository/plugin-name/\"," \
                    "\"description\":\"Plugin description\"," \
                    "\"version\":\"0.1.0\",\"author\":\"Plugin owner's name\",\"author_uri\":\"Plugin owner's uri\"," \
                    "\"license\":\"GPL2\",\"license_uri\":\"https://www.gnu.org/licenses/gpl-2.0.html\"," \
                    "\"contributors\":[\"contributor 1\",\"contributor 2\"]," \
                    "\"donate_link\":\"https://paypal.me/my-donate-link\"," \
                    "\"tags\":[\"tag 1\",\"tag 2\"],\"requires_at_least\":\"6.0\",\"tested_up_to\":\"6.0\"," \
                    "\"stable_tag\":\"0.1.0\",\"requires_php\":\"5.2.4\"}"
    empty_plugin_structure = "{\"items\":[]}"
    plugin_structure = "{\"$schema\":\"http://dev.aheadlabs.com/schemas/json/project-structure-schema.json\"," \
                       "\"items\":[{\"name\":\".devops\",\"type\":\"directory\",\"children\":[{\"name\":\".gitkeep\"," \
                       "\"type\":\"file\",\"condition\":\"when-parent-not-empty\"}]},{\"name\":\"assets\"," \
                       "\"type\":\"directory\",\"children\":[{\"name\":\".gitkeep\",\"type\":\"file\"," \
                       "\"condition\":\"when-parent-not-empty\"}]},{\"name\":\"src\",\"type\":\"directory\"," \
                       "\"children\":[{\"name\":\"[plugin-name]\",\"type\":\"directory\"," \
                       "\"children\":[{\"name\":\"[plugin-name].php\",\"type\":\"file\"," \
                       "\"default_content\":{\"source\":\"from_url\"," \
                       "\"value\":\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/src/" \
                       "devops_toolset/project_types/wordpress/default-files/default-plugin-code.php\"}}]}," \
                       "{\"name\":\"readme.txt\",\"type\":\"file\",\"default_content\":{\"source\":\"from_url\"," \
                       "\"value\":\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/src/" \
                       "devops_toolset/project_types/wordpress/default-files/default-plugin-readme.txt\"}}]}," \
                       "{\"name\":\".gitignore\",\"type\":\"file\",\"default_content\":{\"source\":\"from_url\"," \
                       "\"value\":\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/src/" \
                       "devops_toolset/project_types/wordpress/default-files/default-plugin.gitignore\"}}," \
                       "{\"name\":\"LICENSE\",\"type\":\"file\",\"default_content\":{\"source\":\"from_url\"," \
                       "\"value\":\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/src/" \
                       "devops_toolset/project_types/wordpress/default-files/default-plugin-LICENSE\"}}," \
                       "{\"name\":\"README.md\",\"type\":\"file\",\"default_content\":{\"source\":\"from_url\"," \
                       "\"value\":\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/src/" \
                       "devops_toolset/project_types/wordpress/default-files/default-plugin-README.md\"}}]}"


class ThemesData:
    """Class used to create the themesdata fixture"""
    default_scss_file_example = "/*!\nTheme Name: MyTheme WordPress theme\nTheme URI: https://example.com/\n" \
                                "Description: Ad hoc WordPres theme.\nAuthor: Ahead Labs, S.L.\nAuthor URI: " \
                                "https://aheadlabs.com\nTags: ahead-labs, theme\nVersion: {{version}}\n" \
                                "Requires at least: 5.6\nTested up to: 5.6\nRequires PHP: 7.4.11\n" \
                                "License: Copyright\nText Domain: mytheme\nTemplate: w74-framework\n*/"
    default_scss_file_expected = "/*!\nTheme Name: theme\nTheme URI: https://mytheme\n" \
                                "Description: mytheme-description\nAuthor: theme-author\nAuthor URI: " \
                                "https://example.com\nTags: tag1, tag2\nVersion: {{version}}\n" \
                                "Requires at least: 5.6\nTested up to: 5.6\nRequires PHP: 7.4.11\nLicense: Copyright\n" \
                                "Text Domain: mytheme\nTemplate: w74-framework\n*/"
    default_functions_core_php_example = "function mytheme_register_styles()\n{\n\n}\nadd_action('wp_enqueue_scripts', " \
                                         "'mytheme_register_styles')"
    default_functions_core_php_example_expected = "function mytheme_replaced_register_styles()\n{\n\n}\n" \
                                                  "add_action('wp_enqueue_scripts', 'mytheme_replaced_register_styles')"
    replacements_on_scss_file = "{\"Theme Name\":\"theme\", \"Text Domain\":\"mytheme\", " \
                                "\"Description\":\"mytheme-description\", \"Theme URI\":\"https://mytheme\"," \
                                "\"Author\":\"theme-author\", \"Author URI\":\"https://example.com\", " \
                                "\"Tags\": \"tag1, tag2\"}"
    themes_content_with_three_themes_no_activate = \
        "[{\"name\":\"theme1\",\"source_type\":\"zip\",\"source\":\"source1.zip\"}," \
        "{\"name\":\"theme2\",\"source_type\":\"zip\",\"source\":\"source2.zip\"}," \
        "{\"name\":\"theme3\",\"source_type\":\"zip\",\"source\":\"source3.zip\"}]"
    themes_content_with_two_themes_none_activated = \
        "[{\"name\":\"theme1\",\"source_type\":\"zip\",\"activate\":false,\"source\":\"source1.zip\"}," \
        "{\"name\":\"theme2\",\"source_type\":\"zip\",\"activate\":false,\"source\":\"source2.zip\"}]"
    themes_content_with_two_activated_themes = \
        "[{\"name\":\"theme1\",\"source_type\":\"zip\",\"activate\":true,\"source\":\"source1.zip\"}," \
        "{\"name\":\"theme2\",\"source_type\":\"zip\",\"activate\":true,\"source\":\"source2.zip\"}]"
    themes_content_with_two_themes_one_activated = \
        "[{\"name\":\"theme1\",\"source_type\":\"zip\",\"activate\":false,\"source\":\"source1.zip\"}," \
        "{\"name\":\"theme2\",\"source_type\":\"zip\",\"activate\":true,\"source\":\"source2.zip\"}]"
    theme_single_content_with_wrong_feed = \
        "{\"name\":\"theme\",\"source_type\":\"feed\",\"activate\":true,\"source\":\"source1.zip\"}"
    theme_single_content_with_correct_feed = \
        "{\"name\":\"theme\",\"source_type\":\"feed\",\"activate\":true,\"source\":\"source1.zip\"," \
        "\"feed\": {\"name\": \"testfeed\", \"organization_url\": \"https://dev.azure.com/organization/\"," \
        " \"package\": \"testpackage\", \"version\": \"1.0\"}}"
    theme_single_content_with_url = \
        "{\"name\":\"theme\",\"source_type\":\"url\",\"activate\":true,\"source\":\"http://theme.zip\"}"
    theme_single_src = "[{\"name\":\"theme\",\"build\":true,\"source_type\":\"src\",\"source\":\"mytheme\"}]"
    theme_single_src_with_metadata = "{\"name\":\"theme\",\"source_type\":\"src\",\"build\":true," \
                                     "\"source\":\"mytheme\",\"description\":\"mytheme-description\"," \
                                     "\"url\":\"https://mytheme\"," \
                                     "\"uri\":\"https://mytheme\"," \
                                     "\"minimum-wordpress-version\":\"1.0\"," \
                                     "\"minimum-wordpress-version-tested\":\"2.0\"," \
                                     "\"minimum-php-version\":\"7.0\"," \
                                     "\"version\":\"1.0.0\"," \
                                     "\"author\":\"theme-author\",\"author_uri\":\"https://example.com\"," \
                                     "\"tags\":[\"tag1\",\"tag2\"]}"
    theme_single_no_src = "[{\"name\":\"theme\",\"source_type\":\"zip\",\"source\":\"source1.zip\", " \
                          "\"build\":\"false\"}]"
    child_name = "child_theme"
    child_url_source = "path-to-source1.zip"
    themes_content_with_child_activated = \
        "[{\"name\":\"child_theme\",\"source_type\":\"url\",\"activate\":true,\"source\":\"path-to-source1.zip\"}]"


class WordPressData:
    """Class used to create the wordpressdata fixture"""
    root_path = "pathto/project"
    devops_toolset_wordpress_path = "/pathto/devops-toolset/wordpress"
    environment_path = "/pathto/environment"
    project_structure_path = "/pathto/structure"
    theme_path = "/content/themes"
    wordpress_path = "/pathto/wordpress"
    wordpress_path_part = "/wordpress"
    wordpress_path_err = "/nonexistentpath"
    empty_dict = "{}"
    required_files_list_one_file = ["*plugin-config.json"]
    required_files_list_two_files = ["*plugin-config.json", "*plugin-structure.json"]
    environment_config_aws_cloudfront_true = {
        "wp_cli_debug": True,
        "wp_config": {
            "p1": {"name": "name1", "type": "constant", "value": "value1"},
            "p2": {"name": "name2", "type": "constant", "value": "value2"}
        },
        "settings": {
            "aws_cloudfront": True
        }
    }
    environment_config_aws_cloudfront_false = {
        "wp_cli_debug": True,
        "wp_config": {
            "p1": {"name": "name1", "type": "constant", "value": "value1"},
            "p2": {"name": "name2", "type": "constant", "value": "value2"}
        },
        "settings": {
            "aws_cloudfront": False
        }
    }
    environment_name = "localhost"
    environment_name_fake = "notfoundhost"
    environment_file_content = \
        "{\"$schema\":\"http://dev.aheadlabs.com/schemas/json/wordpress-site-environments-schema.json\"," \
        "\"environments\":[{\"name\":\"localhost\",\"type\":\"development\",\"default\":true,\"configuration_file\":" \
        "\"default-localhost-site.json\",\"db_admin_user\":\"root\"}]}"
    environment_file_content_duplicated_environment = \
        "{\"$schema\":\"http://dev.aheadlabs.com/schemas/json/wordpress-site-environments-schema.json\"," \
        "\"environments\":[{\"name\":\"localhost\",\"type\":\"development\",\"default\":true,\"configuration_file\":" \
        "\"default-localhost-site.json\"},{\"name\":\"localhost\",\"type\":\"development\",\"default\":true," \
        "\"configuration_file\":\"default-localhost-site.json\"}]}"
    site_config_path_from_json = "/pathto/default-localhost-site.json"
    site_config_path = "/pathto/site-config"
    site_config_file_name = "default-localhost-site.json"
    site_config_content = "{\"$schema\":\"https://dev.aheadlabs.com/schemas/json/wordpress-site-schema.json\"," \
                          "\"content\":{\"author_handling\":\"skip\",\"sources\":[]},\"environments\":[{\"base_url\":" \
                          "\"https://localhost/mysite\",\"database\":{\"charset\":\"utf8mb4\"," \
                          "\"collate\":\"utf8mb4_unicode_ci\",\"db_admin_user\":\"root\",\"db_name\":\"mysite_com\"," \
                          "\"db_user\":\"dbuser_mysite\",\"host\":\"localhost\",\"skip_check\":true," \
                          "\"table_prefix\":\"wp_\"},\"is_default\":true,\"name\":\"localhost\"," \
                          "\"settings\":{\"aws_cloudfront\":false},\"type\":\"development\",\"wp_cli_debug\":false," \
                          "\"wp_config\":{\"accessible_hosts\":{\"name\":\"WP_ACCESSIBLE_HOSTS\"," \
                          "\"type\":\"constant\",\"value\":\"localhost,api.wordpress.org,*.auth0.com\"}," \
                          "\"auto_update_core\":{\"name\":\"WP_AUTO_UPDATE_CORE\",\"type\":\"constant\"," \
                          "\"value\":\"minor\"},\"cache\":{\"name\":\"WP_CACHE\",\"type\":\"constant\"," \
                          "\"value\":false},\"content_url\":{\"name\":\"WP_CONTENT_URL\"," \
                          "\"type\":\"constant\",\"value\":\"/wp-content\"},\"debug\":{\"name\":\"WP_DEBUG\"," \
                          "\"type\":\"constant\",\"value\":true},\"debug_display\":{\"name\":\"WP_DEBUG_DISPLAY\"," \
                          "\"type\":\"constant\",\"value\":false},\"disable_fatal_error_handler\":{\"name\":" \
                          "\"WP_DISABLE_FATAL_ERROR_HANDLER\",\"type\":\"constant\",\"value\":false}," \
                          "\"disallow_file_edit\":{\"name\":\"DISALLOW_FILE_EDIT\",\"type\":\"constant\"," \
                          "\"value\":false},\"disallow_file_mods\":{\"name\":\"DISALLOW_FILE_MODS\"," \
                          "\"type\":\"constant\",\"value\":false},\"empty_trash_days\":{\"name\":" \
                          "\"EMPTY_TRASH_DAYS\",\"type\":\"constant\",\"value\":5},\"force_ssl_admin\":{\"name\":" \
                          "\"FORCE_SSL_ADMIN\",\"type\":\"constant\",\"value\":false},\"home_url\":{\"name\":" \
                          "\"WP_HOME\",\"type\":\"constant\",\"value\":\"\"},\"http_block_external\":{\"name\":" \
                          "\"WP_HTTP_BLOCK_EXTERNAL\",\"type\":\"constant\",\"value\":false}," \
                          "\"image_edit_overwrite\":{\"name\":\"IMAGE_EDIT_OVERWRITE\",\"type\":\"constant\"," \
                          "\"value\":true},\"noblogredirect_url\":{\"name\":\"NOBLOGREDIRECT\",\"type\":\"constant\"," \
                          "\"value\":\"\"},\"plugin_url\":{\"name\":\"WP_PLUGIN_URL\",\"type\":\"constant\"," \
                          "\"value\":\"/wp-content/plugins\"},\"save_queries\":{\"name\":\"SAVEQUERIES\"," \
                          "\"type\":\"constant\",\"value\":false},\"site_url\":{\"name\":\"WP_SITEURL\"," \
                          "\"type\":\"constant\",\"value\":\"\"},\"wpml_auto_updates\":{\"name\":" \
                          "\"OTGS_DISABLE_AUTO_UPDATES\",\"type\":\"constant\",\"value\":false}}}]," \
                          "\"settings\":{\"description\":\"My site description\",\"dumps\":{\"core\":" \
                          "\"[date|Y.m.d-Hisve]-db.core.sql\",\"plugins\":\"[date|Y.m.d-Hisve]-db.plugins.sql\"," \
                          "\"regular\":\"[date|Y.m.d-Hisve]-db-[commit].sql\",\"theme\":" \
                          "\"[date|Y.m.d-Hisve]-db.theme.sql\"},\"locale\":\"en_US\",\"options\":" \
                          "[{\"autoload\":true,\"name\":\"permalink_structure\"," \
                          "\"value\":\"/%category%/%postname%/\"}],\"plugins\":[{\"activate\":false," \
                          "\"force\":true,\"name\":\"akismet\",\"source\":\"akismet\",\"source_type\":\"wordpress\"}," \
                          "{\"activate\":true,\"force\":true,\"name\":\"google-site-kit\"," \
                          "\"source\":\"google-site-kit\",\"source_type\":\"wordpress\"}," \
                          "{\"activate\":true,\"force\":true,\"name\":\"wordpress-importer\"," \
                          "\"source\":\"wordpress-importer\",\"source_type\":\"wordpress\"}," \
                          "{\"activate\":true,\"force\":true,\"name\":\"wp-mail-smtp\",\"source\":\"wp-mail-smtp\"," \
                          "\"source_type\":\"wordpress\"}],\"project\":{\"name\":\"My project name\"," \
                          "\"url\":\"https://aheadlabs.com\",\"version\":\"0.1.0\"},\"skip_content_download\":true," \
                          "\"themes\":[{\"activate\":false,\"author\":\"Automattic\",\"author_uri\":" \
                          "\"https://wordpress.org\",\"build\":false,\"description\":\"WordPress official theme\"," \
                          "\"name\":\"twentytwentytwo\",\"source\":\"twentytwentytwo\",\"source_type\":\"wordpress\"," \
                          "\"minimum-php-version\":\"5.6\",\"minimum-wordpress-version\":\"5.9\"," \
                          "\"minimum-wordpress-version-tested\":\"5.9\",\"tags\":[\"wordpress\"]," \
                          "\"url\":\"https://wordpress.org/themes/twentytwentytwo/\",\"version\":\"1.2.0\"}]," \
                          "\"title\":\"My site\",\"users\":[],\"version\":\"latest\",\"wp_admin\":" \
                          "{\"email\":\"admin@example.com\",\"skip_email\":true,\"user\":\"wp_admin\"}}}"
    import_content_skip_author = "{\"author_handling\":\"skip\",\"sources\":[\"page\",\"nav_menu_item\"]}"
    constants_file_name = "wordpress-constants.json"
    constants_file_content = "{\"$schema\":" \
                             "\"http://dev.aheadlabs.com/schemas/json/wordpress-constants-schema.json\"," \
                             "\"defaults\":{\"version\":\"latest\",\"locale\":\"en_US\"},\"paths\":{\"devops\":" \
                             "\"/.devops\",\"database\":\"/database\",\"wordpress\":\"/wordpress\",\"content\":" \
                             "{\"themes\":\"/content/themes\",\"plugins\":\"/content/plugins\"," \
                             "\"wxr\":\"/content/wxr\"}},\"packages\":{\"devops_toolset\":" \
                             "\"https://github.com/aheadlabs/devops-toolset/archive/master.zip\"},\"regex_base64\":" \
                             "[{\"key\":\"wordpress-theme\",\"value\":" \
                             "\"d29yZHByZXNzL3dwLWNvbnRlbnQvdGhlbWVzLyhbXHdcLV0rKS8=\"}]}"
    structure_file_content = "{\"$schema\":\"http://dev.aheadlabs.com/schemas/json/project-structure-schema.json\"," \
                             "\"items\":[{\"name\":\".devops\",\"type\":\"directory\",\"children\":[{\"name\":" \
                             "\".gitkeep\",\"type\":\"file\",\"condition\":\"when-parent-not-empty\"}]},{\"name\":" \
                             "\".media\",\"type\":\"directory\",\"children\":[{\"name\":\".gitkeep\",\"type\":" \
                             "\"file\",\"condition\":\"when-parent-not-empty\"}]},{\"name\":\"content\",\"type\":" \
                             "\"directory\",\"children\":[{\"name\":\"themes\",\"type\":\"directory\",\"children\":" \
                             "[{\"name\":\".gitkeep\",\"type\":\"file\",\"condition\":\"when-parent-not-empty\"}]}]}" \
                             ",{\"name\":\"database\",\"type\":\"directory\",\"children\":[{\"name\":\".gitkeep\"," \
                             "\"type\":\"file\",\"condition\":\"when-parent-not-empty\"}]},{\"name\":\"wordpress\"," \
                             "\"type\":\"directory\",\"children\":[{\"name\":\".gitkeep\",\"type\":\"file\"," \
                             "\"condition\":\"when-parent-not-empty\"}]},{\"name\":\".gitignore\",\"type\":\"file\"," \
                             "\"default_content\":{\"source\":\"from_url\",\"value\":" \
                             "\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/wordpress/" \
                             "default.gitignore\"}},{\"name\":\"project.xml\",\"type\":\"file\",\"default_content\":" \
                             "{\"source\":\"from_url\",\"value\":" \
                             "\"https://raw.githubusercontent.com/aheadlabs/devops-toolset/master/wordpress/" \
                             "default-project.xml\"}},{\"name\":\"README.md\",\"type\":\"file\",\"default_content\":" \
                             "{\"source\":\"from_url\",\"value\":\"https://raw.githubusercontent.com/aheadlabs/" \
                             "devops-toolset/master/wordpress/default-README.md\"}}]}"
    package_json_example_content = "{\"name\":\"my-wordpress-project\",\"version\":\"0.1.0\"," \
                           "\"description\":\"Ad hoc WordPress theme.\",\"main\":\"index.php\"," \
                           "\"keywords\":[\"wordpress\",\"theme\",\"framework\",\"w74\",\"aheadlabs\"]," \
                           "\"author\":{\"name\":\"@aheadlabs\",\"url\":\"https://example.com\"}," \
                           "\"license\":\"ISC\",\"homepage\":\"https://example.com\"," \
                           "\"devDependencies\":{\"@aheadlabs/gulp-w74framework\":\"latest\",\"bootstrap\":\"latest\","\
                           "\"gulp\":\"latest\"},\"dependencies\":{\"@fortawesome/fontawesome-free\":\"latest\"}}"
    package_json_expected_content = "{\"name\":\"mytheme\",\"version\":\"0.1.0\"," \
                           "\"description\":\"mytheme-description\",\"main\":\"index.php\"," \
                           "\"keywords\":[\"tag1\",\"tag2\"]," \
                           "\"author\":{\"name\":\"theme-author\",\"url\":\"https://example.com\"}," \
                           "\"license\":\"ISC\",\"homepage\":\"https://example.com\"," \
                           "\"devDependencies\":{\"@aheadlabs/gulp-w74framework\":\"latest\",\"bootstrap\":\"latest\","\
                           "\"gulp\":\"latest\"},\"dependencies\":{\"@fortawesome/fontawesome-free\":\"latest\"}}"
    wp_cli_install_path = "/pathto/wp-cli"
    wp_cli_phar = "wp-cli.phar"
    wp_cli_file_path = pathlib.Path.joinpath(pathlib.Path(wp_cli_install_path), wp_cli_phar)
    wp_option = {
        "name": "permalink_structure",
        "value": "/%category%/%postname%/",
        "autoload": "true"
    }
    wp_locale_data = "$wp_local_package = 'en_US'"
    builtins_open = 'builtins.open'
    parent_not_empty_value = 'when_parent_not_empty'
    condition_key = 'condition'
    dump_file_path = "/pathto/dump_file_1.sql"
    path = "/pathto"
    url_resource = "https://url/resource"
    default_pwd = "root"
    token_replacements = []


@pytest.fixture
def pluginsdata():
    """ Sample plugins configuration data for testing"""
    yield PluginsData()
    # Below code is executed as a TearDown
    print("Teardown finished.")


@pytest.fixture
def themesdata():
    """ Sample themes configuration data for testing"""
    yield ThemesData()
    # Below code is executed as a TearDown
    print("Teardown finished.")


@pytest.fixture
def wordpressdata():
    """Sample data for testing"""
    yield WordPressData()
    # Below code is executed as a TearDown
    print("Teardown finished.")


def mocked_requests_get(url: str, *args, **kwargs):
    """Mock to replace requests.get()"""

    # Default values
    bytes_content = b"sample response in bytes"
    text_content = "sample text response"

    # Return instance
    return MockResponse(bytes_content, text_content)


def mocked_requests_get_json_content(url: str, *args, **kwargs):
    """Mock to replace requests.get()"""

    # Return instance
    return MockJsonResponse(WordPressData.structure_file_content)


class MockResponse:
    """This is the mocked Response object returned by requests.get()"""
    def __init__(self, b_content, text_content):
        self.content = b_content
        self.text = text_content


class MockJsonResponse:
    """This is the mocked Response object returned by requests.get()"""
    def __init__(self, json_content):
        self.json_content = json_content

    def json(self):
        return self.json_content



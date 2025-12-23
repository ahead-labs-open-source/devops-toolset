"""Contains wrappers for WP CLI commands"""

import datetime
import logging
import devops_toolset.tools.cli as cli
from devops_toolset.core.app import App
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.project_types.wordpress.commands import Commands as WordpressCommands
from enum import Enum

app: App = App()
literals = LiteralsCore([WordpressLiterals])
commands = CommandsCore([WordpressCommands])


class ValueType(Enum):
    """Defines value types for values at the wp-config.php file"""

    CONSTANT = 1,
    VARIABLE = 2


def add_update_option(option: dict, wordpress_path: str, debug: bool = False, update_permalinks: bool = True):
    """Adds a WordPress option or updates it if exists.

    Args:
        option: WordPress option.
        wordpress_path: Path to the WordPress installation.
        update_permalinks: If True updates the permalink structure.
        debug: It True logs debug information.
    """

    # Check if the option exists
    option_exists, existing_option_value = check_if_option_exists(option["name"], wordpress_path, debug)

    if option_exists:
        update_database_option(option["name"], option["value"], wordpress_path, debug, option["autoload"])
    else:
        add_database_option(option["name"], option["value"], wordpress_path, debug, option["autoload"])

    if option["name"] == "permalink_structure" and update_permalinks:
        cli.call_subprocess(commands.get("wpcli_rewrite_structure").format(
            structure=option["value"],
            path=wordpress_path,
            debug_info=convert_wp_parameter_debug(debug)
        ))


def add_database_option(option_name: str, option_value: str, wordpress_path: str,
                        debug_info: bool, autoload: bool = False):
    """Adds an option at the wp_options (*) table in the WordPress
    database using WP-CLI.

    (*) wp_ prefix could change, but this function will work anyway because
        its value is obtained from the wp-config.php configuration file.
    For more information see:
        https://developer.wordpress.org/cli/commands/option/update/

    Args:
        option_name: Name for the option.
        option_value: Value for the option.
        wordpress_path: Path to WordPress files.
        debug_info: Toggles debug info on the command.
        autoload: If True converts the value to yes, no otherwise.
    """

    # Check if the option exists
    option_exists, existing_option_value = check_if_option_exists(option_name, wordpress_path, debug_info)

    # Adds the option if it does not exist
    if not option_exists and check_if_option_is_valid(option_name, option_value, autoload):
        cli.call_subprocess(commands.get("wpcli_option_add").format(
            option_name=option_name,
            option_value=option_value,
            autoload=convert_wp_parameter_autoload(autoload),
            path=wordpress_path,
            debug_info=convert_wp_parameter_debug(debug_info)),
            log_before_process=[literals.get("wp_wpcli_option_add_before").format(
                option_name=option_name,
                option_value=option_value)],
            log_after_err=[literals.get("wp_wpcli_option_add_error").format(
                option_name=option_name,
                option_value=option_value)])


def check_if_option_exists(option_name: str, wordpress_path: str, debug_info: bool = False) -> (bool, str):
    """Checks if an option exists in the wp_options (*) table in the
    WordPress database using WP-CLI.

    (*) wp_ prefix could change, but this function will work anyway because
        its value is obtained from the wp-config.php configuration file.
    For more information see:
        https://developer.wordpress.org/cli/commands/option/get/

    Args:
        option_name: Name for the option.
        wordpress_path: Path to WordPress files.
        debug_info: Toggles debug info on the command.

    Returns:
        The option value if it exists
    """

    value = cli.call_subprocess_with_result(commands.get("wpcli_option_get").format(
        option_name=option_name,
        path=wordpress_path,
        debug_info=convert_wp_parameter_debug(debug_info)
    ))

    option_exists: bool = True if value is not None else False
    option_value: str = value.rstrip("\n") if option_exists else None

    return option_exists, option_value


def check_if_option_is_valid(name: str, value: str, autoload: bool) -> bool:
    """Checks if the name, value and autoload flag are valid (not empty
    or None)

    Args:
        name: Option name
        value: Option value
        autoload: Option autoload flag

    Returns:
        True if the option is valid, False otherwise
    """
    if name is not None and name != "" and value is not None \
            and autoload is not None:
        return True

    return False


def convert_wp_parameter_autoload(autoload: bool):
    """Converts a boolean value to a --autoload parameter."""
    if autoload:
        return "--autoload=yes"
    else:
        return "--autoload=no"


def convert_wp_parameter_db_user(db_user: str):
    """Converts a str value to a --db_user parameter."""
    if db_user:
        return "--dbuser=" + "\"" + db_user + "\""
    else:
        return ""


def convert_wp_parameter_db_pass(db_pass: str):
    """Converts a str value to a --db_pass parameter."""
    if db_pass:
        return "--dbpass=" + "\"" + db_pass + "\""
    else:
        return ""


def convert_wp_parameter_activate(activate: bool):
    """Converts a str value to a --activate."""
    if activate:
        return "--activate"
    else:
        return ""


def convert_wp_parameter_admin_password(admin_password: str):
    """Converts a str value to a --admin_password parameter."""
    if admin_password:
        return "--admin_password=" + "\"" + admin_password + "\""
    else:
        return ""


def convert_wp_parameter_content(value: bool):
    """Converts a boolean value to a yes/no string."""
    if not value:
        return "yes"
    return "no"


def convert_wp_parameter_debug(value: bool):
    """Converts a boolean value to a --debug string."""
    if value:
        return "--debug"
    return ""


def convert_wp_parameter_force(value: bool):
    """Converts a boolean value to a --force string."""
    if value:
        return "--force"
    return ""


def convert_wp_parameter_raw(value: bool):
    """Converts a boolean value to a --raw string."""
    if value:
        return "--raw"
    return ""


def convert_wp_parameter_send_email(value: bool):
    """Converts a boolean value to a --send-email string."""
    if value:
        return "--send-email"
    return ""


def convert_wp_parameter_skip_check(value: bool):
    """Converts a boolean value to a --skip-check string."""
    if value:
        return "--skip-check"
    return ""


def convert_wp_parameter_skip_content(value: bool):
    """Converts a boolean value to a --skip-content string."""
    if value:
        return "--skip-content"
    return ""


def convert_wp_parameter_skip_email(value: bool):
    """Converts a boolean value to a --skip-email string."""
    if value:
        return "--skip-email"
    return ""


def convert_wp_parameter_str_key_value(key: str, value: str, quoted: bool = False) -> str:
    """Converts a string value to a --role string.

    Args:
        key: WordPress parameter name.
        value: Value for the WordPress parameter.
        quoted: If True quotes the value

    Returns:
        Parameter build as --key=value
    """
    quote = "\"" if quoted else ""

    if value:
        return "--" + key + "=" + quote + value + quote
    return ""


def convert_wp_parameter_yes(value: bool):
    """Converts a boolean value to a --yes string."""
    if value:
        return "--yes"
    return ""


def create_configuration_file(wordpress_path: str, db_host: str, db_name: str, db_user: str,
                              db_pass: str, db_prefix: str, db_charset: str, db_collate: str,
                              skip_check: bool, debug: bool):
    """Creates the wp-config-php WordPress configuration file using WP-CLI.

    For more information see:
        https://developer.wordpress.org/cli/commands/config/create/

    Args:
        wordpress_path: Path to WordPress files
        db_host: Database host
        db_name: Database server
        db_user: Database user
        db_pass: Database password
        db_prefix: Prefix of database tables
        db_charset: Database charset
        db_collate: Database collation
        skip_check: Skip check parameter --skip-check
        debug: If present, --debug will be added to the command showing all debug trace information.
    """
    tools.cli.call_subprocess(commands.get("wpcli_config_create").format(
        path=wordpress_path,
        db_host=db_host,
        db_name=db_name,
        db_user=db_user,
        db_pass=db_pass,
        db_prefix=db_prefix,
        db_charset=db_charset,
        db_collate=db_collate,
        skip_check=convert_wp_parameter_skip_check(skip_check),
        debug_info=convert_wp_parameter_debug(debug)
    ), log_before_process=[literals.get("wp_wpcli_creating_config")],
        log_after_out=[literals.get("wp_wpcli_config_created_ok")],
        log_after_err=[literals.get("wp_wpcli_config_create_err")]
    )


def create_database(wordpress_path: str, debug: bool, db_user: str, db_password: str, schema: str):
    """ Calls wp db create with the parameters
    Args
        wordpress_path: Path to WordPress files
        debug: If True, --debug will be added to the command showing all debug trace information.
        db_user: Database user
        db_pass: Database password
        schema: Schema name to be checked for existence
    """
    # Check if the database exists
    output = cli.call_subprocess_with_result(commands.get("wpcli_db_query_db_exists").format(
        schema=schema,
        admin_user=db_user,
        admin_password=db_password,
        path=wordpress_path
    ))
    database_exists = True if output is not None and output.split("\r\n")[1] == '1' else False

    # Create the database
    if not database_exists:
        tools.cli.call_subprocess(commands.get("wpcli_db_create").format(
            path=wordpress_path,
            db_user=convert_wp_parameter_db_user(db_user),
            db_pass=convert_wp_parameter_db_pass(db_password),
            debug_info=convert_wp_parameter_debug(debug)
        ), log_before_process=[literals.get("wp_wpcli_db_create_before")])

    # Warn the user we will not create the database
    else:
        logging.warning(literals.get("mysql_db_exists_skipping_creation").format(schema=schema))


def create_user(user: dict, wordpress_path: str, debug: bool):
    """Creates a WordPress user.

    Args:
        user: User to be created based on #/definitions/user at
            https://dev.aheadlabs.com/schemas/json/wordpress-site-schema.json
        wordpress_path: Path to WordPress files.
        debug: If present, --debug will be added to the command showing all debug trace information.
    """

    cli.call_subprocess(commands.get("wp_user_create").format(
        user_login=user["user_login"],
        user_email=user["user_email"],
        role=convert_wp_parameter_str_key_value("role", user["role"]),
        display_name=convert_wp_parameter_str_key_value("display_name", user["display_name"], True),
        first_name=convert_wp_parameter_str_key_value("first_name", user["first_name"], True),
        last_name=convert_wp_parameter_str_key_value("last_name", user["last_name"], True),
        send_email=convert_wp_parameter_send_email(user["send_email"]),
        path=wordpress_path,
        debug_info=convert_wp_parameter_debug(debug)
    ),
        log_before_process=[literals.get("wp_wpcli_user_creating").format(user=user["user_login"])],
        log_after_out=[literals.get("wp_wpcli_user_created").format(user=user["user_login"])],
        log_after_err=[literals.get("wp_wpcli_user_creating_err").format(user=user["user_login"])]
    )


def user_exists(user_login: str, wordpress_path: str, debug: bool) -> bool:
    """Creates a WordPress user.

    Args:
        user_login: User login to be checked.
        wordpress_path: Path to WordPress files.
        debug: If present, --debug will be added to the command showing all debug trace information.

    Returns:
        True if the user exists.
    """

    result = cli.call_subprocess_with_result(commands.get("wp_user_get").format(
        user_login=user_login,
        path=wordpress_path,
        debug_info=convert_wp_parameter_debug(debug)
    ))

    if result is None:
        return False
    return True


def create_wordpress_database_user(wordpress_path: str, admin_user: str, admin_password: str, user: str, password: str,
                                   schema: str, host: str = 'localhost',
                                   db_privileges: str = 'create, alter, select, insert, update, delete',
                                   global_privileges: str = 'lock tables, process'):
    """Creates a database user to be used by WordPress
        e.g.:
            wp db query
                "create user '<username>'@'localhost'
                identified by '<password>'"
            wp db query
                "grant create, alter, select, insert, update, delete
                on <schema>.* to '<username>'@'localhost'"

        Args:
            wordpress_path: Path to WordPress files.
            admin_user: Database user with privileges to create databases and
                other users.
            admin_password: Admin user password.
            user: Database user name.
            password: Database user password.
            schema: Existing database schema name.
            host: localhost or FQDN. (% and _ wildcards are permitted).
            db_privileges: comma-separated privileges to be granted on the database. More info at:
                https://dev.mysql.com/doc/refman/en/grant.html#grant-privileges
                e.g.: 'create, alter, select, insert, update, delete'
            global_privileges: comma-separated privileges to be granted globally. More info at:
                https://dev.mysql.com/doc/refman/en/grant.html#grant-privileges
                e.g.: 'process'
    """
    # Check if the user exists
    output = cli.call_subprocess_with_result(commands.get("wpcli_db_query_user_exists").format(
        user=user,
        host=host,
        admin_user=admin_user,
        admin_password=admin_password,
        path=wordpress_path
    ))
    user_exists_db = True if output is not None and len(output.split("\r\n")) > 1 and output.split("\r\n")[1] == '1' \
        else False

    # Create user
    if not user_exists_db:
        cli.call_subprocess(commands.get("wpcli_db_query_create_user").format(
            user=user,
            host=host,
            password=password,
            admin_user=admin_user,
            admin_password=admin_password,
            path=wordpress_path),
            log_before_out=[literals.get("wp_wpcli_db_query_user_creating").format(user=user, host=host)],
            log_after_err=[literals.get("wp_wpcli_db_query_user_creating_err").format(user=user, host=host)]
        )

        # Grant user privileges on the database
        cli.call_subprocess(commands.get("wpcli_db_query_grant").format(
            privileges=db_privileges,
            schema=schema,
            user=user,
            host=host,
            admin_user=admin_user,
            admin_password=admin_password,
            path=wordpress_path),
            log_before_out=[literals.get("wp_wpcli_db_query_user_granting").format(
                user=user, host=host, schema=schema, privileges=db_privileges)],
            log_after_err=[literals.get("wp_wpcli_db_query_user_granting_err").format(
                user=user, host=host, schema=schema)]
        )

        # Grant user global privileges
        cli.call_subprocess(commands.get("wpcli_db_query_grant").format(
            privileges=global_privileges,
            schema="*",
            user=user,
            host=host,
            admin_user=admin_user,
            admin_password=admin_password,
            path=wordpress_path),
            log_before_out=[literals.get("wp_wpcli_db_query_user_granting").format(
                user=user, host=host, schema=schema, privileges=db_privileges)],
            log_after_err=[literals.get("wp_wpcli_db_query_user_granting_err").format(
                user=user, host=host, schema=schema)]
        )

    # Warn the user we are not altering users and permissions
    else:
        logging.warning(literals.get("mysql_user_exists_grant_privileges_manually").format(
            user=user,
            host=host,
            schema=schema,
            db_privileges=db_privileges,
            global_privileges=global_privileges
        ))


def delete_post_type_content(wordpress_path: str, content_type: str, debug_info: bool = False):
    """ Calls db in order to delete content from a concrete post type
    Args:
        wordpress_path: Path to WordPress files.
        content_type: Type of the content to be deleted
        debug_info: If true, --debug will be added to the command showing all debug trace information.
    """

    id_list = get_post_type_ids(wordpress_path, content_type)

    cli.call_subprocess(commands.get("wpcli_post_delete_post_type").format(
        id_list=id_list,
        path=wordpress_path,
        debug_info=convert_wp_parameter_debug(debug_info)),
        log_before_out=[literals.get("wp_wpcli_post_delete_post_type_before").format(post_type=content_type)],
        log_before_err=[literals.get("wp_wpcli_post_delete_post_type_err").format(post_type=content_type)])


def get_post_type_ids(wordpress_path: str, post_type: str):
    """Gets the ids for all the posts that match an specific post type.

    Args:
        wordpress_path: Path to WordPress files.
        post_type: Post type name to filter by.
    """

    return cli.call_subprocess_with_result(commands.get("wpcli_post_list_ids").format(
        post_type=post_type,
        path=wordpress_path
    ))


def wordpress_is_downloaded(path: str) -> bool:
    """Checks if WordPress is downloaded at the specified path.

    Args:
        path: Path to be checked for WordPress files.

    Returns:
        True if WordPress files are present at the specified path.
    """

    version = cli.call_subprocess_with_result(commands.get("wpcli_core_version").format(path=path))

    if version:
        logging.warning(literals.get("wp_wpcli_core_version_already_downloaded")
                        .format(version=version.replace("\n", "")))
        return True
    else:
        return False


def download_wordpress(destination_path: str, version: str, locale: str, skip_content: bool, debug: bool):
    """ Downloads the latest version of the WordPress core files using WP-CLI.

    For more information see:
        https://developer.wordpress.org/cli/commands/core/download/

    Args:
        destination_path: Path where WP-CLI will be downloaded.
        version: Target version to be downloaded (latest by default)
        locale: Wordpress locale
        skip_content: --skip-content parameter
        debug: If present, --debug will be added to the command showing all debug trace information.
    """
    if not wordpress_is_downloaded(destination_path):
        cli.call_subprocess(commands.get("wpcli_core_download").format(
            version=version,
            locale=locale,
            path=destination_path,
            skip_content=convert_wp_parameter_skip_content(skip_content),
            debug_info=convert_wp_parameter_debug(debug)
        ), log_before_process=[
            literals.get("wp_wpcli_downloading_wordpress").format(version=version, locale=locale, content=skip_content),
            literals.get("wp_wpcli_downloading_path").format(path=destination_path),
            literals.get("wp_wpcli_downloading_content").format(content=skip_content)],
            log_after_out=[
                literals.get("wp_wpcli_downloading_wordpress_ok")],
            log_after_err=[
                literals.get("wp_wpcli_downloading_wordpress_err")]
        )


def eval_code(php_code: str, wordpress_path: str) -> str:
    """ Executes a piece of php code
     Args:
        php_code: Piece of php code to be evaluated
        wordpress_path: Path to WordPress files.
    """
    return cli.call_subprocess_with_result(commands.get("wpcli_eval").format(
        php_code=php_code,
        path=wordpress_path))


def export_database(wordpress_path: str, dump_file_path: str, debug: bool):
    """Exports a WordPress database to a dump file using WP-CLI.

    All parameters are obtained from a site configuration file.

    For more information see:
        https://developer.wordpress.org/cli/commands/db/export/

    Args:
        wordpress_path: Path to WordPress files.
        dump_file_path: Path to the destination dump file.
        debug: If present, --debug will be added to the command showing all debug trace information.
    """
    cli.call_subprocess(commands.get("wpcli_db_export").format(
        core_dump_path=dump_file_path,
        path=wordpress_path,
        debug_info=convert_wp_parameter_debug(debug)),
        log_before_out=[literals.get("wp_wpcli_db_export_before").format(path=dump_file_path)],
        log_after_err=[literals.get("wp_wpcli_db_export_error")])


def export_content_to_wxr(wordpress_path: str, destination_path: str, wrx_file_suffix: str = None):
    """Exports all WordPress content to a WXR XML file.

    e.g.:
        wp export --dir="<destination path>" --filename_format="<date>-content.xml"

    Args:
        wordpress_path: Path to WordPress files.
        destination_path: Path where the files will be generated.
        wrx_file_suffix: Suffix to be added to the generated XML file.
    """
    date = datetime.datetime.utcnow().strftime("%Y.%m.%d")
    suffix = "" if wrx_file_suffix is None else f"-{wrx_file_suffix}"

    cli.call_subprocess(commands.get("wpcli_export").format(
        path=wordpress_path,
        destination_path=destination_path,
        date=date,
        suffix=suffix),
        log_before_out=[literals.get("wp_wpcli_export").format(path=destination_path)],
        log_after_err=[literals.get("wp_wpcli_export_err").format(path=destination_path)])


def import_database(wordpress_path: str, dump_file_path: str, debug: bool):
    """Imports a WordPress database from a dump file using WP-CLI.

    All parameters are obtained from a site configuration file.

    Args:
        wordpress_path: Path to WordPress files.
        dump_file_path: Path to dump file to be imported.
        debug: If present, --debug will be added to the command showing all debug trace information.
    """
    cli.call_subprocess(commands.get("wpcli_db_import").format(
        file=dump_file_path, path=wordpress_path, debug_info=convert_wp_parameter_debug(debug)),
                        log_before_process=[literals.get("wp_wpcli_db_import_before"), dump_file_path],
                        log_after_err=[literals.get("wp_wpcli_db_import_error")])


def import_wxr_content(wordpress_path: str, wxr_path: str, authors: str, debug: bool):
    """ Imports wxr files as content for the current WordPress from the wxr_path

    All parameters are obtained from a site configuration file.
    For more info, see: https://developer.wordpress.org/cli/commands/import/

     Args:
        wordpress_path: Path to WordPress files.
        wxr_path: Path the wxr files will be imported from.
        authors: Value for the authors argument.
        debug: If present, --debug will be added to the command showing all debug trace information.

    """
    cli.call_subprocess(commands.get("wpcli_import").format(
        file=wxr_path, path=wordpress_path, authors=authors, debug_info=convert_wp_parameter_debug(debug)),
        log_before_process=[literals.get("wp_wpcli_import_before"), wxr_path],
        log_after_err=[literals.get("wp_wpcli_import_error")])


def install_theme(wordpress_path: str, source: str, activate: bool, debug: bool, theme_name: str):
    """Installs WordPress's theme files (and child themes also) using WP-CLI.

    All parameters are obtained from a site configuration file.

    For more information see:
        https://developer.wordpress.org/cli/commands/theme/install/

    Args:

       wordpress_path: Path to the wordpress installation.
       source: The source of the theme, can be a path to a zip file, an url or a slug.
       activate: --activate present will activate the theme after installing it.
       debug: --debug present will show all debug trace information.
       theme_name: Name of the theme to be installed (just used for log purposes)

    """
    cli.call_subprocess(commands.get("wpcli_theme_install").format(
        path=wordpress_path,
        source=source,
        activate=convert_wp_parameter_activate(activate),
        debug_info=convert_wp_parameter_debug(debug)),
        log_before_process=[literals.get("wp_wpcli_theme_install_before").format(theme_name=theme_name)],
        log_after_err=[literals.get("wp_wpcli_theme_install_error").format(theme_name=theme_name)])


def install_plugin(plugin_name: str, wordpress_path: str, activate: bool, force: bool, source: str, debug: bool):
    """ Uses WP-CLI command to install a plugin with 'wp plugin install <source>'.

           All parameters are obtained from a site configuration file.

           For more information see:
               https://developer.wordpress.org/cli/commands/theme/install/

           Args:
               plugin_name: Plugin name / slug
               wordpress_path: Path to the wordpress installation.
               activate: Activates the plugin.
               force: Forces install by removing previous version of the plugin.
               source: Source of the installation.
               debug: Adds optional --debug parameter in order to better track the command result.
           """
    cli.call_subprocess(commands.get("wpcli_plugin_install").format(
        path=wordpress_path,
        activate=convert_wp_parameter_activate(activate),
        force=convert_wp_parameter_force(force),
        source=source,
        debug_info=convert_wp_parameter_debug(debug)
    ),
        log_before_process=[literals.get("wp_wpcli_plugin_install_before").format(plugin_name=plugin_name)],
        log_after_err=[literals.get("wp_wpcli_plugin_install_error").format(plugin_name=plugin_name)])


def install_wordpress_core(wordpress_path: str, url: str, title: str, admin_user: str, admin_email: str,
                           admin_password: str, skip_email: bool, debug: bool):
    """Installs WordPress core files using WP-CLI.

        All parameters are obtained from a site configuration file.

        For more information see:
            https://developer.wordpress.org/cli/commands/core/install/

        Args:
            wordpress_path: Path to WordPress files.
            url: The url for this wordpress site
            title: The title of this wordpress site
            admin_user: Name of the admin user of this site
            admin_email: Email if the admin user of this site
            admin_password: Password for the WordPress administrator user
            skip_email: --skip-mail parameter will send an email to the address specified if present.
            debug: Adds optional --debug parameter in order to better track the command result.
        """
    cli.call_subprocess(commands.get("wpcli_core_install").format(
        path=wordpress_path,
        url=url,
        title=title,
        admin_user=admin_user,
        admin_email=admin_email,
        admin_password=convert_wp_parameter_admin_password(admin_password),
        skip_email=convert_wp_parameter_skip_email(skip_email),
        debug_info=convert_wp_parameter_debug(debug)),
        log_before_process=[literals.get("wp_wpcli_core_install_before")],
        log_after_err=[literals.get("wp_wpcli_core_install_error")]
    )


def reset_database(wordpress_path: str, quiet: bool, debug_info: bool):
    """Removes all WordPress core tables from the database using WP-CLI.

    For more information see:
        https://developer.wordpress.org/cli/commands/db/reset/

    Args:
        debug_info:
        wordpress_path: Path to WordPress files.
        quiet: If True, no questions are asked.
    """
    cli.call_subprocess(commands.get("wpcli_db_reset").format(
        path=wordpress_path,
        yes=convert_wp_parameter_yes(quiet),
        debug_info=convert_wp_parameter_debug(debug_info)),
        log_before_process=[literals.get("wp_wpcli_db_reset_before")],
        log_after_err=[literals.get("wp_wpcli_db_reset_error")])


def reset_transients(wordpress_path: str):
    """Removes all WordPress transients from database using WP-CLI

    Args:
        wordpress_path: Path to WordPress files.
    """

    cli.call_subprocess(commands.get("wpcli_db_delete_transient").format(path=wordpress_path),
                        log_before_out=[literals.get("wp_wpcli_delete_transients")],
                        log_after_err=[literals.get("wp_wpcli_delete_transients_err")])


def set_configuration_value(name: str, value: str, value_type: ValueType, wordpress_path: str, raw: bool, debug: bool):
    """Creates or updates a value (constant or variable) at the wp-config-php
    WordPress configuration file using WP-CLI.

    For more information see:
        https://developer.wordpress.org/cli/commands/config/set/

        Args:
            name: Name of the parameter
            value: Value of the parameter
            value_type: CONSTANT or VARIABLE
            wordpress_path: Path to WordPress files.
            raw: Toggles --raw as parameter that decides if value will placed as it gets, without quotes
            debug: Toggles --debug_info as a parameter inside the command.
    """
    cli.call_subprocess(commands.get("wpcli_config_set").format(
        name=name,
        value=value,
        raw=convert_wp_parameter_raw(raw),
        type=value_type,
        path=wordpress_path,
        debug_info=convert_wp_parameter_debug(debug)
    ),  log_after_err=[literals.get("wp_wpcli_config_set_value_err")]
    )


def update_database_option(option_name: str, option_value: str, wordpress_path: str,
                           debug_info: bool, autoload: bool = False):
    """Updates an option at the wp_options (*) table in the WordPress
    database using WP-CLI.

    (*) wp_ prefix could change, but this function will work anyway because
        its value is obtained from the wp-config.php configuration file.
    For more information see:
        https://developer.wordpress.org/cli/commands/option/update/

    Args:
        option_name: Name for the option.
        option_value: Value for the option.
        wordpress_path: Path to WordPress files.
        debug_info: Toggles debug info on the command.
        autoload: If True converts the value to yes, no otherwise.
    """

    # Check if the option exists
    option_exists, existing_option_value = check_if_option_exists(option_name, wordpress_path, debug_info)

    # Update the option if the new value is different than the existing one
    if option_exists and existing_option_value != option_value:
        cli.call_subprocess(commands.get("wpcli_option_update").format(
            option_name=option_name,
            option_value=option_value,
            autoload=convert_wp_parameter_autoload(autoload),
            path=wordpress_path,
            debug_info=convert_wp_parameter_debug(debug_info)),
            log_before_process=[literals.get("wp_wpcli_option_update_before").format(
                option_name=option_name,
                option_value=option_value)],
            log_after_err=[literals.get("wp_wpcli_option_update_error").format(
                option_name=option_name,
                option_value=option_value)])
    else:
        logging.warning(literals.get("wp_wpcli_option_skipping").format(option_name=option_name))


def wp_cli_info():
    """Executes wp info command and logs output based on the result. """
    cli.call_subprocess(commands.get("wpcli_info"),
                        log_before_out=[literals.get("wp_wpcli_install_ok"), literals.get("wp_wpcli_info")],
                        log_after_out=[literals.get("wp_wpcli_add_ev")])


if __name__ == "__main__":
    help(__name__)

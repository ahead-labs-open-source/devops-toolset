"""wordpress module commands"""

from devops_toolset.core.value_dicts_base import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Commands(ValueDictsBase):
    """Commands for the wordpress module."""

    # Add your wordpress literal dictionaries here
    _commands = {
        "wpcli_config_create": "wp config create --path={path} --dbhost={db_host} --dbname={db_name} "
                               "--dbuser={db_user} --dbpass={db_pass} --dbprefix={db_prefix} --dbcharset={db_charset} "
                               "--dbcollate={db_collate} --force {skip_check} {debug_info}",
        "wpcli_config_set": "wp config set {name} {value} {raw} --type={type} --path={path} --separator=\\n "
                            "{debug_info}",
        "wpcli_core_download": "wp core download --version={version} --locale={locale} --path={path} "
                               "{skip_content} {debug_info}",
        "wpcli_core_install": "wp core install --path={path} --url={url} --title=\"{title}\" --admin_user={admin_user} "
                              "--admin_email={admin_email} {admin_password} {skip_email} {debug_info}",
        "wpcli_core_version": "wp core version --path={path}",
        "wpcli_db_create": "wp db create {db_user} {db_pass} --path={path} {debug_info}",
        "wpcli_db_export": "wp db export \"{core_dump_path}\" --path={path} --extended-insert=false {debug_info}",
        "wpcli_db_reset": "wp db reset --path={path} {yes} {debug_info}",
        "wpcli_db_import": "wp db import {file} --path={path} {debug_info}",
        "wpcli_db_delete_transient": "wp transient delete --all --path={path}",
        "wpcli_db_query_create_user":
            "wp db query \"create user '{user}'@'{host}' identified by '{password}'\" "
            "--dbuser={admin_user} --dbpass={admin_password} --path={path}",
        "wpcli_db_query_db_exists": "wp db query \"select exists (select 1 from information_schema.schemata where "
                                    "schema_name = '{schema}')\" --dbuser={admin_user} --dbpass={admin_password} "
                                      "--path={path}",
        "wpcli_db_query_grant": "wp db query \"grant {privileges} on {schema}.* to '{user}'@'{host}'\" "
            "--dbuser={admin_user} --dbpass={admin_password} --path={path}",
        "wpcli_db_query_user_exists": "wp db query \"select exists (select 1 from mysql.user where user='{user}')\" "
                                      "--dbuser={admin_user} --dbpass={admin_password} "
                                      "--path={path}",
        "wpcli_post_list_ids": "wp post list --post_type={post_type} --path={path} --format=ids",
        "wpcli_post_delete_post_type": "wp post delete {id_list} --force --path={path} {debug_info}",
        "wpcli_eval": "wp eval \"{php_code}\" --path={path}",
        "wpcli_export": "wp export --path=\"{path}\" --dir=\"{destination_path}\" "
                        "--filename_format={date}_UTC-content{suffix}.xml",
        "wpcli_import": "wp import \"{file}\" --authors={authors} --path=\"{path}\" {debug_info}",
        "wpcli_info": "wp --info",
        "wpcli_option_add": "wp option add {option_name} \"{option_value}\" {autoload} --path={path} {debug_info}",
        "wpcli_option_get": "wp option get {option_name} --path={path} {debug_info}",
        "wpcli_option_update": "wp option update {option_name} \"{option_value}\" {autoload} "
                               "--path={path} {debug_info}",
        "wpcli_plugin_install": "wp plugin install {source} --path={path} {force} {activate} {debug_info}",
        "wpcli_rewrite_structure": "wp rewrite structure {structure} --path={path} {debug_info}",
        "wpcli_theme_install": "wp theme install {source} --path={path} {activate} --force {debug_info}",
        "wp_theme_src_build": "gulp build --theme-slug=\"{theme_slug}\" --dist=\"{path}\"",
        "wp_theme_src_watch":
            "gulp watch --theme-slug=\"{theme_slug}\" --dev-proxy=\"{local_web_server}\" --wordpress-path=\"{path}\"",
        "wp_user_create": "wp user create {user_login} {user_email} "
                          "{role} {display_name} {first_name} {last_name} {send_email} --path={path} {debug_info}",
        "wp_user_get": "wp user get {user_login} --format=json --path={path} {debug_info}"
    }

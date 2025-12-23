"""wordpress module literals"""

from devops_toolset.core.ValueDictsBase import ValueDictsBase
from devops_toolset.core.app import App

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the wordpress module."""

    _titles = {
        "wp_title_bootstrap_repository": _("Bootstrap WordPress repository"),
        "wp_title_build_wordpress": _("Build WordPress site"),
        "wp_title_deploy_wordpress": _("Deploy WordPress site"),
        "wp_title_generate_plugin": _("Generate WordPress plugin"),
        "wp_title_generate_wordpress": _("Generate WordPress site"),
        "wp_title_wordpress_files": _("WordPress core"),
        "wp_title_wordpress_new_repo": _("WordPress\nexisting repo"),
        "wp_title_wordpress_rollback_db": _("WordPress\ndatabase rollback"),
    }
    _info = {
        "wp_created_project_structure": _("Finished creation of the project structure."),
        "wp_creating_project_structure": _("Starting to create the project structure..."),
        "wp_created_theme_structure": _("Finished creation of the development theme {theme_name} structure."),
        "wp_project_structure_creating_from_file": _("Creating project structure from {file_name}"),
        "wp_project_structure_creating_from_default_file": _("Creating default project structure from {resource}..."),
        "wp_theme_structure_creating_from_file": _("Creating development theme [{theme_name}] structure from "
                                                   "{file_name}"),
        "wp_theme_structure_creating_from_default_file": _("Creating default development theme structure from "
                                                           "{resource}"),
        "wp_default_files": _("These are the default files from the GitHub repository:"),
        "wp_downloading_default_file": _("Downloading default file {file} from {url}."),
        "wp_directory_created": _("Directory created: {directory}"),
        "wp_environment_file_used": _("The following environment file will be used: {file}"),
        "wp_file_created": _("File created: {file}"),
        "wp_file_deleted": _("File deleted: {file}"),
        "wp_got_db_admin_user": _("I got the following database admin user from the environment configuration file: "
                                  "{db_admin_user}"),
        "wp_init_git_repo": _("Do you want me to initialize a local Git repository for you?"),
        "wp_looking_for_src_themes": _("Looking for development themes to build..."),
        "wp_no_src_themes": _("No development themes to build. Skipping this step."),
        "wp_parsing_theme_metadata": _("Parsing theme metadata..."),
        "wp_parsing_theme_regex": _("Regex to match theme metadata content is: {regex}"),
        "wp_parsing_theme_no_matches_found": _("No matches found for key: {key}"),
        "wp_parsing_theme_matches_found": _("Matched value \"{value}\" for key \"{key}\""),
        "wp_required_file_paths_not_found": _("No required file paths were found"),
        "wp_required_file_paths_found": _("The following file paths were found:"),
        "wp_root_path": _("The root path is: {path}"),
        "wp_themes_install_manually": _("Please, install the theme/s manually."),
        "wp_themes_installing_theme": _("Installing theme \"{theme}\"..."),
        "wp_plugin_add": _("Adding content under {plugin_path} into svn repository."),
        "wp_plugin_checkin": _("Checking in content under {plugin_path} into svn repository."),
        "wp_plugin_path": _("The plugin path is: {path}"),
        "wp_plugin_tag_path_created": _("Plugin's tag path created: {plugin_tag_path}"),
        "wp_plugin_trunk_copied": _("Plugin's trunk content copied successfully to: {plugin_trunk_path}"),
        "wp_parsing_plugin_config_file": _("Parsing plugin's config file from {file}."),
        "wp_parsing_plugin_structure_file": _("Parsing plugin's structure file from {file}."),
        "wp_theme_path": _("The theme path is: {path}"),
        "wp_theme_src_will_not_be_built": _("Development theme wil not be built due to configuration settings."),
        "wp_themes_path": _("The themes path is: {path}"),
        "wp_use_default_files": _("Do you want me to use the default ones instead for those missing files?"),
        "wp_wordpress_path": _("The WordPress path is: {path}"),
        "wp_wordpress_zip_file_and_settings_version_mismatch":
            _("WordPress files version ({version}) and version specified in settings ({settings_version}) mismatch."),
        "wp_wordpress_zip_file_format_ok": _("WordPress zip file name format is ok. Version number is {version}."),
        "wp_wordpress_zip_file_version_ok": _("WordPress zip file version has been checked successfully."),
        "wp_wpcli_add_ev": _("Remember to add the path to the PATH or BIN, depending on your operating system."),
        "wp_wpcli_backup_create_before": _("Creating database backup..."),
        "wp_wpcli_config_created_ok": _("File wp-config.php created successfully."),
        "wp_wpcli_core_install_before": _("Preparing wordpress core files to install..."),
        "wp_wpcli_creating_config": _("Creating wp-config.php..."),
        "wp_wpcli_db_create_before":
            _("Creating Wordpress database (by default, user_name and host will be taken from wp_config)"),
        "wp_wpcli_db_import_before": _("Importing database dump from file:"),
        "wp_wpcli_db_export_before": _("Exporting database dump to: {path}"),
        "wp_wpcli_db_query_user_creating": _("Creating database user {user} for host {host}"),
        "wp_wpcli_db_query_user_granting": _("Granting database user {user} for host {host} the following privileges "
                                             "on schema {schema}: {privileges}"),
        "wp_wpcli_db_reset_before": _("Resetting the database (drop and create)..."),
        "wp_wpcli_delete_transients": _("Transients are going to be deleted"),
        "wp_wpcli_downloading": _("Downloading WP-CLI from {url}"),
        "wp_wpcli_downloading_content": _("Downloading WordPress content (default themes and plugins): {content}"),
        "wp_wpcli_downloading_path": _("WordPress core destination path: {path}"),
        "wp_wpcli_downloading_wordpress": _("Downloading WordPress core files version {version}, locale {locale}"),
        "wp_wpcli_downloading_wordpress_ok": _("WordPress core files were successfully downloaded."),
        "wp_wpcli_export": _("Exporting WordPress content to {path}"),
        "wp_wpcli_import_after": _("{type} content imported successfully. "),
        "wp_wpcli_import_before": _("Importing {type} content..."),
        "wp_wpcli_import_error": _("There was an error when importing {type} content..."),
        "wp_wpcli_info": _("Here is the WP-CLI information:"),
        "wp_wpcli_install_ok": _("WP-CLI installation was successful."),
        "wp_wpcli_option_add_before": _("Adding database option {option_name}..."),
        "wp_wpcli_option_update_before": _("Updating database option {option_name}..."),
        "wp_wpcli_option_skipping": _("Skipping option update for {option_name} since the new value is the same as the "
                                      "existing one."),
        "wp_wpcli_plugin_install_before": _("Installing plugin {plugin_name}..."),
        "wp_wpcli_plugin_install_error": _("An error occurred installing plugin {plugin_name}..."),
        "wp_wpcli_post_delete_post_type_before": _("Deleting posts of type {post_type}..."),
        "wp_wpcli_setting_value_ok": _("Config value {name} set as {value}"),
        "wp_wpcli_theme_install_before": _("Installing wordpress theme {theme_name}"),
        "wp_wpcli_user_creating": _("Creating WordPress user {user}..."),
        "wp_wpcli_user_created": _("Created WordPress user {user}."),
        "wp_write_default_content": _("Writing default content to file \"{file}\" from {source}"),
        "wp_webpack_build_before": _("Webpack build task has launched for theme {theme_slug}."),
        "wp_webpack_build_after": _("Webpack build task has completed successfully for theme {theme_slug}."),
    }
    _warnings = {
        "mysql_user_exists_grant_privileges_manually": _("User {user} exists in the {host} host and will not be "
                                                         "altered. Please grant the following privileges manually to "
                                                         "{host} for this user in the {schema} schema: "
                                                         "(db privileges) {db_privileges}; "
                                                         "(global privileges) {global_privileges};"),
        "mysql_db_exists_skipping_creation": _("Database {schema} exists. I will not create any database..."),
        "wp_wordpress_wp_local_package_value_not_set": _("$wp_local_package value was not set in {version_file_path}"),
        "wp_wordpress_zip_file_locale_mismatch": _("Locale specified in settings ({locale}) doesn't match WordPress "
                                                   "files locale ({wordpress_files_locale})."),
        "wp_wordpress_zip_file_no_translations": _("WordPress files don't have translations for the locale specified "
                                                   "in settings ({locale})"),
        "wp_wordpress_zip_file_removed_wp_content": _("Themes and plugins not specified in settings where removed from "
                                                      "wp-content/ directory from WordPress unzipped files"),
        "wp_wordpress_zip_file_version_not_valid": _("WordPress zip file version is not valid."),
        "wp_wordpress_zip_file_version_settings_latest":
            _("WordPress zip file version was not checked since settings value is 'latest'."),
        "wp_wpcli_export_db_skipping_as_set": _("I am skipping the {dump} database dump as configured in settings..."),
        "wp_wpcli_user_exists": _("User {user} already exists. Skipping user creation..."),
        "wp_plugin_tag_already_exists": _("The tag {tag_name} already exist. Are you sure it is correct?")
    }
    _errors = {
        "wp_checking_devops_toolset": _("Checking for devops-toolset in: {path}"),
        "wp_config_file_bad_themes_number": _("There are {number} themes in the configuration file (must be 1 or 2)."),
        "wp_config_file_only_one_activated_theme": _("You can only activate one theme and there are {number} themes "
                                                     "marked to be activated. Please, check the configuration file."),
        "wp_current_version": _("Current version: {version}"),
        "wp_devops_toolset_needs_update": _("devops-toolset needs to be updated."),
        "wp_devops_toolset_not_found": _("devops-toolset not found in required path: {path} "),
        "wp_devops_toolset_obtained": _("devops-toolset has been successfully downloaded on: {path}"),
        "wp_devops_toolset_obtaining": _("Obtaining latest version of devops-toolset from: {resource}"),
        "wp_devops_toolset_up_to_date": _("devops-toolset is up to date."),
        "wp_env_gt1": _("There are more than 1 matching environments in the environments JSON file."),
        "wp_env_not_found": _("Environment not found in the environments list."),
        "wp_env_x_not_found": _("Environment {environment} not found in the environments list."),
        "wp_environment_name_mandatory": _("environment-name is a mandatory parameter. I cannot continue."),
        "wp_environment_name_not_found": _("Environment name was not found. I cannot continue."),
        "wp_environment_of_type_not_found": _("The environment of type {type} was not found. I cannot continue."),
        "wp_theme_src_not_found": _("The src/development theme was not found. I cannot continue."),
        "wp_environment_path_mandatory": _("environment-path is a mandatory parameter. I cannot continue."),
        "wp_environment_path_not_found": _("Environment file path was not found. I cannot continue."),
        "wp_environment_x_found_multiple": _("Multiple environments found with name {environment}. "
                                             "I take the first one."),
        "wp_file_not_found": _("The following file was not found: {file}"),
        "wp_latest_version": _("Latest version: {version}"),
        "wp_mandatory_parameter": _("{parameter_name} is a mandatory parameter. I cannot continue"),
        "wp_not_dir": _("Path must be a dir, not a file."),
        "wp_non_valid_dir_path": _("Path must be an existent dir."),
        "wp_required_files_mandatory": _("Required files are mandatory. I cannot continue."),
        "wp_required_files_not_found": _("The required files where not found at {path}."),
        "wp_required_files_not_found_detail": _("The following required files where not found at {path}:"),
        "wp_theme_path_not_exist": _("The following theme path does not exist: {path}"),
        "wp_theme_feed_no_info": _("The {theme} theme has a source type of feed, but it has no feed configuration. "
                                   "Please, check the configuration file."),
        "wp_wordpress_path_mandatory": _("wordpress-path is a mandatory parameter. I cannot continue."),
        "wp_wordpress_zip_file_format_error": _("WordPress zip file name format is not valid."),
        "wp_wpcli_config_create_err": _("File wp-config.php cannot be created."),
        "wp_wpcli_config_set_value_err": _("Cannot set {name} property as {value}"),
        "wp_wpcli_core_install_error": _("Wordpress installation could not be done."),
        "wp_wpcli_core_version_already_downloaded": _("Wordpress {version} is already present in the specified path. "
                                                      "Skipping download..."),
        "wp_wpcli_db_export_error": _("Database dump could not be exported due to an error."),
        "wp_wpcli_db_import_error": _("Dump file could not be imported due to an error."),
        "wp_wpcli_db_query_user_creating_err": _("Database user {user} for host {host} could not be created"),
        "wp_wpcli_db_query_user_granting_err": _("Privileges could not be granted to database user {user} for host "
                                                 "{host} on schema {schema}"),
        "wp_wpcli_db_reset_error": _("Database could not be reset due to an error."),
        "wp_wpcli_delete_transients_err": _("Transients could not be deleted"),
        "wp_wpcli_downloading_wordpress_err": _("WordPress core files could not be downloaded."),
        "wp_wpcli_export_err": _("WordPress content could not be exported to {path}"),
        "wp_wpcli_option_add_error":
            _("Database option {option_name} cannot be added due to an error."),
        "wp_wpcli_option_update_error":
            _("Database option {option_name} cannot be set to {option_value} due to an error."),
        "wp_wpcli_plugin_install_err": _("Plugin {plugin_name} could not be installed due to an error."),
        "wp_wpcli_post_delete_post_type_err": _("Unable to delete content from type {post_type} due to an error."),
        "wp_wpcli_user_creating_err": _("An error occurred creating the user {user}."),
        "wp_src_theme_not_found": _("Create development theme was called but no src themes found."),
        "wp_wpcli_theme_install_error": _("Theme {theme_name} could not be installed."),
        "wp_webpack_build_error": _("Webpack build task has encountered an error for theme {theme_slug}. "
                                    "Please check above logs for more details."),
    }

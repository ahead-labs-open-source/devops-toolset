"""Unit core for the wordpress.wp_cli file"""
import pytest
import devops_toolset.project_types.wordpress.wp_cli as sut
from devops_toolset.core.app import App
from devops_toolset.core.CommandsCore import CommandsCore
from devops_toolset.core.LiteralsCore import LiteralsCore
from devops_toolset.project_types.wordpress.literals import Literals as WordpressLiterals
from devops_toolset.project_types.wordpress.commands import Commands as WordpressCommands
from unittest.mock import patch, ANY

app: App = App()
literals = LiteralsCore([WordpressLiterals])
commands = CommandsCore([WordpressCommands])

# region add_update_option


@patch("devops_toolset.project_types.wordpress.wp_cli.add_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_exists")
def test_add_update_option_should_check_if_exists(
        check_if_option_exists_mock,
        update_database_option_mock,
        add_database_option_mock,
        wordpressdata):
    """Given an option, should check if it exists in the database"""

    # Arrange
    option = wordpressdata.wp_option
    wordpress_path = wordpressdata.wordpress_path
    debug = False
    update_permalinks = False

    check_if_option_exists_mock.return_value = True, ""

    # Act
    sut.add_update_option(option, wordpress_path, debug, update_permalinks)

    # Assert
    check_if_option_exists_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_cli.add_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_exists")
def test_add_update_option_when_exists_calls_update_function(
        check_if_option_exists_mock,
        update_database_option_mock,
        add_database_option_mock,
        wordpressdata):
    """Given an option that exists, should call the update function"""

    # Arrange
    option = wordpressdata.wp_option
    wordpress_path = wordpressdata.wordpress_path
    debug = False
    update_permalinks = False

    check_if_option_exists_mock.return_value = True, ""

    # Act
    sut.add_update_option(option, wordpress_path, debug, update_permalinks)

    # Assert
    update_database_option_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_cli.add_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_exists")
def test_add_update_option_when_not_exists_calls_add_function(
        check_if_option_exists_mock,
        update_database_option_mock,
        add_database_option_mock,
        wordpressdata):
    """Given an option that doesn't exist, should call the update function"""

    # Arrange
    option = wordpressdata.wp_option
    wordpress_path = wordpressdata.wordpress_path
    debug = False
    update_permalinks = False

    check_if_option_exists_mock.return_value = False, None

    # Act
    sut.add_update_option(option, wordpress_path, debug, update_permalinks)

    # Assert
    add_database_option_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_cli.add_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.update_database_option")
@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_exists")
@patch("devops_toolset.tools.cli.call_subprocess")
def test_add_update_option_should_update_permalinks_when_structure_is_updated(
        call_subprocess_mock,
        check_if_option_exists_mock,
        update_database_option_mock,
        add_database_option_mock,
        wordpressdata):
    """Given an option, if it is the permalink_structure option, permalinks
    should be updated afterwards"""

    # Arrange
    option = wordpressdata.wp_option
    wordpress_path = wordpressdata.wordpress_path
    debug = False
    update_permalinks = True

    check_if_option_exists_mock.return_value = True, wordpressdata.wp_option["value"]

    # Act
    sut.add_update_option(option, wordpress_path, debug, update_permalinks)

    # Assert
    call_subprocess_mock.assert_called_once()

# endregion

# region add_database_option


@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_exists")
@patch("devops_toolset.tools.cli.call_subprocess")
def test_add_database_option_should_check_if_exists(
        call_subprocess_mock,
        check_if_option_exists_mock,
        wordpressdata):
    """Given an option, should check if it exists in the database"""

    # Arrange
    option = wordpressdata.wp_option
    wordpress_path = wordpressdata.wordpress_path
    debug = False

    check_if_option_exists_mock.return_value = True, wordpressdata.wp_option["value"]

    # Act
    sut.add_database_option(
        option["name"], option["value"],
        wordpress_path, debug, option["autoload"])

    # Assert
    check_if_option_exists_mock.assert_called_once()


@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_is_valid")
@patch("devops_toolset.project_types.wordpress.wp_cli.check_if_option_exists")
@patch("devops_toolset.tools.cli.call_subprocess")
def test_add_database_option_when_not_exists_calls_add_function(
        call_subprocess_mock,
        check_if_option_exists_mock,
        check_if_option_is_valid_mock,
        wordpressdata):
    """Given an option, if it doesn't exist must call add function"""

    # Arrange
    option = wordpressdata.wp_option
    wordpress_path = wordpressdata.wordpress_path
    debug = False

    check_if_option_exists_mock.return_value = False, None
    check_if_option_is_valid_mock.return_value = True

    # Act
    sut.add_database_option(
        option["name"], option["value"],
        wordpress_path, debug, option["autoload"])

    # Assert
    call_subprocess_mock.assert_called_once()

# endregion

# region check_if_option_exists


@patch("devops_toolset.tools.cli.call_subprocess_with_result")
@pytest.mark.parametrize("exists, option_value, expected", [
    (True, "value\n", (True, "value")),
    (False, None, (False, None))
])
def test_check_if_option_exists_returns_boolean(
        call_subprocess_with_result_mock,
        exists,
        option_value,
        expected,
        wordpressdata):
    """Given an option name, must return a boolean that indicates if exists"""

    # Arrange
    option_name = "name"
    wordpress_path = wordpressdata.wordpress_path
    debug = False

    call_subprocess_with_result_mock.return_value = option_value

    # Act
    result = sut.check_if_option_exists(option_name, wordpress_path, debug)

    # Assert
    assert result == expected

# endregion

# region check_if_option_is_valid


@pytest.mark.parametrize("name, value, autoload, expected", [
    ("name", "", True, True),
    ("name", None, True, False),
    ("", "value", True, False),
    (None, "value", True, False),
    ("name", "value", None, False)
])
def test_check_if_option_is_valid(name, value, autoload, expected):
    """When option data is given, returns True when all three parameters are
    valid"""

    # Arrange

    # Act
    result = sut.check_if_option_is_valid(name, value, autoload)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_autoload


@pytest.mark.parametrize("value, expected", [
    (True, "--autoload=yes"),
    (False, "--autoload=no")])
def test_convert_wp_parameter_autoload(value, expected):
    """When True , returns a --autoload="yes".
    When False , returns a --autoload="no".
    """

    # Arrange

    # Act
    result = sut.convert_wp_parameter_autoload(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_db_user


@pytest.mark.parametrize("value, expected", [
    ("user", "--dbuser=\"user\""),
    ("", ""),
    (None, "")])
def test_convert_wp_parameter_db_user(value, expected):
    """When not None or "", returns a --dbuser="value"."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_db_user(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_db_pass


@pytest.mark.parametrize("value, expected", [
    ("password", "--dbpass=\"password\""),
    ("", ""),
    (None, "")])
def test_convert_wp_parameter_db_pass(value, expected):
    """When not None or "", returns a --dbpass="value"."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_db_pass(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_activate


@pytest.mark.parametrize("value, expected", [(True, "--activate"), (False, "")])
def test_convert_wp_parameter_activate(value, expected):
    """When True, returns a --activate string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_activate(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_admin_password


@pytest.mark.parametrize(
    "value, expected",
    [("my-admin-password", "--admin_password=" + "\"" + "my-admin-password" + "\""),
     ("", "")])
def test_convert_wp_parameter_admin_password_when_admin_pass_then_return_admin_pass_parameter(
        value, expected):
    """ Given admin_password str, when it has content, then return --admin_password token"""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_admin_password(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_content


@pytest.mark.parametrize("value, expected", [(True, "no"), (False, "yes")])
def test_convert_wp_parameter_content(value, expected):
    """When True, returns a "no" string.
    When False, returns a "yes" string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_content(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_debug


@pytest.mark.parametrize("value, expected", [(True, "--debug"), (False, "")])
def test_convert_wp_parameter_debug(value, expected):
    """When True, returns a --debug string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_debug(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_force


@pytest.mark.parametrize("value, expected", [(True, "--force"), (False, "")])
def test_convert_wp_parameter_force(value, expected):
    """When True, returns a --force string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_force(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_raw


@pytest.mark.parametrize("value, expected", [(True, "--raw"), (False, "")])
def test_convert_wp_parameter_raw(value, expected):
    """When True, returns a --raw string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_raw(value)

    # Assert
    assert result == expected

# endregion


# region convert_wp_parameter_autoload


@pytest.mark.parametrize("value, expected", [
    (True, "--send-email"),
    (False, "")])
def test_convert_wp_parameter_send_email(value, expected):
    """When True , returns a --send-email.
    When False , returns an empty string.
    """

    # Arrange

    # Act
    result = sut.convert_wp_parameter_send_email(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_skip_check


@pytest.mark.parametrize("value, expected", [(True, "--skip-check"), (False, "")])
def test_convert_wp_parameter_skip_check(value, expected):
    """When True, returns a --skip-content string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_skip_check(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_skip_content


@pytest.mark.parametrize("value, expected", [(True, "--skip-content"), (False, "")])
def test_convert_wp_parameter_skip_content(value, expected):
    """When True, returns a --skip-content string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_skip_content(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_skip_email


@pytest.mark.parametrize("value, expected", [(True, "--skip-email"), (False, "")])
def test_convert_wp_parameter_skip_email(value, expected):
    """When True, returns a --skip-content string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_skip_email(value)

    # Assert
    assert result == expected

# endregion

# region convert_wp_parameter_yes


@pytest.mark.parametrize("value, expected", [(True, "--yes"), (False, "")])
def test_convert_wp_parameter_yes(value, expected):
    """When True, returns a --yes string.
    When False, returns an empty string."""

    # Arrange

    # Act
    result = sut.convert_wp_parameter_yes(value)

    # Assert
    assert result == expected

# endregion

# region import_database()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_import_database(call_subprocess, wordpressdata):
    """Given arguments, calls subprocess"""

    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    dump_file_path = wordpressdata.dump_file_path
    debug = False

    # Act
    sut.import_database(wordpress_path, dump_file_path, debug)

    # Assert
    call_subprocess.assert_called_once_with(commands.get("wpcli_db_import").format(
        file=dump_file_path, path=wordpress_path, debug_info=sut.convert_wp_parameter_debug(debug)),
        log_before_process=ANY, log_after_err=ANY)

# endregion

# region reset_database()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_reset_database(call_subprocess, wordpressdata):
    """Given arguments, calls subprocess"""

    # Arrange
    wordpress_path = wordpressdata.wordpress_path
    quiet = True
    debug = False

    # Act
    sut.reset_database(wordpress_path, quiet, debug)

    # Assert
    call_subprocess.assert_called_once_with(commands.get("wpcli_db_reset").format(
        path=wordpress_path, yes=sut.convert_wp_parameter_yes(quiet), debug_info=sut.convert_wp_parameter_debug(debug)),
        log_before_process=ANY, log_after_err=ANY)

# endregion

# region reset_transients()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_reset_transients(call_subprocess):
    """Given arguments, when the method is called, then delete transients"""

    # Arrange
    wordpress_path = ""

    # Act
    sut.reset_transients(wordpress_path)

    # Assert
    call_subprocess.assert_called()

# endregion

# region wp_cli_info()

@patch("devops_toolset.tools.cli.call_subprocess")
def test_wp_cli_info(call_subprocess):
    """Calls subprocess with the required command"""
    # Arrange
    info_command = "wpcli_info"
    log_before_literals = [literals.get("wp_wpcli_install_ok"), literals.get("wp_wpcli_info")]
    log_after_literals = [literals.get("wp_wpcli_add_ev")]
    # Act
    sut.wp_cli_info()
    # Assert
    call_subprocess.assert_called_once_with(
        commands.get(info_command), log_before_out=log_before_literals, log_after_out=log_after_literals)

# endregion

# region create_wordpress_database_user()


@patch("devops_toolset.tools.cli.call_subprocess")
@pytest.mark.skip(reason="Need to fix this test")
def test_create_wordpress_database_user(call_subprocess):
    """Given arguments, when the method is called, then creates a db user"""

    # Arrange
    wordpress_path = ""
    user_name = "user1"
    user_p = "pass"
    schema = "db1"
    host = "localhost"
    privileges = "create, alter, select, insert, update, delete"

    # Act
    sut.create_wordpress_database_user(wordpress_path, user_name, user_p, schema, host, privileges)

    # Assert
    call_subprocess.assert_called()

# endregion

# region create_wordpress_database_user()


@patch("devops_toolset.tools.cli.call_subprocess")
def test_export_content_to_wxr(call_subprocess):
    """Given arguments, when the method is called, then exports WordPress
    content"""

    # Arrange
    wordpress_path = ""
    destination_path = ""
    wxr_file_suffix = "suffix"

    # Act
    sut.export_content_to_wxr(wordpress_path, destination_path, wxr_file_suffix)

    # Assert
    call_subprocess.assert_called()

# endregion

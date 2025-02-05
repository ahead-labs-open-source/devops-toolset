""" Unit core for the log_tools script """
import devops_toolset as sut
import logging
from unittest.mock import call, patch

# region log_list(list[str], level)


@patch.object(logging, "log")
def test_log_list_given_list_of_log_str_when_list_is_invalid_then_not_log(logging_mock):
    """ Given a list of strings to log and a loglevel, when the list is invalid, then
    pass away and don't log everything at all """
    # Arrange
    log_list = []
    loglevel = sut.LogLevel.info
    # Act
    sut.log_list(log_list, loglevel)
    # Assert
    logging_mock.assert_not_called()


@patch.object(logging, "log")
def test_log_list_given_list_of_log_str_and_loglevel_then_calls_logging_for_each_line(logging_mock):
    """ Given a list of strings to log and a loglevel, then calls logging with passed level for
    each string of the list"""
    # Arrange
    log_list = ["log1", "log2"]
    loglevel = sut.LogLevel.info
    logging.getLogger(__name__)
    # Act
    sut.log_list(log_list, loglevel)
    # Assert
    calls = [call(loglevel.value[0], log_list[0]), call(loglevel.value[0], log_list[1])]
    logging_mock.assert_has_calls(calls, any_order=True)

# endregion

# region log_stdouterr(output, level)


@patch.object(logging, "log")
def test_log_stdouterr_given_bytes_output_and_loglevel_then_calls_logging_decoding_lines_on_utf8(logging_mock):
    """ Given a list of strings to log and a loglevel, then calls logging with passed level for
    each string of the list"""
    # Arrange
    output = b'line1\r\nline2'
    loglevel = sut.LogLevel.info
    # Act
    sut.log_stdouterr(output, loglevel)
    # Assert
    calls = [call(loglevel.value[0], 'line1'), call(loglevel.value[0], 'line2')]
    logging_mock.assert_has_calls(calls, any_order=True)

# endregion

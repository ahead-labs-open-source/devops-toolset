""" Unit core for the xmlparser file"""
from unittest.mock import patch

from devops_toolset import XMLParser

# region parse_from_path


@patch("xml.etree.ElementTree.parse")
@patch("os.path.exists")
def test_parse_from_path_when_xml_path_exist_then_calls_et_parse(exist_mock, parse_mock, paths):
    """ Given xml path, when path exist, then should call ET.parse """
    # Arrange
    xml_path = paths.xml_path
    exist_mock.return_value = True

    # Act
    sut = XMLParser()
    sut.parse_from_path(xml_path)

    # Assert
    parse_mock.assert_called()


@patch("os.path.exists")
def test_parse_from_path_when_xml_path_not_exist_then_assigns_xml_file_as_empty(exist_mock, paths):
    """ Given xml path, when path not exist, then should set xml file as empty """
    # Arrange
    xml_path = paths.xml_path
    exist_mock.return_value = False
    # Act
    sut = XMLParser()
    sut.parse_from_path(xml_path)
    # Assert
    assert sut.xml_file == ""

# endregion

# region parse_from_content


def test_parse_from_content_given_content_then_set_xml_file_as_content(paths):
    """ Given xml str content, should set xml_file as content """
    # Arrange
    xml_content = \
        "<project><name>devops-toolset</name><version>0.34.0</version><organization>aheadlabs</organization></project>"
    # Act
    sut = XMLParser()
    sut.parse_from_content(xml_content)
    # Assert
    assert sut.xml_file != ""

# endregion

# region get_attribute_value


def test_get_attribute_value_given_name_when_xml_file_then_return_find(paths):
    """ Given attribute name, when xml_file has value, then return find attribute value """
    # Arrange
    xml_content = \
        "<project><name>devops-toolset</name></project>"
    attribute_name = "name"
    expected_attribute_value = "devops-toolset"
    # Act
    sut = XMLParser()
    sut.parse_from_content(xml_content)
    result = sut.get_attribute_value(attribute_name)
    # Assert
    assert result == expected_attribute_value

# endregion

"""XML toolset to interact and parse xml files"""

import xml.etree.ElementTree as ET
import os.path


class XMLParser(object):
    """ Class to to interact to xml files """

    def __init__(self):
        self.xml_file = ""

    def parse_from_path(self, xmlpath: str):
        """ Parses an xml file from a path and assign to xml_file
        Args
            xmlpath: Path to retrieve the xml file from
        """
        if os.path.exists(xmlpath):
            self.xml_file = ET.parse(xmlpath)

    def parse_from_content(self, content: str):
        """ Parses an xml file from an xml string content
                Args
                    content: The xml content to parse from
                """
        self.xml_file = ET.fromstring(content)

    def get_attribute_value(self, attribute_name: str) -> str:
        """ Gets a string containing a value of the attribute requested inside the xml_file
                Args
                    attribute_name: Name of the attribute which value will be recovered
                """
        if self.xml_file:
            return self.xml_file.find(attribute_name).text

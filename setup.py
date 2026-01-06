"""Project setup"""
import pathlib
import xml.etree.ElementTree as ET
import setuptools

root_path: pathlib.Path = pathlib.Path(__file__).parent

with open(pathlib.Path(root_path, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(pathlib.Path(root_path, "requirements.txt"), "r", encoding="utf-8") as req_file:
    install_requires = req_file.read().splitlines()

def _read_project_xml_metadata(project_xml_path: pathlib.Path) -> tuple[str, str]:
    tree = ET.parse(project_xml_path)
    root = tree.getroot()

    name_node = root.find("name")
    version_node = root.find("version")
    if name_node is None or not (name_node.text or "").strip():
        raise ValueError("Missing <name> in project.xml")
    if version_node is None or not (version_node.text or "").strip():
        raise ValueError("Missing <version> in project.xml")

    return name_node.text.strip(), version_node.text.strip()


name, version = _read_project_xml_metadata(pathlib.Path(root_path, "project.xml"))

setuptools.setup(
    name=name,
    version=version,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=install_requires,
    include_package_data=True,
    package_data={"devops_toolset.core": ["*.json"],
                  "devops_toolset.locales": ["**/LC_MESSAGES/*.mo"]},
    url='https://github.com/aheadlabs/devops-toolset/',
    license='https://github.com/aheadlabs/devops-toolset/blob/master/LICENSE',
    author='Ivan Sainz | Alberto Carbonell',
    author_email='aheadlabs@gmail.com',
    description='General purpose DevOps-related scripts and tools.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9"
)

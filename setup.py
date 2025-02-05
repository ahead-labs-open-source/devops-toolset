"""Project setup"""
import pathlib
import setuptools
import devops_toolset as parsers

root_path: pathlib.Path = pathlib.Path(__file__).parent

with open(pathlib.Path(root_path, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(pathlib.Path(root_path, "requirements.txt"), "r", encoding="utf-8") as req_file:
    install_requires = req_file.read().splitlines()

project_xml_parsed = parsers.parse_project_xml_data(False)
name = project_xml_parsed["PROJECT_NAME"]
version = project_xml_parsed["PROJECT_VERSION"]

setuptools.setup(
    name=name,
    version=version,
    classifiers=[
        "Programming Language :: Python :: 3",
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

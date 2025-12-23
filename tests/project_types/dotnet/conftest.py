"""Test configuration file for dotnet package.

This code is executed once per unit test session.
Add here whatever you want to pass as a fixture in your core.

    ie: (see FileNames example)
        - Add a class that contains what you want to pass as a fixture in your core.
        - Create a fixture with that same lowered name that returns an instance to that class."""

import typing
import pytest


class DotNetData(object):
    """Class used to create the dotnetdata fixture"""

    csproj_file_content = "<Project><PropertyGroup><Version>6.6.6</Version></PropertyGroup></Project>"
    dddd_webapi_template = "{\"settings\":{\"create_folders\":{\"physical\":true,\"solution\":true}," \
                           "\"default_frameworks\":{\"classlib\":\"net6.0\",\"webapi\":\"net6.0\"," \
                           "\"webapiminimal\":\"net6.0\",\"xunit\":\"net6.0\"},\"git_exclusions\":[\".vs/\"," \
                           "\".vscode/\",\".idea/\",\"obj/\",\"bin/\"],\"relational_database_engine\":\"mysql\"," \
                           "\"skip_unit_tests\":false},\"layers\":[{\"name\":\"4. Traverse infrastructure layer\"," \
                           "\"projects\":[{\"name\":\"Settings\",\"template\":\"classlib\",\"references\":[]," \
                           "\"packages\":[\"DotnetToolset|*\"],\"unit-test-eligible\":false, " \
                           "\"framework\": \"net6.0\"}]},{\"name\":\"3. Persistence infrastructure layer\"," \
                           "\"projects\":[{\"name\":\"DataModel\",\"template\":\"classlib\",\"references\":[]," \
                           "\"packages\":[\"Microsoft.EntityFrameworkCore.Design|*\"],\"unit-test-eligible\":false}," \
                           "{\"name\":\"Data\",\"template\":\"classlib\",\"references\":[\"DataModel\",\"Settings\"]," \
                           "\"packages\":[\"CsvHelper|*\",\"DotnetToolset|*\"," \
                           "\"Microsoft.EntityFrameworkCore.Design|*\",\"Newtonsoft.Json|*\"," \
                           "\"Pomelo.EntityFrameworkCore.MySql|*\"],\"unit-test-eligible\":true}]}," \
                           "{\"name\":\"2. Domain layer\",\"projects\":[{\"name\":\"Domain\"," \
                           "\"template\":\"classlib\",\"references\":[\"Data\",\"DataModel\",\"Settings\"]," \
                           "\"packages\":[\"DotnetRepository|*\",\"DotnetToolset|*\",\"DotnetToolset.Patterns|*\"," \
                           "\"Microsoft.EntityFrameworkCore|*\"],\"unit-test-eligible\":true}]}," \
                           "{\"name\":\"1. Application layer\",\"projects\":[{\"name\":\"Application\"," \
                           "\"template\":\"classlib\",\"references\":[\"Data\",\"Domain\"]," \
                           "\"packages\":[\"AutoMapper|*\",\"DotnetRepository|*\",\"DotnetToolset|*\"," \
                           "\"DotnetToolset.Patterns|*\"],\"unit-test-eligible\":true}]}," \
                           "{\"name\":\"0. Distributed services layer\",\"projects\":[{\"name\":\"Api\"," \
                           "\"template\":\"webapi\",\"template_options\":\"-minimal\"," \
                           "\"references\":[\"Application\",\"Settings\"]," \
                           "\"packages\":[\"AutoMapper.Extensions.Microsoft.DependencyInjection|*\"," \
                           "\"Microsoft.AspNetCore.Authentication.JwtBearer|*\"," \
                           "\"Microsoft.EntityFrameworkCore.Tools|*\"],\"unit-test-eligible\":true," \
                           "\"startup_project\":true}]}]}"
    project_config = {
        "project_name": "MySolutionApi",
        "template": "webapi",
        "framework": "net6.0",
        "solution_path": "pathto/solution",
        "solution_name": "MySolution",
        "solution_folder": "MySolutionFolder",
        "project_path": "pathto/project",
        "references": ["DataModel", "Settings"],
        "packages": ["DotnetToolset|*"],
        "unit-test-eligible": True
    }
    project_layers = {
        "MySolutionSettings": "4. Traverse infrastructure layer",
        "MySolutionDataModel": "3. Persistence infrastructure layer",
        "MySolutionData": "3. Persistence infrastructure layer",
        "MySolutionDomain": "2. Domain layer",
        "MySolutionApplication": "1. Application layer",
        "MySolutionApi": "0. Distributed services layer",
    }
    project_path = "pathto/project"
    solution_path = "pathto/solution"
    template_config_git_exclusions = {
        "settings": {
            "git_exclusions": [
                ".vs/", ".vscode/", ".idea/", "obj/", "bin/"
            ]
        }
    }
    template_config_pass_unit_tests = {
        "settings": {
            "skip_unit_tests": False,
            "default_frameworks": {
                "xunit": "net6.0"
            }
        }
    }
    template_config_skip_unit_tests = {
        "settings": {
            "skip_unit_tests": True
        }
    }

    @staticmethod
    def get_appsettings_files() -> typing.Generator:
        for file in ["appsettings.Development.json", "appsettings.Staging.json", "appsettings.Production.json"]:
            yield file

    @staticmethod
    def get_wrong_appsettings_files() -> typing.Generator:
        for file in ["appsettings.1.json", "appsettings.2.json"]:
            yield file


class MigrationsData(object):
    """Class used to create the migrationsdata fixture"""

    one_migration_and_applied = \
        "[{\"id\":\"20220529212511_Init-V1\",\"name\":\"Init-V1\",\"safeName\":\"Init-V1\",\"applied\":true}," \
        "{\"id\":\"20220529212512_Second-V2\",\"name\":\"Second-V2\",\"safeName\":\"Second-V2\",\"applied\":false}]"

    migrations_list_command_result = \
        "info: Microsoft.EntityFrameworkCore.Infrastructure[10403]\n" \
        "      Executed DbCommand (22ms) [Parameters=[], CommandType='Text', CommandTimeout='30']\n" \
        "[{\"id\":\"20220529212511_Init-V1\",\"name\":\"Init-V1\",\"safeName\":\"Init-V1\",\"applied\":true}]"


@pytest.fixture
def dotnetdata():
    """Sample data for testing .NET related functionality"""
    return DotNetData()


@pytest.fixture
def migrationsdata():
    """Sample data for testing Entity Framework functionality"""
    return MigrationsData()

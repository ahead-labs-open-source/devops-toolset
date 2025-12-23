"""Provides support for deployment operations in Azure API Management service."""
import json
import logging
import yaml

from devops_toolset.core import log_tools
from devops_toolset.core.app import App
from devops_toolset.core.commands_core import CommandsCore
from devops_toolset.core.literals_core import LiteralsCore
from devops_toolset.filesystem.paths import get_file_paths_in_tree
from devops_toolset.project_types.azure.commands import Commands as AzureCommands
from devops_toolset.project_types.azure.literals import Literals as AzureLiterals
from devops_toolset.tools import cli

app: App = App()
literals = LiteralsCore([AzureLiterals])
commands = CommandsCore([AzureCommands])


def check_apim_exists(resource_group_name, apim_name):
    """Checks if an API Management service exists.

    Args:
        resource_group_name: The name of the resource group.
        apim_name: The name of the API Management service.

    Returns:
        True if the API Management service exists, False otherwise.
    """

    logging.info(literals.get("azure_cli_apim_checking").format(name=apim_name))
    result = cli.call_subprocess_with_result(commands.get("azure_cli_apim_exists")
                                             .format(resource_group_name=resource_group_name, name=apim_name))

    if isinstance(result, str) and 'ResourceNotFound' not in result:
        logging.info(literals.get("azure_cli_apim_exists").format(name=apim_name))
        return True
    elif isinstance(result, tuple) and 'ResourceNotFound' in result[1]:
        logging.info(literals.get("azure_cli_apim_not_exists").format(name=apim_name))
        return False
    else:
        logging.error(literals.get("azure_cli_apim_check_failed").format(name=apim_name))
        return False


def get_apim_apis(resource_group_name, apim_name):
    """Gets the list of APIs in an API Management service.

    Args:
        resource_group_name: The name of the resource group.
        apim_name: The name of the API Management service.

    Returns:
        List of APIs in the API Management service or None if none found.
    """

    logging.info(literals.get("azure_cli_apim_getting_apis").format(name=apim_name))
    result = cli.call_subprocess_with_result(commands.get("azure_cli_apim_get_apis")
                                             .format(resource_group_name=resource_group_name, name=apim_name))

    if isinstance(result, str):
        try:
            json_result = json.loads(result)
            logging.info(literals.get("azure_cli_apim_apis_found").format(number=len(json_result), name=apim_name))
            log_tools.log_list(['\t' + api.get('displayName') for api in json_result])
            return json_result
        except json.JSONDecodeError:
            logging.error(literals.get("azure_cli_command_output").format(output=result))
            return None
    else:
        logging.error(literals.get("azure_cli_apim_apis_not_found").format(name=apim_name))
        if isinstance(result, tuple):
            logging.error(result[1])
        else:
            logging.error(result)
        return None


def get_openapi_contracts(base_path):
    """Gets all OpenAPI contracts from a path with a specific structure.

    Args:
        base_path: The path where the OpenAPI contracts are located.

    Returns:
        List of OpenAPI contracts.
    """

    # Get a list of all OpenAPI contracts paths
    contract_paths = get_file_paths_in_tree(base_path, "*.openapi.y*ml")
    logging.info(literals.get("openapi_contracts_found").format(number=len(contract_paths), directory=base_path))
    log_tools.log_list(["\t" + str(path) for path in contract_paths])

    # Parse the contracts and filter out the ones that don't have a x-deploy property with value true
    contracts = [contract for contract in contract_paths if is_openapi_contract_deployable(contract)]
    logging.info(literals.get("openapi_contracts_found_deployable").format(number=len(contracts)))
    log_tools.log_list(["\t" + str(path) for path in contracts])

    return contracts


def is_openapi_contract_deployable(contract_path):
    """Checks if an OpenAPI contract is deployable based on the existence of the x-deploy OpenAPI extended property.

    Args:
        contract_path: The path to the OpenAPI contract.

    Returns:
        True if the contract is deployable, False otherwise.
    """

    with open(contract_path, 'r') as contract_file:
        contract = yaml.safe_load(contract_file)
        return contract.get('x-deploy', False)

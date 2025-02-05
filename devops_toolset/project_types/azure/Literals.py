"""Azure module literals"""

from devops_toolset.core.app import App
from devops_toolset.core.ValueDictsBase import ValueDictsBase
import gettext

app: App = App()
_ = gettext.gettext


class Literals(ValueDictsBase):
    """ValueDicts for the Azure module."""

    _info = {
        "azure_cli_apim_apis_found": _("Found {number} APIs in API Management service {name}."),
        "azure_cli_apim_apis_not_found": _("No APIs found in API Management service {name}."),
        "azure_cli_apim_check_failed": _("Failed to check if API Management service {name} exists."),
        "azure_cli_apim_checking": _("Checking if API Management service {name} exists..."),
        "azure_cli_apim_exists": _("API Management service {name} exists."),
        "azure_cli_apim_getting_apis": _("Getting APIs from API Management service {name}..."),
        "azure_cli_apim_not_exists": _("API Management service {name} does not exist."),
        "azure_cli_command_output": _("I got this output from the Azure CLI command:\n{output}"),
        "azure_cli_resource_group_checking": _("Checking if resource group {name} exists..."),
        "azure_cli_resource_group_created": _("Resource group {name} created."),
        "azure_cli_resource_group_creating": _("Creating resource group {name}..."),
        "azure_cli_resource_group_delete_failed": _("Resource group '{name}' deleted."),
        "azure_cli_resource_group_deleting": _("Deleting resource group '{name}'..."),
        "azure_cli_resource_group_deleted": _("Resource group '{name}' deleted."),
        "azure_cli_resource_group_exists": _("Resource group {name} exists."),
        "azure_cli_resource_group_not_exists": _("Resource group {name} does not exist."),
        "azure_cli_executing_command": _("Executing command => {command}"),
        "azure_cli_logging_in_service_principal":
            _("Logging into Azure using service principal {service_principal} on tenant {tenant}"),
        "azure_cli_logging_out":
            _("Logging out from Azure (current logged in account)"),
        "openapi_contracts_found": _("Found {number} OpenAPI contracts in {directory}."),
        "openapi_contracts_found_deployable": _("Parsed {number} deployable OpenAPI contracts."),
    }
    _errors = {
        "azure_cli_db_mysql_flexible_server_execute_file_query_parameters_error":
            _("You must either pass a SQL file path or SQL query text to be executed."),
        "azure_mysql_script_not_found":
            _("Script {file_path} was not found. Skipping mysql execute action...")
    }

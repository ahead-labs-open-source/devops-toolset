"""Azure module literals"""

from devops_toolset.core.app import App
from devops_toolset.core.value_dicts_base import ValueDictsBase

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the Azure module."""

    _info = {
        "azure_cli_command_output": _("I got this output from the Azure CLI command:\n{output}"),
        "azure_cli_executing_command": _("Executing command => {command}"),
        "azure_cli_logging_in_service_principal":
            _("Logging into Azure using service principal {service_principal} on tenant {tenant}"),
        "azure_cli_logging_out":
            _("Logging out from Azure (current logged in account)"),

        # API Management (APIM)
        "azure_cli_apim_checking": _("Checking if APIM service '{name}' exists..."),
        "azure_cli_apim_exists": _("APIM service '{name}' exists."),
        "azure_cli_apim_not_exists": _("APIM service '{name}' does not exist."),
        "azure_cli_apim_check_failed": _("APIM service '{name}' existence check failed."),
        "azure_cli_apim_getting_apis": _("Getting APIs from APIM service '{name}'..."),
        "azure_cli_apim_apis_found": _("Found {number} APIs in APIM service '{name}'."),
        "azure_cli_apim_apis_not_found": _("Could not retrieve APIs from APIM service '{name}'."),

        # OpenAPI contracts
        "openapi_contracts_found": _("Found {number} OpenAPI contract(s) in '{directory}'."),
        "openapi_contracts_found_deployable": _("Found {number} deployable OpenAPI contract(s)."),
    }
    _errors = {
        "azure_cli_db_mysql_flexible_server_execute_file_query_parameters_error":
            _("You must either pass a SQL file path or SQL query text to be executed."),
        "azure_mysql_script_not_found":
            _("Script {file_path} was not found. Skipping mysql execute action...")
    }

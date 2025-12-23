"""dotnet module commands"""

from devops_toolset.core.value_dicts_base import ValueDictsBase
from devops_toolset.core.app import App
from enum import Enum

app: App = App()


class Log(Enum):
    """Log level for Azure CLI commands"""
    OFF = 0
    VERBOSE = 1
    DEBUG = 2


class Commands(ValueDictsBase):
    """ Commands for the project_types/azure module."""

    # Add your dotnet commands dictionaries here
    _commands = {
        "azure_cli_db_mysql_flexible_server_execute":
            "az mysql flexible-server execute -n {server_name} -u {admin_user} -p {admin_password} "
            "-d {database_name} {file_path} {query} {log}",
        "azure_cli_db_mysql_flexible_server_firewall_rule_create":
            "az mysql flexible-server firewall-rule create -n {server_name} -g {resource_group} "
            "-r {rule_name} --start-ip-address {start_ip_address} --end-ip-address {end_ip_address} {log}",
        "azure_cli_db_mysql_flexible_server_firewall_rule_delete":
            "az mysql flexible-server firewall-rule delete -n {server_name} -g {resource_group} "
            "-r {rule_name} -y {log}",
        "azure_cli_extension_list": "az extension list",
        "azure_cli_extension_add": "az extension add --name {name}",
        "azure_cli_login_service_principal": "az login --service-principal -u {user}  -p {secret} --tenant {tenant}",
        "azure_cli_logout": "az logout",
    }

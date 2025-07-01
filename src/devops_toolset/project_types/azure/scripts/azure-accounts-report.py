"""
Lists all Azure accounts and shows which one is currently active using Azure CLI (az).

This script runs 'az account list' to show all accounts and 'az account show' to display the active account.

Requirements:
  - Azure CLI (az) must be installed and available in PATH.
  - You must be logged in to Azure CLI (run 'az login' if needed).

No arguments are required.
"""

import json
from devops_toolset.tools import cli
from devops_toolset.project_types.azure.commands import Commands as AzureCommands
from devops_toolset.core.CommandsCore import CommandsCore

def main():
    commands = CommandsCore([AzureCommands])
    account_list_cmd = commands.get("azure_cli_account_list")
    account_show_cmd = commands.get("azure_cli_account_show")

    # Get all accounts
    accounts_result = cli.call_subprocess_with_result(account_list_cmd)
    
    # Get the current active account
    current_result = cli.call_subprocess_with_result(account_show_cmd)

    try:
        accounts = json.loads(accounts_result[0] if isinstance(accounts_result, tuple) else accounts_result)
    except Exception as e:
        print("Error parsing accounts list:", e)
        print(accounts_result)
        return

    try:
        current = json.loads(current_result[0] if isinstance(current_result, tuple) else current_result)
    except Exception as e:
        print("Error parsing current account:", e)
        print(current_result)
        return

    print("\nAzure Accounts:")
    for acc in accounts:
        marker = "<-- ACTIVE" if acc.get("id") == current.get("id") else ""
        print(f"- {acc.get('name')} ({acc.get('id')}) {marker}")
    print("\nCurrent active account:")
    print(json.dumps(current, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 
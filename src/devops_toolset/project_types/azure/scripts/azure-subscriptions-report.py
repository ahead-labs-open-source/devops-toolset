"""
Lists all Azure subscriptions for the currently logged-in user using the Azure CLI (az).

This script executes the 'az account subscription list' command and prints the result as pretty-printed JSON.

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
    az_command = commands.get("azure_cli_subscription_list")
    result = cli.call_subprocess_with_result(az_command)
    if result:
        if isinstance(result, tuple):
            output, error = result
            if error:
                print("Error executing command az:", error)
            result_str = output
        else:
            result_str = result
        try:
            subscriptions = json.loads(result_str)
            print(json.dumps(subscriptions, indent=2, ensure_ascii=False))
        except Exception as e:
            print("Error parsing subscriptions output:", e)
            print(result_str)
    else:
        print("No result was obtained from the az command.")

if __name__ == "__main__":
    main()

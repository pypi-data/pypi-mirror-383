"""Azure CLI command wrappers for MCP server.

This module provides Python wrapper functions for Azure CLI commands.
All commands are read-only and return structured JSON data.
"""

import json
import subprocess
from typing import Any, Dict, List, Optional


class AzureCliError(Exception):
    """Exception raised when Azure CLI command fails."""
    pass


def _run_az_command(command: List[str]) -> Any:
    """Run an Azure CLI command and return parsed JSON output.

    Args:
        command: List of command arguments (e.g., ['az', 'group', 'list'])

    Returns:
        Parsed JSON output from the Azure CLI command

    Raises:
        AzureCliError: If the command fails or returns invalid JSON
    """
    try:
        # Add --output json to ensure JSON format
        if '--output' not in command and '-o' not in command:
            command.extend(['--output', 'json'])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )

        # Parse JSON output
        if result.stdout:
            return json.loads(result.stdout)
        return None

    except subprocess.CalledProcessError as e:
        error_msg = f"Azure CLI command failed: {' '.join(command)}\nError: {e.stderr}"
        raise AzureCliError(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON output from: {' '.join(command)}\nOutput: {result.stdout}"
        raise AzureCliError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error running command: {' '.join(command)}\nError: {str(e)}"
        raise AzureCliError(error_msg) from e


def list_resource_groups() -> List[Dict[str, Any]]:
    """List all resource groups in the Azure subscription.

    Returns:
        List of resource group objects with properties like name, location, id, etc.

    Example output:
        [
            {
                "id": "/subscriptions/.../resourceGroups/rg-example",
                "name": "rg-example",
                "location": "eastus",
                "properties": {"provisioningState": "Succeeded"},
                "tags": {}
            }
        ]
    """
    return _run_az_command(['az', 'group', 'list'])


def list_resources_in_group(resource_group: str) -> List[Dict[str, Any]]:
    """List all resources in a specific resource group.

    Args:
        resource_group: Name of the resource group

    Returns:
        List of resource objects with properties like name, type, location, etc.

    Example output:
        [
            {
                "id": "/subscriptions/.../resourceGroups/rg-example/providers/...",
                "name": "storage-account-name",
                "type": "Microsoft.Storage/storageAccounts",
                "location": "eastus"
            }
        ]
    """
    return _run_az_command(['az', 'resource', 'list', '--resource-group', resource_group])


def export_resource_group_template(resource_group: str) -> Dict[str, Any]:
    """Export ARM template for a resource group (JSON format).

    Args:
        resource_group: Name of the resource group

    Returns:
        ARM template as a dictionary

    Note:
        This returns the JSON ARM template. To convert to Bicep, you would need to
        save this output to a file and run 'az bicep decompile'.
    """
    return _run_az_command(['az', 'group', 'export', '--name', resource_group])


def decompile_arm_to_bicep(arm_template_path: str, output_path: Optional[str] = None) -> str:
    """Decompile an ARM template JSON file to Bicep format.

    Args:
        arm_template_path: Path to the ARM template JSON file
        output_path: Optional output path for the Bicep file. If not provided,
                    will use the same name with .bicep extension

    Returns:
        Path to the generated Bicep file

    Note:
        This command requires the ARM template to be saved as a file first.
    """
    command = ['az', 'bicep', 'decompile', '--file', arm_template_path]
    if output_path:
        command.extend(['--outfile', output_path])

    _run_az_command(command)

    # Return the output path
    if output_path:
        return output_path
    else:
        # Default behavior: same name with .bicep extension
        return arm_template_path.rsplit('.', 1)[0] + '.bicep'


def list_storage_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """List storage accounts.

    Args:
        resource_group: Optional resource group name. If provided, lists only
                       storage accounts in that group. Otherwise, lists all
                       storage accounts in the subscription.

    Returns:
        List of storage account objects

    Example output:
        [
            {
                "name": "storageaccountname",
                "resourceGroup": "rg-example",
                "location": "eastus",
                "kind": "StorageV2",
                "sku": {"name": "Standard_LRS"}
            }
        ]
    """
    command = ['az', 'storage', 'account', 'list']
    if resource_group:
        command.extend(['--resource-group', resource_group])
    return _run_az_command(command)


def list_storage_containers(account_name: str, resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """List blob containers in a storage account.

    Args:
        account_name: Name of the storage account
        resource_group: Optional resource group name

    Returns:
        List of container objects

    Example output:
        [
            {
                "name": "container-name",
                "properties": {
                    "lastModified": "2025-01-15T10:00:00+00:00",
                    "publicAccess": null
                }
            }
        ]
    """
    command = ['az', 'storage', 'container', 'list', '--account-name', account_name]
    if resource_group:
        command.extend(['--resource-group', resource_group])
    return _run_az_command(command)


def list_cosmosdb_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Cosmos DB accounts.

    Args:
        resource_group: Optional resource group name. If provided, lists only
                       Cosmos DB accounts in that group. Otherwise, lists all
                       accounts in the subscription.

    Returns:
        List of Cosmos DB account objects

    Example output:
        [
            {
                "name": "cosmosdb-account-name",
                "resourceGroup": "rg-example",
                "location": "eastus",
                "kind": "GlobalDocumentDB",
                "documentEndpoint": "https://...documents.azure.com:443/"
            }
        ]
    """
    command = ['az', 'cosmosdb', 'list']
    if resource_group:
        command.extend(['--resource-group', resource_group])
    return _run_az_command(command)


def list_cosmosdb_sql_databases(account_name: str, resource_group: str) -> List[Dict[str, Any]]:
    """List SQL databases in a Cosmos DB account.

    Args:
        account_name: Name of the Cosmos DB account
        resource_group: Resource group containing the account

    Returns:
        List of database objects

    Example output:
        [
            {
                "name": "database-name",
                "id": "/subscriptions/.../databases/database-name",
                "type": "Microsoft.DocumentDB/databaseAccounts/sqlDatabases"
            }
        ]
    """
    return _run_az_command([
        'az', 'cosmosdb', 'sql', 'database', 'list',
        '--account-name', account_name,
        '--resource-group', resource_group
    ])


def list_cosmosdb_sql_containers(account_name: str, resource_group: str, database_name: str) -> List[Dict[str, Any]]:
    """List SQL containers in a Cosmos DB database.

    Args:
        account_name: Name of the Cosmos DB account
        resource_group: Resource group containing the account
        database_name: Name of the database

    Returns:
        List of container objects

    Example output:
        [
            {
                "name": "container-name",
                "id": "/subscriptions/.../containers/container-name",
                "resource": {
                    "partitionKey": {"paths": ["/id"]}
                }
            }
        ]
    """
    return _run_az_command([
        'az', 'cosmosdb', 'sql', 'container', 'list',
        '--account-name', account_name,
        '--resource-group', resource_group,
        '--database-name', database_name
    ])


def get_subscription_info() -> Dict[str, Any]:
    """Get information about the current Azure subscription.

    Returns:
        Subscription information including id, name, state, etc.

    Example output:
        {
            "id": "/subscriptions/...",
            "subscriptionId": "...",
            "name": "Subscription Name",
            "state": "Enabled",
            "tenantId": "..."
        }
    """
    result = _run_az_command(['az', 'account', 'show'])
    return result


def list_locations() -> List[Dict[str, Any]]:
    """List all available Azure locations/regions.

    Returns:
        List of location objects

    Example output:
        [
            {
                "name": "eastus",
                "displayName": "East US",
                "regionalDisplayName": "(US) East US"
            }
        ]
    """
    return _run_az_command(['az', 'account', 'list-locations'])

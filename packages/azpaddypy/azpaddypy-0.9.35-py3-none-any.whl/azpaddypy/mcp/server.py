"""FastMCP server for Azure infrastructure information.

This module implements a Model Context Protocol (MCP) server using FastMCP 2.0
that exposes Azure infrastructure information through Azure CLI commands.
"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

from . import az_commands


def create_mcp_server(server_name: str = "Azure Infrastructure MCP") -> FastMCP:
    """Create and configure the Azure Infrastructure MCP server.

    Args:
        server_name: Name of the MCP server (default: "Azure Infrastructure MCP")

    Returns:
        Configured FastMCP server instance

    Example:
        mcp = create_mcp_server()
        mcp.run()
    """
    mcp = FastMCP(server_name)

    # Register all tools
    _register_resource_group_tools(mcp)
    _register_storage_tools(mcp)
    _register_cosmosdb_tools(mcp)
    _register_subscription_tools(mcp)

    return mcp


def _register_resource_group_tools(mcp: FastMCP) -> None:
    """Register resource group related tools."""

    @mcp.tool()
    def list_resource_groups() -> List[Dict[str, Any]]:
        """List all resource groups in the Azure subscription.

        Returns a list of resource groups with their properties including:
        - name: Resource group name
        - location: Azure region
        - id: Full resource ID
        - properties: Provisioning state and other properties
        - tags: Resource tags

        Example usage:
            Use this tool to discover what resource groups exist in the subscription.
        """
        return az_commands.list_resource_groups()

    @mcp.tool()
    def list_resources_in_group(resource_group: str) -> List[Dict[str, Any]]:
        """List all resources in a specific resource group.

        Args:
            resource_group: Name of the resource group to query

        Returns a list of resources with properties including:
        - name: Resource name
        - type: Resource type (e.g., Microsoft.Storage/storageAccounts)
        - location: Azure region
        - id: Full resource ID

        Example usage:
            After listing resource groups, use this to see what resources are in a group.
        """
        return az_commands.list_resources_in_group(resource_group)

    @mcp.tool()
    def export_resource_group_template(resource_group: str) -> Dict[str, Any]:
        """Export ARM template for a resource group in JSON format.

        Args:
            resource_group: Name of the resource group to export

        Returns the ARM template as a JSON object containing:
        - $schema: ARM template schema version
        - contentVersion: Template version
        - resources: List of resource definitions
        - parameters: Template parameters

        Note:
            This exports the template in ARM JSON format. To convert to Bicep,
            you would need to save the output to a file and use the
            decompile_arm_to_bicep tool.

        Example usage:
            Use this to get the infrastructure-as-code representation of a
            resource group's resources.
        """
        return az_commands.export_resource_group_template(resource_group)

    @mcp.tool()
    def decompile_arm_to_bicep(arm_template_path: str, output_path: Optional[str] = None) -> str:
        """Decompile an ARM template JSON file to Bicep format.

        Args:
            arm_template_path: Path to the ARM template JSON file
            output_path: Optional output path for the Bicep file. If not provided,
                        uses the same name with .bicep extension

        Returns the path to the generated Bicep file.

        Note:
            This requires the ARM template to be saved as a file first.
            You typically would:
            1. Use export_resource_group_template to get the ARM JSON
            2. Save it to a file
            3. Use this tool to convert it to Bicep

        Example usage:
            After exporting an ARM template and saving it, use this to convert
            it to the more readable Bicep format.
        """
        return az_commands.decompile_arm_to_bicep(arm_template_path, output_path)


def _register_storage_tools(mcp: FastMCP) -> None:
    """Register storage account related tools."""

    @mcp.tool()
    def list_storage_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
        """List storage accounts in the subscription or a specific resource group.

        Args:
            resource_group: Optional resource group name. If provided, lists only
                          storage accounts in that group. Otherwise, lists all
                          storage accounts in the subscription.

        Returns a list of storage accounts with properties including:
        - name: Storage account name
        - resourceGroup: Resource group containing the account
        - location: Azure region
        - kind: Storage account kind (StorageV2, BlobStorage, etc.)
        - sku: SKU information (Standard_LRS, Premium_LRS, etc.)
        - primaryEndpoints: URLs for blob, queue, table, file services

        Example usage:
            Use this to discover storage accounts in your subscription.
            Filter by resource group to narrow down the results.
        """
        return az_commands.list_storage_accounts(resource_group)

    @mcp.tool()
    def list_storage_containers(account_name: str, resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
        """List blob containers in a storage account.

        Args:
            account_name: Name of the storage account
            resource_group: Optional resource group name

        Returns a list of containers with properties including:
        - name: Container name
        - properties: Container metadata (lastModified, publicAccess, etc.)

        Example usage:
            After listing storage accounts, use this to see what blob containers
            exist in a specific storage account.
        """
        return az_commands.list_storage_containers(account_name, resource_group)


def _register_cosmosdb_tools(mcp: FastMCP) -> None:
    """Register Cosmos DB related tools."""

    @mcp.tool()
    def list_cosmosdb_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Cosmos DB accounts in the subscription or a specific resource group.

        Args:
            resource_group: Optional resource group name. If provided, lists only
                          Cosmos DB accounts in that group. Otherwise, lists all
                          accounts in the subscription.

        Returns a list of Cosmos DB accounts with properties including:
        - name: Cosmos DB account name
        - resourceGroup: Resource group containing the account
        - location: Azure region
        - kind: Account kind (GlobalDocumentDB, MongoDB, etc.)
        - documentEndpoint: Document endpoint URL
        - consistencyPolicy: Consistency level settings

        Example usage:
            Use this to discover Cosmos DB accounts in your subscription.
        """
        return az_commands.list_cosmosdb_accounts(resource_group)

    @mcp.tool()
    def list_cosmosdb_sql_databases(account_name: str, resource_group: str) -> List[Dict[str, Any]]:
        """List SQL databases in a Cosmos DB account.

        Args:
            account_name: Name of the Cosmos DB account
            resource_group: Resource group containing the account

        Returns a list of databases with properties including:
        - name: Database name
        - id: Full resource ID
        - type: Resource type

        Example usage:
            After listing Cosmos DB accounts, use this to see what databases
            exist in a specific account.
        """
        return az_commands.list_cosmosdb_sql_databases(account_name, resource_group)

    @mcp.tool()
    def list_cosmosdb_sql_containers(
        account_name: str,
        resource_group: str,
        database_name: str
    ) -> List[Dict[str, Any]]:
        """List SQL containers in a Cosmos DB database.

        Args:
            account_name: Name of the Cosmos DB account
            resource_group: Resource group containing the account
            database_name: Name of the database

        Returns a list of containers with properties including:
        - name: Container name
        - id: Full resource ID
        - resource: Container configuration (partition key, indexing policy, etc.)

        Example usage:
            After listing databases, use this to see what containers exist
            in a specific database.
        """
        return az_commands.list_cosmosdb_sql_containers(
            account_name, resource_group, database_name
        )


def _register_subscription_tools(mcp: FastMCP) -> None:
    """Register subscription and location tools."""

    @mcp.tool()
    def get_subscription_info() -> Dict[str, Any]:
        """Get information about the current Azure subscription.

        Returns subscription information including:
        - id: Full subscription resource ID
        - subscriptionId: Subscription GUID
        - name: Subscription name
        - state: Subscription state (Enabled, Disabled, etc.)
        - tenantId: Azure AD tenant ID

        Example usage:
            Use this to understand which Azure subscription context you're
            operating in.
        """
        return az_commands.get_subscription_info()

    @mcp.tool()
    def list_locations() -> List[Dict[str, Any]]:
        """List all available Azure locations/regions.

        Returns a list of locations with properties including:
        - name: Location short name (e.g., 'eastus')
        - displayName: Human-readable name (e.g., 'East US')
        - regionalDisplayName: Regional display name with country code

        Example usage:
            Use this to discover available Azure regions for deploying resources.
        """
        return az_commands.list_locations()


# Entry point for running the server directly
if __name__ == "__main__":
    server = create_mcp_server()
    server.run()

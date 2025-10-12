"""Azure Infrastructure MCP Server - FastMCP 2.0 Style.

This MCP server provides read-only access to Azure infrastructure information
through Azure SDK. It uses the FastMCP 2.0 decorator pattern and integrates
with mgmt_config.py for authentication and Key Vault access.

The server exposes tools for:
- Resource groups and ARM template operations
- Storage account and container listing
- Cosmos DB account, database, and container operations
- Subscription and location information

Example:
    # Run the server directly
    python -m azpaddypy.mcp.azure_mcp_server

    # Or import and run programmatically
    from azpaddypy.mcp.azure_mcp_server import mcp
    mcp.run()
"""

from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

from .services import base
from .services import resources
from .services import storage
from .services import cosmos
from .services import subscription

# Create FastMCP server instance
mcp = FastMCP("Azure Infrastructure")


# =============================================================================
# Server Initialization
# =============================================================================

def initialize_server(
    use_mgmt_config: bool = True,
    credential: Optional[Any] = None,
    subscription_id: Optional[str] = None
) -> None:
    """Initialize the MCP server with Azure credentials.

    Args:
        use_mgmt_config: If True, uses mgmt_config.py for authentication (default)
        credential: Azure credential object (used if use_mgmt_config=False)
        subscription_id: Azure subscription ID (used if use_mgmt_config=False)

    Raises:
        AzureMCPError: If initialization fails
    """
    ctx = base.get_context()

    if use_mgmt_config:
        ctx.initialize_from_mgmt_config()
    else:
        ctx.initialize(credential=credential, subscription_id=subscription_id)


# =============================================================================
# Resource Group Tools
# =============================================================================

@mcp.tool()
def list_resource_groups() -> List[Dict[str, Any]]:
    """List all resource groups in the Azure subscription.

    Returns a list of resource groups with their properties including:
    - name: Resource group name
    - location: Azure region
    - id: Full resource ID
    - properties: Provisioning state and other properties
    - tags: Resource tags
    - application: Extracted 'application' tag value (or 'None')

    Use this tool to discover what resource groups exist in the subscription.
    """
    return resources.list_resource_groups()


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

    After listing resource groups, use this to see what resources are in a group.
    """
    return resources.list_resources_in_group(resource_group)


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

    Use this to get the infrastructure-as-code representation of a
    resource group's resources.
    """
    return resources.export_resource_group_template(resource_group)


@mcp.tool()
def decompile_arm_to_bicep(
    arm_template_path: str,
    output_path: Optional[str] = None
) -> str:
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

    Requires Azure CLI with Bicep extension installed.

    After exporting an ARM template and saving it, use this to convert
    it to the more readable Bicep format.
    """
    return resources.decompile_arm_to_bicep(arm_template_path, output_path)


# =============================================================================
# Storage Tools
# =============================================================================

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

    Use this to discover storage accounts in your subscription.
    Filter by resource group to narrow down the results.
    """
    return storage.list_storage_accounts(resource_group)


@mcp.tool()
def list_storage_containers(
    account_name: str,
    resource_group: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List blob containers in a storage account.

    Args:
        account_name: Name of the storage account
        resource_group: Optional resource group name

    Returns a list of containers with properties including:
    - name: Container name
    - properties: Container metadata (lastModified, publicAccess, etc.)

    After listing storage accounts, use this to see what blob containers
    exist in a specific storage account.
    """
    return storage.list_storage_containers(account_name, resource_group)


# =============================================================================
# Cosmos DB Tools
# =============================================================================

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

    Use this to discover Cosmos DB accounts in your subscription.
    """
    return cosmos.list_cosmosdb_accounts(resource_group)


@mcp.tool()
def list_cosmosdb_sql_databases(
    account_name: str,
    resource_group: str
) -> List[Dict[str, Any]]:
    """List SQL databases in a Cosmos DB account.

    Args:
        account_name: Name of the Cosmos DB account
        resource_group: Resource group containing the account

    Returns a list of databases with properties including:
    - name: Database name
    - id: Full resource ID
    - type: Resource type

    After listing Cosmos DB accounts, use this to see what databases
    exist in a specific account.
    """
    return cosmos.list_cosmosdb_sql_databases(account_name, resource_group)


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

    After listing databases, use this to see what containers exist
    in a specific database.
    """
    return cosmos.list_cosmosdb_sql_containers(
        account_name,
        resource_group,
        database_name
    )


# =============================================================================
# Subscription Tools
# =============================================================================

@mcp.tool()
def get_subscription_info() -> Dict[str, Any]:
    """Get information about the current Azure subscription.

    Returns subscription information including:
    - id: Full subscription resource ID
    - subscriptionId: Subscription GUID
    - name: Subscription name
    - state: Subscription state (Enabled, Disabled, etc.)
    - tenantId: Azure AD tenant ID

    Use this to understand which Azure subscription context you're
    operating in.
    """
    return subscription.get_subscription_info()


@mcp.tool()
def list_locations() -> List[Dict[str, Any]]:
    """List all available Azure locations/regions.

    Returns a list of locations with properties including:
    - name: Location short name (e.g., 'eastus')
    - displayName: Human-readable name (e.g., 'East US')
    - regionalDisplayName: Regional display name with country code

    Use this to discover available Azure regions for deploying resources.
    """
    return subscription.list_locations()


# =============================================================================
# Server Entry Point
# =============================================================================

if __name__ == "__main__":
    # Initialize with mgmt_config for authentication
    try:
        initialize_server(use_mgmt_config=True)
    except base.AzureMCPError as e:
        print(f"Warning: Failed to initialize from mgmt_config: {e}")
        print("Server will attempt auto-initialization on first tool use.")

    # Run the server
    mcp.run()

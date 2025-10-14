from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

from .services import base
from .services import resources
from .services import storage
from .services import cosmos
from .services import subscription

mcp = FastMCP("Azure Infrastructure")


def initialize_server(
    credential: Optional[Any] = None,
    subscription_id: Optional[str] = None,
    auto_discover: bool = True
) -> None:
    ctx = base.get_context()

    if subscription_id or credential:
        ctx.initialize(credential=credential, subscription_id=subscription_id)
    elif auto_discover:
        ctx.initialize_with_auto_discovery()
    else:
        pass


@mcp.tool()
def list_resource_groups() -> List[Dict[str, Any]]:
    return resources.list_resource_groups()


@mcp.tool()
def list_resources_in_group(resource_group: str) -> List[Dict[str, Any]]:
    return resources.list_resources_in_group(resource_group)


@mcp.tool()
def export_resource_group_template(resource_group: str) -> Dict[str, Any]:
    return resources.export_resource_group_template(resource_group)


@mcp.tool()
def decompile_arm_to_bicep(
    arm_template_path: str,
    output_path: Optional[str] = None
) -> str:
    return resources.decompile_arm_to_bicep(arm_template_path, output_path)


@mcp.tool()
def list_storage_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    return storage.list_storage_accounts(resource_group)


@mcp.tool()
def list_storage_containers(
    account_name: str,
    resource_group: Optional[str] = None
) -> List[Dict[str, Any]]:
    return storage.list_storage_containers(account_name, resource_group)


@mcp.tool()
def upload_blob(
    account_name: str,
    container_name: str,
    blob_name: str,
    data: str,
    resource_group: Optional[str] = None,
    overwrite: bool = False,
    content_type: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    base64_encoded: bool = False
) -> Dict[str, Any]:
    return storage.upload_blob(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        data=data,
        resource_group=resource_group,
        overwrite=overwrite,
        content_type=content_type,
        metadata=metadata,
        base64_encoded=base64_encoded
    )


@mcp.tool()
def list_cosmosdb_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    return cosmos.list_cosmosdb_accounts(resource_group)


@mcp.tool()
def list_cosmosdb_sql_databases(
    account_name: str,
    resource_group: str
) -> List[Dict[str, Any]]:
    return cosmos.list_cosmosdb_sql_databases(account_name, resource_group)


@mcp.tool()
def list_cosmosdb_sql_containers(
    account_name: str,
    resource_group: str,
    database_name: str
) -> List[Dict[str, Any]]:
    return cosmos.list_cosmosdb_sql_containers(
        account_name,
        resource_group,
        database_name
    )


@mcp.tool()
def list_subscriptions() -> List[Dict[str, Any]]:
    return subscription.list_subscriptions()


@mcp.tool()
def get_subscription_info() -> Dict[str, Any]:
    return subscription.get_subscription_info()


@mcp.tool()
def list_locations() -> List[Dict[str, Any]]:
    return subscription.list_locations()


if __name__ == "__main__":
    try:
        initialize_server(auto_discover=True)
        print("Azure MCP Server initialized successfully with auto-discovery")
    except base.AzureMCPError as e:
        print(f"Warning: Failed to auto-initialize: {e}")
        print("Server will attempt initialization on first tool use.")

    mcp.run()

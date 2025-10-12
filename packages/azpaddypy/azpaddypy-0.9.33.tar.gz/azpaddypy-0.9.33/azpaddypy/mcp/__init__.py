"""Azure Infrastructure MCP Server.

A Model Context Protocol (MCP) server that provides read-only access to Azure
infrastructure information through Azure SDK. Agents can use this server to
gather information about resource groups, storage accounts, Cosmos DB, and
export Bicep templates.

Usage:
    from azpaddypy.mcp import create_mcp_server, initialize

    # Initialize with explicit credentials (optional)
    initialize(subscription_id="your-subscription-id")

    # Create and run the MCP server
    mcp = create_mcp_server()
    mcp.run()

    # Or use with mgmt_config (when running as part of azpaddypy app)
    from azpaddypy.mcp import initialize_from_mgmt_config
    initialize_from_mgmt_config()

Requirements:
    - Azure SDK packages (azure-identity, azure-mgmt-*, etc.)
    - fastmcp>=2.0.0 package
    - Azure CLI (optional, for Bicep decompilation)
"""

from .server import create_mcp_server
from .az_commands import (
    initialize,
    initialize_from_mgmt_config,
    AzureCliError
)

__all__ = [
    "create_mcp_server",
    "initialize",
    "initialize_from_mgmt_config",
    "AzureCliError"
]

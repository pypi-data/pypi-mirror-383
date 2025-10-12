"""Azure Infrastructure MCP Server.

A Model Context Protocol (MCP) server that provides read-only access to Azure
infrastructure information through Azure SDK. This server follows FastMCP 2.0
patterns and integrates with azpaddypy's mgmt_config for authentication.

The server enables AI agents to:
- List and explore Azure resource groups and resources
- Export ARM templates and convert them to Bicep
- Query storage accounts and blob containers
- Access Cosmos DB account, database, and container information
- Get subscription and location details

Quick Start:
    # Run the server directly
    python -m azpaddypy.mcp.azure_mcp_server

    # Or use in code
    from azpaddypy.mcp import mcp, initialize_server

    initialize_server(use_mgmt_config=True)
    mcp.run()

Architecture:
    - azure_mcp_server.py: FastMCP 2.0 server with decorator-based tools
    - services/base.py: Azure client management and authentication
    - services/resources.py: Resource group and ARM template operations
    - services/storage.py: Storage account operations
    - services/cosmos.py: Cosmos DB operations
    - services/subscription.py: Subscription and location operations

Authentication:
    The server uses mgmt_config.py from the parent application for Azure
    authentication. This provides:
    - Azure Identity credential from mgmt_config.identity
    - Subscription ID from Key Vault via mgmt_config.keyvaults

    If mgmt_config is not available, the server falls back to environment-based
    initialization using AZURE_SUBSCRIPTION_ID environment variable.

Requirements:
    - Azure SDK packages (azure-identity, azure-mgmt-*, etc.)
    - fastmcp>=2.0.0 package
    - Azure CLI (optional, for Bicep decompilation)
    - mgmt_config.py configured with Key Vault access (recommended)
"""

from .azure_mcp_server import mcp, initialize_server
from .services.base import AzureMCPError, get_context

# Backward compatibility exports (deprecated, use azure_mcp_server instead)
from .server import create_mcp_server

__all__ = [
    # FastMCP 2.0 style (recommended)
    "mcp",
    "initialize_server",
    "AzureMCPError",
    "get_context",
    # Backward compatibility (deprecated)
    "create_mcp_server",
]

__version__ = "2.0.0"

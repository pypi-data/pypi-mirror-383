"""Azure Infrastructure MCP Server.

A Model Context Protocol (MCP) server that provides read-only access to Azure
infrastructure information through Azure SDK. This server follows FastMCP 2.0
patterns and uses automatic credential and subscription discovery.

The server enables AI agents to:
- List and explore Azure resource groups and resources
- Export ARM templates and convert them to Bicep
- Query storage accounts and blob containers
- Access Cosmos DB account, database, and container information
- Get subscription and location details
- Discover available Azure subscriptions

Quick Start:
    # Run the server directly (uses auto-discovery)
    python -m azpaddypy.mcp

    # Or with explicit subscription ID via environment variable
    AZURE_SUBSCRIPTION_ID=your-sub-id python -m azpaddypy.mcp

    # Or use in code
    from azpaddypy.mcp import mcp, initialize_server

    # Auto-discover subscription
    initialize_server(auto_discover=True)
    mcp.run()

    # Or provide explicit subscription ID
    initialize_server(subscription_id="your-subscription-id")
    mcp.run()

Architecture:
    - azure_mcp_server.py: FastMCP 2.0 server with decorator-based tools
    - services/base.py: Azure client management and authentication
    - services/resources.py: Resource group and ARM template operations
    - services/storage.py: Storage account operations
    - services/cosmos.py: Cosmos DB operations
    - services/subscription.py: Subscription and location operations

Authentication:
    The server automatically discovers Azure credentials and subscriptions:
    1. Uses DefaultAzureCredential for authentication (supports Managed Identity,
       Azure CLI, Environment Variables, etc.)
    2. Checks AZURE_SUBSCRIPTION_ID environment variable if set
    3. Auto-discovers first available subscription via subscription listing

    No configuration files or Key Vault setup required!

Requirements:
    - Azure SDK packages (azure-identity, azure-mgmt-*, etc.)
    - fastmcp>=2.0.0 package
    - Azure CLI (optional, for Bicep decompilation)
    - Valid Azure credential available to DefaultAzureCredential
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

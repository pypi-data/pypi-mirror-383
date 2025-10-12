"""Azure Infrastructure MCP Server.

A Model Context Protocol (MCP) server that provides read-only access to Azure
infrastructure information through Azure CLI commands. Agents can use this
server to gather information about resource groups, storage accounts, Cosmos DB,
and export Bicep templates.

Usage:
    from azpaddypy.mcp import create_mcp_server

    # Create and run the MCP server
    mcp = create_mcp_server()
    mcp.run()

Requirements:
    - Azure CLI must be installed and authenticated
    - fastmcp>=2.0.0 package
"""

from .server import create_mcp_server

__all__ = ["create_mcp_server"]

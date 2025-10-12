"""Entry point for running the Azure MCP server as a module.

Usage:
    python -m azpaddypy.mcp

Environment Variables:
    AZURE_SUBSCRIPTION_ID: Optional. If set, uses this subscription ID.
                          Otherwise, auto-discovers the first available subscription.
"""

from .azure_mcp_server import mcp, initialize_server
from .services.base import AzureMCPError

if __name__ == "__main__":
    # Initialize with auto-discovery
    try:
        initialize_server(auto_discover=True)
        print("Azure MCP Server initialized successfully with auto-discovery")
    except AzureMCPError as e:
        print(f"Warning: Failed to auto-initialize: {e}")
        print("Server will attempt initialization on first tool use.")

    # Run the server
    print("Starting Azure Infrastructure MCP Server...")
    mcp.run()

"""Entry point for running the Azure MCP server as a module.

Usage:
    python -m azpaddypy.mcp
"""

from .azure_mcp_server import mcp, initialize_server
from .services.base import AzureMCPError

if __name__ == "__main__":
    # Initialize with mgmt_config for authentication
    try:
        initialize_server(use_mgmt_config=True)
        print("Azure MCP Server initialized with mgmt_config")
    except AzureMCPError as e:
        print(f"Warning: Failed to initialize from mgmt_config: {e}")
        print("Server will attempt auto-initialization on first tool use.")

    # Run the server
    print("Starting Azure Infrastructure MCP Server...")
    mcp.run()

"""
Tests for azpaddypy.mcp.server module.

Tests the FastMCP server creation and tool registration.
"""

import pytest
from unittest.mock import Mock, patch


class TestServerCreation:
    """Test MCP server creation."""

    @patch("azpaddypy.mcp.server.FastMCP")
    def test_create_mcp_server_default_name(self, mock_fastmcp_class):
        """Test creating MCP server with default name."""
        # Import inside test to ensure patch is applied
        from azpaddypy.mcp.server import create_mcp_server

        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f)
        mock_fastmcp_class.return_value = mock_server

        result = create_mcp_server()

        mock_fastmcp_class.assert_called_once_with("Azure Infrastructure MCP")
        assert result == mock_server

    @patch("azpaddypy.mcp.server.FastMCP")
    def test_create_mcp_server_custom_name(self, mock_fastmcp_class):
        """Test creating MCP server with custom name."""
        # Import inside test to ensure patch is applied
        from azpaddypy.mcp.server import create_mcp_server

        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f)
        mock_fastmcp_class.return_value = mock_server

        result = create_mcp_server(server_name="Custom Azure Server")

        mock_fastmcp_class.assert_called_once_with("Custom Azure Server")
        assert result == mock_server

    @patch("azpaddypy.mcp.server.FastMCP")
    def test_tools_registered(self, mock_fastmcp_class):
        """Test that all tools are registered on the server."""
        # Import inside test to ensure patch is applied
        from azpaddypy.mcp.server import create_mcp_server

        mock_server = Mock()
        tool_call_count = 0

        def capture_tool_decorator(*args, **kwargs):
            """Capture tool registration calls."""
            def decorator(func):
                nonlocal tool_call_count
                tool_call_count += 1
                return func
            return decorator

        mock_server.tool = capture_tool_decorator
        mock_fastmcp_class.return_value = mock_server

        with patch("azpaddypy.mcp.server.az_commands"):
            create_mcp_server()

            # Verify expected number of tools are registered (11 total tools)
            expected_tool_count = 11
            assert tool_call_count == expected_tool_count, f"Expected {expected_tool_count} tools registered, got {tool_call_count}"


class TestToolImplementations:
    """Test that tool implementations call the correct az_commands functions."""

    @patch("azpaddypy.mcp.server.az_commands")
    def test_list_resource_groups_tool(self, mock_az_commands):
        """Test list_resource_groups tool calls az_commands function."""
        # Import the registration function to test the tool directly
        from azpaddypy.mcp.server import _register_resource_group_tools

        mock_server = Mock()
        registered_tools = {}

        def capture_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        mock_server.tool = capture_tool
        mock_az_commands.list_resource_groups.return_value = [{"name": "rg-1"}]

        _register_resource_group_tools(mock_server)

        # Call the registered tool
        result = registered_tools["list_resource_groups"]()

        mock_az_commands.list_resource_groups.assert_called_once()
        assert result == [{"name": "rg-1"}]

    @patch("azpaddypy.mcp.server.az_commands")
    def test_list_storage_accounts_tool(self, mock_az_commands):
        """Test list_storage_accounts tool calls az_commands function."""
        # Import the registration function to test the tool directly
        from azpaddypy.mcp.server import _register_storage_tools

        mock_server = Mock()
        registered_tools = {}

        def capture_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        mock_server.tool = capture_tool
        mock_az_commands.list_storage_accounts.return_value = [{"name": "storage1"}]

        _register_storage_tools(mock_server)

        # Call the registered tool with resource_group parameter
        result = registered_tools["list_storage_accounts"](resource_group="test-rg")

        mock_az_commands.list_storage_accounts.assert_called_once_with("test-rg")
        assert result == [{"name": "storage1"}]

    @patch("azpaddypy.mcp.server.az_commands")
    def test_export_resource_group_template_tool(self, mock_az_commands):
        """Test export_resource_group_template tool calls az_commands function."""
        # Import the registration function to test the tool directly
        from azpaddypy.mcp.server import _register_resource_group_tools

        mock_server = Mock()
        registered_tools = {}

        def capture_tool(*args, **kwargs):
            def decorator(func):
                registered_tools[func.__name__] = func
                return func
            return decorator

        mock_server.tool = capture_tool
        mock_az_commands.export_resource_group_template.return_value = {"$schema": "..."}

        _register_resource_group_tools(mock_server)

        # Call the registered tool
        result = registered_tools["export_resource_group_template"](resource_group="test-rg")

        mock_az_commands.export_resource_group_template.assert_called_once_with("test-rg")
        assert result == {"$schema": "..."}

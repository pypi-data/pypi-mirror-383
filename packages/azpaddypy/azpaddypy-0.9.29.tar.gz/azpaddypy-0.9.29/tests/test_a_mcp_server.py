"""Tests for azpaddypy.mcp.server module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from azpaddypy.mcp.server import create_mcp_server


class TestCreateMcpServer:
    """Tests for the create_mcp_server function."""

    def test_create_mcp_server_default_name(self):
        """Test creating MCP server with default name."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            mock_instance = Mock()
            mock_fastmcp.return_value = mock_instance

            result = create_mcp_server()

            mock_fastmcp.assert_called_once_with("Azure Infrastructure MCP")
            assert result == mock_instance

    def test_create_mcp_server_custom_name(self):
        """Test creating MCP server with custom name."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            mock_instance = Mock()
            mock_fastmcp.return_value = mock_instance

            result = create_mcp_server(server_name="Custom Server Name")

            mock_fastmcp.assert_called_once_with("Custom Server Name")
            assert result == mock_instance

    def test_create_mcp_server_registers_tools(self):
        """Test that create_mcp_server registers all tool functions."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            with patch("azpaddypy.mcp.server.az_commands"):
                mock_instance = Mock()
                mock_fastmcp.return_value = mock_instance

                # Track tool registrations
                registered_tools = []

                def mock_tool():
                    def decorator(func):
                        registered_tools.append(func.__name__)
                        return func
                    return decorator

                mock_instance.tool = mock_tool

                create_mcp_server()

                # Verify that multiple tools were registered
                # We expect at least resource group, storage, cosmosdb, and subscription tools
                assert len(registered_tools) >= 10  # We have 12 tools total

    def test_create_mcp_server_returns_fastmcp_instance(self):
        """Test that create_mcp_server returns a FastMCP instance."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            mock_instance = Mock()
            mock_fastmcp.return_value = mock_instance

            result = create_mcp_server()

            assert result is mock_instance
            # Verify the instance has the expected FastMCP interface
            assert hasattr(result, "tool")


class TestToolRegistration:
    """Tests for tool registration logic."""

    def test_resource_group_tools_registration(self):
        """Test that resource group tools are properly registered."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            with patch("azpaddypy.mcp.server.az_commands"):
                mock_instance = Mock()
                mock_fastmcp.return_value = mock_instance

                tool_functions = []

                def mock_tool():
                    def decorator(func):
                        tool_functions.append(func)
                        return func
                    return decorator

                mock_instance.tool = mock_tool

                create_mcp_server()

                # Check that we have resource group related tools
                tool_names = [func.__name__ for func in tool_functions]
                assert "list_resource_groups" in tool_names
                assert "list_resources_in_group" in tool_names
                assert "export_resource_group_template" in tool_names
                assert "decompile_arm_to_bicep" in tool_names

    def test_storage_tools_registration(self):
        """Test that storage tools are properly registered."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            with patch("azpaddypy.mcp.server.az_commands"):
                mock_instance = Mock()
                mock_fastmcp.return_value = mock_instance

                tool_functions = []

                def mock_tool():
                    def decorator(func):
                        tool_functions.append(func)
                        return func
                    return decorator

                mock_instance.tool = mock_tool

                create_mcp_server()

                # Check that we have storage related tools
                tool_names = [func.__name__ for func in tool_functions]
                assert "list_storage_accounts" in tool_names
                assert "list_storage_containers" in tool_names

    def test_cosmosdb_tools_registration(self):
        """Test that Cosmos DB tools are properly registered."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            with patch("azpaddypy.mcp.server.az_commands"):
                mock_instance = Mock()
                mock_fastmcp.return_value = mock_instance

                tool_functions = []

                def mock_tool():
                    def decorator(func):
                        tool_functions.append(func)
                        return func
                    return decorator

                mock_instance.tool = mock_tool

                create_mcp_server()

                # Check that we have Cosmos DB related tools
                tool_names = [func.__name__ for func in tool_functions]
                assert "list_cosmosdb_accounts" in tool_names
                assert "list_cosmosdb_sql_databases" in tool_names
                assert "list_cosmosdb_sql_containers" in tool_names

    def test_subscription_tools_registration(self):
        """Test that subscription tools are properly registered."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            with patch("azpaddypy.mcp.server.az_commands"):
                mock_instance = Mock()
                mock_fastmcp.return_value = mock_instance

                tool_functions = []

                def mock_tool():
                    def decorator(func):
                        tool_functions.append(func)
                        return func
                    return decorator

                mock_instance.tool = mock_tool

                create_mcp_server()

                # Check that we have subscription related tools
                tool_names = [func.__name__ for func in tool_functions]
                assert "get_subscription_info" in tool_names
                assert "list_locations" in tool_names

    def test_all_tools_have_docstrings(self):
        """Test that all registered tools have proper docstrings."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            mock_instance = Mock()
            mock_fastmcp.return_value = mock_instance

            tool_functions = []

            def mock_tool():
                def decorator(func):
                    tool_functions.append(func)
                    return func
                return decorator

            mock_instance.tool = mock_tool

            create_mcp_server()

            # Verify all tools have docstrings
            for func in tool_functions:
                assert func.__doc__ is not None
                assert len(func.__doc__.strip()) > 0

    def test_tool_functions_call_az_commands(self):
        """Test that registered tool functions properly call az_commands module."""
        with patch("azpaddypy.mcp.server.FastMCP") as mock_fastmcp:
            with patch("azpaddypy.mcp.server.az_commands") as mock_az_commands:
                mock_instance = Mock()
                mock_fastmcp.return_value = mock_instance

                tool_functions = {}

                def mock_tool():
                    def decorator(func):
                        tool_functions[func.__name__] = func
                        return func
                    return decorator

                mock_instance.tool = mock_tool

                # Setup mock return values
                mock_az_commands.list_resource_groups.return_value = [{"name": "test-rg"}]
                mock_az_commands.list_storage_accounts.return_value = [{"name": "test-storage"}]
                mock_az_commands.get_subscription_info.return_value = {"id": "test-sub"}

                create_mcp_server()

                # Test that calling the tool functions calls the underlying az_commands
                if "list_resource_groups" in tool_functions:
                    result = tool_functions["list_resource_groups"]()
                    mock_az_commands.list_resource_groups.assert_called_once()
                    assert result == [{"name": "test-rg"}]

                if "list_storage_accounts" in tool_functions:
                    result = tool_functions["list_storage_accounts"](resource_group=None)
                    mock_az_commands.list_storage_accounts.assert_called_once_with(None)
                    assert result == [{"name": "test-storage"}]

                if "get_subscription_info" in tool_functions:
                    result = tool_functions["get_subscription_info"]()
                    mock_az_commands.get_subscription_info.assert_called_once()
                    assert result == {"id": "test-sub"}

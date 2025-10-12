"""Tests for azpaddypy.mcp.az_commands module."""

import pytest
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock
from azpaddypy.mcp.az_commands import (
    AzureCliError,
    _run_az_command,
    list_resource_groups,
    list_resources_in_group,
    export_resource_group_template,
    decompile_arm_to_bicep,
    list_storage_accounts,
    list_cosmosdb_accounts,
    get_subscription_info,
)


class TestRunAzCommand:
    """Tests for the _run_az_command internal function."""

    def test_run_az_command_success(self):
        """Test successful Azure CLI command execution with JSON output."""
        mock_result = Mock()
        mock_result.stdout = '{"result": "success"}'
        mock_result.stderr = ""

        with patch("azpaddypy.mcp.az_commands.subprocess.run", return_value=mock_result) as mock_run:
            result = _run_az_command(["az", "test", "command"])

            assert result == {"result": "success"}
            mock_run.assert_called_once()
            # Verify --output json was added
            assert "--output" in mock_run.call_args[0][0]
            assert "json" in mock_run.call_args[0][0]

    def test_run_az_command_with_existing_output_flag(self):
        """Test that --output flag is not added if already present."""
        mock_result = Mock()
        mock_result.stdout = '{"result": "success"}'

        with patch("azpaddypy.mcp.az_commands.subprocess.run", return_value=mock_result) as mock_run:
            result = _run_az_command(["az", "test", "--output", "json"])

            assert result == {"result": "success"}
            # Verify no duplicate --output was added
            call_args = mock_run.call_args[0][0]
            assert call_args.count("--output") == 1

    def test_run_az_command_empty_output(self):
        """Test handling of empty output from Azure CLI."""
        mock_result = Mock()
        mock_result.stdout = ""

        with patch("azpaddypy.mcp.az_commands.subprocess.run", return_value=mock_result):
            result = _run_az_command(["az", "test"])

            assert result is None

    def test_run_az_command_subprocess_error(self):
        """Test handling of subprocess CalledProcessError."""
        mock_error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["az", "test"],
            stderr="Error: Command failed"
        )

        with patch("azpaddypy.mcp.az_commands.subprocess.run", side_effect=mock_error):
            with pytest.raises(AzureCliError, match="Azure CLI command failed"):
                _run_az_command(["az", "test"])

    def test_run_az_command_invalid_json(self):
        """Test handling of invalid JSON output."""
        mock_result = Mock()
        mock_result.stdout = "not valid json"

        with patch("azpaddypy.mcp.az_commands.subprocess.run", return_value=mock_result):
            with pytest.raises(AzureCliError, match="Failed to parse JSON"):
                _run_az_command(["az", "test"])

    def test_run_az_command_unexpected_error(self):
        """Test handling of unexpected exceptions."""
        with patch("azpaddypy.mcp.az_commands.subprocess.run", side_effect=OSError("OS error")):
            with pytest.raises(AzureCliError, match="Unexpected error"):
                _run_az_command(["az", "test"])


class TestResourceGroupCommands:
    """Tests for resource group related commands."""

    def test_list_resource_groups_returns_list(self):
        """Test that list_resource_groups returns a list of resource groups."""
        mock_rgs = [
            {"name": "rg-test-1", "location": "eastus"},
            {"name": "rg-test-2", "location": "westus"}
        ]

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_rgs):
            result = list_resource_groups()

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "rg-test-1"

    def test_list_resources_in_group_with_resource_group_name(self):
        """Test that list_resources_in_group passes correct resource group parameter."""
        mock_resources = [
            {"name": "resource-1", "type": "Microsoft.Storage/storageAccounts"}
        ]

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_resources) as mock_run:
            result = list_resources_in_group("test-rg")

            assert isinstance(result, list)
            assert len(result) == 1
            # Verify the resource group parameter was passed
            call_args = mock_run.call_args[0][0]
            assert "--resource-group" in call_args
            assert "test-rg" in call_args

    def test_export_resource_group_template_returns_dict(self):
        """Test that export_resource_group_template returns ARM template dictionary."""
        mock_template = {
            "$schema": "https://schema.management.azure.com/...",
            "contentVersion": "1.0.0.0",
            "resources": []
        }

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_template):
            result = export_resource_group_template("test-rg")

            assert isinstance(result, dict)
            assert "$schema" in result
            assert "resources" in result

    def test_decompile_arm_to_bicep_returns_output_path(self):
        """Test that decompile_arm_to_bicep returns the correct output path."""
        with patch("azpaddypy.mcp.az_commands._run_az_command"):
            # Test with explicit output path
            result = decompile_arm_to_bicep("/path/template.json", "/path/output.bicep")
            assert result == "/path/output.bicep"

            # Test with default output path (replaces .json with .bicep)
            result = decompile_arm_to_bicep("/path/template.json")
            assert result == "/path/template.bicep"


class TestStorageCommands:
    """Tests for storage account related commands."""

    def test_list_storage_accounts_without_resource_group(self):
        """Test listing all storage accounts without resource group filter."""
        mock_accounts = [
            {"name": "storage1", "location": "eastus"},
            {"name": "storage2", "location": "westus"}
        ]

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_accounts) as mock_run:
            result = list_storage_accounts()

            assert isinstance(result, list)
            assert len(result) == 2
            # Verify no resource group filter was added
            call_args = mock_run.call_args[0][0]
            assert "--resource-group" not in call_args

    def test_list_storage_accounts_with_resource_group(self):
        """Test listing storage accounts filtered by resource group."""
        mock_accounts = [{"name": "storage1", "location": "eastus"}]

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_accounts) as mock_run:
            result = list_storage_accounts("test-rg")

            assert isinstance(result, list)
            # Verify resource group filter was added
            call_args = mock_run.call_args[0][0]
            assert "--resource-group" in call_args
            assert "test-rg" in call_args


class TestCosmosDBCommands:
    """Tests for Cosmos DB related commands."""

    def test_list_cosmosdb_accounts_without_resource_group(self):
        """Test listing all Cosmos DB accounts."""
        mock_accounts = [
            {"name": "cosmos1", "kind": "GlobalDocumentDB"},
            {"name": "cosmos2", "kind": "MongoDB"}
        ]

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_accounts) as mock_run:
            result = list_cosmosdb_accounts()

            assert isinstance(result, list)
            assert len(result) == 2
            # Verify no resource group filter was added
            call_args = mock_run.call_args[0][0]
            assert "--resource-group" not in call_args

    def test_list_cosmosdb_accounts_with_resource_group(self):
        """Test listing Cosmos DB accounts filtered by resource group."""
        mock_accounts = [{"name": "cosmos1", "kind": "GlobalDocumentDB"}]

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_accounts) as mock_run:
            result = list_cosmosdb_accounts("test-rg")

            assert isinstance(result, list)
            # Verify resource group filter was added
            call_args = mock_run.call_args[0][0]
            assert "--resource-group" in call_args
            assert "test-rg" in call_args


class TestSubscriptionCommands:
    """Tests for subscription and location commands."""

    def test_get_subscription_info_returns_dict(self):
        """Test that get_subscription_info returns subscription dictionary."""
        mock_sub_info = {
            "id": "/subscriptions/sub-id",
            "subscriptionId": "sub-id",
            "name": "Test Subscription",
            "state": "Enabled"
        }

        with patch("azpaddypy.mcp.az_commands._run_az_command", return_value=mock_sub_info):
            result = get_subscription_info()

            assert isinstance(result, dict)
            assert "subscriptionId" in result
            assert result["name"] == "Test Subscription"

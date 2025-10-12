"""
Tests for azpaddypy.mcp.az_commands module.

Tests Azure SDK command wrappers used by the MCP server.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, call
from typing import Any, Dict, List

# Import az_commands directly without going through __init__.py to avoid fastmcp
import importlib.util
spec = importlib.util.spec_from_file_location("az_commands", "azpaddypy/mcp/az_commands.py")
az_commands = importlib.util.module_from_spec(spec)
spec.loader.exec_module(az_commands)

AzureCliError = az_commands.AzureCliError


@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset module state before each test."""
    az_commands._credential = None
    az_commands._subscription_id = None
    az_commands._clients = {
        "resource": None,
        "storage_mgmt": None,
        "cosmos": None,
        "subscription": None,
    }
    yield
    # Reset after test as well
    az_commands._credential = None
    az_commands._subscription_id = None
    az_commands._clients = {
        "resource": None,
        "storage_mgmt": None,
        "cosmos": None,
        "subscription": None,
    }


@pytest.fixture
def mock_credential():
    """Create a mock Azure credential."""
    return Mock()


@pytest.fixture
def mock_subscription_id():
    """Create a mock subscription ID."""
    return "12345678-1234-1234-1234-123456789abc"


class TestInitialization:
    """Test module initialization functions."""

    def test_initialize_with_explicit_params(self, mock_credential, mock_subscription_id):
        """Test explicit initialization with credential and subscription ID."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

        assert az_commands._credential == mock_credential
        assert az_commands._subscription_id == mock_subscription_id

    def test_initialize_with_env_var(self, mock_credential, monkeypatch):
        """Test initialization with subscription ID from environment variable."""
        sub_id = "env-subscription-id"
        monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", sub_id)

        az_commands.initialize(credential=mock_credential)

        assert az_commands._credential == mock_credential
        assert az_commands._subscription_id == sub_id

    def test_initialize_with_default_credential(self, monkeypatch):
        """Test initialization with DefaultAzureCredential."""
        sub_id = "env-subscription-id"
        monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", sub_id)
        mock_cred = Mock()

        with patch.object(az_commands, "DefaultAzureCredential") as mock_default_cred_class:
            mock_default_cred_class.return_value = mock_cred

            az_commands.initialize()

            assert az_commands._credential == mock_cred
            assert az_commands._subscription_id == sub_id
            mock_default_cred_class.assert_called_once()

    def test_initialize_without_subscription_id_raises_error(self, mock_credential):
        """Test that initialization without subscription ID raises error."""
        with pytest.raises(AzureCliError, match="subscription_id must be provided"):
            az_commands.initialize(credential=mock_credential, subscription_id=None)

    def test_initialize_from_mgmt_config_success(self):
        """Test successful initialization from mgmt_config."""
        mock_identity = Mock()
        mock_credential = Mock()
        mock_identity.get_credential.return_value = mock_credential

        mock_keyvault = Mock()
        mock_secret = Mock()
        mock_secret.value = "subscription-from-kv"
        mock_keyvault.get_secret.return_value = mock_secret

        mock_keyvaults = {"main": mock_keyvault}

        with patch.dict("sys.modules", {
            "mgmt_config": Mock(identity=mock_identity, keyvaults=mock_keyvaults)
        }):
            az_commands.initialize_from_mgmt_config()

            assert az_commands._credential == mock_credential
            assert az_commands._subscription_id == "subscription-from-kv"

    def test_initialize_from_mgmt_config_import_error(self):
        """Test initialization from mgmt_config when module not found."""
        with patch.dict("sys.modules", {"mgmt_config": None}):
            with pytest.raises(AzureCliError, match="Failed to import mgmt_config"):
                az_commands.initialize_from_mgmt_config()

    def test_ensure_initialized_auto_initializes(self, monkeypatch):
        """Test that _ensure_initialized auto-initializes when needed."""
        monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "auto-init-sub-id")

        with patch.object(az_commands, "DefaultAzureCredential") as mock_cred_class:
            mock_cred = Mock()
            mock_cred_class.return_value = mock_cred

            az_commands._ensure_initialized()

            assert az_commands._credential == mock_cred
            assert az_commands._subscription_id == "auto-init-sub-id"


class TestResourceGroups:
    """Test resource group related functions."""

    @pytest.fixture
    def setup_clients(self, mock_credential, mock_subscription_id):
        """Setup initialized module."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

    def test_list_resource_groups(self, setup_clients):
        """Test listing resource groups."""
        mock_rg1 = Mock()
        mock_rg1.as_dict.return_value = {"name": "rg-1", "location": "eastus"}
        mock_rg2 = Mock()
        mock_rg2.as_dict.return_value = {"name": "rg-2", "location": "westus"}

        with patch.object(az_commands, "ResourceManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.resource_groups.list.return_value = [mock_rg1, mock_rg2]
            mock_client_class.return_value = mock_client

            result = az_commands.list_resource_groups()

            assert len(result) == 2
            assert result[0]["name"] == "rg-1"
            assert result[1]["name"] == "rg-2"

    def test_list_resources_in_group(self, setup_clients):
        """Test listing resources in a resource group."""
        mock_resource = Mock()
        mock_resource.as_dict.return_value = {
            "name": "storage-account",
            "type": "Microsoft.Storage/storageAccounts"
        }

        with patch.object(az_commands, "ResourceManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.resources.list_by_resource_group.return_value = [mock_resource]
            mock_client_class.return_value = mock_client

            result = az_commands.list_resources_in_group("test-rg")

            assert len(result) == 1
            assert result[0]["name"] == "storage-account"
            mock_client.resources.list_by_resource_group.assert_called_once_with("test-rg")

    def test_export_resource_group_template(self, setup_clients):
        """Test exporting resource group template."""
        mock_export_result = Mock()
        mock_export_result.as_dict.return_value = {
            "template": {
                "$schema": "https://schema.management.azure.com/...",
                "resources": []
            }
        }

        with patch.object(az_commands, "ResourceManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_operation = Mock()
            mock_operation.result.return_value = mock_export_result
            mock_client.resource_groups.begin_export_template.return_value = mock_operation
            mock_client_class.return_value = mock_client

            result = az_commands.export_resource_group_template("test-rg")

            # The function extracts and returns the template directly
            assert "$schema" in result
            assert "resources" in result


class TestStorageAccounts:
    """Test storage account related functions."""

    @pytest.fixture
    def setup_clients(self, mock_credential, mock_subscription_id):
        """Setup initialized module."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

    def test_list_storage_accounts_all(self, setup_clients):
        """Test listing all storage accounts."""
        mock_account = Mock()
        mock_account.as_dict.return_value = {
            "name": "storageaccount1",
            "location": "eastus"
        }

        with patch.object(az_commands, "StorageManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.storage_accounts.list.return_value = [mock_account]
            mock_client_class.return_value = mock_client

            result = az_commands.list_storage_accounts()

            assert len(result) == 1
            assert result[0]["name"] == "storageaccount1"

    def test_list_storage_accounts_by_resource_group(self, setup_clients):
        """Test listing storage accounts in a resource group."""
        mock_account = Mock()
        mock_account.as_dict.return_value = {
            "name": "storageaccount1",
            "location": "eastus"
        }

        with patch.object(az_commands, "StorageManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.storage_accounts.list_by_resource_group.return_value = [mock_account]
            mock_client_class.return_value = mock_client

            result = az_commands.list_storage_accounts(resource_group="test-rg")

            assert len(result) == 1
            mock_client.storage_accounts.list_by_resource_group.assert_called_once_with("test-rg")

    def test_list_storage_containers(self, setup_clients):
        """Test listing storage containers."""
        # Mock storage account key retrieval
        mock_key = Mock()
        mock_key.value = "mock-storage-key"
        mock_keys_response = Mock()
        mock_keys_response.keys = [mock_key]

        # Mock container properties
        mock_container = Mock()
        mock_container.name = "container1"
        mock_container.last_modified = None
        mock_container.public_access = None
        mock_container.metadata = {}

        with patch.object(az_commands, "StorageManagementClient") as mock_storage_mgmt_class, \
             patch.object(az_commands, "BlobServiceClient") as mock_blob_service_class:

            mock_storage_mgmt = Mock()
            mock_storage_mgmt.storage_accounts.list_keys.return_value = mock_keys_response
            mock_storage_mgmt_class.return_value = mock_storage_mgmt

            mock_blob_service = Mock()
            mock_blob_service.list_containers.return_value = [mock_container]
            mock_blob_service_class.return_value = mock_blob_service

            result = az_commands.list_storage_containers("testaccount", "test-rg")

            assert len(result) == 1
            assert result[0]["name"] == "container1"
            mock_storage_mgmt.storage_accounts.list_keys.assert_called_once_with("test-rg", "testaccount")


class TestCosmosDB:
    """Test Cosmos DB related functions."""

    @pytest.fixture
    def setup_clients(self, mock_credential, mock_subscription_id):
        """Setup initialized module."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

    def test_list_cosmosdb_accounts(self, setup_clients):
        """Test listing Cosmos DB accounts."""
        mock_account = Mock()
        mock_account.as_dict.return_value = {
            "name": "cosmosaccount1",
            "location": "eastus"
        }

        with patch.object(az_commands, "CosmosDBManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.database_accounts.list.return_value = [mock_account]
            mock_client_class.return_value = mock_client

            result = az_commands.list_cosmosdb_accounts()

            assert len(result) == 1
            assert result[0]["name"] == "cosmosaccount1"

    def test_list_cosmosdb_sql_databases(self, setup_clients):
        """Test listing Cosmos DB SQL databases."""
        mock_database = Mock()
        mock_database.as_dict.return_value = {
            "name": "database1",
            "id": "/subscriptions/.../databases/database1"
        }

        with patch.object(az_commands, "CosmosDBManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.sql_resources.list_sql_databases.return_value = [mock_database]
            mock_client_class.return_value = mock_client

            result = az_commands.list_cosmosdb_sql_databases("account1", "test-rg")

            assert len(result) == 1
            assert result[0]["name"] == "database1"

    def test_list_cosmosdb_sql_containers(self, setup_clients):
        """Test listing Cosmos DB SQL containers."""
        mock_container = Mock()
        mock_container.as_dict.return_value = {
            "name": "container1",
            "id": "/subscriptions/.../containers/container1"
        }

        with patch.object(az_commands, "CosmosDBManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.sql_resources.list_sql_containers.return_value = [mock_container]
            mock_client_class.return_value = mock_client

            result = az_commands.list_cosmosdb_sql_containers("account1", "test-rg", "database1")

            assert len(result) == 1
            assert result[0]["name"] == "container1"


class TestSubscription:
    """Test subscription and location functions."""

    @pytest.fixture
    def setup_clients(self, mock_credential, mock_subscription_id):
        """Setup initialized module."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

    def test_get_subscription_info(self, setup_clients, mock_subscription_id):
        """Test getting subscription information."""
        mock_subscription = Mock()
        mock_subscription.as_dict.return_value = {
            "subscriptionId": mock_subscription_id,
            "displayName": "Test Subscription",
            "state": "Enabled"
        }

        with patch.object(az_commands, "SubscriptionClient") as mock_client_class:
            mock_client = Mock()
            mock_client.subscriptions.get.return_value = mock_subscription
            mock_client_class.return_value = mock_client

            result = az_commands.get_subscription_info()

            assert result["subscriptionId"] == mock_subscription_id
            assert result["displayName"] == "Test Subscription"

    def test_list_locations(self, setup_clients, mock_subscription_id):
        """Test listing Azure locations."""
        mock_location = Mock()
        mock_location.as_dict.return_value = {
            "name": "eastus",
            "displayName": "East US"
        }

        with patch.object(az_commands, "SubscriptionClient") as mock_client_class:
            mock_client = Mock()
            mock_client.subscriptions.list_locations.return_value = [mock_location]
            mock_client_class.return_value = mock_client

            result = az_commands.list_locations()

            assert len(result) == 1
            assert result[0]["name"] == "eastus"


class TestBicepDecompilation:
    """Test Bicep decompilation function."""

    @pytest.fixture
    def setup_clients(self, mock_credential, mock_subscription_id):
        """Setup initialized module."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

    def test_decompile_arm_to_bicep_success(self, setup_clients, tmp_path):
        """Test successful ARM to Bicep decompilation."""
        arm_file = tmp_path / "template.json"
        arm_file.write_text('{"$schema": "..."}')
        bicep_file = tmp_path / "template.bicep"

        with patch("shutil.which") as mock_which, \
             patch("subprocess.run") as mock_run:

            mock_which.return_value = "/usr/bin/az"
            mock_run.return_value = Mock(returncode=0)

            result = az_commands.decompile_arm_to_bicep(str(arm_file), str(bicep_file))

            assert result == str(bicep_file)
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "az"
            assert call_args[1] == "bicep"
            assert call_args[2] == "decompile"

    def test_decompile_arm_to_bicep_no_cli(self, setup_clients, tmp_path):
        """Test decompilation when Azure CLI is not available."""
        arm_file = tmp_path / "template.json"

        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            with pytest.raises(AzureCliError, match="Azure CLI is not available"):
                az_commands.decompile_arm_to_bicep(str(arm_file))

    def test_decompile_arm_to_bicep_default_output_path(self, setup_clients, tmp_path):
        """Test decompilation with default output path."""
        arm_file = tmp_path / "template.json"
        arm_file.write_text('{"$schema": "..."}')

        with patch("shutil.which") as mock_which, \
             patch("subprocess.run") as mock_run:

            mock_which.return_value = "/usr/bin/az"
            mock_run.return_value = Mock(returncode=0)

            result = az_commands.decompile_arm_to_bicep(str(arm_file))

            expected_output = str(tmp_path / "template.bicep")
            assert result == expected_output


class TestErrorHandling:
    """Test error handling throughout the module."""

    def test_uninitialized_module_raises_error(self):
        """Test that using functions without initialization raises error."""
        with pytest.raises(AzureCliError, match="Module not initialized"):
            az_commands.list_resource_groups()

    def test_azure_sdk_error_wrapped(self, mock_credential, mock_subscription_id):
        """Test that Azure SDK errors are wrapped in AzureCliError."""
        az_commands.initialize(credential=mock_credential, subscription_id=mock_subscription_id)

        with patch.object(az_commands, "ResourceManagementClient") as mock_client_class:
            mock_client = Mock()
            mock_client.resource_groups.list.side_effect = Exception("Azure SDK error")
            mock_client_class.return_value = mock_client

            with pytest.raises(AzureCliError, match="Failed to list resource groups"):
                az_commands.list_resource_groups()

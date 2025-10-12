"""
Azure SDK-based command wrappers for MCP server.

Uses Azure SDK (azure-mgmt-*, azure-identity, azure-storage-blob) to interact with Azure resources.
This module is designed to be independent and can be initialized with credentials from various sources.
"""

import json
import os
from typing import Any, Dict, List, Optional

# Management clients
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.cosmosdb import CosmosDBManagementClient

# Identity
from azure.identity import DefaultAzureCredential, AzureCliCredential

# Storage data-plane (for listing containers)
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureNamedKeyCredential

# Exceptions
class AzureCliError(Exception):
    """Raised for errors interacting with Azure SDKs."""
    pass


# -------------------------
# Module-level state for clients
# -------------------------
_credential = None
_subscription_id = None


# -------------------------
# Initialization functions
# -------------------------
def initialize_from_mgmt_config() -> None:
    """
    Initialize the module using mgmt_config from the project root.
    This is the preferred method when running as part of the azpaddypy application.

    Raises:
        ImportError: If mgmt_config cannot be imported
        AzureCliError: If initialization fails
    """
    global _credential, _subscription_id

    try:
        from mgmt_config import keyvaults

        # Use DefaultAzureCredential directly instead of getting from mgmt_config
        _credential = DefaultAzureCredential()

        # Get subscription ID from Key Vault
        main_kv = keyvaults.get("main")
        if main_kv is None:
            raise AzureCliError("main key vault client not found in mgmt_config.keyvaults")

        secret = main_kv.get_secret("subscription-id")
        if secret is None:
            raise AzureCliError('Subscription id secret "subscription-id" not found in main key vault')

        if isinstance(secret, str):
            _subscription_id = secret
        elif hasattr(secret, "value"):
            _subscription_id = secret.value
        else:
            _subscription_id = str(secret)

    except ImportError as e:
        raise AzureCliError(
            f"Failed to import mgmt_config. Ensure the module is available or use initialize() instead: {e}"
        ) from e
    except Exception as e:
        raise AzureCliError(f"Failed to initialize from mgmt_config: {e}") from e


def initialize(
    credential: Optional[Any] = None,
    subscription_id: Optional[str] = None
) -> None:
    """
    Initialize the module with explicit credentials and subscription ID.

    Args:
        credential: Azure credential object (DefaultAzureCredential, AzureCliCredential, etc.)
                   If None, uses DefaultAzureCredential
        subscription_id: Azure subscription ID. If None, attempts to read from
                        AZURE_SUBSCRIPTION_ID environment variable

    Raises:
        AzureCliError: If subscription_id cannot be determined
    """
    global _credential, _subscription_id

    # Set credential
    if credential is None:
        try:
            _credential = DefaultAzureCredential()
        except Exception as e:
            raise AzureCliError(f"Failed to create DefaultAzureCredential: {e}") from e
    else:
        _credential = credential

    # Set subscription ID
    if subscription_id is None:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            raise AzureCliError(
                "subscription_id must be provided or set in AZURE_SUBSCRIPTION_ID environment variable"
            )

    _subscription_id = subscription_id


def _ensure_initialized() -> None:
    """
    Ensure the module is initialized. If not, try to auto-initialize.

    Raises:
        AzureCliError: If module is not initialized and auto-initialization fails
    """
    global _credential, _subscription_id

    if _credential is None or _subscription_id is None:
        # Try to auto-initialize from mgmt_config
        try:
            initialize_from_mgmt_config()
        except (ImportError, AzureCliError):
            # Fall back to default initialization
            try:
                initialize()
            except AzureCliError as e:
                raise AzureCliError(
                    "Module not initialized. Call initialize() or initialize_from_mgmt_config() first."
                ) from e


def _get_credential():
    """Get the credential object."""
    _ensure_initialized()
    return _credential


def _get_subscription_id() -> str:
    """Get the subscription ID."""
    _ensure_initialized()
    return _subscription_id


# -------------------------
# Lazy clients (initialized on first use)
# -------------------------
_clients = {
    "resource": None,
    "storage_mgmt": None,
    "cosmos": None,
    "subscription": None,
}


def _init_clients():
    """Initialize mgmt clients once (lazy)."""
    if _clients["resource"] is not None:
        return

    cred = _get_credential()
    subscription_id = _get_subscription_id()

    _clients["resource"] = ResourceManagementClient(cred, subscription_id)
    _clients["storage_mgmt"] = StorageManagementClient(cred, subscription_id)
    _clients["cosmos"] = CosmosDBManagementClient(cred, subscription_id)
    _clients["subscription"] = SubscriptionClient(cred)


# -------------------------
# Resource Group & Resource functions
# -------------------------
def list_resource_groups() -> List[Dict[str, Any]]:
    """List all resource groups in the subscription."""
    try:
        _init_clients()
        client: ResourceManagementClient = _clients["resource"]
        rgs = client.resource_groups.list()
        return [rg.as_dict() for rg in rgs]
    except Exception as e:
        raise AzureCliError(f"Failed to list resource groups: {e}") from e


def list_resources_in_group(resource_group: str) -> List[Dict[str, Any]]:
    """List resources in a resource group."""
    try:
        _init_clients()
        client: ResourceManagementClient = _clients["resource"]
        resources = client.resources.list_by_resource_group(resource_group)
        return [r.as_dict() for r in resources]
    except Exception as e:
        raise AzureCliError(f"Failed to list resources in group '{resource_group}': {e}") from e


def export_resource_group_template(resource_group: str) -> Dict[str, Any]:
    """
    Export the ARM template for a resource group (ARM JSON).
    Uses ResourceManagementClient.resource_groups.export_template method.
    """
    try:
        _init_clients()
        client: ResourceManagementClient = _clients["resource"]
        # The SDK's export_template returns a response model; call it with default parameters.
        export_result = client.resource_groups.begin_export_template(
            resource_group_name=resource_group,
            parameters={
                "options": "IncludeParameterDefaultValue",
                "resources": ["*"]
            }
        ).result()
        # export_result.properties.template is usually the template dict (depending on SDK version)
        # fallback to as_dict when available
        if hasattr(export_result, "as_dict"):
            d = export_result.as_dict()
            # try to find the template content inside the returned dict
            if "template" in d:
                return d["template"]
            # older/newer SDKs may nest differently
            return d
        # fallback: try to inspect attributes
        if hasattr(export_result, "template"):
            return export_result.template
        # as final fallback, return raw object converted to str
        return {"export_result": str(export_result)}
    except Exception as e:
        raise AzureCliError(f"Failed to export resource group template for '{resource_group}': {e}") from e


def decompile_arm_to_bicep(arm_template_path: str, output_path: Optional[str] = None) -> str:
    """
    Decompile an ARM template to Bicep format using Azure CLI.

    Note: This function requires Azure CLI with Bicep extension installed.
    It falls back to subprocess call since Bicep decompilation is not available
    in the Azure SDK.

    Args:
        arm_template_path: Path to the ARM template JSON file
        output_path: Optional output path for the Bicep file. If not provided,
                    uses the same name with .bicep extension

    Returns:
        Path to the generated Bicep file

    Raises:
        AzureCliError: If decompilation fails or Azure CLI is not available
    """
    import subprocess
    import shutil

    # Check if az CLI is available
    if shutil.which("az") is None:
        raise AzureCliError(
            "Azure CLI is not available. Install Azure CLI to use Bicep decompilation. "
            "See: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
        )

    # Determine output path
    if output_path is None:
        output_path = arm_template_path.rsplit(".", 1)[0] + ".bicep"

    try:
        # Run az bicep decompile command
        result = subprocess.run(
            ["az", "bicep", "decompile", "--file", arm_template_path, "--outfile", output_path],
            capture_output=True,
            text=True,
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise AzureCliError(
            f"Bicep decompilation failed: {e.stderr or e.stdout or str(e)}"
        ) from e
    except Exception as e:
        raise AzureCliError(f"Failed to decompile ARM template: {e}") from e


# -------------------------
# Storage functions
# -------------------------
def list_storage_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """List storage accounts (all or by resource group)."""
    try:
        _init_clients()
        storage_client: StorageManagementClient = _clients["storage_mgmt"]
        if resource_group:
            accounts = storage_client.storage_accounts.list_by_resource_group(resource_group)
        else:
            accounts = storage_client.storage_accounts.list()
        # Convert models to dicts (as_dict available on model objects)
        result = []
        for acc in accounts:
            if hasattr(acc, "as_dict"):
                result.append(acc.as_dict())
            else:
                # build minimal dict fallback
                result.append({
                    "name": getattr(acc, "name", None),
                    "id": getattr(acc, "id", None),
                    "location": getattr(acc, "location", None),
                    "kind": getattr(acc, "kind", None),
                    "sku": getattr(acc, "sku", None),
                })
        return result
    except Exception as e:
        raise AzureCliError(f"Failed to list storage accounts: {e}") from e


def list_storage_containers(account_name: str, resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List blob containers in a storage account.

    Implementation:
      1. Use StorageManagementClient to retrieve account keys (requires resource_group).
      2. Use azure-storage-blob BlobServiceClient with StorageSharedKeyCredential to list containers.

    If resource_group is not provided, we'll attempt to locate the storage account via management client.
    """
    try:
        _init_clients()
        storage_client: StorageManagementClient = _clients["storage_mgmt"]

        # If resource_group not provided, try to find the account
        if resource_group is None:
            # search across subscription (this can be slower)
            found_rg = None
            for sa in storage_client.storage_accounts.list():
                if getattr(sa, "name", "").lower() == account_name.lower():
                    # SDK has resource_group in id string sometimes, try to parse it
                    sa_id = getattr(sa, "id", "")
                    # id format: /subscriptions/{subId}/resourceGroups/{rg}/providers/...
                    parts = [p for p in sa_id.split("/") if p]
                    if "resourceGroups" in parts:
                        rg_index = parts.index("resourceGroups") + 1
                        if rg_index < len(parts):
                            found_rg = parts[rg_index]
                            break
            if found_rg is None:
                raise AzureCliError("resource_group not provided and could not be inferred for storage account")
            resource_group = found_rg

        # Get account keys (management plane) to create shared-key cred
        keys = storage_client.storage_accounts.list_keys(resource_group, account_name)
        # `keys.keys` usually holds the key objects; pick first
        key_value = None
        if hasattr(keys, "keys") and len(keys.keys) > 0:
            # each key may be a dict-like or object with .value
            first = keys.keys[0]
            if isinstance(first, dict) and "value" in first:
                key_value = first["value"]
            elif hasattr(first, "value"):
                key_value = first.value
            elif hasattr(first, "key"):
                key_value = first.key
        # Some SDKs return a dict-like with 'value' key under keys[0]
        if key_value is None:
            # try direct attribute
            try:
                key_value = keys.as_dict()["keys"][0]["value"]
            except Exception:
                raise AzureCliError("Could not parse storage account keys from management client response")

        # Build BlobServiceClient using named key credential
        account_url = f"https://{account_name}.blob.core.windows.net"
        named_key_cred = AzureNamedKeyCredential(account_name, key_value)
        blob_service = BlobServiceClient(account_url=account_url, credential=named_key_cred)

        # List containers
        containers = blob_service.list_containers()
        result = []
        for c in containers:
            # c is ContainerProperties; convert to dict
            container_dict = {
                "name": getattr(c, "name", None),
            }
            # container properties (last_modified, metadata, public_access) when available
            try:
                props = {}
                if hasattr(c, "last_modified"):
                    props["lastModified"] = c.last_modified.isoformat() if c.last_modified else None
                if hasattr(c, "public_access"):
                    props["publicAccess"] = c.public_access
                if hasattr(c, "metadata"):
                    props["metadata"] = c.metadata
                container_dict["properties"] = props
            except Exception:
                # ignore property extraction errors
                pass
            result.append(container_dict)
        return result

    except Exception as e:
        raise AzureCliError(f"Failed to list containers for storage account '{account_name}': {e}") from e


# -------------------------
# Cosmos DB functions
# -------------------------
def list_cosmosdb_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Cosmos DB accounts across subscription or within a resource group."""
    try:
        _init_clients()
        cosmos_client: CosmosDBManagementClient = _clients["cosmos"]
        if resource_group:
            accounts = cosmos_client.database_accounts.list_by_resource_group(resource_group)
        else:
            accounts = cosmos_client.database_accounts.list()
        return [a.as_dict() for a in accounts]
    except Exception as e:
        raise AzureCliError(f"Failed to list Cosmos DB accounts: {e}") from e


def list_cosmosdb_sql_databases(account_name: str, resource_group: str) -> List[Dict[str, Any]]:
    """
    List SQL databases under a Cosmos DB account.
    Uses the SqlResources operations on the Cosmos DB management client.
    """
    try:
        _init_clients()
        cosmos_client: CosmosDBManagementClient = _clients["cosmos"]
        # The method signature varies across SDK versions; commonly:
        # cosmos_client.sql_resources.list_sql_databases(resource_group_name, account_name)
        dbs = cosmos_client.sql_resources.list_sql_databases(resource_group, account_name)
        # list_sql_databases returns an iterable of models
        return [d.as_dict() if hasattr(d, "as_dict") else dict(d) for d in dbs]
    except Exception as e:
        raise AzureCliError(f"Failed to list SQL databases for Cosmos DB account '{account_name}': {e}") from e


def list_cosmosdb_sql_containers(account_name: str, resource_group: str, database_name: str) -> List[Dict[str, Any]]:
    """List SQL containers (aka containers/collections) in a Cosmos DB SQL database."""
    try:
        _init_clients()
        cosmos_client: CosmosDBManagementClient = _clients["cosmos"]
        containers = cosmos_client.sql_resources.list_sql_containers(resource_group, account_name, database_name)
        return [c.as_dict() if hasattr(c, "as_dict") else dict(c) for c in containers]
    except Exception as e:
        raise AzureCliError(
            f"Failed to list SQL containers for database '{database_name}' in account '{account_name}': {e}"
        ) from e


# -------------------------
# Subscription and location functions
# -------------------------
def get_subscription_info() -> Dict[str, Any]:
    """Get information about the current subscription (id, display name, state, tenant)."""
    try:
        _init_clients()
        subscription_id = _get_subscription_id()
        sub_client: SubscriptionClient = _clients["subscription"]
        # subscription_client.subscriptions.get(subscription_id) is the common method
        sub = sub_client.subscriptions.get(subscription_id)
        # Return as dict when possible
        if hasattr(sub, "as_dict"):
            return sub.as_dict()
        # fallback attributes
        return {
            "subscriptionId": getattr(sub, "subscription_id", subscription_id),
            "displayName": getattr(sub, "display_name", None),
            "state": getattr(sub, "state", None),
            "tenantId": getattr(sub, "tenant_id", None),
        }
    except Exception as e:
        raise AzureCliError(f"Failed to get subscription info: {e}") from e


def list_locations() -> List[Dict[str, Any]]:
    """List locations available for the subscription."""
    try:
        _init_clients()
        subscription_id = _get_subscription_id()
        sub_client: SubscriptionClient = _clients["subscription"]
        locs = sub_client.subscriptions.list_locations(subscription_id)
        return [l.as_dict() if hasattr(l, "as_dict") else {"name": getattr(l, "name", None), "displayName": getattr(l, "display_name", None)} for l in locs]
    except Exception as e:
        raise AzureCliError(f"Failed to list locations: {e}") from e

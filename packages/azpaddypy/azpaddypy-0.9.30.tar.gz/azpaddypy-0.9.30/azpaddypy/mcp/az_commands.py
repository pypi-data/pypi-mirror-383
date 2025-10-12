"""
Azure SDK-based command wrappers for MCP server.

Replaces subprocess 'az' calls with Azure SDK (azure-mgmt-*, azure-identity, azure-storage-blob).
Relies on `mgmt_config` to provide identity / keyvault and to retrieve the subscription id
(secret named "subscription-id" in the main key vault).
"""

import json
from typing import Any, Dict, List, Optional

# mgmt_config provides identity, keyvaults and possibly storage helper objects
from mgmt_config import identity, keyvaults

# Management clients
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.cosmosdb import CosmosDBManagementClient

# Storage data-plane (for listing containers)
from azure.storage.blob import BlobServiceClient, ContainerProperties, StorageSharedKeyCredential

# Exceptions
class AzureCliError(Exception):
    """Legacy name retained for compatibility: raised for errors interacting with Azure SDKs."""
    pass


# -------------------------
# Helpers: credential + subscription
# -------------------------
def _get_credential():
    """
    Return a credential object from mgmt_config.identity.
    This assumes mgmt_config.identity has a get_credential() method (as in your mgmt_config).
    If identity itself is already a credential, return it directly.
    """
    try:
        # handle both patterns: AzureIdentity object (with get_credential) or direct credential
        if hasattr(identity, "get_credential"):
            cred = identity.get_credential()
        else:
            cred = identity
        return cred
    except Exception as e:
        raise AzureCliError(f"Failed to obtain Azure credential from mgmt_config.identity: {e}") from e


def _get_subscription_id() -> str:
    """
    Read the subscription id from the main key vault secret "subscription-id".
    Supports either:
     - keyvaults.get("main").get_secret("subscription-id") -> returns plain string
     - or returns an object with .value (KeyVaultSecret)
    """
    try:
        main_kv = keyvaults.get("main")
        if main_kv is None:
            raise AzureCliError("main key vault client not found in mgmt_config.keyvaults")
        secret = main_kv.get_secret("subscription-id")
        # support either string or KeyVaultSecret-like object
        if secret is None:
            raise AzureCliError('Subscription id secret "subscription-id" not found in main key vault')
        if isinstance(secret, str):
            return secret
        if hasattr(secret, "value"):
            return secret.value
        # fallback to string conversion
        return str(secret)
    except Exception as e:
        raise AzureCliError(f"Failed to obtain subscription id from key vault: {e}") from e


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
    Decompiling ARM -> Bicep requires the Bicep CLI (or `az bicep decompile`).
    This project is intended to use SDKs for management plane operations; the Bicep decompiler
    is currently a CLI tool and not exposed via the management SDKs.

    If you want this to call the CLI automatically, tell me and I can add a call to:
       subprocess.run(["az", "bicep", "decompile", "--file", arm_template_path, "--outfile", output_path])
    for environments where az/bicep is available.

    For now, raise NotImplementedError to keep the SDK-only approach clear.
    """
    raise NotImplementedError(
        "ARM -> Bicep decompilation is not implemented in the SDK. "
        "Install Bicep CLI or Azure CLI and run `az bicep decompile` locally, "
        "or tell me to enable an automatic CLI fallback in this function."
    )


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

        # Build BlobServiceClient using shared key credential
        account_url = f"https://{account_name}.blob.core.windows.net"
        shared_cred = StorageSharedKeyCredential(account_name, key_value)
        blob_service = BlobServiceClient(account_url=account_url, credential=shared_cred)

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

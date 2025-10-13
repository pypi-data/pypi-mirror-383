from typing import Any, Dict, List, Optional
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureNamedKeyCredential

from .base import get_context, AzureMCPError


def list_storage_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        ctx = get_context()
        client = ctx.storage_client

        if resource_group:
            accounts = list(client.storage_accounts.list_by_resource_group(resource_group))
        else:
            accounts = list(client.storage_accounts.list())

        result = []
        for acc in accounts:
            if hasattr(acc, "as_dict"):
                result.append(acc.as_dict())
            else:
                result.append({
                    "name": getattr(acc, "name", None),
                    "id": getattr(acc, "id", None),
                    "location": getattr(acc, "location", None),
                    "kind": getattr(acc, "kind", None),
                    "sku": getattr(acc, "sku", None),
                })

        return result

    except AzureMCPError:
        raise
    except Exception as e:
        raise AzureMCPError(f"Failed to list storage accounts: {e}") from e


def list_storage_containers(
    account_name: str,
    resource_group: Optional[str] = None
) -> List[Dict[str, Any]]:
    try:
        ctx = get_context()
        client = ctx.storage_client

        if resource_group is None:
            found_rg = None
            for sa in list(client.storage_accounts.list()):
                if getattr(sa, "name", "").lower() == account_name.lower():
                    sa_id = getattr(sa, "id", "")
                    parts = [p for p in sa_id.split("/") if p]
                    if "resourceGroups" in parts:
                        rg_index = parts.index("resourceGroups") + 1
                        if rg_index < len(parts):
                            found_rg = parts[rg_index]
                            break

            if found_rg is None:
                raise AzureMCPError(
                    "resource_group not provided and could not be inferred for storage account"
                )
            resource_group = found_rg

        keys = client.storage_accounts.list_keys(resource_group, account_name)

        key_value = None
        if hasattr(keys, "keys") and len(keys.keys) > 0:
            first = keys.keys[0]
            if isinstance(first, dict) and "value" in first:
                key_value = first["value"]
            elif hasattr(first, "value"):
                key_value = first.value
            elif hasattr(first, "key"):
                key_value = first.key

        if key_value is None:
            try:
                key_value = keys.as_dict()["keys"][0]["value"]
            except Exception:
                raise AzureMCPError(
                    "Could not parse storage account keys from management client response"
                )

        account_url = f"https://{account_name}.blob.core.windows.net"
        named_key_cred = AzureNamedKeyCredential(account_name, key_value)
        blob_service = BlobServiceClient(
            account_url=account_url,
            credential=named_key_cred
        )

        containers = blob_service.list_containers()
        result = []
        for c in containers:
            container_dict = {"name": getattr(c, "name", None)}

            try:
                props = {}
                if hasattr(c, "last_modified"):
                    props["lastModified"] = (
                        c.last_modified.isoformat() if c.last_modified else None
                    )
                if hasattr(c, "public_access"):
                    props["publicAccess"] = c.public_access
                if hasattr(c, "metadata"):
                    props["metadata"] = c.metadata
                container_dict["properties"] = props
            except Exception:
                pass

            result.append(container_dict)

        return result

    except AzureMCPError:
        raise
    except Exception as e:
        raise AzureMCPError(
            f"Failed to list containers for storage account '{account_name}': {e}"
        ) from e

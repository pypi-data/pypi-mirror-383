"""Azure Cosmos DB operations."""

from typing import Any, Dict, List, Optional

from .base import get_context, AzureMCPError


def list_cosmosdb_accounts(resource_group: Optional[str] = None) -> List[Dict[str, Any]]:
    """List Cosmos DB accounts in the subscription or a specific resource group.

    Args:
        resource_group: Optional resource group name. If provided, lists only
                       Cosmos DB accounts in that group. Otherwise, lists all.

    Returns:
        List of Cosmos DB accounts with their properties

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        client = ctx.cosmos_client

        if resource_group:
            accounts = client.database_accounts.list_by_resource_group(resource_group)
        else:
            accounts = client.database_accounts.list()

        return [a.as_dict() for a in accounts]

    except Exception as e:
        raise AzureMCPError(f"Failed to list Cosmos DB accounts: {e}") from e


def list_cosmosdb_sql_databases(
    account_name: str,
    resource_group: str
) -> List[Dict[str, Any]]:
    """List SQL databases in a Cosmos DB account.

    Args:
        account_name: Name of the Cosmos DB account
        resource_group: Resource group containing the account

    Returns:
        List of SQL databases with their properties

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        client = ctx.cosmos_client

        dbs = client.sql_resources.list_sql_databases(resource_group, account_name)
        return [
            d.as_dict() if hasattr(d, "as_dict") else dict(d)
            for d in dbs
        ]

    except Exception as e:
        raise AzureMCPError(
            f"Failed to list SQL databases for Cosmos DB account '{account_name}': {e}"
        ) from e


def list_cosmosdb_sql_containers(
    account_name: str,
    resource_group: str,
    database_name: str
) -> List[Dict[str, Any]]:
    """List SQL containers in a Cosmos DB database.

    Args:
        account_name: Name of the Cosmos DB account
        resource_group: Resource group containing the account
        database_name: Name of the database

    Returns:
        List of SQL containers with their properties

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        client = ctx.cosmos_client

        containers = client.sql_resources.list_sql_containers(
            resource_group,
            account_name,
            database_name
        )
        return [
            c.as_dict() if hasattr(c, "as_dict") else dict(c)
            for c in containers
        ]

    except Exception as e:
        raise AzureMCPError(
            f"Failed to list SQL containers for database '{database_name}' "
            f"in account '{account_name}': {e}"
        ) from e

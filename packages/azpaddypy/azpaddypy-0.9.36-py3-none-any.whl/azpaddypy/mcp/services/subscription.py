"""Azure Subscription and location operations."""

from typing import Any, Dict, List, Optional

from .base import get_context, AzureMCPError


def list_subscriptions() -> List[Dict[str, Any]]:
    """List all subscriptions accessible to the current credential.

    This method does not require a subscription ID to be set, making it useful
    for auto-discovery of available subscriptions.

    Returns:
        List of subscriptions with their properties including id, name, state, and tenant

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        # Create subscription client with just credential (no subscription_id needed)
        from azure.mgmt.resource import SubscriptionClient
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        client = SubscriptionClient(credential)

        subs = list(client.subscriptions.list())
        return [
            s.as_dict() if hasattr(s, "as_dict")
            else {
                "subscriptionId": getattr(s, "subscription_id", None),
                "displayName": getattr(s, "display_name", None),
                "state": getattr(s, "state", None),
                "tenantId": getattr(s, "tenant_id", None),
            }
            for s in subs
        ]

    except Exception as e:
        raise AzureMCPError(f"Failed to list subscriptions: {e}") from e


def get_subscription_info() -> Dict[str, Any]:
    """Get information about the current Azure subscription.

    Returns:
        Subscription information including id, name, state, and tenant

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        subscription_id = ctx.subscription_id
        client = ctx.subscription_client

        sub = client.subscriptions.get(subscription_id)

        if hasattr(sub, "as_dict"):
            return sub.as_dict()

        # Fallback attributes
        return {
            "subscriptionId": getattr(sub, "subscription_id", subscription_id),
            "displayName": getattr(sub, "display_name", None),
            "state": getattr(sub, "state", None),
            "tenantId": getattr(sub, "tenant_id", None),
        }

    except Exception as e:
        raise AzureMCPError(f"Failed to get subscription info: {e}") from e


def list_locations() -> List[Dict[str, Any]]:
    """List all available Azure locations/regions.

    Returns:
        List of locations with their properties

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        subscription_id = ctx.subscription_id
        client = ctx.subscription_client

        locs = list(client.subscriptions.list_locations(subscription_id))
        return [
            l.as_dict() if hasattr(l, "as_dict")
            else {
                "name": getattr(l, "name", None),
                "displayName": getattr(l, "display_name", None)
            }
            for l in locs
        ]

    except Exception as e:
        raise AzureMCPError(f"Failed to list locations: {e}") from e

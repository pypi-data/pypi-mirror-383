"""Base module for Azure service clients and authentication.

This module manages Azure SDK clients and authentication using the mgmt_config
module from the parent application.
"""

from typing import Any, Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.cosmosdb import CosmosDBManagementClient


class AzureMCPError(Exception):
    """Base exception for Azure MCP server errors."""
    pass


class AzureServiceContext:
    """Context manager for Azure service clients and authentication.

    This class provides centralized access to Azure SDK clients and credentials,
    with support for initialization from mgmt_config.py or explicit parameters.
    """

    def __init__(self):
        self._credential: Optional[Any] = None
        self._subscription_id: Optional[str] = None
        self._resource_client: Optional[ResourceManagementClient] = None
        self._storage_client: Optional[StorageManagementClient] = None
        self._cosmos_client: Optional[CosmosDBManagementClient] = None
        self._subscription_client: Optional[SubscriptionClient] = None
        self._initialized: bool = False

    def initialize_with_auto_discovery(self) -> None:
        """Initialize with auto-discovery of subscription ID.

        This method:
        1. Creates a DefaultAzureCredential
        2. Lists available subscriptions
        3. Uses the first subscription found (or only one if single subscription)

        Raises:
            AzureMCPError: If initialization fails or no subscriptions found
        """
        try:
            # Create credential
            self._credential = DefaultAzureCredential()

            # Create subscription client to list subscriptions
            temp_client = SubscriptionClient(self._credential)
            subs = list(temp_client.subscriptions.list())

            if not subs:
                raise AzureMCPError("No Azure subscriptions found for this credential")

            # Use the first subscription
            first_sub = subs[0]
            self._subscription_id = first_sub.subscription_id

            self._initialized = True

        except Exception as e:
            raise AzureMCPError(f"Failed to auto-discover subscription: {e}") from e

    def initialize(
        self,
        credential: Optional[Any] = None,
        subscription_id: Optional[str] = None
    ) -> None:
        """Initialize with explicit credentials and subscription ID.

        Args:
            credential: Azure credential object. If None, uses DefaultAzureCredential
            subscription_id: Azure subscription ID

        Raises:
            AzureMCPError: If subscription_id is not provided
        """
        if credential is None:
            try:
                self._credential = DefaultAzureCredential()
            except Exception as e:
                raise AzureMCPError(f"Failed to create DefaultAzureCredential: {e}") from e
        else:
            self._credential = credential

        if subscription_id is None:
            raise AzureMCPError("subscription_id must be provided")

        self._subscription_id = subscription_id
        self._initialized = True

    def ensure_initialized(self) -> None:
        """Ensure the context is initialized, auto-initializing if needed.

        Attempts initialization in the following order:
        1. Environment variable AZURE_SUBSCRIPTION_ID (if set)
        2. Auto-discovery using subscription listing

        Raises:
            AzureMCPError: If initialization fails
        """
        if self._initialized:
            return

        # Try environment variable first
        import os
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        if subscription_id:
            try:
                self.initialize(subscription_id=subscription_id)
                return
            except AzureMCPError:
                pass

        # Fall back to auto-discovery
        try:
            self.initialize_with_auto_discovery()
            return
        except AzureMCPError:
            pass

        raise AzureMCPError(
            "Context not initialized. Either:\n"
            "1. Set AZURE_SUBSCRIPTION_ID environment variable, or\n"
            "2. Call initialize() with explicit credentials, or\n"
            "3. Ensure Azure credential is available for auto-discovery"
        )

    @property
    def credential(self) -> Any:
        """Get the Azure credential."""
        self.ensure_initialized()
        return self._credential

    @property
    def subscription_id(self) -> str:
        """Get the Azure subscription ID."""
        self.ensure_initialized()
        assert self._subscription_id is not None, "Subscription ID should be set after initialization"
        return self._subscription_id

    @property
    def resource_client(self) -> ResourceManagementClient:
        """Get or create the Resource Management client."""
        self.ensure_initialized()
        if self._resource_client is None:
            self._resource_client = ResourceManagementClient(
                self.credential,
                self.subscription_id
            )
        return self._resource_client

    @property
    def storage_client(self) -> StorageManagementClient:
        """Get or create the Storage Management client."""
        self.ensure_initialized()
        if self._storage_client is None:
            self._storage_client = StorageManagementClient(
                self.credential,
                self.subscription_id
            )
        return self._storage_client

    @property
    def cosmos_client(self) -> CosmosDBManagementClient:
        """Get or create the Cosmos DB Management client."""
        self.ensure_initialized()
        if self._cosmos_client is None:
            self._cosmos_client = CosmosDBManagementClient(
                self.credential,
                self.subscription_id
            )
        return self._cosmos_client

    @property
    def subscription_client(self) -> SubscriptionClient:
        """Get or create the Subscription client."""
        self.ensure_initialized()
        if self._subscription_client is None:
            self._subscription_client = SubscriptionClient(self.credential)
        return self._subscription_client

    def reset(self) -> None:
        """Reset the context, clearing all clients and credentials."""
        self._credential = None
        self._subscription_id = None
        self._resource_client = None
        self._storage_client = None
        self._cosmos_client = None
        self._subscription_client = None
        self._initialized = False


# Global context instance
_context = AzureServiceContext()


def get_context() -> AzureServiceContext:
    """Get the global Azure service context.

    Returns:
        The global AzureServiceContext instance
    """
    return _context

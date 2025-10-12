# AzPaddyPy

Comprehensive Python logger for Azure, integrating OpenTelemetry for advanced, structured, and distributed tracing.

A standardized Python package for Azure cloud services integration with builder patterns, OpenTelemetry tracing, and comprehensive configuration management.

## Module Architecture

```
azpaddypy/
|
+-- mgmt/                     # Management Services
|   +-- logging.py            # OpenTelemetry Azure Logger
|   +-- identity.py           # Azure Identity Management
|   +-- local_env_manager.py  # Local Environment Variables
|
+-- resources/                # Azure Resource Clients
|   +-- storage.py            # Blob, File, Queue Storage
|   +-- keyvault.py           # Secrets, Keys, Certificates
|   +-- cosmosdb.py           # Cosmos DB Client
|
+-- builder/                  # Builder Pattern Architecture
|   +-- configuration.py      # ConfigurationSetupBuilder
|   |                         # AzureManagementBuilder
|   |                         # AzureResourceBuilder
|   +-- directors.py          # Pre-configured Directors
|
+-- tools/                    # Higher-Level Tools
|   +-- configuration_manager.py  # Multi-source Config
|   +-- cosmos_prompt_manager.py  # Cosmos Prompt Storage
|   +-- prompt_models.py          # Pydantic Models for Prompts
|
+-- errors/                   # Custom Exception Classes
    +-- exceptions.py         # AzPaddyPyError, ConfigError

mgmt_config.py                # Production-Ready Configuration

Configuration Flow:
[.env files] --> [ConfigurationSetupBuilder] --> [Environment Config]
                                                         |
                  [Key Vault URIs from Environment] <---+
                                |                        |
[Management Services] <-- [AzureManagementBuilder] <----+
        |                   (logger, identity, keyvaults)
        v                                               |
[Resource Services] <-- [AzureResourceBuilder] <--------+
        |               (storage, cosmosdb)
        v
[Tools & Managers] <-- (ConfigurationManager, CosmosPromptManager)
        |
        v
[Application Usage]

Builder Pattern Composition:
ConfigurationSetupDirector.build_default_config()
  --> AzureManagementBuilder(env_config)
        .with_logger()
        .with_identity()
        .with_keyvault(vault_url=primary_uri, name="main")
        .with_keyvault(vault_url=head_uri, name="head")
  --> AzureResourceBuilder(mgmt, env_config)
        .with_storage(name="main", account_url=storage_url)
        .with_cosmosdb(name="promptmgmt", endpoint=cosmos_url)
```



## Key Features

- **OpenTelemetry Integration**: Distributed tracing with Azure Monitor
- **Builder Pattern Architecture**: Flexible service composition with directors
- **Comprehensive Azure SDK Integration**: Storage, Key Vault, Cosmos DB, Identity
- **Environment Detection**: Automatic configuration for local/cloud deployment
- **Token Caching**: Secure Azure identity management with credential chaining
- **Configuration Management**: Multi-source environment, JSON, and Key Vault configuration
- **Production-Ready mgmt_config.py**: Complete example with multi-vault and dynamic resource naming
- **Cosmos Prompt Manager**: Structured prompt storage and versioning for AI/ML applications
- **Function Execution Logging**: Track function calls with configurable argument/result logging

## Installation

```bash
pip install azpaddypy
```

## Quick Start Examples

### Basic Logger Setup

```python
from azpaddypy.mgmt.logging import AzureLogger

# Initialize with Application Insights
logger = AzureLogger(
    service_name="my-app",
    connection_string="InstrumentationKey=your-key;IngestionEndpoint=https://..."
)

# Use structured logging with correlation
logger.info("Processing user request", extra={
    "user_id": "12345",
    "operation": "data_processing"
})

# Function tracing decorator
@logger.trace_function
def process_data(data):
    logger.info("Processing started", extra={"record_count": len(data)})
    return processed_data
```

### Azure Storage Operations

```python
from azpaddypy.resources.storage import AzureStorage

# Create storage client
storage = AzureStorage(
    account_url="https://myaccount.blob.core.windows.net",
    credential=credential,
    logger=logger
)

# Upload blob with automatic content type detection
blob_url = storage.upload_blob_from_path(
    container_name="documents",
    blob_name="report.pdf",
    file_path="/path/to/report.pdf"
)

# Download blob with encoding detection
content = storage.download_blob_as_text(
    container_name="documents",
    blob_name="data.csv"
)

# Generate SAS URL for secure access
sas_url = storage.generate_blob_sas_url(
    container_name="documents",
    blob_name="report.pdf",
    expiry_hours=24
)
```

### Builder Pattern Configuration

```python
from azpaddypy.builder import AzureManagementBuilder, AzureResourceBuilder
from azpaddypy.builder.directors import ConfigurationSetupDirector

# Create environment configuration
env_config = ConfigurationSetupDirector.build_default_config()

# Build management services (logger, identity, keyvaults)
mgmt = (AzureManagementBuilder(env_config)
        .with_logger()
        .with_identity()
        .with_keyvault(vault_url="https://my-vault.vault.azure.net/", name="main")
        .with_keyvault(vault_url="https://admin-vault.vault.azure.net/", name="admin")
        .build())

# Build resource services (storage, cosmosdb)
resources = (AzureResourceBuilder(mgmt, env_config)
            .with_storage(name="main", account_url="https://mystorageacct.blob.core.windows.net/")
            .with_cosmosdb(name="prompts", endpoint="https://mycosmosdb.documents.azure.com:443/")
            .build())

# Access configured services
logger = mgmt.logger
identity = mgmt.identity
keyvaults = mgmt.keyvaults  # Dictionary: {"main": AzureKeyVault, "admin": AzureKeyVault}
storage_accounts = resources.storage_accounts  # Dictionary: {"main": AzureStorage}
cosmos_dbs = resources.cosmosdb_clients  # Dictionary: {"prompts": AzureCosmosDB}
```

### Configuration Management

```python
from azpaddypy.tools.configuration_manager import create_configuration_manager

# Multi-source configuration with tracking and Key Vault integration
config_manager = create_configuration_manager(
    environment_configuration=env_config,
    configs_dir="./configs",  # Directory with JSON config files
    auto_reload=False,
    include_env_vars=True,
    env_var_prefix=None,  # Include all environment variables
    keyvault_clients=keyvaults,  # Dictionary of AzureKeyVault clients
    logger=logger
)

# Get configuration with origin tracking
database_url = config_manager.get_config("DATABASE_URL")
api_key = config_manager.get_config("API_KEY", default="default-key")

# View configuration state with access tracking
config_manager.print_configuration_state()

# Create function execution logging configuration
log_execution = LogExecution.from_config_manager(config_manager)
```

### Advanced Custom Setup

```python
from azpaddypy.builder.configuration import ConfigurationSetupBuilder

# Custom environment configuration
env_config = (ConfigurationSetupBuilder()
              .with_local_env_management()  # Load .env files first
              .with_environment_detection()
              .with_environment_variables({
                  "CUSTOM_API_URL": "https://api.example.com",
                  "FEATURE_FLAGS": "feature1,feature2"
              }, in_docker=True)
              .with_service_configuration()
              .with_logging_configuration()
              .with_identity_configuration()
              .build())

# Use custom configuration with builders
mgmt = (AzureManagementBuilder(env_config)
        .with_logger(log_level="DEBUG")
        .with_identity(enable_token_cache=True)
        .build())
```

### Cosmos DB Prompt Management

```python
from azpaddypy.tools.cosmos_prompt_manager import create_cosmos_prompt_manager

# Initialize with Cosmos DB connection
prompt_manager = create_cosmos_prompt_manager(
    cosmos_client=cosmos_dbs.get("prompts"),
    database_name="prompts",
    container_name="templates",
    service_name="prompt_service",
    service_version="1.0.0",
    logger=logger
)

# Store prompt with metadata
prompt_manager.save_prompt(
    prompt_id="welcome_message",
    prompt_text="Welcome {user_name} to {service_name}!",
    metadata={"category": "greetings", "version": "1.0"}
)

# Retrieve and use prompts
prompt = prompt_manager.get_prompt("welcome_message")
message = prompt.prompt_text.format(user_name="Alice", service_name="MyApp")

# List all prompts
all_prompts = prompt_manager.list_prompts()
```

## Environment Variables

### Core Configuration
- `REFLECTION_NAME`: Service name for Application Insights cloud role
- `REFLECTION_KIND`: Service type (app, functionapp)
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Application Insights connection

### Storage Configuration
- `STORAGE_ACCOUNT_URL`: Azure Storage Account URL (can be overridden in builder)
- `STORAGE_ENABLE_BLOB`: Enable blob storage (default: true)
- `STORAGE_ENABLE_FILE`: Enable file storage (default: true)
- `STORAGE_ENABLE_QUEUE`: Enable queue storage (default: true)

### Key Vault Configuration
- `key_vault_uri`: Primary Azure Key Vault URL
- `head_key_vault_uri`: Administrative Key Vault URL (optional)
- `KEYVAULT_ENABLE_SECRETS`: Enable secrets access (default: true)
- `KEYVAULT_ENABLE_KEYS`: Enable keys access (default: false)
- `KEYVAULT_ENABLE_CERTIFICATES`: Enable certificates access (default: false)

### Cosmos DB Configuration
- Cosmos DB endpoints are typically constructed dynamically or passed to builder
- No environment variables required (configured via builder)

### Identity Configuration
- `IDENTITY_ENABLE_TOKEN_CACHE`: Enable token caching (default: true)
- `IDENTITY_ALLOW_UNENCRYPTED_STORAGE`: Allow unencrypted cache (default: true)

## Production Configuration Pattern

AzPaddyPy includes a production-ready [mgmt_config.py](mgmt_config.py) that demonstrates best practices:

```python
# 1. Environment Configuration with Local Development Support
LOCAL_DEVELOPMENT_STORAGE_CONFIG = {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AzureWebJobsDashboard": "UseDevelopmentStorage=true",
    "AZURE_CLIENT_ID": "...",  # Service Principal for local development
    "AZURE_TENANT_ID": "...",
    "AZURE_CLIENT_SECRET": "..."
}

environment_configuration = (
    ConfigurationSetupBuilder()
    .with_local_env_management()  # FIRST: Load .env files
    .with_environment_detection()
    .with_environment_variables(LOCAL_DEVELOPMENT_STORAGE_CONFIG, in_docker=True, in_machine=True)
    .with_service_configuration()
    .with_logging_configuration()
    .with_identity_configuration()
    .build()
)

# 2. Management Services with Multi-Vault Support
azure_management_configuration = (
    AzureManagementBuilder(environment_configuration)
    .with_logger()
    .with_identity()
    .with_keyvault(vault_url=primary_key_vault_uri, name="main")
    .with_keyvault(vault_url=head_key_vault_uri, name="head")
    .build()
)

# 3. Dynamic Resource Naming from Key Vault
project_code = keyvaults.get("main").get_secret("project-code")
azure_environment = keyvaults.get("main").get_secret("resource-group-environment")
full_storage_account_url = f"https://st{storage_name}{project_code}{azure_environment}.blob.core.windows.net/"

# 4. Resource Services with Named Instances
azure_resource_configuration = (
    azure_resource_builder
    .with_storage(name=storage_account_name, account_url=full_storage_account_url)
    .with_cosmosdb(name=cosmos_db_name, endpoint=full_cosmos_db_name_url)
    .build()
)

# 5. Export Configured Services
logger = azure_management_configuration.logger
identity = azure_management_configuration.identity
keyvaults = azure_management_configuration.keyvaults
storage_accounts = azure_resource_configuration.storage_accounts
cosmos_dbs = azure_resource_configuration.cosmosdb_clients
```

## Local Development

For local development, AzPaddyPy automatically detects the environment and applies appropriate settings:

- Uses **Azurite** storage emulator when `UseDevelopmentStorage=true` is configured
- Supports **Service Principal** authentication via environment variables
- Supports **Azure CLI** authentication with `az login`
- Automatic environment detection via `with_environment_detection()`

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_storage.py

# Run with coverage
uv run pytest --cov=azpaddypy
```

## Package Exports

The [mgmt_config.py](mgmt_config.py) demonstrates comprehensive service exports:

```python
__all__ = [
    # Core Classes
    "AzureStorage",
    "AzureKeyVault",
    "AzureCosmosDB",
    "AzureLogger",
    "AzureIdentity",
    "ConfigurationManager",
    "CosmosPromptManager",

    # Configured Service Instances
    "logger",                          # OpenTelemetry logger
    "identity",                        # Azure Identity provider
    "keyvaults",                       # Dict[str, AzureKeyVault]
    "storage_accounts",                # Dict[str, AzureStorage]
    "cosmos_dbs",                      # Dict[str, AzureCosmosDB]
    "configuration_manager",           # Multi-source configuration
    "azure_resource_builder",          # Reusable resource builder
    "log_execution_config",            # Function logging config
    "prompt_manager",                  # Cosmos prompt storage

    # Configuration Objects (advanced usage)
    "environment_configuration",       # EnvironmentConfiguration
    "azure_management_configuration",  # AzureManagementConfiguration
    "azure_resource_configuration",    # AzureResourceConfiguration
]
```

## Requirements

- Python >= 3.11.10, < 3.13
- Azure SDK packages (azure-identity, azure-keyvault-*, azure-storage-*, azure-cosmos)
- OpenTelemetry integration (azure-monitor-opentelemetry)
- Pydantic for data validation
- UV for dependency management and testing

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=azpaddypy

# Build package
uv build

# Publish package
uv publish --token <pypi-token>
```

## License

This project is licensed under the MIT License.
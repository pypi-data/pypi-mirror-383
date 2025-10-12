"""Azure Resource Groups and ARM template operations."""

import subprocess
import shutil
from typing import Any, Dict, List, Optional

from .base import get_context, AzureMCPError


def list_resource_groups() -> List[Dict[str, Any]]:
    """List all resource groups in the subscription.

    Returns:
        List of resource groups with their properties including name, location,
        tags, and the extracted 'application' tag value.

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        client = ctx.resource_client
        rgs = client.resource_groups.list()

        result = []
        for rg in rgs:
            rg_dict = rg.as_dict()
            # Extract the "application" tag, default to "None" if not present
            tags = rg_dict.get("tags", {}) or {}
            rg_dict["application"] = tags.get("application", "None")
            result.append(rg_dict)

        return result

    except Exception as e:
        raise AzureMCPError(f"Failed to list resource groups: {e}") from e


def list_resources_in_group(resource_group: str) -> List[Dict[str, Any]]:
    """List all resources in a specific resource group.

    Args:
        resource_group: Name of the resource group

    Returns:
        List of resources with their properties

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        client = ctx.resource_client
        resources = client.resources.list_by_resource_group(resource_group)
        return [r.as_dict() for r in resources]

    except Exception as e:
        raise AzureMCPError(
            f"Failed to list resources in group '{resource_group}': {e}"
        ) from e


def export_resource_group_template(resource_group: str) -> Dict[str, Any]:
    """Export the ARM template for a resource group.

    Args:
        resource_group: Name of the resource group

    Returns:
        ARM template as a dictionary

    Raises:
        AzureMCPError: If the operation fails
    """
    try:
        ctx = get_context()
        client = ctx.resource_client

        # Export template using management client
        export_result = client.resource_groups.begin_export_template(
            resource_group_name=resource_group,
            parameters={
                "options": "IncludeParameterDefaultValue",
                "resources": ["*"]
            }
        ).result()

        # Extract template from result
        if hasattr(export_result, "as_dict"):
            d = export_result.as_dict()
            if "template" in d:
                return d["template"]
            return d

        if hasattr(export_result, "template"):
            return export_result.template

        # Fallback
        return {"export_result": str(export_result)}

    except Exception as e:
        raise AzureMCPError(
            f"Failed to export resource group template for '{resource_group}': {e}"
        ) from e


def decompile_arm_to_bicep(
    arm_template_path: str,
    output_path: Optional[str] = None
) -> str:
    """Decompile an ARM template to Bicep format.

    This function requires Azure CLI with Bicep extension installed.

    Args:
        arm_template_path: Path to the ARM template JSON file
        output_path: Optional output path for the Bicep file. If not provided,
                    uses the same name with .bicep extension

    Returns:
        Path to the generated Bicep file

    Raises:
        AzureMCPError: If decompilation fails or Azure CLI is not available
    """
    # Check if az CLI is available
    if shutil.which("az") is None:
        raise AzureMCPError(
            "Azure CLI is not available. Install Azure CLI to use Bicep decompilation. "
            "See: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
        )

    # Determine output path
    if output_path is None:
        output_path = arm_template_path.rsplit(".", 1)[0] + ".bicep"

    try:
        # Run az bicep decompile command
        result = subprocess.run(
            [
                "az", "bicep", "decompile",
                "--file", arm_template_path,
                "--outfile", output_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return output_path

    except subprocess.CalledProcessError as e:
        raise AzureMCPError(
            f"Bicep decompilation failed: {e.stderr or e.stdout or str(e)}"
        ) from e
    except Exception as e:
        raise AzureMCPError(f"Failed to decompile ARM template: {e}") from e

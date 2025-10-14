"""
Deploy related CLI functions for AIP Model CLI.
"""

import click
from adxp_cli.auth.service import get_credential
from adxp_sdk.models.hub import AXModelHub


def create_deployment(deployment_data):
    """Create a new deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.create_deployment(deployment_data)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create deployment: {e}")


def list_deployments():
    """List all deployments."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.list_deployments()
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list deployments: {e}")


def get_deployment(deployment_id):
    """Get a specific deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.get_deployment(deployment_id)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get deployment: {e}")


def update_deployment(deployment_id, deployment_data):
    """Update a deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.update_deployment(deployment_id, deployment_data)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update deployment: {e}")


def delete_deployment(deployment_id):
    """Delete a deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.delete_deployment(deployment_id)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete deployment: {e}")


def start_deployment(deployment_id):
    """Start a deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.start_deployment(deployment_id)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to start deployment: {e}")


def stop_deployment(deployment_id):
    """Stop a deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.stop_deployment(deployment_id)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to stop deployment: {e}")


def get_deployment_apikeys(deployment_id, page=1, size=10):
    """Get deployment API keys."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.get_deployment_apikeys(deployment_id, page=page, size=size)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get deployment API keys: {e}")


def hard_delete_deployment():
    """Hard delete a deployment."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        return hub.hard_delete_deployment()
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to hard delete deployment: {e}")


def get_task_resources(task_type="serving", project_id=None):
    """Get task resource information."""
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        
        if not project_id:
            project_id = config.client_id
            
        return hub.get_task_resources(task_type, project_id)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg or "Authentication failed" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get task resources: {e}")

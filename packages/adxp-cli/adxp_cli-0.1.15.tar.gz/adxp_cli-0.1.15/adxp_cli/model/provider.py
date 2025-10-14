import json
from adxp_cli.auth.service import get_credential
from adxp_sdk.auth.credentials import Credentials
from adxp_sdk.models.hub import AXModelHub
import click

# Create AXModelHub instance with credentials

def get_model_hub():
    headers, config = get_credential()
    # Use headers directly if token is available (avoids password authentication)
    if hasattr(config, 'token') and config.token:
        return AXModelHub(headers=headers, base_url=config.base_url)
    else:
        # Fallback to credentials-based authentication
        credentials = Credentials(
            username=config.username,
            password="",  # Only token is needed
            project=config.client_id,
            base_url=config.base_url
        )
        return AXModelHub(credentials)


def create_provider(provider_data: dict):
    """Create a model provider"""
    try:
        hub = get_model_hub()
        result = hub.create_model_provider(provider_data)
        click.secho("✅ Model provider created successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create model provider: {e}")


def list_providers(page=1, size=10, sort=None, search=None):
    """List model providers"""
    try:
        hub = get_model_hub()
        result = hub.get_model_providers(page=page, size=size, sort=sort, search=search)
        click.secho("✅ Model providers listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list model providers: {e}")


def get_provider(provider_id: str):
    """Get a specific model provider"""
    try:
        hub = get_model_hub()
        result = hub.get_model_provider_by_id(provider_id)
        click.secho("✅ Model provider retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get model provider: {e}")


def update_provider(provider_id: str, provider_data: dict):
    """Update a specific model provider"""
    try:
        hub = get_model_hub()
        result = hub.update_model_provider(provider_id, provider_data)
        click.secho("✅ Model provider updated successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update model provider: {e}")


def delete_provider(provider_id: str):
    """Delete a specific model provider"""
    try:
        hub = get_model_hub()
        result = hub.delete_model_provider(provider_id)
        click.secho("✅ Model provider deleted successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete model provider: {e}") 
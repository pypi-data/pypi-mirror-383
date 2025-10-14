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


def list_versions(model_id: str, page=1, size=10, sort=None, filter=None, search=None, ids=None):
    """List versions for a specific model"""
    try:
        hub = get_model_hub()
        result = hub.get_model_versions(model_id, page=page, size=size, sort=sort, filter=filter, search=search, ids=ids)
        click.secho("✅ Model versions listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list model versions: {e}")


def get_model_version(model_id: str, version_id: str):
    """Get a specific version of a model"""
    try:
        hub = get_model_hub()
        result = hub.get_model_version_by_id(model_id, version_id)
        click.secho("✅ Model version retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get model version: {e}")


def get_version(version_id: str):
    """Get a specific version by version_id only"""
    try:
        hub = get_model_hub()
        result = hub.get_version_by_id(version_id)
        click.secho("✅ Version retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get version: {e}")


def delete_model_version(model_id: str, version_id: str):
    """Delete a specific version of a model"""
    try:
        hub = get_model_hub()
        result = hub.delete_model_version_by_id(model_id, version_id)
        click.secho("✅ Model version deleted successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete model version: {e}")


def update_model_version(model_id: str, version_id: str, version_data: dict):
    """Update a specific version of a model"""
    try:
        hub = get_model_hub()
        result = hub.update_model_version_by_id(model_id, version_id, version_data)
        click.secho("✅ Model version updated successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update model version: {e}")


def create_version(model_id: str, version_data: dict):
    """Create a new version for a model"""
    try:
        hub = get_model_hub()
        result = hub.create_version(model_id, version_data)
        click.secho("✅ Model version created successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create model version: {e}")


def promote_version(version_id: str, promotion_data: dict):
    """Promote a specific version to a model"""
    try:
        hub = get_model_hub()
        result = hub.promote_version(version_id, promotion_data)
        click.secho("✅ Model version promoted successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to promote model version: {e}") 
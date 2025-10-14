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


def create_endpoint(model_id: str, endpoint_data: dict):
    """Create a model endpoint"""
    try:
        hub = get_model_hub()
        result = hub.create_model_endpoint(model_id, endpoint_data)
        click.secho("✅ Model endpoint created successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create model endpoint: {e}")


def list_endpoints(model_id: str, page=1, size=10, sort=None, filter=None, search=None):
    """List model endpoints for a specific model"""
    try:
        hub = get_model_hub()
        result = hub.get_model_endpoints(model_id, page=page, size=size, sort=sort, filter=filter, search=search)
        click.secho("✅ Model endpoints listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list model endpoints: {e}")


def get_endpoint(model_id: str, endpoint_id: str):
    """Get a specific model endpoint"""
    try:
        hub = get_model_hub()
        result = hub.get_model_endpoint_by_id(model_id, endpoint_id)
        click.secho("✅ Model endpoint retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get model endpoint: {e}")


def delete_endpoint(model_id: str, endpoint_id: str):
    """Delete a specific model endpoint"""
    try:
        hub = get_model_hub()
        result = hub.delete_model_endpoint_by_id(model_id, endpoint_id)
        click.secho("✅ Model endpoint deleted successfully", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete model endpoint: {e}") 
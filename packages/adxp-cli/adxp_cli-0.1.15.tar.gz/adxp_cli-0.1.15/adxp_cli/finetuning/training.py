from adxp_cli.auth.service import get_credential
from adxp_sdk.auth.credentials import Credentials
from adxp_sdk.finetuning.hub import AXFineTuningHub
import click

# Create AXFineTuningHub instance with credentials
def get_finetuning_hub():
    headers, config = get_credential()
    # Use headers directly if token is available (avoids password authentication)
    if hasattr(config, 'token') and config.token:
        return AXFineTuningHub(headers=headers, base_url=config.base_url)
    else:
        # Fallback to credentials-based authentication
        credentials = Credentials(
            username=config.username,
            password="",  # Only token is needed
            project=config.client_id,
            base_url=config.base_url
        )
        return AXFineTuningHub(credentials)

# [Training 관련]
def create_training(training_data: dict):
    """Create a new training"""
    try:
        hub = get_finetuning_hub()
        result = hub.create_training(training_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create training: {e}")

def list_trainings(page=1, size=10, sort=None, filter=None, search=None, ids=None):
    """List all trainings"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_trainings(page=page, size=size, sort=sort, filter=filter, search=search, ids=ids)
        click.secho("✅ Trainings listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list trainings: {e}")

def get_training(training_id: str):
    """Get a training by ID"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_training_by_id(training_id)
        click.secho("✅ Training retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get training: {e}")

def update_training(training_id: str, training_data: dict):
    """Update a training"""
    try:
        hub = get_finetuning_hub()
        result = hub.update_training(training_id, training_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update training: {e}")

def delete_training(training_id: str):
    """Delete a training"""
    try:
        hub = get_finetuning_hub()
        result = hub.delete_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete training: {e}")

def get_training_status(training_id: str):
    """Get training status"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_training_status(training_id)
        click.secho("✅ Training status retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get training status: {e}")

def start_training(training_id: str):
    """Start a training"""
    try:
        hub = get_finetuning_hub()
        result = hub.start_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to start training: {e}")

def stop_training(training_id: str):
    """Stop a training"""
    try:
        hub = get_finetuning_hub()
        result = hub.stop_training(training_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to stop training: {e}")

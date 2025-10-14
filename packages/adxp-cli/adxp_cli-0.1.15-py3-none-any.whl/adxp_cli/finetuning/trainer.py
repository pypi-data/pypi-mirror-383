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

# [Trainer 관련]
def list_trainers(page=1, size=10, sort=None, filter=None, search=None):
    """List all trainers"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_trainers(page=page, size=size, sort=sort, filter=filter, search=search)
        click.secho("✅ Trainers listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list trainers: {e}")

def get_trainer(trainer_id: str):
    """Get a trainer by ID"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_trainer_by_id(trainer_id)
        click.secho("✅ Trainer retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get trainer: {e}")

def create_trainer(trainer_data: dict):
    """Create a new trainer"""
    try:
        hub = get_finetuning_hub()
        result = hub.create_trainer(trainer_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create trainer: {e}")

def update_trainer(trainer_id: str, trainer_data: dict):
    """Update a trainer"""
    try:
        hub = get_finetuning_hub()
        result = hub.update_trainer(trainer_id, trainer_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update trainer: {e}")

def delete_trainer(trainer_id: str):
    """Delete a trainer"""
    try:
        hub = get_finetuning_hub()
        result = hub.delete_trainer(trainer_id)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete trainer: {e}")

def get_platform_info():
    """Get platform information"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_platform_info()
        click.secho("✅ Platform info retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get platform info: {e}")

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

# [Training Metrics 관련]
def get_training_events(training_id: str, after=None, limit=100):
    """Get training events"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_training_events(training_id, after=after, limit=limit)
        click.secho("✅ Training events retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get training events: {e}")

def get_training_metrics(training_id: str, type="train", page=1, size=10):
    """Get training metrics"""
    try:
        hub = get_finetuning_hub()
        result = hub.get_training_metrics(training_id, type=type, page=page, size=size)
        click.secho("✅ Training metrics retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get training metrics: {e}")

def register_training_metrics(training_id: str, metrics_data: list):
    """Register training metrics"""
    try:
        hub = get_finetuning_hub()
        result = hub.register_training_metrics(training_id, metrics_data)
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to register training metrics: {e}")

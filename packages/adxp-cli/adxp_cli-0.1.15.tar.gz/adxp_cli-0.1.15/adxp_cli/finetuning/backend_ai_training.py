import click
from adxp_sdk.finetuning.backend_ai_hub import BackendAIFineTuningHub
from ..auth.service import get_credential


def get_backend_ai_finetuning_hub():
    """Get BackendAI fine-tuning hub instance with credentials."""
    try:
        headers, config = get_credential()
        # Use headers directly if token is available (avoids password authentication)
        if hasattr(config, 'token') and config.token:
            return BackendAIFineTuningHub(headers=headers, base_url=config.base_url)
        else:
            # Fallback to credentials-based authentication
            from adxp_sdk.auth.credentials import Credentials
            credentials = Credentials(
                username=config.username,
                password="",  # Only token is needed
                project=config.client_id,
                base_url=config.base_url
            )
            return BackendAIFineTuningHub(credentials)
    except Exception as e:
        raise click.ClickException(f"Failed to initialize BackendAI fine-tuning hub: {e}")


# ====================================================================
# Backend.ai Training Functions
# ====================================================================

def create_backend_ai_training(training_data: dict):
    """Create a new Backend.ai training"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.create_backend_ai_training(training_data)
        click.secho("✅ Backend.ai training created", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to create Backend.ai training: {e}")


def list_backend_ai_trainings(page=1, size=10, sort=None, filter=None, search=None):
    """List Backend.ai trainings"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.list_backend_ai_trainings(page=page, size=size, sort=sort, filter=filter, search=search)
        click.secho("✅ Backend.ai trainings listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to list Backend.ai trainings: {e}")


def get_backend_ai_training(training_id: str):
    """Get a Backend.ai training by ID"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.get_backend_ai_training(training_id)
        click.secho("✅ Backend.ai training retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get Backend.ai training: {e}")


def update_backend_ai_training(training_id: str, training_data: dict):
    """Update a Backend.ai training"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.update_backend_ai_training(training_id, training_data)
        click.secho("✅ Backend.ai training updated", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to update Backend.ai training: {e}")


def delete_backend_ai_training(training_id: str):
    """Delete a Backend.ai training"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.delete_backend_ai_training(training_id)
        click.secho("✅ Backend.ai training deleted", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to delete Backend.ai training: {e}")


def get_backend_ai_training_status(training_id: str):
    """Get Backend.ai training status"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.get_backend_ai_training_status(training_id)
        click.secho("✅ Backend.ai training status retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get Backend.ai training status: {e}")


def get_backend_ai_training_events(training_id: str, after: str = None, limit: int = 100):
    """Get Backend.ai training events"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.get_backend_ai_training_events(training_id, after=after, limit=limit)
        click.secho("✅ Backend.ai training events retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get Backend.ai training events: {e}")


def get_backend_ai_training_metrics(training_id: str, type: str = "train", page: int = 1, size: int = 10):
    """Get Backend.ai training metrics"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.get_backend_ai_training_metrics(training_id, type=type, page=page, size=size)
        click.secho("✅ Backend.ai training metrics retrieved", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get Backend.ai training metrics: {e}")


def force_stop_backend_ai_training(training_id: str):
    """Force stop a Backend.ai training"""
    try:
        hub = get_backend_ai_finetuning_hub()
        result = hub.force_stop_backend_ai_training(training_id)
        click.secho("✅ Backend.ai training force stop requested", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to force stop Backend.ai training: {e}")


# ====================================================================
# Platform Type Functions
# ====================================================================

def get_platform_info():
    """Get platform information"""
    try:
        hub = get_backend_ai_finetuning_hub()
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


def validate_backend_ai_platform():
    """Validate that the current platform is Backend.ai"""
    import os
    
    # Check if platform validation is disabled via environment variable
    skip_platform_check = os.getenv('ADXP_SKIP_PLATFORM_CHECK', '').lower() in ('true', '1', 'yes')
    if skip_platform_check:
        click.secho("⚠️  Platform validation skipped (ADXP_SKIP_PLATFORM_CHECK=true)", fg="yellow")
        return True
    
    try:
        platform_info = get_platform_info()
        platform_type = platform_info.get('platform_type', '').lower()
        
        if platform_type != 'backend_ai':
            raise click.ClickException(
                f"❌ This command is only available for Backend.ai platform. "
                f"Current platform: {platform_type}. "
                f"Please connect to a Backend.ai fine-tuning server.\n"
                f"💡 To skip this check, set ADXP_SKIP_PLATFORM_CHECK=true"
            )
        return True
    except click.ClickException:
        # Re-raise click exceptions (like the one above)
        raise
    except Exception as e:
        raise click.ClickException(f"❌ Failed to validate platform: {e}")

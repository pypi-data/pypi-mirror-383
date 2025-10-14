from adxp_cli.auth.service import get_credential
from adxp_sdk.auth.credentials import Credentials
from adxp_sdk.apikey.hub import AXApiKeyHub
import click


def get_apikey_hub():
    """공통 Hub 생성 (토큰 있으면 토큰 기반, 없으면 Credentials 기반)"""
    headers, config = get_credential()
    if hasattr(config, "token") and config.token:
        return AXApiKeyHub(headers=headers, base_url=config.base_url)
    else:
        return AXApiKeyHub(
            credentials=Credentials(
                username=config.username,
                password="",  # 토큰 기반이면 필요 없음
                project=config.client_id,
                base_url=config.base_url,
            )
        )


def list_apikeys(page=1, size=10, sort=None, filter=None, search=None):
    """List API Keys"""
    try:
        hub = get_apikey_hub()
        result = hub.list_apikeys(
            page=page, size=size, sort=sort, filter=filter, search=search
        )
        click.secho("✅ API Keys listed", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again.\n Run: adxp-cli auth login"
            )
        raise click.ClickException(f"❌ Failed to list API keys: {e}")


def create_apikey(apikey_data: dict):
    """Create API Key"""
    try:
        hub = get_apikey_hub()
        result = hub.create_apikey(apikey_data)
        click.secho("✅ API Key created", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again.\n Run: adxp-cli auth login"
            )
        raise click.ClickException(f"❌ Failed to create API key: {e}")


def update_apikey(api_key_id: str, data: dict):
    """Update API Key"""
    try:
        hub = get_apikey_hub()
        result = hub.update_apikey(api_key_id, data)
        click.secho("✅ API Key updated", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again.\n Run: adxp-cli auth login"
            )
        raise click.ClickException(f"❌ Failed to update API key: {e}")
    
def delete_apikey(api_key_id: str):
    """Delete API Key"""
    try:
        hub = get_apikey_hub()
        result = hub.delete_apikey(api_key_id)
        click.secho("✅ API Key deleted", fg="green")
        return result
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again.\n Run: adxp-cli auth login"
            )
        raise click.ClickException(f"❌ Failed to delete API key: {e}")


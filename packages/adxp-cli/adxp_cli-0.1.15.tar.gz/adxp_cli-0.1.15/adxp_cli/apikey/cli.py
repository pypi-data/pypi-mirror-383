import click
import json
from .service import list_apikeys, create_apikey, update_apikey, delete_apikey

@click.group()
def apikey():
    """Command-line interface for API Keys"""
    pass

# ================================
# List API Keys
# ================================
@apikey.command()
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=10, help="Page size")
@click.option("--sort", default=None, help="Sort condition")
@click.option("--filter", default=None, help="Filter condition")
@click.option("--search", default=None, help="Search keyword")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def list(page, size, sort, filter, search, json_output):
    """List API Keys"""
    try:
        result = list_apikeys(page=page, size=size, sort=sort, filter=filter, search=search)
        if json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            click.secho("API Key List:", fg="cyan")
            data = result.get("data", [])
            if not data:
                click.secho("No API keys found.", fg="yellow")
            for idx, apikey in enumerate(data, 1):
                key_id = apikey.get("api_key_id", "N/A")
                gateway_type = apikey.get("gateway_type", "N/A")
                key_value = apikey.get("api_key", "N/A")
                is_master = apikey.get("is_master", "N/A")
                tags = ",".join(apikey.get("tag", [])) if apikey.get("tag") else "[]"

                click.echo(
                    f"{idx}. ID={key_id} | Type={gateway_type} | Master={is_master} | Tag={tags} | Key={key_value}"
                )
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg="red")




# ================================
# Create API Key
# ================================
@apikey.command()
@click.option("--gateway-type", type=click.Choice(["model", "agent", "mcp"], case_sensitive=False),
              prompt="Gateway type (model/agent/mcp)", help="Gateway type for the API key")
@click.option("--is-master", type=bool, prompt="Is master? (true/false)",
              help="Whether this is a master API key (true/false)")
@click.option("--serving-id", default=None,
              help="Comma-separated Serving ID(s). Required if is-master=false")
@click.option("--allowed-host", default=None,
              help="Comma-separated allowed hosts (optional)")
@click.option("--tag", default=None,
              help="Comma-separated tags (optional)")
@click.option("--started-at", default=None,
              help="Start date in YYYY-MM-DD format (optional)")
@click.option("--expires-at", default=None,
              help="Expiry date in YYYY-MM-DD format (optional)")
@click.option("--project-id", prompt="Enter Project ID", help="Project ID (required)")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def create(gateway_type, is_master, serving_id, allowed_host, tag,
           started_at, expires_at, project_id, json_output):
    """Create a new API Key"""
    try:
        # 조건부 입력: is-master가 False일 때 serving-id 필수
        serving_ids = None
        if not is_master:
            if not serving_id:
                serving_id = click.prompt("Enter Serving ID(s), comma-separated", type=str)
            serving_ids = [s.strip() for s in serving_id.split(",") if s.strip()]
        else:
            serving_ids = None

        allowed_hosts = [h.strip() for h in allowed_host.split(",")] if allowed_host else []
        tags = [t.strip() for t in tag.split(",")] if tag else []

        payload = {
            "gateway_type": gateway_type,
            "is_master": is_master,
            "serving_id": serving_ids,
            "allowed_host": allowed_hosts if allowed_hosts else None,
            "tag": tags if tags else None,
            "started_at": started_at,
            "expires_at": expires_at,
            "is_active": True,
            "project_id": project_id,
        }

        result = create_apikey(payload)
        if json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            click.secho("✅ API Key Created", fg="green")
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.secho(str(e), fg="red")


# ================================
# Update API Key
# ================================
@apikey.command()
@click.argument("api_key_id", required=False)
@click.option("--is-master", type=click.Choice(["true", "false"]), help="Whether the key is master")
@click.option("--is-active", type=click.Choice(["true", "false"]), help="Whether the key is active")
@click.option("--serving-id", default=None, help="Comma-separated Serving IDs (only required if is-master=false)")
@click.option("--allowed-host", multiple=True, help="Allowed hosts")
@click.option("--tag", multiple=True, help="Tags")
@click.option("--started-at", default=None, help="Start date (YYYY-MM-DD) or null")
@click.option("--expires-at", default=None, help="Expiration date (YYYY-MM-DD) or null")
def update(api_key_id, is_master, is_active, serving_id, allowed_host, tag, started_at, expires_at):
    """Update an API Key"""
    try:
        if not api_key_id:
            api_key_id = click.prompt("API Key ID", type=str)

        if not is_master:
            is_master = click.prompt("Is master? (true/false)", type=click.Choice(["true", "false"]))
        is_master = is_master.lower() == "true"

        # 조건부 입력: is-master가 False일 때 serving-id 필수
        serving_ids = None
        if not is_master:
            if not serving_id:
                serving_id = click.prompt("Enter Serving ID(s), comma-separated", type=str)
            serving_ids = [s.strip() for s in serving_id.split(",") if s.strip()]
        else:
            serving_ids = None

        if not is_active:
            is_active = click.prompt("Is active? (true/false)", type=click.Choice(["true", "false"]))
        is_active = is_active.lower() == "true"

        data = {
            "is_master": is_master,
            "is_active": is_active,
            "serving_id": serving_ids,
            "allowed_host": list(allowed_host) if allowed_host else None,
            "tag": list(tag) if tag else None,
            "started_at": started_at,
            "expires_at": expires_at,
        }

        click.secho(f"[DEBUG] update payload: {json.dumps(data, indent=2)}", fg="yellow")

        result = update_apikey(api_key_id, data)
        click.secho(f"✅ API Key {api_key_id} updated successfully", fg="green")
        click.echo(json.dumps(result, indent=2))

    except Exception as e:
        click.secho(f"❌ Failed to update API Key: {e}", fg="red")

        
# ================================
# Delete API Key
# ================================
@apikey.command()
@click.argument("api_key_id", required=False)
def delete(api_key_id):
    """Delete an API Key"""
    try:
        if not api_key_id:
            api_key_id = click.prompt("API Key ID", type=str)

        # ✅ 삭제 전 사용자 확인
        confirm = click.confirm(f"Are you sure you want to delete API Key {api_key_id}?", default=False)
        if not confirm:
            click.secho("❌ Delete cancelled.", fg="yellow")
            return

        result = delete_apikey(api_key_id)
        click.secho(f"✅ API Key {api_key_id} deleted successfully", fg="green")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.secho(f"❌ Failed to delete API Key: {e}", fg="red")

        
__all__ = ["apikey"]

import click
from .provider import (
    create_provider,
    list_providers,
    get_provider,
    update_provider,
    delete_provider,
)
from .endpoint import (
    create_endpoint,
    list_endpoints,
    get_endpoint,
    delete_endpoint,
)
from .version import (
    list_versions,
    get_model_version,
    get_version,
    delete_model_version,
    update_model_version,
    promote_version,
    create_version,
)
from .model import (
    create_model,
    update_model,
    list_models,
    get_model,
    delete_model,
    recover_model,
    list_model_types,
    list_model_tags,
    add_tags_to_model,
    remove_tags_from_model,
    add_languages_to_model,
    remove_languages_from_model,
    add_tasks_to_model,
    remove_tasks_from_model,
)
from .custom_runtime import (
    create_custom_runtime,
    get_custom_runtime_by_model,
    delete_custom_runtime_by_model,
)
from .deploy import (
    create_deployment,
    list_deployments,
    get_deployment,
    update_deployment,
    delete_deployment,
    start_deployment,
    stop_deployment,
    get_deployment_apikeys,
    hard_delete_deployment,
    get_task_resources,
)
from adxp_cli.auth.service import get_credential
from adxp_sdk.models.hub import AXModelHub
from tabulate import tabulate
import json as json_module


def print_model_detail(model, title=None):
    """Prints a single model as a table."""
    if not model:
        click.secho("No model found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Field", "Value"]
    rows = []
    for key, value in model.items():
        # custom_runtime은 별도로 처리
        if key == 'custom_runtime' and isinstance(value, dict):
            # custom_runtime 정보를 모델 테이블 아래에 append
            rows.append(["custom_runtime_id", value.get('id', '-')])
            rows.append(["custom_runtime_image_url", value.get('image_url', '-')])
            rows.append(["custom_runtime_use_bash", value.get('use_bash', '-')])
            rows.append(["custom_runtime_command", ', '.join(value.get('command', [])) if value.get('command') else '-'])
            rows.append(["custom_runtime_args", ', '.join(value.get('args', [])) if value.get('args') else '-'])
            rows.append(["custom_runtime_created_at", value.get('created_at', '-')])
            rows.append(["custom_runtime_updated_at", value.get('updated_at', '-')])
            continue
        
        # languages, tasks, tags는 name만 추출해서 쉼표로 구분
        if key in ['languages', 'tasks', 'tags'] and hasattr(value, '__iter__') and not isinstance(value, str):
            names = [item.get('name', '') for item in value if isinstance(item, dict)]
            display_value = ', '.join(names) if names else '-'
        else:
            display_value = value
        rows.append([key, display_value])
    click.echo(tabulate(rows, headers, tablefmt="github"))

def print_model_list(models, title=None):
    """Prints a list of models as a table."""
    if not models:
        click.secho("No models found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["id", "name", "display_name", "type", "serving_type", "size", "is_valid", "is_custom", "provider_name", "tags", "tasks", "updated_at"]
    rows = []
    for m in models:
        # Name을 30자로 제한
        name = m.get("name", "")
        if len(name) > 30:
            name = name[:27] + "..."
        
        # Display Name 처리 (30자로 제한)
        display_name = m.get("display_name", "")
        if not display_name:
            display_name = "-"
        elif len(display_name) > 30:
            display_name = display_name[:27] + "..."
        
        # Size 정보 처리
        size = m.get("size", "")
        if size:
            # 크기를 읽기 쉽게 변환 (예: 7B, 70B 등)
            if size.endswith("000000000"):
                size = size[:-9] + "B"
            elif size.endswith("000000"):
                size = size[:-6] + "M"
        
        # Valid 상태
        is_valid = "✅" if m.get("is_valid", True) else "❌"
        
        # Custom 상태
        is_custom = "✅" if m.get("is_custom", False) else "-"
        
        # Provider ID를 짧게 표시
        provider_name = m.get("provider_name", "")
        
        # tags name만 추출
        tags = m.get("tags", [])
        if hasattr(tags, '__iter__') and not isinstance(tags, str):
            tag_names = ', '.join([t.get('name', '') for t in tags if isinstance(t, dict)])
        else:
            tag_names = '-'
        
        # tasks name만 추출
        tasks = m.get("tasks", [])
        if hasattr(tasks, '__iter__') and not isinstance(tasks, str):
            task_names = ', '.join([t.get('name', '') for t in tasks if isinstance(t, dict)])
        else:
            task_names = '-'
        
        # Created At을 간단하게 표시
        updated_at = m.get("updated_at", "")
        if updated_at:
            updated_at = updated_at.split("T")[0]  # YYYY-MM-DD만 표시
        
        rows.append([
            m.get("id", ""), 
            name, 
            display_name,
            m.get("type", ""), 
            m.get("serving_type", ""),
            size,
            is_valid,
            is_custom,
            provider_name, 
            tag_names,
            task_names,
            updated_at
        ])
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_endpoint_list(endpoints, title=None):
    if not endpoints:
        click.secho("No endpoints found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "URL", "Identifier", "Key", "Description"]
    rows = [
        [e.get("id"), e.get("url"), e.get("identifier"), e.get("key"), e.get("description")] for e in endpoints
    ]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_version_list(versions, title=None):
    if not versions:
        click.secho("No versions found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "Display Name", "Description", "Created"]
    rows = [
        [v.get("id"), v.get("display_name"), v.get("description"), v.get("created_at")] for v in versions
    ]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_type_list(types, title=None):
    if not types:
        click.secho("No model types found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Type"]
    rows = [[t] for t in types]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_tag_list(tags, title=None):
    if not tags:
        click.secho("No model tags found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Tag"]
    rows = [[t] for t in tags]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_provider_list(providers, title=None):
    if not providers:
        click.secho("No providers found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "Name", "Description", "Created"]
    rows = []
    for p in providers:
        # Description을 30자로 제한
        desc = p.get("description", "")
        if len(desc) > 30:
            desc = desc[:27] + "..."
        # Created At을 간단하게 표시
        created_at = p.get("created_at", "")
        if created_at:
            created_at = created_at.split("T")[0]  # YYYY-MM-DD만 표시
        
        rows.append([p.get("id"), p.get("name"), desc, created_at])
    
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_provider_detail(provider, title=None):
    if not provider:
        click.secho("No provider data.", fg="yellow")
        return
    if title:
        click.secho(title, fg="green")
    rows = [[k, v] for k, v in provider.items()]
    click.echo(tabulate(rows, headers=["Field", "Value"], tablefmt="github"))

def print_model_and_endpoint(model, endpoint):
    """모델과 엔드포인트 결과를 prefix를 붙여 한 줄 테이블로 출력"""
    combined = {}
    for k, v in model.items():
        combined[f"model_{k}"] = v
    for k, v in endpoint.items():
        combined[f"endpoint_{k}"] = v
    headers = list(combined.keys())
    values = [combined[k] for k in headers]
    tablefmt = "github" if len(headers) <= 8 else "simple"
    click.echo(tabulate([values], headers, tablefmt=tablefmt))

@click.group()
def model():
    """Command-line interface for AIP model catalog."""
    pass

@model.group()
def version():
    """Manage model versions and deployments."""
    pass

@version.command()
@click.argument('model_id')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated version IDs')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(model_id, page, size, sort, filter, search, ids, json):
    """List versions for a specific model."""
    result = list_versions(model_id, page, size, sort, filter, search, ids)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        versions = result.get("data", result)
        print_version_list(versions, title="🏗️ Version List:")

@version.command()
@click.argument('model_id')
@click.option('--path', required=True, help='Server file path (already uploaded file path)')
@click.option('--description', default='', help='Version description')
@click.option('--fine-tuning-id', help='Fine-tuning ID (UUID)')
@click.option('--is-valid', is_flag=True, default=True, help='Whether the version is valid (default: True)')
@click.option('--policy', help='Access policy configuration (JSON string)')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Version creation JSON file path (for dict style)')
def create(model_id, path, description, fine_tuning_id, is_valid, policy, json_path):
    """Create a new version for a model. (JSON file or params style both supported)
    
    \b
    Supports two styles:
    1. Parameter style: --path "/server/path/to/model" --description "Version 1.0"
    2. JSON file style: --json version_config.json
    
    Examples:
    
    \b
    # Basic version creation
    adxp-cli model version create 3fa85f64-5717-4562-b3fc-2c963f66afa6 \\
     --path "/server/path/to/model" \\
     --description "Version 1.0"
    
    \b
    # With fine-tuning ID
    adxp-cli model version create 3fa85f64-5717-4562-b3fc-2c963f66afa6 \\
     --path "/server/path/to/model" \\
     --description "Fine-tuned version" \\
     --fine-tuning-id "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    
    \b
    # With policy
    adxp-cli model version create 3fa85f64-5717-4562-b3fc-2c963f66afa6 \\
     --path "/server/path/to/model" \\
     --description "Version with policy" \\
     --policy '[{"cascade": false, "decision_strategy": "UNANIMOUS", "logic": "POSITIVE", "policies": [{"logic": "POSITIVE", "names": ["admin"], "type": "user"}], "scopes": ["GET", "POST", "PUT", "DELETE"]}]'
    
    \b
    # JSON file style
    adxp-cli model version create 3fa85f64-5717-4562-b3fc-2c963f66afa6 --json version_config.json
    """
    if json_path:
        # JSON file style
        try:
            with open(json_path, 'r') as f:
                data = json_module.load(f)
        except json_module.JSONDecodeError:
            raise click.ClickException("Invalid JSON file format")
        except FileNotFoundError:
            raise click.ClickException(f"JSON file not found: {json_path}")
        
        try:
            result = create_version(model_id, data)
            if json:
                click.echo(json_module.dumps(result, indent=2))
            else:
                print_model_detail(result, title="🏗️ Version Created:")
        except ValueError as e:
            raise click.ClickException(str(e))
    else:
        # Parameter style
        data = {
            'path': path,
            'description': description,
            'is_valid': is_valid
        }
        
        # Optional fields
        if fine_tuning_id:
            data['fine_tuning_id'] = fine_tuning_id
        
        # Parse policy JSON
        if policy:
            try:
                data['policy'] = json_module.loads(policy)
            except json_module.JSONDecodeError:
                raise click.ClickException("--policy must be valid JSON")
        
        try:
            result = create_version(model_id, data)
            if json:
                click.echo(json_module.dumps(result, indent=2))
            else:
                print_model_detail(result, title="🏗️ Version Created:")
        except ValueError as e:
            raise click.ClickException(str(e))

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, version_id, json):
    """Get a specific version of a model."""
    result = get_model_version(model_id, version_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Detail:")

@version.command('get-by-version')
@click.argument('version_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get_by_version(version_id, json):
    """Get a specific version by version_id only."""
    result = get_version(version_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Detail:")

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, version_id, json):
    """Delete a specific version of a model."""
    result = delete_model_version(model_id, version_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Deleted:")

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--description', default=None, help='Description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def update(model_id, version_id, description, json):
    """Update a specific version of a model (only description can be updated)."""
    data = {}
    if description is not None:
        data['description'] = description
    result = update_model_version(model_id, version_id, data)
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Updated:")

@version.command()
@click.argument('version_id')
@click.option('--display-name', prompt=True, help='Display name')
@click.option('--description', default='', help='Description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def promote(version_id, display_name, description, json):
    """Promote a specific version to a model."""
    data = {'display_name': display_name, 'description': description}
    result = promote_version(version_id, data)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Promoted:")

@model.command()
@click.option('--name', help='Model name (for parameter style)')
@click.option('--type', 'model_type', help='Model type (for parameter style)')
@click.option('--display-name', help='Display name for the model')
@click.option('--description', default='', help='Model description')
@click.option('--size', help='Model size')
@click.option('--token-size', help='Token size')
@click.option('--dtype', help='Data type')
@click.option('--serving-type', help='Serving type (e.g., serverless)')
@click.option('--is-private', is_flag=True, default=False, help='Whether the model is private')
@click.option('--license', help='License information')
@click.option('--readme', help='README content')
@click.option('--path', help='Model file path (required for self-hosting models)')
@click.option('--provider-id', help='Provider ID')
@click.option('--is-custom', is_flag=True, default=False, help='Whether the model is custom')
@click.option('--custom-code-path', help='Custom code path')
@click.option('--tags', multiple=True, help='Model tags')
@click.option('--languages', multiple=True, help='Model languages')
@click.option('--tasks', multiple=True, help='Model tasks')
@click.option('--inference-param', help='Inference parameters (JSON string)')
@click.option('--quantization', help='Quantization parameters (JSON string)')
@click.option('--default-params', help='Default parameters (JSON string)')
@click.option('--endpoint-url', help='Endpoint URL (for serverless)')
@click.option('--endpoint-identifier', help='Endpoint identifier (for serverless)')
@click.option('--endpoint-key', help='Endpoint key (for serverless)')
@click.option('--endpoint-description', help='Endpoint description (for serverless)')
@click.option('--custom-runtime-image-url', help='Custom runtime image URL (required if is_custom=True)')
@click.option('--custom-runtime-use-bash', is_flag=True, default=False, help='Whether to use bash for custom runtime (default: False)')
@click.option('--custom-runtime-command', help='Custom runtime command (comma-separated values)')
@click.option('--custom-runtime-args', help='Custom runtime arguments (comma-separated values)')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Model creation JSON file path (for dict style)')
def create(name, model_type, display_name, description, size, token_size, dtype, serving_type, 
           is_private, license, readme, path, provider_id,
           is_custom, custom_code_path, tags, languages, tasks,
           inference_param, quantization, default_params, endpoint_url, endpoint_identifier, endpoint_key, endpoint_description, 
           custom_runtime_image_url, custom_runtime_use_bash, custom_runtime_command, custom_runtime_args, json_path):
    """Create a new model. (JSON file or params style both supported, file path options are auto uploaded)
    This process is complicated, so please refer to the examples below.

    \b
    Supports two styles:
    1. Parameter style: --name "model" --type "self-hosting" --path "/path/to/file.bin"
    2. JSON file style: --json model_config.json

    Examples:

    \b
    # Serverless model with endpoint
    adxp-cli model create \\
     --display-name "display name of your model" \\
     --name "name of your model" \\
     --type language \\
     --description "description of your model" \\
     --serving-type serverless \\
     --provider-id 3fa85f64-5717-4562-b3fc-2c963f66afa6 \\
     --languages Korean \\
     --languages English \\
     --tasks completion \\
     --tasks chat \\
     --tags team1 \\
     --tags team2 \\
     --endpoint-url "https://api.sktaip.com/v1" \\
     --endpoint-identifier "openai/gpt-3.5-turbo" \\
     --endpoint-key "key-1234567890"

    \b
    # Self-hosting model
    adxp-cli model create \\
     --display-name "display name of your model" \\
     --name "name of your model" \\
     --type language \\
     --description "description of your model" \\
     --serving-type self-hosting \\
     --provider-id 3fa85f64-5717-4562-b3fc-2c963f66afa6 \\
     --languages Korean \\
     --tasks completion \\
     --tags tag \\
     --path /path/to/your-model.zip

    \b
    # Self-hosting model (Model custom serving)
    adxp-cli model create \\
     --display-name "display name of your model" \\
     --name "name of your model" \\
     --type language \\
     --description "description of your model" \\
     --serving-type self-hosting \\
     --provider-id 3fa85f64-5717-4562-b3fc-2c963f66afa6 \\
     --languages Korean \\
     --tasks completion \\
     --tags tag \\
     --path /path/to/your-model.zip \\
     --is-custom \\
     --custom-code-path /path/to/your-code.zip \\
     --custom-runtime-image-url "https://hub.docker.com/r/adxpai/adxp-custom-runtime" \\
     --custom-runtime-use-bash \\
     --custom-runtime-command "/bin/bash,-c" \\
     --custom-runtime-args "uvicorn,main:app"
    """
    
    if json_path:
        # JSON file style
        with open(json_path, 'r') as f:
            data = json_module.load(f)
        # endpoint 관련 옵션은 serverless일 때만 data에 포함, 아닐 때는 완전히 제거
        if data.get('serving_type') != 'serverless':
            for k in ['endpoint_url', 'endpoint_identifier', 'endpoint_key', 'endpoint_description']:
                if k in data:
                    del data[k]
        try:
            result = create_model(data)
            if isinstance(result, dict) and "model" in result and "endpoint" in result:
                print_model_detail(result["model"], title="✅ Model created:")
                print_endpoint_list([result["endpoint"]], title="🔗 Endpoint created:")
            elif isinstance(result, dict) and "model" in result:
                print_model_detail(result["model"], title="✅ Model created:")
            else:
                print_model_detail(result, title="✅ Model created:")
        except ValueError as e:
            raise click.ClickException(str(e))
    elif name and model_type:
        # Parameter style
        data = {
            'name': name,
            'type': model_type,
            'description': description,
            'is_private': is_private,
            'is_custom': is_custom
        }
        
        # Validate that path is provided for self-hosting models
        if model_type == 'self-hosting' and not path:
            raise click.ClickException("--path is required for self-hosting models")
        
        # Optional fields
        if display_name:
            data['display_name'] = display_name
        if size:
            data['size'] = size
        if token_size:
            data['token_size'] = token_size
        if dtype:
            data['dtype'] = dtype
        if serving_type:
            data['serving_type'] = serving_type
        if license:
            data['license'] = license
        if readme:
            data['readme'] = readme
        if path:
            data['path'] = path
        if provider_id:
            data['provider_id'] = provider_id
        if custom_code_path:
            data['custom_code_path'] = custom_code_path
        # Endpoint 관련 옵션 추가
        if endpoint_url:
            data['endpoint_url'] = endpoint_url
        if endpoint_identifier:
            data['endpoint_identifier'] = endpoint_identifier
        if endpoint_key:
            data['endpoint_key'] = endpoint_key
        if endpoint_description:
            data['endpoint_description'] = endpoint_description
        
        # Parse JSON parameters
        if inference_param:
            try:
                data['inference_param'] = json_module.loads(inference_param)
            except json_module.JSONDecodeError:
                raise click.ClickException("--inference-param must be valid JSON")
        
        if quantization:
            try:
                data['quantization'] = json_module.loads(quantization)
            except json_module.JSONDecodeError:
                raise click.ClickException("--quantization must be valid JSON")
        
        if default_params:
            try:
                data['default_params'] = json_module.loads(default_params)
            except json_module.JSONDecodeError:
                raise click.ClickException("--default-params must be valid JSON")
        
        # List fields
        if tags:
            data['tags'] = [{'name': tag} for tag in tags]
        if languages:
            data['languages'] = [{'name': lang} for lang in languages]
        if tasks:
            data['tasks'] = [{'name': task} for task in tasks]
        
        # Custom runtime fields
        if custom_runtime_image_url:
            data['custom_runtime_image_url'] = custom_runtime_image_url
        if custom_runtime_use_bash is not None:
            data['custom_runtime_use_bash'] = custom_runtime_use_bash
        if custom_runtime_command:
            # 쉼표로 구분된 문자열을 리스트로 변환
            data['custom_runtime_command'] = [cmd.strip() for cmd in custom_runtime_command.split(',')]
        if custom_runtime_args:
            # 쉼표로 구분된 문자열을 리스트로 변환
            data['custom_runtime_args'] = [arg.strip() for arg in custom_runtime_args.split(',')]
        
        # endpoint 관련 옵션은 serverless일 때만 data에 포함, 아닐 때는 완전히 제거
        if serving_type == 'serverless':
            if endpoint_url:
                data['endpoint_url'] = endpoint_url
            if endpoint_identifier:
                data['endpoint_identifier'] = endpoint_identifier
            if endpoint_key:
                data['endpoint_key'] = endpoint_key
            if endpoint_description:
                data['endpoint_description'] = endpoint_description
        else:
            # 혹시라도 남아있을 수 있으니 완전히 제거
            for k in ['endpoint_url', 'endpoint_identifier', 'endpoint_key', 'endpoint_description']:
                if k in data:
                    del data[k]
        
        try:
            result = create_model(data)
            if isinstance(result, dict) and "model" in result and "endpoint" in result:
                print_model_detail(result["model"], title="✅ Model created:")
                print_endpoint_list([result["endpoint"]], title="🔗 Endpoint created:")
            elif isinstance(result, dict) and "model" in result:
                print_model_detail(result["model"], title="✅ Model created:")
            else:
                print_model_detail(result, title="✅ Model created:")
        except ValueError as e:
            raise click.ClickException(str(e))
    else:
        raise click.ClickException(
            "Invalid parameters. Use either:\n"
            "1. Parameter style: --name 'model' --type 'self-hosting' --path '/path/to/file.bin'\n"
            "2. JSON file style: --json model_config.json"
        )

@model.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated model IDs')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, filter, search, ids, json):
    """List all models."""
    result = list_models(page, size, sort, filter, search, ids)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        models = result.get("data", result)
        print_model_list(models, title="🤖 Model List:")

@model.command()
@click.argument('model_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, json):
    """Get a model by ID."""
    result = get_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🤖 Model Detail:")
        
        # serverless 모델이면 endpoint 정보도 함께 보여주기
        if result.get('serving_type') == 'serverless':
            try:
                endpoints_result = list_endpoints(model_id, page=1, size=10)
                if endpoints_result and endpoints_result.get('data'):
                    print_endpoint_list(endpoints_result['data'], title="🔗 Model Endpoints:")
            except Exception as e:
                click.secho(f"⚠️ Failed to get endpoints: {e}", fg="yellow")
        
        # self-hosting 모델이면 custom_runtime 정보도 함께 보여주기
        elif result.get('serving_type') == 'self-hosting' and result.get('is_custom'):
            try:
                custom_runtime = get_custom_runtime_by_model(model_id)
                if custom_runtime:
                    print_model_detail(custom_runtime, title="⚙️ Custom Runtime:")
            except Exception as e:
                click.secho(f"⚠️ Failed to get custom runtime: {e}", fg="yellow")

@model.command()
@click.argument('model_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, json):
    """Delete a model by ID."""
    result = delete_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🗑️ Model Deleted:")

@model.command()
@click.argument('model_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def recover(model_id, json):
    """Recover a deleted model by ID."""
    result = recover_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="♻️ Model Recovered:")

@model.command()
@click.argument('model_id')
@click.option('--name', help='Model name')
@click.option('--type', 'model_type', help='Model type')
@click.option('--display-name', help='Display name for the model')
@click.option('--description', help='Model description')
@click.option('--size', help='Model size')
@click.option('--token-size', help='Token size')
@click.option('--dtype', help='Data type')
@click.option('--serving-type', help='Serving type (e.g., serverless)')
@click.option('--license', help='License information')
@click.option('--readme', help='README content')
@click.option('--provider-id', help='Provider ID')
@click.option('--inference-param', help='Inference parameters (JSON string)')
@click.option('--quantization', help='Quantization parameters (JSON string)')
@click.option('--default-params', help='Default parameters (JSON string)')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Model update JSON file path (alternative to individual options)')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def update(model_id, name, model_type, display_name, description, size, token_size, dtype, serving_type,
           license, readme, provider_id,
           inference_param, quantization, default_params, json_path, json_output):
    """Update a model using individual options or JSON file."""
    data = {}
    
    # If JSON file is provided, use it
    if json_path:
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
    else:
        # Build data from individual options
        if name is not None:
            data['name'] = name
        if model_type is not None:
            data['type'] = model_type
        if display_name is not None:
            data['display_name'] = display_name
        if description is not None:
            data['description'] = description
        if size is not None:
            data['size'] = size
        if token_size is not None:
            data['token_size'] = token_size
        if dtype is not None:
            data['dtype'] = dtype
        if serving_type is not None:
            data['serving_type'] = serving_type
        if license is not None:
            data['license'] = license
        if readme is not None:
            data['readme'] = readme
        if provider_id is not None:
            data['provider_id'] = provider_id
        if inference_param is not None:
            try:
                data['inference_param'] = json.loads(inference_param)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for inference_param")
        if quantization is not None:
            try:
                data['quantization'] = json.loads(quantization)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for quantization")
        if default_params is not None:
            try:
                data['default_params'] = json.loads(default_params)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for default_params")
    
    if not data:
        raise click.ClickException("No update data provided. Use individual options or --json file.")
    
    result = update_model(model_id, data)
    
    if json_output:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="✅ Model Updated:")

@model.command('type-list')
@click.option('--json', is_flag=True, help='Output in JSON format')
def type_list(json):
    """List all model types."""
    types = list_model_types()
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(types, indent=2))
    else:
        print_type_list(types, title="📦 Model Types:")

@model.command('tag-list')
@click.option('--json', is_flag=True, help='Output in JSON format')
def tag_list(json):
    """List all model tags."""
    tags = list_model_tags()
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(tags, indent=2))
    else:
        print_tag_list(tags, title="🏷️ Model Tags:")

@model.command('tag-add')
@click.argument('model_id')
@click.argument('tags', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def tag_add(model_id, tags, json):
    """Add tags to a specific model."""
    tag_list = [{'name': tag} for tag in tags]
    result = add_tags_to_model(model_id, tag_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏷️ Tags Added:")

@model.command('tag-remove')
@click.argument('model_id')
@click.argument('tags', nargs=-1)
def tag_remove(model_id, tags):
    """Remove tags from a specific model."""
    tag_list = [{'name': tag} for tag in tags]
    result = remove_tags_from_model(model_id, tag_list)
    print_model_detail(result, title="🏷️ Tags Removed:")

@model.command('lang-add')
@click.argument('model_id')
@click.argument('languages', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def lang_add(model_id, languages, json):
    """Add languages to a specific model."""
    lang_list = [{'name': lang} for lang in languages]
    result = add_languages_to_model(model_id, lang_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🌐 Languages Added:")

@model.command('lang-remove')
@click.argument('model_id')
@click.argument('languages', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def lang_remove(model_id, languages, json):
    """Remove languages from a specific model."""
    lang_list = [{'name': lang} for lang in languages]
    result = remove_languages_from_model(model_id, lang_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🌐 Languages Removed:")

@model.command('task-add')
@click.argument('model_id')
@click.argument('tasks', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def task_add(model_id, tasks, json):
    """Add tasks to a specific model."""
    task_list = [{'name': task} for task in tasks]
    result = add_tasks_to_model(model_id, task_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🛠️ Tasks Added:")

@model.command('task-remove')
@click.argument('model_id')
@click.argument('tasks', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def task_remove(model_id, tasks, json):
    """Remove tasks from a specific model."""
    task_list = [{'name': task} for task in tasks]
    result = remove_tasks_from_model(model_id, task_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🛠️ Tasks Removed:")

# provider group 및 하위 명령어
@model.group()
def provider():
    """Manage model providers (SKT, OpenAI, Huggingface,etc.)."""
    pass

@provider.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--search', default=None, help='Search keyword')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, search, json):
    """List model providers."""
    result = list_providers(page, size, sort, search)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        providers = result.get("data", result)
        print_provider_list(providers, title="🏢 Provider List:")

@provider.command()
@click.argument('provider_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(provider_id, json):
    """Get a specific model provider."""
    result = get_provider(provider_id)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Detail:")

@provider.command()
@click.option('--name', prompt=True, required=True, help='Provider name. Provider name should be unique.')
@click.option('--logo', default='', help='Provider logo')
@click.option('--description', default='', help='Provider description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def create(name, logo, description, json):
    """Create a model provider."""
    data = {'name': name, 'logo': logo, 'description': description}
    result = create_provider(data)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Created:")

@provider.command()
@click.argument('provider_id')
@click.option('--name', default=None, help='Provider name')
@click.option('--logo', default=None, help='Provider logo')
@click.option('--description', default=None, help='Provider description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def update(provider_id, name, logo, description, json):
    """Update a specific model provider."""
    data = {}
    if name is not None:
        data['name'] = name
    if logo is not None:
        data['logo'] = logo
    if description is not None:
        data['description'] = description
    result = update_provider(provider_id, data)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Updated:")

@provider.command()
@click.argument('provider_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(provider_id, json):
    """Delete a specific model provider."""
    result = delete_provider(provider_id)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Deleted:")

# endpoint group 및 하위 명령어를 provider group 바로 아래로 이동
@model.group()
def endpoint():
    """Manage model endpoints and API configurations."""
    pass

@endpoint.command()
@click.argument('model_id')
@click.option('--url', prompt=True, help='Endpoint URL')
@click.option('--identifier', prompt=True, help='Endpoint identifier')
@click.option('--key', prompt=True, help='Endpoint key')
@click.option('--description', default='', help='Endpoint description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def create(model_id, url, identifier, key, description, json):
    """Create a model endpoint."""
    data = {'url': url, 'identifier': identifier, 'key': key, 'description': description}
    result = create_endpoint(model_id, data)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🔗 Endpoint Created:")

@endpoint.command()
@click.argument('model_id')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(model_id, page, size, sort, filter, search, json):
    """List model endpoints for a specific model."""
    result = list_endpoints(model_id, page, size, sort, filter, search)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        endpoints = result.get("data", result)
        print_endpoint_list(endpoints, title="🔗 Endpoint List:")

@endpoint.command()
@click.argument('model_id')
@click.argument('endpoint_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, endpoint_id, json):
    """Get a specific model endpoint."""
    result = get_endpoint(model_id, endpoint_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🔗 Endpoint Detail:")

@endpoint.command()
@click.argument('model_id')
@click.argument('endpoint_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, endpoint_id, json):
    """Delete a specific model endpoint."""
    result = delete_endpoint(model_id, endpoint_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🔗 Endpoint Deleted:")

# 19. custom-runtime group 및 하위 명령어
@model.group('custom-runtime')
def custom_runtime():
    """Manage custom runtime configurations for models."""
    pass

@custom_runtime.command("create")
@click.option("--model-id", required=True, help="Model ID (UUID)")
@click.option("--image-url", required=True, help="Custom Docker image URL")
@click.option("--use-bash", is_flag=True, default=False, help="Use Bash")
@click.option("--command", help="Execution command (comma-separated values)")
@click.option("--args", help="Execution arguments (comma-separated values)")
@click.option('--json', is_flag=True, help='Output in JSON format')
def create(model_id, image_url, use_bash, command, args, json):
    """Create a custom runtime."""
    runtime_data = {
        "model_id": model_id,
        "image_url": image_url,
        "use_bash": use_bash,
        "command": [cmd.strip() for cmd in command.split(',')] if command else None,
        "args": [arg.strip() for arg in args.split(',')] if args else None
    }
    result = create_custom_runtime(runtime_data)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🧩 Custom Runtime Created:")

@custom_runtime.command("get")
@click.option("--model-id", required=True, help="Model ID (UUID)")
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, json):
    """Get a custom runtime."""
    result = get_custom_runtime_by_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🧩 Custom Runtime Detail:")

@custom_runtime.command("delete")
@click.option("--model-id", required=True, help="Model ID (UUID)")
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, json):
    """Delete a custom runtime."""
    result = delete_custom_runtime_by_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        # 삭제 성공 메시지는 이미 delete_custom_runtime_by_model에서 출력됨
        if result:
            print_model_detail(result, title="🧩 Custom Runtime Deleted:")
        else:
            click.secho("🧩 Custom Runtime Deleted Successfully", fg="green")

# ====================================================================
# Deploy Helper Functions
# ====================================================================

def print_deployment_detail_with_apikeys(deployment_id, deployment_data):
    """Print deployment details and API keys."""
    from datetime import datetime
    
    click.echo("\n" + "="*80)
    click.secho("🚀 Deployment Details", fg="cyan", bold=True)
    click.echo("="*80 + "\n")
    
    # 기본 정보
    click.secho("📋 Basic Information", fg="yellow", bold=True)
    click.echo("-" * 80)
    
    basic_info = [
        ["ID", deployment_data.get('serving_id', deployment_data.get('id', 'N/A'))],
        ["Name", deployment_data.get('name', 'N/A')],
        ["Status", deployment_data.get('status', 'N/A')],
        ["Model ID", deployment_data.get('model_id', 'N/A')],
        ["Description", deployment_data.get('description', 'N/A') or '-'],
    ]
    click.echo(tabulate(basic_info, tablefmt="plain"))
    
    # 리소스 정보
    click.echo("\n")
    click.secho("💻 Resource Configuration", fg="yellow", bold=True)
    click.echo("-" * 80)
    
    resource_info = [
        ["CPU Request", deployment_data.get('cpu_request', 'N/A') or '-'],
        ["CPU Limit", deployment_data.get('cpu_limit', 'N/A') or '-'],
        ["Memory Request", deployment_data.get('memory_request', 'N/A') or '-'],
        ["Memory Limit", deployment_data.get('memory_limit', 'N/A') or '-'],
        ["Min Replicas", deployment_data.get('min_replicas', 'N/A') or '-'],
        ["Max Replicas", deployment_data.get('max_replicas', 'N/A') or '-'],
        ["Workers Per Core", deployment_data.get('workers_per_core', 'N/A') or '-'],
    ]
    click.echo(tabulate(resource_info, tablefmt="plain"))
    
    # 시간 정보
    click.echo("\n")
    click.secho("🕐 Timestamps", fg="yellow", bold=True)
    click.echo("-" * 80)
    
    time_info = [
        ["Created At", deployment_data.get('created_at', 'N/A')],
        ["Updated At", deployment_data.get('updated_at', 'N/A')],
    ]
    click.echo(tabulate(time_info, tablefmt="plain"))
    
    # API 키 정보 가져오기
    click.echo("\n")
    click.secho("🔑 API Keys", fg="yellow", bold=True)
    click.echo("-" * 80)
    
    try:
        apikeys_result = get_deployment_apikeys(deployment_id, page=1, size=10)
        if apikeys_result and 'data' in apikeys_result and apikeys_result['data']:
            apikeys_data = apikeys_result['data']
            
            # isinstance 대신 hasattr와 len으로 안전하게 확인
            if hasattr(apikeys_data, '__len__') and hasattr(apikeys_data, '__iter__') and len(apikeys_data) > 0:
                apikey_table = []
                for key in apikeys_data:
                    try:
                        # 태그 정보 처리 - 안전한 방식
                        tags = key.get('tag', [])
                        tag_str = '-'
                        
                        try:
                            if tags:
                                # tags가 iterable한지 확인
                                if hasattr(tags, '__iter__') and not isinstance(tags, str):
                                    # 리스트나 튜플 같은 iterable인 경우
                                    tag_list = []
                                    for t in tags:
                                        tag_list.append(str(t))
                                    tag_str = ', '.join(tag_list)
                                else:
                                    # 단일 값인 경우
                                    tag_str = str(tags)
                        except Exception:
                            # 어떤 오류가 발생해도 기본값 사용
                            tag_str = str(tags) if tags else '-'
                        
                        # API 키 부분 표시 (보안을 위해 앞 10자만)
                        api_key = key.get('api_key', '')
                        if api_key:
                            api_key_display = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else api_key
                        else:
                            api_key_display = 'N/A'
                        
                        # 활성 상태 표시
                        is_active = key.get('is_active', False)
                        status = "🟢 Active" if is_active else "🔴 Inactive"
                        
                        apikey_table.append([
                            key.get('api_key_id', 'N/A'),
                            api_key_display,
                            tag_str,
                            status,
                            key.get('created_at', 'N/A'),
                        ])
                    except Exception as key_error:
                        # 개별 키 처리 중 오류가 발생한 경우 건너뛰기
                        click.secho(f"  ⚠️  Error processing API key: {str(key_error)}", fg="yellow")
                        continue
                
                if apikey_table:
                    headers = ['API Key ID', 'Key (Partial)', 'Tags', 'Status', 'Created At']
                    click.echo(tabulate(apikey_table, headers=headers, tablefmt="grid"))
                else:
                    click.secho("  No valid API keys found.", fg="white", dim=True)
                
                # 총 개수와 페이지네이션 정보 표시
                pagination = apikeys_result.get('payload', {}).get('pagination', {})
                total = pagination.get('total', len(apikeys_data))
                current_page = pagination.get('page', 1)
                items_per_page = pagination.get('items_per_page', len(apikeys_data))
                last_page = pagination.get('last_page', 1)
                
                click.echo(f"\n📊 Showing {len(apikeys_data)} of {total} API keys (Page {current_page}/{last_page})")
            else:
                click.secho("  No API keys found for this deployment.", fg="white", dim=True)
        else:
            click.secho("  No API keys found for this deployment.", fg="white", dim=True)
    except Exception as e:
        click.secho(f"  ⚠️  Could not fetch API keys: {str(e)}", fg="yellow")
    
    click.echo("\n" + "="*80 + "\n")

def print_apikeys_only(deployment_id, apikeys_result):
    """Print API keys only."""
    click.echo("\n" + "="*80)
    click.secho("🔑 Deployment API Keys", fg="cyan", bold=True)
    click.echo("="*80 + "\n")
    
    if apikeys_result and 'data' in apikeys_result and apikeys_result['data']:
        apikeys_data = apikeys_result['data']
        
        # isinstance 대신 hasattr와 len으로 안전하게 확인
        if hasattr(apikeys_data, '__len__') and hasattr(apikeys_data, '__iter__') and len(apikeys_data) > 0:
            apikey_table = []
            for key in apikeys_data:
                try:
                    # 태그 정보 처리 - 안전한 방식
                    tags = key.get('tag', [])
                    tag_str = '-'
                    
                    try:
                        if tags:
                            # tags가 iterable한지 확인
                            if hasattr(tags, '__iter__') and not isinstance(tags, str):
                                # 리스트나 튜플 같은 iterable인 경우
                                tag_list = []
                                for t in tags:
                                    tag_list.append(str(t))
                                tag_str = ', '.join(tag_list)
                            else:
                                # 단일 값인 경우
                                tag_str = str(tags)
                    except Exception:
                        # 어떤 오류가 발생해도 기본값 사용
                        tag_str = str(tags) if tags else '-'
                    
                    # API 키 부분 표시 (보안을 위해 앞 10자만)
                    api_key = key.get('api_key', '')
                    if api_key:
                        api_key_display = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else api_key
                    else:
                        api_key_display = 'N/A'
                    
                    # 활성 상태 표시
                    is_active = key.get('is_active', False)
                    status = "🟢 Active" if is_active else "🔴 Inactive"
                    
                    apikey_table.append([
                        key.get('api_key_id', 'N/A'),
                        api_key_display,
                        tag_str,
                        status,
                        key.get('created_at', 'N/A'),
                    ])
                except Exception as key_error:
                    # 개별 키 처리 중 오류가 발생한 경우 건너뛰기
                    click.secho(f"  ⚠️  Error processing API key: {str(key_error)}", fg="yellow")
                    continue
            
            if apikey_table:
                headers = ['API Key ID', 'Key (Partial)', 'Tags', 'Status', 'Created At']
                click.echo(tabulate(apikey_table, headers=headers, tablefmt="grid"))
            else:
                click.secho("  No valid API keys found.", fg="white", dim=True)
            
            # 총 개수와 페이지네이션 정보 표시
            pagination = apikeys_result.get('payload', {}).get('pagination', {})
            total = pagination.get('total', len(apikeys_data))
            current_page = pagination.get('page', 1)
            items_per_page = pagination.get('items_per_page', len(apikeys_data))
            last_page = pagination.get('last_page', 1)
            
            click.echo(f"\n📊 Showing {len(apikeys_data)} of {total} API keys (Page {current_page}/{last_page})")
        else:
            click.secho("  No API keys found for this deployment.", fg="white", dim=True)
    else:
        click.secho("  No API keys found for this deployment.", fg="white", dim=True)
    
    click.echo("\n" + "="*80 + "\n")

def print_deployment_success(deployment_data):
    """Print deployment success information in a clean format."""
    click.echo("\n" + "="*80)
    click.secho("🎉 Deployment Created Successfully!", fg="green", bold=True)
    click.echo("="*80 + "\n")
    
    # 기본 배포 정보
    click.secho("📋 Deployment Details:", fg="cyan", bold=True)
    click.echo("-" * 40)
    
    deployment_info = [
        ["Deployment ID", deployment_data.get('serving_id', deployment_data.get('id', 'N/A'))],
        ["Name", deployment_data.get('name', 'N/A')],
        ["Status", deployment_data.get('status', 'N/A')],
        ["Model ID", deployment_data.get('model_id', 'N/A')],
        ["Created At", deployment_data.get('created_at', 'N/A')],
    ]
    
    click.echo(tabulate(deployment_info, tablefmt="plain"))
    
    click.echo("\n")
    click.secho("🚀 Next Steps:", fg="yellow", bold=True)
    click.echo("-" * 40)
    deployment_id = deployment_data.get('serving_id', deployment_data.get('id', 'N/A'))
    click.echo("• Check deployment status: adxp-cli model deploy-get --deployment-id " + deployment_id)
    click.echo("• List all deployments: adxp-cli model deploy-list")
    click.echo("• Start deployment: adxp-cli model deploy-start --deployment-id " + deployment_id)
    
    click.echo("\n" + "="*80 + "\n")


def get_available_gpu_types(resource_data):
    """리소스 데이터에서 사용 가능한 GPU 타입을 추출합니다."""
    try:
        if not resource_data or not isinstance(resource_data, dict):
            return []
            
        available_gpu_list = []
        node_resources = resource_data.get('node_resource', [])
        
        if not hasattr(node_resources, '__iter__'):
            return []
        
        for node in node_resources:
            if not hasattr(node, 'get'):
                continue
                
            node_labels = node.get('node_label', [])
            
            if not hasattr(node_labels, '__iter__'):
                continue
                
            for label in node_labels:
                if hasattr(label, 'startswith') and label.startswith('gputype='):
                    # "gputype=H100" -> "H100" 추출
                    gpu_type_name = label.split('=', 1)[1]
                    if gpu_type_name and gpu_type_name not in available_gpu_list:
                        available_gpu_list.append(gpu_type_name)
        
        return sorted(available_gpu_list)
    except Exception as e:
        # 에러가 발생하면 빈 리스트 반환
        return []


def print_resource_summary(resource_data):
    """프로젝트 리소스 요약만 출력합니다."""
    namespace_resource = resource_data.get('namespace_resource', {})
    
    click.echo("\n" + "="*80)
    click.secho("💻 Project Resource Summary", fg="cyan", bold=True)
    click.echo("="*80 + "\n")
    
    namespace_info = [
        ["CPU", f"{namespace_resource.get('cpu_used', 0):.2f} / {namespace_resource.get('cpu_quota', 0):.2f} cores", f"{namespace_resource.get('cpu_usable', 0):.2f} available"],
        ["Memory", f"{namespace_resource.get('mem_used', 0):.2f} / {namespace_resource.get('mem_quota', 0):.2f} GB", f"{namespace_resource.get('mem_usable', 0):.2f} GB available"],
        ["GPU", f"{namespace_resource.get('gpu_used', 0):.2f} / {namespace_resource.get('gpu_quota', 0):.2f} units", f"{namespace_resource.get('gpu_usable', 0):.2f} available"],
    ]
    headers = ['Resource', 'Used / Total', 'Available']
    click.echo(tabulate(namespace_info, headers=headers, tablefmt="grid"))


def print_filtered_node_resources(resource_data, gpu_type=None):
    """GPU 타입별로 필터링된 노드 리소스를 출력합니다."""
    node_resources = resource_data.get('node_resource', [])
    
    if gpu_type:
        # GPU 타입별로 노드 필터링
        filtered_nodes = []
        for node in node_resources:
            node_labels = node.get('node_label', [])
            # Check if any label contains the GPU type
            for label in node_labels:
                if hasattr(label, 'lower') and gpu_type.lower() in label.lower():
                    filtered_nodes.append(node)
                    break
        
        if not filtered_nodes:
            click.secho(f"No nodes found with {gpu_type} GPU", fg="yellow")
            return
        
        click.secho(f"\n🖥️  {gpu_type} GPU Resource Details:", fg="cyan", bold=True)
        nodes_to_show = filtered_nodes
    else:
        click.secho(f"\n💻 CPU-only Resource Details:", fg="cyan", bold=True)
        nodes_to_show = node_resources
    
    click.echo("-" * 80)
    node_table = []
    for node in nodes_to_show:
        if gpu_type:
            # GPU 정보 표시
            node_table.append([
                node.get('node_name', 'N/A'),
                f"{node.get('cpu_used', 0):.2f} / {node.get('cpu_quota', 0):.2f}",
                f"{node.get('mem_used', 0):.2f} / {node.get('mem_quota', 0):.2f} GB",
                f"{node.get('gpu_used', 0):.2f} / {node.get('gpu_quota', 0):.2f}",
                f"{node.get('cpu_usable', 0):.2f}",
                f"{node.get('mem_usable', 0):.2f} GB",
                f"{node.get('gpu_usable', 0):.2f}",
            ])
        else:
            # CPU 전용 정보
            node_table.append([
                node.get('node_name', 'N/A'),
                f"{node.get('cpu_used', 0):.2f} / {node.get('cpu_quota', 0):.2f}",
                f"{node.get('mem_used', 0):.2f} / {node.get('mem_quota', 0):.2f} GB",
                f"{node.get('cpu_usable', 0):.2f}",
                f"{node.get('mem_usable', 0):.2f} GB",
            ])
    
    if gpu_type:
        headers = ['Node Name', 'CPU Used/Total', 'Memory Used/Total', 'GPU Used/Total', 'CPU Available', 'Memory Available', 'GPU Available']
    else:
        headers = ['Node Name', 'CPU Used/Total', 'Memory Used/Total', 'CPU Available', 'Memory Available']
    
    click.echo(tabulate(node_table, headers=headers, tablefmt="grid"))


def print_resource_info(resource_data):
    """Print resource information in a formatted way."""
    click.echo("\n" + "="*80)
    click.secho("💻 Resource Information", fg="cyan", bold=True)
    click.echo("="*80 + "\n")
    
    # 네임스페이스 리소스 요약
    namespace_resource = resource_data.get('namespace_resource', {})
    click.secho("📊 Project Resource Summary", fg="yellow", bold=True)
    click.echo("-" * 80)
    
    namespace_info = [
        ["CPU", f"{namespace_resource.get('cpu_used', 0):.2f} / {namespace_resource.get('cpu_quota', 0):.2f} cores", f"{namespace_resource.get('cpu_usable', 0):.2f} available"],
        ["Memory", f"{namespace_resource.get('mem_used', 0):.2f} / {namespace_resource.get('mem_quota', 0):.2f} GB", f"{namespace_resource.get('mem_usable', 0):.2f} GB available"],
        ["GPU", f"{namespace_resource.get('gpu_used', 0):.2f} / {namespace_resource.get('gpu_quota', 0):.2f} units", f"{namespace_resource.get('gpu_usable', 0):.2f} available"],
    ]
    headers = ['Resource', 'Used / Total', 'Available']
    click.echo(tabulate(namespace_info, headers=headers, tablefmt="grid"))
    
    # 노드 리소스 상세 정보
    node_resources = resource_data.get('node_resource', [])
    if node_resources:
        click.echo("\n")
        click.secho("🖥️  Node Resource Details", fg="yellow", bold=True)
        click.echo("-" * 80)
        
        node_table = []
        for node in node_resources:
            node_table.append([
                node.get('node_name', 'N/A'),
                node.get('node_label', [])[0] if node.get('node_label') else 'N/A',
                f"{node.get('cpu_used', 0):.2f} / {node.get('cpu_quota', 0):.2f}",
                f"{node.get('mem_used', 0):.2f} / {node.get('mem_quota', 0):.2f} GB",
                f"{node.get('gpu_used', 0):.2f} / {node.get('gpu_quota', 0):.2f}",
                f"{node.get('cpu_usable', 0):.2f}",
                f"{node.get('mem_usable', 0):.2f} GB",
                f"{node.get('gpu_usable', 0):.2f}",
            ])
        
        headers = ['Node Name', 'GPU Type', 'CPU Used/Total', 'Memory Used/Total', 'GPU Used/Total', 'CPU Available', 'Memory Available', 'GPU Available']
        click.echo(tabulate(node_table, headers=headers, tablefmt="grid"))
    
    
    click.echo("\n" + "="*80 + "\n")

def select_model_version(model_id):
    """Show model versions and let user select one."""
    try:
        # Get model information using SDK directly
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        model_info = hub.get_model_by_id(model_id)
        
        click.echo("\n" + "="*80)
        click.secho(f"📦 Model Information: {model_info.get('name', 'Unknown')}", fg="cyan", bold=True)
        click.echo("="*80 + "\n")
        
        # Get model versions
        versions = list_versions(model_id)
        
        if not versions or 'data' not in versions or not versions['data']:
            # No versions available, use base model (version_id = null)
            click.secho("📋 Available Model Versions:", fg="yellow", bold=True)
            click.echo("-" * 80)
            click.secho("No specific versions found. Using base model.", fg="blue")
            click.secho("✅ Selected version: base model (version_id = null)", fg="green")
            return None  # No version_id for base model
        
        version_data = versions['data']
        
        # Display versions in a table
        click.secho("📋 Available Model Versions:", fg="yellow", bold=True)
        click.echo("-" * 80)
        
        version_table = []
        for i, version in enumerate(version_data, 1):
            version_num = version.get('version', 'N/A')
            # If version is 0, show it as "base model"
            if version_num == 0:
                version_display = "base model"
            else:
                version_display = str(version_num)
            
            version_table.append([
                i,
                version.get('id', 'N/A'),
                version_display,
                version.get('path', 'N/A'),
                version.get('is_valid', 'N/A'),
                version.get('created_at', 'N/A')[:10] if version.get('created_at') else 'N/A'
            ])
        
        headers = ['#', 'Version ID', 'Version', 'Path', 'Valid', 'Created']
        click.echo(tabulate(version_table, headers=headers, tablefmt="grid"))
        
        # Let user select
        while True:
            try:
                choice = click.prompt(f"\nSelect model version (1-{len(version_data)})", type=int)
                if 1 <= choice <= len(version_data):
                    selected_version = version_data[choice - 1]
                    version_num = selected_version.get('version', 'Unknown')
                    version_display = "base model" if version_num == 0 else str(version_num)
                    click.secho(f"✅ Selected version: {version_display} ({selected_version.get('id', 'N/A')})", fg="green")
                    return selected_version['id']
                else:
                    click.secho(f"❌ Please enter a number between 1 and {len(version_data)}", fg="red")
            except click.Abort:
                click.secho("❌ Deployment cancelled by user.", fg="yellow")
                return False  # Return False to indicate user cancellation
            except ValueError:
                click.secho("❌ Please enter a valid number.", fg="red")
                
    except Exception as e:
        click.secho(f"❌ Failed to get model versions: {str(e)}", fg="red")
        return False  # Return False to indicate error

# ====================================================================
# Deploy CLI Commands
# ====================================================================

@model.command()
@click.option("--model-id", help="Model ID to deploy")
@click.option("--name", help="Deployment name")
@click.option("--description", help="Deployment description")
# Resource options for self-hosting
@click.option("--serving-mode", help="Serving mode ('single_node', 'single_node_preferred', 'multi_node')")
@click.option("--gpu-type", help="GPU type (e.g., T4, A100)")
@click.option("--cpu", type=float, help="CPU cores")
@click.option("--memory", type=float, help="Memory (GB)")
@click.option("--gpu", type=int, help="Number of GPUs")
@click.option("--min-replicas", type=int, help="Minimum number of replicas")
@click.option("--max-replicas", type=int, help="Maximum number of replicas")
@click.option("--safety-filter-input", is_flag=True, help="Enable safety filter for input")
@click.option("--safety-filter-output", is_flag=True, help="Enable safety filter for output")
@click.option("--data-masking-input", is_flag=True, help="Enable data masking for input")
@click.option("--data-masking-output", is_flag=True, help="Enable data masking for output")
@click.option("--serving-params", help="Serving parameters as JSON string (e.g., '{\"gpu_memory_utilization\": 0.8, \"max_model_len\": 2048}')")
@click.option("--show-resources", is_flag=True, help="Show available resources before deployment")
@click.option('--json', is_flag=True, help='Output in JSON format')
def deploy(model_id, name, description, serving_mode, gpu_type, cpu, memory, gpu, min_replicas, max_replicas,
          safety_filter_input, safety_filter_output, data_masking_input, data_masking_output,
          serving_params,
          show_resources, json):
    """Deploy a model with resource configuration."""
    
    # Prompt for required fields if not provided
    if not model_id:
        model_id = click.prompt("Enter Model ID", type=str)
    if not name:
        name = click.prompt("Enter Deployment Name", type=str)
    
    # Select model version
    click.secho("🔍 Fetching model versions...", fg="blue")
    version_id = select_model_version(model_id)
    if version_id is False:  # Only return if user cancelled (False), not if None (base model)
        return  # User cancelled or error occurred
    
    # Get model information to determine if it's self-hosting
    try:
        # Use SDK directly to avoid CLI-specific code execution
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        model_info = hub.get_model_by_id(model_id)
        serving_type = model_info.get('serving_type', '').lower()
        is_self_hosting = serving_type == 'self-hosting'
    except Exception:
        # If we can't get model info, assume self-hosting if resource options are provided
        is_self_hosting = any([serving_mode, gpu_type, cpu, memory, gpu])
    
    # Show resources if requested OR if it's a self-hosting model
    if show_resources or is_self_hosting:
        try:
            click.secho("🔍 Fetching available resources...", fg="blue")
            # Extract project_id from headers (it will be automatically extracted in get_task_resources)
            resource_data = get_task_resources("serving")
            print_resource_summary(resource_data)
        except Exception as resource_error:
            click.secho(f"⚠️  Could not fetch resource information: {str(resource_error)}", fg="yellow")
            if not click.confirm("Continue with deployment anyway?"):
                click.secho("❌ Deployment cancelled by user.", fg="yellow")
                return
        
        # Ask user to configure resources for self-hosting
        if is_self_hosting:
            # First, select GPU type
            if not gpu_type:
                click.secho("\n🎮 Select GPU Type:", fg="yellow", bold=True)
                # Get available GPU types from resource data
                try:
                    # Get available GPU types from resource data
                    available_gpu_types = get_available_gpu_types(resource_data)
                    
                    if available_gpu_types:
                        for i, gpu_type_option in enumerate(available_gpu_types, 1):
                            click.echo(f"{i}. {gpu_type_option}")
                        
                        while True:
                            try:
                                choice = click.prompt("Choose GPU type (1-{}) or 'none' for CPU-only".format(len(available_gpu_types)), type=str, default='none')
                                
                                if choice.lower() == 'none':
                                    gpu_type = None
                                    break
                                elif choice.isdigit():
                                    choice_num = int(choice)
                                    if 1 <= choice_num <= len(available_gpu_types):
                                        gpu_type = available_gpu_types[choice_num - 1]
                                        break
                                    else:
                                        click.secho("❌ Please enter a number between 1 and {}".format(len(available_gpu_types)), fg="red")
                                else:
                                    click.secho("❌ Invalid choice. Please enter a number or 'none'", fg="red")
                            except click.Abort:
                                click.secho("❌ Deployment cancelled by user.", fg="yellow")
                                return
                            except ValueError:
                                click.secho("❌ Please enter a valid choice", fg="red")
                    else:
                        click.secho("No GPU types available. Using CPU-only deployment.", fg="yellow")
                        gpu_type = None
                except Exception as e:
                    click.secho(f"⚠️  Could not get available GPU types: {str(e)}", fg="yellow")
                    click.secho("Using CPU-only deployment.", fg="yellow")
                    gpu_type = None
            
            # Show selected GPU type resource information
            print_filtered_node_resources(resource_data, gpu_type)
            
            click.secho("\n🔧 Configure Resources for Self-Hosting Deployment:", fg="cyan", bold=True)
            click.echo("-" * 80)
            
            # Select serving mode
            if not serving_mode:
                click.secho("📋 Select Serving Mode:", fg="yellow", bold=True)
                click.echo("1. Single Node")
                click.echo("2. Single Node Preferred") 
                click.echo("3. Multi Node")
                
                serving_mode_options = ['single_node', 'single_node_preferred', 'multi_node']
                
                while True:
                    try:
                        choice = click.prompt("Choose serving mode (1-3)", type=str, default='1')
                        
                        # Handle numeric input
                        if choice.isdigit():
                            choice_num = int(choice)
                            if 1 <= choice_num <= 3:
                                serving_mode = serving_mode_options[choice_num - 1]
                                break
                            else:
                                click.secho("❌ Please enter a number between 1 and 3", fg="red")
                        # Handle text input
                        elif choice.lower() in ['single_node', 'single_node_preferred', 'multi_node']:
                            serving_mode = choice.lower()
                            break
                        # Handle partial matches
                        elif choice.lower() in ['single', '1']:
                            serving_mode = 'single_node'
                            break
                        elif choice.lower() in ['preferred', '2']:
                            serving_mode = 'single_node_preferred'
                            break
                        elif choice.lower() in ['multi', '3']:
                            serving_mode = 'multi_node'
                            break
                        else:
                            click.secho("❌ Invalid choice. Please enter 1, 2, 3, or the mode name", fg="red")
                    except click.Abort:
                        click.secho("❌ Deployment cancelled by user.", fg="yellow")
                        return
                    except ValueError:
                        click.secho("❌ Please enter a valid choice", fg="red")
            
            # Convert to uppercase for API
            serving_mode_upper = serving_mode.upper().replace('_', '_')
            
            # Get resource configuration from user
            if cpu is None:
                cpu_value = click.prompt("Enter CPU cores to allocate", type=float, default=4.0)
                cpu = cpu_value
            
            if memory is None:
                memory_value = click.prompt("Enter Memory in GB to allocate", type=float, default=8.0)
                memory = memory_value
            
            if gpu is None:
                if gpu_type:
                    gpu_value = click.prompt("Enter number of GPUs to allocate", type=int, default=1)
                    gpu = gpu_value
                else:
                    gpu = 0
            
            # Get mode-specific configurations
            if serving_mode == 'single_node':
                # Single Node: Get replica configuration
                if min_replicas is None and max_replicas is None:
                    replicas = click.prompt("Enter number of replicas", type=int, default=1)
                    min_replicas = replicas
                    max_replicas = replicas
            elif serving_mode == 'single_node_preferred':
                # Single Node Preferred: Fixed replicas
                min_replicas = 1
                max_replicas = 1
            elif serving_mode == 'multi_node':
                # Multi Node: Fixed replicas + Tensor Parallel Size
                min_replicas = 1
                max_replicas = 1
                
                # Get tensor parallel size for multi node
                tensor_parallel_size = click.prompt("Enter Tensor Parallel Size", type=int, default=1)
            
            # Show configured resources
            click.secho("\n📋 Configured Resources:", fg="green", bold=True)
            click.echo(f"  CPU: {cpu} cores")
            click.echo(f"  Memory: {memory} GB")
            click.echo(f"  GPU: {gpu} units ({gpu_type if gpu_type else 'N/A'})")
            click.echo(f"  Serving Mode: {serving_mode}")
            if serving_mode == 'single_node':
                click.echo(f"  Min Replicas: {min_replicas}")
                click.echo(f"  Max Replicas: {max_replicas}")
            elif serving_mode == 'multi_node':
                click.echo(f"  Replicas: 1 (fixed)")
                click.echo(f"  Tensor Parallel Size: {tensor_parallel_size}")
            else:
                click.echo(f"  Replicas: 1 (fixed)")
            
            # Ask user to continue
            if not click.confirm("\nDo you want to continue with deployment using these resources?"):
                click.secho("❌ Deployment cancelled by user.", fg="yellow")
                return
        else:
            # For non-self-hosting models, just ask to continue
            if not click.confirm("Do you want to continue with deployment?"):
                click.secho("❌ Deployment cancelled by user.", fg="yellow")
                return
    
    # Build deployment data
    serving_data = {
        "model_id": model_id,
        "name": name,
    }
    
    # Add version_id only if it exists
    if version_id:
        serving_data["version_id"] = version_id
    
    # Basic options
    if description:
        serving_data["description"] = description
    
    # Self-hosting specific options
    if is_self_hosting:
        if serving_mode:
            # Convert to uppercase for API (SINGLE_NODE, SINGLE_NODE_PREFERRED, MULTI_NODE)
            serving_mode_upper = serving_mode.upper().replace('_', '_')
            serving_data["serving_mode"] = serving_mode_upper
        if gpu_type:
            serving_data["gpu_type"] = gpu_type
        if cpu is not None:
            serving_data["cpu_request"] = int(cpu)
            serving_data["cpu_limit"] = int(cpu)
        if memory is not None:
            serving_data["mem_request"] = int(memory)
            serving_data["mem_limit"] = int(memory)
        if gpu is not None:
            serving_data["gpu_request"] = gpu
            serving_data["gpu_limit"] = gpu
        if min_replicas is not None:
            serving_data["min_replicas"] = min_replicas
        if max_replicas is not None:
            serving_data["max_replicas"] = max_replicas
        
        # Add tensor parallel size for multi node mode
        if serving_mode == 'multi_node' and 'tensor_parallel_size' in locals():
            serving_data["tensor_parallel_size"] = tensor_parallel_size
    
    
    # Safety filter and data masking options
    serving_data["safety_filter_input"] = safety_filter_input
    serving_data["safety_filter_output"] = safety_filter_output
    serving_data["data_masking_input"] = data_masking_input
    serving_data["data_masking_output"] = data_masking_output
    
    # Additional deployment metadata
    serving_data["is_custom"] = False  # Default to False as shown in UI result
    
    # Parse serving_params if provided
    if serving_params:
        try:
            serving_data["serving_params"] = json_module.loads(serving_params)
        except json_module.JSONDecodeError as e:
            click.secho(f"❌ Invalid JSON format for serving_params: {str(e)}", fg="red")
            return
    
    # Create deployment
    result = create_deployment(serving_data)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_deployment_success(result)

@model.command("deploy-list")
@click.option('--json', is_flag=True, help='Output in JSON format')
def list_servings_cmd(json):
    """List all deployments."""
    result = list_deployments()
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        if result and 'data' in result and result['data']:
            table_data = []
            for serving in result['data']:
                table_data.append([
                    serving.get('serving_id', serving.get('id', '')),
                    serving.get('name', ''),
                    serving.get('status', ''),
                    serving.get('model_id', ''),
                    serving.get('created_at', '')
                ])
            
            headers = ['ID', 'Name', 'Status', 'Model ID', 'Created At']
            click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            click.echo("No deployments found.")

@model.command("deploy-get")
@click.option("--deployment-id", required=True, help="Deployment ID")
@click.option('--json', is_flag=True, help='Output in JSON format')
def get_serving_cmd(deployment_id, json):
    """Get a specific deployment."""
    result = get_deployment(deployment_id)
    
    if json:
        # JSON 출력 시에는 API 키도 함께 포함
        try:
            apikeys_result = get_deployment_apikeys(deployment_id, page=1, size=10)
            if apikeys_result and 'data' in apikeys_result:
                result['apikeys'] = apikeys_result['data']
            else:
                result['apikeys'] = []
        except Exception:
            result['apikeys'] = []
        click.echo(json_module.dumps(result, indent=2))
    else:
        # 테이블 형식으로 예쁘게 출력
        print_deployment_detail_with_apikeys(deployment_id, result)

@model.command("deploy-update")
@click.option("--deployment-id", required=True, help="Deployment ID")
@click.option("--description", help="New deployment description")
@click.option("--serving-mode", help="Serving mode ('single_node', 'single_node_preferred', 'multi_node')")
@click.option("--cpu", type=float, help="CPU cores")
@click.option("--memory", type=float, help="Memory (GB)")
@click.option("--gpu", type=int, help="Number of GPUs")
@click.option("--min-replicas", type=int, help="Minimum number of replicas")
@click.option("--max-replicas", type=int, help="Maximum number of replicas")
@click.option("--safety-filter-input", is_flag=True, help="Enable safety filter for input")
@click.option("--safety-filter-output", is_flag=True, help="Enable safety filter for output")
@click.option("--data-masking-input", is_flag=True, help="Enable data masking for input")
@click.option("--data-masking-output", is_flag=True, help="Enable data masking for output")
@click.option("--serving-params", help="Serving parameters as JSON string (e.g., '{\"gpu_memory_utilization\": 0.8, \"max_model_len\": 2048}')")
@click.option('--json', is_flag=True, help='Output in JSON format')
def update_serving_cmd(deployment_id, description, serving_mode, cpu, memory, gpu, min_replicas, max_replicas,
                      safety_filter_input, safety_filter_output, data_masking_input, data_masking_output,
                      serving_params, json):
    """Update a deployment."""
    
    # Get current deployment info to check if it's self-hosting
    try:
        headers, config = get_credential()
        hub = AXModelHub(headers=headers, base_url=config.base_url)
        current_deployment = hub.get_deployment(deployment_id)
        serving_type = current_deployment.get('serving_type', '')
        is_self_hosting = serving_type in ['self-hosting', 'self_hosting']
    except Exception:
        # If we can't get deployment info, assume self-hosting if resource options are provided
        is_self_hosting = any([serving_mode, cpu, memory, gpu, min_replicas, max_replicas])
    
    serving_data = {}
    
    # Basic options (always available)
    if description:
        serving_data["description"] = description
    
    # Self-hosting specific options
    if is_self_hosting:
        if serving_mode:
            # Convert to uppercase for API (SINGLE_NODE, SINGLE_NODE_PREFERRED, MULTI_NODE)
            serving_mode_upper = serving_mode.upper().replace('_', '_')
            serving_data["serving_mode"] = serving_mode_upper
        
        # Resource options - handle like create command
        if cpu is not None:
            serving_data["cpu_request"] = int(cpu)
            serving_data["cpu_limit"] = int(cpu)
        if memory is not None:
            serving_data["mem_request"] = int(memory)
            serving_data["mem_limit"] = int(memory)
        if gpu is not None:
            serving_data["gpu_request"] = gpu
            serving_data["gpu_limit"] = gpu
        
        # Replica options - handle like create command
        if min_replicas is not None and max_replicas is not None:
            # Both provided - use as is
            serving_data["min_replicas"] = min_replicas
            serving_data["max_replicas"] = max_replicas
        elif min_replicas is not None and max_replicas is None:
            # Only min provided - set both to same value (like create)
            serving_data["min_replicas"] = min_replicas
            serving_data["max_replicas"] = min_replicas
        elif min_replicas is None and max_replicas is not None:
            # Only max provided - set both to same value (like create)
            serving_data["min_replicas"] = max_replicas
            serving_data["max_replicas"] = max_replicas
        
        # Parse serving_params if provided
        if serving_params:
            try:
                serving_data["serving_params"] = json_module.loads(serving_params)
            except json_module.JSONDecodeError as e:
                click.secho(f"❌ Invalid JSON format for serving_params: {str(e)}", fg="red")
                return
    
    # Safety filter and data masking options (always available)
    if safety_filter_input is not None:
        serving_data["safety_filter_input"] = safety_filter_input
    if safety_filter_output is not None:
        serving_data["safety_filter_output"] = safety_filter_output
    if data_masking_input is not None:
        serving_data["data_masking_input"] = data_masking_input
    if data_masking_output is not None:
        serving_data["data_masking_output"] = data_masking_output
    
    result = update_deployment(deployment_id, serving_data)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_deployment_success(result)

@model.command("deploy-delete")
@click.option("--deployment-id", required=True, help="Deployment ID")
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete_serving_cmd(deployment_id, json):
    """Delete a deployment."""
    result = delete_deployment(deployment_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("🚀 Deployment Deleted Successfully", fg="green")

@model.command("deploy-start")
@click.option("--deployment-id", required=True, help="Deployment ID")
@click.option('--json', is_flag=True, help='Output in JSON format')
def start_serving_cmd(deployment_id, json):
    """Start a deployment."""
    result = start_deployment(deployment_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("🚀 Deployment Started Successfully", fg="green")

@model.command("deploy-stop")
@click.option("--deployment-id", required=True, help="Deployment ID")
@click.option('--json', is_flag=True, help='Output in JSON format')
def stop_serving_cmd(deployment_id, json):
    """Stop a deployment."""
    result = stop_deployment(deployment_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("🚀 Deployment Stopped Successfully", fg="yellow")

@model.command("deploy-apikeys")
@click.option("--deployment-id", required=True, help="Deployment ID")
@click.option('--page', default=1, help='Page number (default: 1)')
@click.option('--size', default=10, help='Page size (default: 10)')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get_serving_apikeys_cmd(deployment_id, page, size, json):
    """Get deployment API keys."""
    result = get_deployment_apikeys(deployment_id, page=page, size=size)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_apikeys_only(deployment_id, result)

@model.command("deploy-hard-delete")
@click.option('--json', is_flag=True, help='Output in JSON format')
def hard_delete_serving_cmd(json):
    """Hard delete a deployment (permanent deletion)."""
    result = hard_delete_deployment()
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("🚀 Deployment Hard Deleted Successfully", fg="red")

@click.group()
def cli():
    """AIP Model CLI"""
    pass

cli.add_command(model)

if __name__ == "__main__":
    cli()
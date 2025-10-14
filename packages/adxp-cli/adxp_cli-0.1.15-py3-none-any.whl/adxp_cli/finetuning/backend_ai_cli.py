import click
import json as json_module
from .backend_ai_training import (
    create_backend_ai_training,
    list_backend_ai_trainings,
    get_backend_ai_training,
    update_backend_ai_training,
    delete_backend_ai_training,
    get_backend_ai_training_status,
    get_backend_ai_training_events,
    get_backend_ai_training_metrics,
    force_stop_backend_ai_training,
    get_platform_info,
    validate_backend_ai_platform
)
from .utils import print_training_detail, print_training_list


@click.group()
def backend_ai():
    """Backend.ai specific fine-tuning commands."""
    pass


# ====================================================================
# Platform Type Commands
# ====================================================================

@backend_ai.command()
@click.option('--json', is_flag=True, help='Output in JSON format')
def platform_info(json):
    """Get platform information.
    
    \b
    Examples:
        # Get platform info
        adxp-cli finetuning backend-ai platform-info
        
        # Get platform info in JSON format
        adxp-cli finetuning backend-ai platform-info --json
    """
    try:
        result = get_platform_info()
        
        if json:
            click.echo(json_module.dumps(result, indent=2))
        else:
            platform = result.get('platform_type', 'unknown')
            base_url = result.get('base_url', 'N/A')
            click.secho(f"✅ Platform Type: {platform}", fg="green")
            if base_url != 'N/A':
                click.secho(f"🌐 Base URL: {base_url}", fg="blue")
            
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            raise click.ClickException(
                "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
            )
        raise click.ClickException(f"❌ Failed to get platform info: {e}")


# ====================================================================
# Backend.ai Training Commands
# ====================================================================

@backend_ai.group()
def training():
    """Manage Backend.ai fine-tuning trainings."""
    pass


@training.command()
@click.option('--name', prompt=True, help='Training name')
@click.option('--dataset-ids', prompt=True, help='Comma-separated dataset IDs for training')
@click.option('--base-model-id', prompt=True, help='Base model ID for fine-tuning')
@click.option('--trainer-id', prompt=True, help='Trainer ID for the training')
@click.option('--params', prompt=True, help='Training parameters as string (e.g., "learning_rate=0.001\\nepochs=10\\nbatch_size=32")')
@click.option('--project-id', prompt=True, help='Project ID')
@click.option('--type', default='sft', help='Training type (e.g., "sft"(default), "dpo")')
@click.option('--policy', prompt=True, help='Policy configuration as JSON string (e.g., {"allowed_actions": ["read", "update", "delete"]})')
@click.option('--description', default='', help='Training description')
@click.option('--id', help='Training ID (UUID, auto-generated if not provided)')
@click.option('--envs', help='Environment variables as JSON string (e.g., {"CUDA_VISIBLE_DEVICES": "0"})')
@click.option('--is-auto-model-creation', is_flag=True, help='Auto model creation after training')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Training creation JSON file path')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def create(name, dataset_ids, base_model_id, trainer_id, params, project_id, type, policy, description, id, envs, is_auto_model_creation, json_path, json_output):
    """Create a new Backend.ai training.
    
    \b
    ** params field's examples **
    Training Parameters (--params):
    learning_rate=0.001
    epochs=10
    batch_size=32
    
    \b
    ** policy field's examples **
    Policy Configuration (--policy):
    {"allowed_actions": ["read", "update", "delete"]}
    
    \b
    Examples:
        # Interactive mode (will prompt for each field)
        adxp-cli finetuning backend-ai training create
        
        # Command line mode (basic)
        adxp-cli finetuning backend-ai training create --name "My Backend.ai Training" --dataset-ids "uuid,uuid" --base-model-id "uuid" --trainer-id "uuid" --params "learning_rate=0.001\\nepochs=10" --project-id "uuid" --policy '{"allowed_actions": ["read", "update", "delete"]}'
        
        # Command line mode (with new fields)
        adxp-cli finetuning backend-ai training create --name "My Backend.ai Training" --dataset-ids "uuid,uuid" --base-model-id "uuid" --trainer-id "uuid" --params "learning_rate=0.001" --project-id "uuid" --type "sft" --policy '{"allowed_actions": ["read", "update", "delete"]}' --is-auto-model-creation
        
        # Using JSON file
        adxp-cli finetuning backend-ai training create --json training_config.json
    """
    # Validate platform before proceeding
    validate_backend_ai_platform()
    if json_path:
        # JSON file style
        with open(json_path, 'r') as f:
            data = json_module.load(f)
    else:
        # Parameter style
        try:
            # Parse dataset_ids from comma-separated string
            dataset_ids_list = [id.strip() for id in dataset_ids.split(',')]
            
            # Parse policy from JSON string
            policy_dict = json_module.loads(policy)
            
            data = {
                'name': name,
                'dataset_ids': dataset_ids_list,
                'base_model_id': base_model_id,
                'trainer_id': trainer_id,
                'params': params,
                'project_id': project_id,
                'policy': policy_dict,
                'description': description
            }
            
            # Add optional fields if provided
            if id:
                data['id'] = id
            if envs:
                data['envs'] = json_module.loads(envs)
            if is_auto_model_creation:
                data['is_auto_model_creation'] = True
            if type is not None:
                data['type'] = type
            if project_id is not None:
                data['project_id'] = project_id

        except json_module.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON format in --policy or --envs: {e}")
        except Exception as e:
            raise click.ClickException(f"Error parsing parameters: {e}")
    
    result = create_backend_ai_training(data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Backend.ai Training Created:")


@training.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, filter, search, json):
    """List Backend.ai trainings.
    
    \b
    Examples:
        # List all trainings
        adxp-cli finetuning backend-ai training list
        
        # List with pagination
        adxp-cli finetuning backend-ai training list --page 2 --size 20
        
        # List with filtering
        adxp-cli finetuning backend-ai training list --filter "status:running" --sort "created_at,desc"
        
        # Search trainings
        adxp-cli finetuning backend-ai training list --search "my_training"
    """
    # Validate platform before proceeding
    validate_backend_ai_platform()
    
    result = list_backend_ai_trainings(page=page, size=size, sort=sort, filter=filter, search=search)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_list(result, title="🎯 Backend.ai Trainings:")


@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(training_id, json):
    """Get Backend.ai training details.
    
    \b
    Examples:
        # Get training details
        adxp-cli finetuning backend-ai training get eaa6b26d-388e-45d4-b338-287df73c3bf3
    """
    # Validate platform before proceeding
    validate_backend_ai_platform()
    
    result = get_backend_ai_training(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Backend.ai Training Detail:")


@training.command()
@click.argument('training_id')
@click.option('--name', help='Training name')
@click.option('--description', help='Training description')
@click.option('--status', help='Training status (initialized, starting, training, trained, error, etc.)')
@click.option('--id', help='Training ID (UUID)')
@click.option('--envs', help='Environment variables as JSON string (e.g., {"CUDA_VISIBLE_DEVICES": "0"})')
@click.option('--is-auto-model-creation', is_flag=True, help='Auto model creation after training')
@click.option('--type', help='Training type (e.g., "sft"(default), "dpo")')
@click.option('--policy', help='Access policy configuration as JSON string')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Training update JSON file path')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def update(training_id, name, description, status, id, envs, is_auto_model_creation, type, policy, json_path, json_output):
    """Update a Backend.ai training.
    
    \b
    Examples:
        # Update training name
        adxp-cli finetuning backend-ai training update eaa6b26d-388e-45d4-b338-287df73c3bf3 --name "Updated Training Name"
        
        # Update training status
        adxp-cli finetuning backend-ai training update eaa6b26d-388e-45d4-b338-287df73c3bf3 --status "starting"
        
        # Update with new fields
        adxp-cli finetuning backend-ai training update eaa6b26d-388e-45d4-b338-287df73c3bf3 --is-auto-model-creation --policy '[{"scopes": ["GET", "POST"], "policies": [{"type": "user", "logic": "POSITIVE", "names": ["admin"]}]}]'
        
        # Update multiple fields
        adxp-cli finetuning backend-ai training update eaa6b26d-388e-45d4-b338-287df73c3bf3 --name "New Name" --description "Updated description" --is-auto-model-creation
        
        # Using JSON file
        adxp-cli finetuning backend-ai training update eaa6b26d-388e-45d4-b338-287df73c3bf3 --json update_config.json
    """
    # Validate platform before proceeding
    validate_backend_ai_platform()
    
    data = {}
    
    if json_path:
        with open(json_path, 'r') as f:
            data = json_module.load(f)
    else:
        # Parse individual options
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if status is not None:
            data['status'] = status
        if id is not None:
            data['id'] = id
        if envs is not None:
            try:
                data['envs'] = json_module.loads(envs)
            except json_module.JSONDecodeError as e:
                raise click.ClickException(f"Invalid JSON format in --envs: {e}")
        if is_auto_model_creation is not None:
            data['is_auto_model_creation'] = is_auto_model_creation
        if type is not None:
            data['type'] = type
        if policy is not None:
            try:
                data['policy'] = json_module.loads(policy)
            except json_module.JSONDecodeError as e:
                raise click.ClickException(f"Invalid JSON format in --policy: {e}")
    
    if not data:
        raise click.ClickException("No update data provided. Use individual options or --json file.")
    
    result = update_backend_ai_training(training_id, data)
    
    if json_output:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_training_detail(result, title="🎯 Backend.ai Training Updated:")


@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(training_id, json):
    """Delete a Backend.ai training.
    
    \b
    Examples:
        # Delete training
        adxp-cli finetuning backend-ai training delete eaa6b26d-388e-45d4-b338-287df73c3bf3
    """
    result = delete_backend_ai_training(training_id)
    
    if json:
        click.echo(json_module.dumps({"success": result}, indent=2))
    else:
        click.secho("✅ Backend.ai training deleted successfully", fg="green")


@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def status(training_id, json):
    """Get Backend.ai training status.
    
    \b
    Examples:
        # Get training status
        adxp-cli finetuning backend-ai training status eaa6b26d-388e-45d4-b338-287df73c3bf3
    """
    result = get_backend_ai_training_status(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        status = result.get('status', 'unknown')
        prev_status = result.get('prev_status', 'unknown')
        click.secho(f"✅ Current Status: {status}", fg="green")
        click.secho(f"📊 Previous Status: {prev_status}", fg="blue")


@training.command()
@click.argument('training_id')
@click.option('--after', help='Get events after this timestamp (e.g., "2024-10-22T15:00:00.000Z")')
@click.option('--limit', default=100, help='Limit number of events (default: 100, max: 1000)')
@click.option('--json', is_flag=True, help='Output in JSON format')
def events(training_id, after, limit, json):
    """Get Backend.ai training events.
    
    \b
    Examples:
        # Get training events
        adxp-cli finetuning backend-ai training events eaa6b26d-388e-45d4-b338-287df73c3bf3
        
        # Get events with limit
        adxp-cli finetuning backend-ai training events eaa6b26d-388e-45d4-b338-287df73c3bf3 --limit 50
        
        # Get events after timestamp
        adxp-cli finetuning backend-ai training events eaa6b26d-388e-45d4-b338-287df73c3bf3 --after "2024-10-22T15:00:00.000Z"
    """
    result = get_backend_ai_training_events(training_id, after=after, limit=limit)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        events = result.get('data', [])
        if events:
            click.secho(f"📋 Found {len(events)} events:", fg="green")
            for event in events:
                timestamp = event.get('timestamp', 'N/A')
                level = event.get('level', 'INFO')
                message = event.get('message', 'N/A')
                source = event.get('source', 'N/A')
                click.echo(f"  [{timestamp}] [{level}] [{source}] {message}")
        else:
            click.secho("📋 No events found", fg="yellow")


@training.command()
@click.argument('training_id')
@click.option('--type', default='train', help='Metric type (default: train)')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--json', is_flag=True, help='Output in JSON format')
def metrics(training_id, type, page, size, json):
    """Get Backend.ai training metrics.
    
    \b
    Examples:
        # Get training metrics
        adxp-cli finetuning backend-ai training metrics eaa6b26d-388e-45d4-b338-287df73c3bf3
        
        # Get metrics with pagination
        adxp-cli finetuning backend-ai training metrics eaa6b26d-388e-45d4-b338-287df73c3bf3 --page 2 --size 20
        
        # Get specific metric type
        adxp-cli finetuning backend-ai training metrics eaa6b26d-388e-45d4-b338-287df73c3bf3 --type validation
    """
    result = get_backend_ai_training_metrics(training_id, type=type, page=page, size=size)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        metrics = result.get('data', [])
        if metrics:
            click.secho(f"📊 Found {len(metrics)} metrics:", fg="green")
            for metric in metrics:
                key = metric.get('key', 'N/A')
                value = metric.get('value', 'N/A')
                step = metric.get('step', 'N/A')
                created_at = metric.get('created_at', 'N/A')
                click.echo(f"  Step {step}: {key} = {value} (at {created_at})")
        else:
            click.secho("📊 No metrics found", fg="yellow")


@training.command()
@click.argument('training_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def force_stop(training_id, json):
    """Force stop a Backend.ai training.
    
    \b
    Examples:
        # Force stop training
        adxp-cli finetuning backend-ai training force-stop eaa6b26d-388e-45d4-b338-287df73c3bf3
    """
    result = force_stop_backend_ai_training(training_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        click.secho("✅ Backend.ai training force stop requested", fg="green")

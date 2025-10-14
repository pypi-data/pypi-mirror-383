import click
from tabulate import tabulate
import json as json_module

def print_training_detail(training, title=None):
    """Prints a single training as a table."""
    if not training:
        click.secho("No training found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Field", "Value"]
    rows = []
    for key, value in training.items():
        # Handle params field specially - convert newlines to \\n
        if key == "params" and isinstance(value, str):
            display_value = value.replace('\n', '\\n')
            rows.append([key, display_value])
        # Handle nested objects
        elif isinstance(value, dict):
            for nested_key, nested_value in value.items():
                rows.append([f"{key}.{nested_key}", nested_value])
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                # List of objects - show first few items
                display_value = f"[{len(value)} items]"
                if len(value) <= 3:
                    display_value = ', '.join([str(item) for item in value])
            else:
                display_value = ', '.join([str(item) for item in value]) if value else '-'
            rows.append([key, display_value])
        else:
            rows.append([key, value])
    click.echo(tabulate(rows, headers, tablefmt="github"))

def print_training_list(trainings, title=None):
    """Prints a list of trainings as a table."""
    if not trainings:
        click.secho("No trainings found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    
    # Extract data from response if it's wrapped
    if isinstance(trainings, dict) and 'data' in trainings:
        training_data = trainings['data']
    else:
        training_data = trainings
    
    headers = ["id", "name", "status", "model_id", "dataset_id", "created_at", "updated_at"]
    rows = []
    for t in training_data:
        # Truncate long names
        name = t.get("name", "")
        if len(name) > 30:
            name = name[:27] + "..."
        
        # Format dates
        created_at = t.get("created_at", "")
        if created_at:
            created_at = created_at.split("T")[0]  # YYYY-MM-DD only
        
        updated_at = t.get("updated_at", "")
        if updated_at:
            updated_at = updated_at.split("T")[0]  # YYYY-MM-DD only
        
        rows.append([
            t.get("id", ""),
            name,
            t.get("status", ""),
            t.get("model_id", ""),
            t.get("dataset_id", ""),
            created_at,
            updated_at
        ])
    
    click.echo(tabulate(rows, headers, tablefmt="simple"))

def print_trainer_detail(trainer, title=None):
    """Prints a single trainer as a table."""
    if not trainer:
        click.secho("No trainer found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Field", "Value"]
    rows = []
    for key, value in trainer.items():
        if key == 'policy' and isinstance(value, list):
            # Special handling for policy - show as formatted JSON
            if value:
                import json
                policy_str = json.dumps(value, indent=2)
                rows.append([key, f"\\n{policy_str}"])
            else:
                rows.append([key, "No policy configured"])
        elif isinstance(value, dict):
            for nested_key, nested_value in value.items():
                rows.append([f"{key}.{nested_key}", nested_value])
        elif isinstance(value, list):
            display_value = ', '.join([str(item) for item in value]) if value else '-'
            rows.append([key, display_value])
        elif key == 'is_private':
            # Special handling for is_private - show with emoji
            privacy_display = "🔒 Private" if value else "🌐 Public"
            rows.append([key, privacy_display])
        else:
            rows.append([key, value])
    click.echo(tabulate(rows, headers, tablefmt="github"))

def print_trainer_list(trainers, title=None):
    """Prints a list of trainers as a table."""
    if not trainers:
        click.secho("No trainers found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    
    # Extract data from response if it's wrapped
    if isinstance(trainers, dict) and 'data' in trainers:
        trainer_data = trainers['data']
    else:
        trainer_data = trainers
    
    headers = ["id", "registry_url", "description", "is_private", "created_at", "updated_at"]
    rows = []
    for t in trainer_data:
        # Truncate long descriptions
        description = t.get("description") or ""
        if len(description) > 50:
            description = description[:47] + "..."
        
        # Format privacy flag
        is_private = t.get("is_private", False)
        privacy_display = "🔒 Private" if is_private else "🌐 Public"
        
        # Format dates
        created_at = t.get("created_at", "")
        if created_at:
            created_at = created_at.split("T")[0]  # YYYY-MM-DD only
        
        updated_at = t.get("updated_at", "")
        if updated_at:
            updated_at = updated_at.split("T")[0]  # YYYY-MM-DD only
        
        rows.append([
            t.get("id", ""),
            t.get("registry_url", ""),
            description,
            privacy_display,
            created_at,
            updated_at
        ])
    
    click.echo(tabulate(rows, headers, tablefmt="simple"))

def print_metrics_list(metrics, title=None):
    """Prints a list of metrics as a table."""
    if not metrics:
        click.secho("No metrics found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    
    # Extract data from response if it's wrapped
    if isinstance(metrics, dict) and 'data' in metrics:
        metrics_data = metrics['data']
    else:
        metrics_data = metrics
    
    headers = ["step", "loss", "type", "custom_metrics", "created_at"]
    rows = []
    for m in metrics_data:
        # Format custom metrics
        custom_metrics = m.get("custom_metric", {})
        custom_str = ', '.join([f"{k}: {v}" for k, v in custom_metrics.items()]) if custom_metrics else '-'
        if len(custom_str) > 50:
            custom_str = custom_str[:47] + "..."
        
        # Format date
        created_at = m.get("created_at", "")
        if created_at:
            created_at = created_at.split("T")[0]  # YYYY-MM-DD only
        
        rows.append([
            m.get("step", ""),
            m.get("loss", ""),
            m.get("type", ""),
            custom_str,
            created_at
        ])
    
    click.echo(tabulate(rows, headers, tablefmt="simple"))

def print_events_list(events, title=None):
    """Prints a list of events as a table."""
    if not events:
        click.secho("No events found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    
    # Extract data from response if it's wrapped
    if isinstance(events, dict) and 'data' in events:
        events_data = events['data']
    else:
        events_data = events
    
    # Check if this is the new format with 'time' and 'log' fields
    if events_data and isinstance(events_data[0], dict) and 'time' in events_data[0]:
        # New format: time, log fields
        headers = ["time", "log"]
        rows = []
        for e in events_data:
            # Keep full log messages for better debugging
            log = e.get("log", "")
            
            # Format time (keep full timestamp for now)
            time = e.get("time", "")
            
            rows.append([time, log])
    else:
        # Old format: event, message, level, created_at fields
        headers = ["event", "message", "level", "created_at"]
        rows = []
        for e in events_data:
            # Truncate long messages
            message = e.get("message", "")
            if len(message) > 60:
                message = message[:57] + "..."
            
            # Format date
            created_at = e.get("created_at", "")
            if created_at:
                created_at = created_at.split("T")[0]  # YYYY-MM-DD only
            
            rows.append([
                e.get("event", ""),
                message,
                e.get("level", ""),
                created_at
            ])
    
    click.echo(tabulate(rows, headers, tablefmt="simple"))

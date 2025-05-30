import json
from pathlib import Path
import typer


CONFIG_DIR = Path.home() / ".vibe"
CONFIG_FILE = CONFIG_DIR / "config.json"

def _ensure_config_file_exists():
    """Ensures the config directory and file exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump({}, f)
        typer.secho(f"ℹ️ Created Vibe CLI config file at {CONFIG_FILE}", fg=typer.colors.BLUE)

def _load_config():
    """Loads the configuration from the JSON file."""
    _ensure_config_file_exists()
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        typer.secho(f"⚠️ Config file {CONFIG_FILE} is corrupted. Initializing with empty config.", fg=typer.colors.YELLOW)
        return {}

def _save_config(config_data):
    """Saves the configuration to the JSON file."""
    _ensure_config_file_exists()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def get_value(args):
    """Handler for 'vibe config get <key>'."""
    if not args or len(args) != 1:
        typer.secho("❌ Usage: vibe config get <key>", fg=typer.colors.RED)
        return {"success": False, "error": "Usage: vibe config get <key>"}
    key = args[0]
    config = _load_config()
    value = config.get(key)
    if value is not None:
        typer.secho(f"ℹ️ {key} = {json.dumps(value)}", fg=typer.colors.BLUE) # Use json.dumps for consistent output
        return f"{key} = {value}" 
    else:
        typer.secho(f"❌ Key '{key}' not found in configuration.", fg=typer.colors.RED)
        return {"success": False, "error": f"Key '{key}' not found in configuration."}

def set_value(args):
    """Handler for 'vibe config set <key> <value>'."""
    if not args or len(args) != 2:
        typer.secho("❌ Usage: vibe config set <key> <value>", fg=typer.colors.RED)
        return {"success": False, "error": "Usage: vibe config set <key> <value>"}
    key, value_str = args[0], args[1]
    config = _load_config()
    
    # Attempt to parse value as JSON (e.g., for bools, numbers)
    try:
        actual_value = json.loads(value_str)
    except json.JSONDecodeError:
        actual_value = value_str # Store as string if not valid JSON
        
    config[key] = actual_value
    _save_config(config)
    typer.secho(f"✅ Successfully set: {key} = {actual_value}", fg=typer.colors.GREEN)
    return {"message": f"Configuration updated: {key} = {actual_value}"}

def list_values(args):
    """Handler for 'vibe config list'."""
    if args:
        typer.secho("❌ Usage: vibe config list (takes no arguments)", fg=typer.colors.RED)
        return {"success": False, "error": "Usage: vibe config list (takes no arguments)"}
    config = _load_config()
    if not config:
        typer.secho("ℹ️ Configuration is empty.", fg=typer.colors.BLUE)
        return "Configuration is empty."
    
    typer.secho("Current Vibe CLI Configuration:", fg=typer.colors.CYAN)
    for key, value in config.items():
        typer.secho(f"  ➡️ {key}: {json.dumps(value)}")
    # Return the config data for potential programmatic use, though display is handled by typer
    return config

# Example of how you might add more later, e.g., for telemetry config
# def set_telemetry_status(args):
#     if not args or len(args) != 1 or args[0] not in ['enable', 'disable']:
#         return {"success": False, "error": "Usage: vibe config telemetry <enable|disable>"}
#     status_to_set = args[0] == 'enable'
#     # ... logic to set telemetry status ...
#     return {"message": f"Telemetry has been {args[0]}d."}

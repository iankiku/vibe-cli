"""
Configuration command mappings for Vibe CLI

This module provides commands for managing the vibe.config.json file.
All commands are prefixed with 'vibe' when used in the terminal.
Example: 'vibe config list' instead of a traditional command
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from ..utils import telemetry
from cli.utils.config import (
    load_config,
    save_config,
    get_config_value,
    set_config_value,
    add_mcp_server,
    remove_mcp_server,
    get_mcp_server,
    list_mcp_servers,
    CONFIG_FILE
)

# Helper function for update command
def _run_update_script(check_only=False):
    """Run the update script with the appropriate arguments."""
    update_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts", "update.py")
    
    if not os.path.exists(update_script):
        print("❌ Update script not found. Please reinstall Vibe CLI.")
        return 1
    
    args = [sys.executable, update_script]
    if check_only:
        args.append("--check-only")
    
    try:
        result = subprocess.run(args, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Update failed with error code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        return 1

# Helper functions for telemetry commands
def _telemetry_status():
    """Show telemetry status."""
    telemetry_instance = telemetry.get_telemetry()
    status = telemetry_instance.status()
    
    print(f"Telemetry status: {'Enabled' if status['enabled'] else 'Disabled'}")
    if status['enabled']:
        print(f"Anonymous ID: {status['user_id']}")
        print(f"Events queued: {status['events_queued']}")
    
    print("\nTelemetry helps us improve Vibe CLI by collecting anonymous usage data.")
    print("We respect your privacy and never collect personal information.")
    print("You can disable telemetry at any time with 'vibe config telemetry disable'")

def _telemetry_enable():
    """Enable telemetry."""
    telemetry_instance = telemetry.get_telemetry()
    if telemetry_instance.enable():
        print("✅ Telemetry enabled. Thank you for helping improve Vibe CLI!")
        print("You can disable telemetry at any time with 'vibe config telemetry disable'")
    else:
        print("❌ Failed to enable telemetry")

def _telemetry_disable():
    """Disable telemetry."""
    telemetry_instance = telemetry.get_telemetry()
    if telemetry_instance.disable():
        print("✅ Telemetry disabled. No usage data will be collected.")
        print("You can enable telemetry at any time with 'vibe config telemetry enable'")
    else:
        print("❌ Failed to disable telemetry")

# Configuration command mappings
COMMANDS = {
    # Configuration commands
    "config show": lambda: print(json.dumps(load_config(), indent=2)),
    "config list": lambda: print(json.dumps(load_config(), indent=2)),
    "config path": lambda: print(CONFIG_FILE),
    
    # Get specific values
    "config get": lambda key: print(json.dumps(get_config_value(key), indent=2) if get_config_value(key) is not None else f"Config value '{key}' not found"),

    # Set values
    "config set": lambda key_value: set_config_value(
        key_value.split("=")[0], 
        key_value.split("=")[1]
    ) if "=" in key_value else print("Error: Format should be 'key=value'"),
    
    # MCP server management
    "config mcp list": lambda: print(json.dumps(list_mcp_servers(), indent=2)),
    "config mcp show": lambda name: print(json.dumps(get_mcp_server(name), indent=2) if get_mcp_server(name) else f"MCP server '{name}' not found"),
    "config mcp add": lambda name_command_args: _add_mcp_server_handler(name_command_args),
    "config mcp remove": lambda name: remove_mcp_server(name) and print(f"Removed MCP server '{name}'") or print(f"MCP server '{name}' not found"),

    # Reset configuration
    "config reset": lambda: save_config({}) and print("Configuration reset to empty") or print("Failed to reset configuration"),
    
    # Update commands
    "update": lambda: _run_update_script(False),
    "update check": lambda: _run_update_script(True),
    
    # Telemetry commands
    "config telemetry": lambda: _telemetry_status(),
    "config telemetry status": lambda: _telemetry_status(),
    "config telemetry enable": lambda: _telemetry_enable(),
    "config telemetry disable": lambda: _telemetry_disable(),
}

def _add_mcp_server_handler(args_string):
    """Handler for the 'config mcp add' command."""
    try:
        # Parse the arguments string into name, command, and args
        parts = args_string.split()
        if len(parts) < 2:
            print("Error: Format should be 'name command [args...]'")
            return
        
        name = parts[0]
        command = parts[1]
        command_args = parts[2:] if len(parts) > 2 else []
        
        # Add the MCP server
        if add_mcp_server(name, command, command_args):
            print(f"Added MCP server '{name}'")
        else:
            print(f"Failed to add MCP server '{name}'")
    except Exception as e:
        print(f"Error adding MCP server: {str(e)}")

# Helper function to execute a config command
def execute_config_command(command, args):
    """Execute a configuration command with arguments."""
    if command in COMMANDS:
        if callable(COMMANDS[command]):
            if args:
                # For commands that take arguments
                COMMANDS[command](args)
            else:
                # For commands that don't take arguments
                COMMANDS[command]()
        else:
            # For static command mappings
            return COMMANDS[command]
    else:
        print(f"Unknown config command: {command}")
        print("Available commands:", ", ".join(COMMANDS.keys()))
        return None

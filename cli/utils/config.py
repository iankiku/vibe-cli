"""
Configuration utility for Vibe CLI.

This module handles loading, saving, and accessing the vibe.config.json file
that stores user-specific settings and configurations.
"""

import json
import os
import sys
import platform
import subprocess
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vibe-config")

# Default installation directory
if platform.system() == "Windows":
    DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), ".vibe-cli")
else:
    DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), ".vibe-cli")

# Config file path
CONFIG_FILE = os.path.join(DEFAULT_INSTALL_DIR, "vibe.config.json")

def get_python_version():
    """Get the current Python version."""
    return {
        "major": sys.version_info.major,
        "minor": sys.version_info.minor,
        "micro": sys.version_info.micro,
        "full": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

def get_npm_version():
    """Get the npm version if available."""
    try:
        result = subprocess.run(["npm", "--version"], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

def get_yarn_version():
    """Get the yarn version if available."""
    try:
        result = subprocess.run(["yarn", "--version"], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

def get_pnpm_version():
    """Get the pnpm version if available."""
    try:
        result = subprocess.run(["pnpm", "--version"], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

def get_os_info():
    """Get information about the OS."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version()
    }

def get_shell_info():
    """Get information about the user's shell."""
    shell = os.environ.get("SHELL", None)
    if shell:
        return os.path.basename(shell)
    return None

def generate_default_config():
    """Generate a default configuration file with system information."""
    config = {
        "version": "1.0.0",
        "created_at": "",  # Will be set when saved
        "system": {
            "python": get_python_version(),
            "os": get_os_info(),
            "shell": get_shell_info()
        },
        "package_managers": {
            "npm": get_npm_version(),
            "yarn": get_yarn_version(),
            "pnpm": get_pnpm_version()
        },
        "mcpServers": {}
    }
    
    return config

def load_config():
    """
    Load the vibe.config.json file.
    If the file doesn't exist, create a default one.
    """
    try:
        if not os.path.exists(CONFIG_FILE):
            logger.info(f"Config file not found at {CONFIG_FILE}, creating default...")
            save_config(generate_default_config())
        
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        # If there's an error loading, create a fresh config
        default_config = generate_default_config()
        save_config(default_config)
        return default_config

def save_config(config):
    """Save the configuration to vibe.config.json."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # Update created_at if it's a new config
        if not config.get("created_at"):
            from datetime import datetime
            config["created_at"] = datetime.now().isoformat()
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Config saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        return False

def get_config_value(key_path, default=None):
    """
    Get a value from the config using a dot-separated path.
    Example: get_config_value("system.python.version")
    """
    config = load_config()
    keys = key_path.split('.')
    
    current = config
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default

def set_config_value(key_path, value):
    """
    Set a value in the config using a dot-separated path.
    Example: set_config_value("mcpServers.myserver.command", "npx")
    """
    config = load_config()
    keys = key_path.split('.')
    
    # Navigate to the nested dictionary
    current = config
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the value
    current[keys[-1]] = value
    
    # Save the updated config
    return save_config(config)

def add_mcp_server(name, command, args=None, env=None):
    """
    Add a new MCP server configuration.
    
    Args:
        name: Name of the MCP server
        command: Command to run the server
        args: List of arguments for the command
        env: Dictionary of environment variables
    """
    config = load_config()
    
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"][name] = {
        "command": command,
        "args": args or [],
        "env": env or {}
    }
    
    return save_config(config)

def remove_mcp_server(name):
    """Remove an MCP server configuration."""
    config = load_config()
    
    if "mcpServers" in config and name in config["mcpServers"]:
        del config["mcpServers"][name]
        return save_config(config)
    
    return False

def get_mcp_server(name):
    """Get the configuration for a specific MCP server."""
    return get_config_value(f"mcpServers.{name}")

def list_mcp_servers():
    """List all configured MCP servers."""
    servers = get_config_value("mcpServers", {})
    return list(servers.keys())

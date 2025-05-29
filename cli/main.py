#!/usr/bin/env python3
"""
Vibe CLI - Natural language command line interface

Vibe CLI is a command-line tool that provides a natural language interface
for common development tasks using Git, npm, Python, and more.
All commands start with 'vibe' followed by natural language instructions.
"""

import os
import sys
import shlex
import subprocess
import logging
from typing import List, Dict, Any, Union, Callable, Optional

# Import command modules
from cli.commands import git_commands
from cli.commands import npm_commands
from cli.commands import python_commands
from cli.commands import config_commands

# Import utilities
from cli.utils import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vibe-cli")

# Load config on startup
def load_cli_config():
    """Load CLI configuration and ensure it exists."""
    try:
        return config.load_config()
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return None

# Build the command registry from all command modules
def build_command_registry():
    """
    Build a registry of all available commands from different modules.
    """
    registry = {}
    
    # Add Git commands
    registry.update(git_commands.COMMANDS)
    
    # Add npm commands
    registry.update(npm_commands.COMMANDS)
    
    # Add Python commands
    registry.update(python_commands.COMMANDS)
    
    return registry

def get_all_commands():
    """Get a list of all available commands."""
    registry = build_command_registry()
    config_cmds = {f"config {cmd}": None for cmd in config_commands.COMMANDS.keys()}
    
    # Combine all commands
    all_commands = list(registry.keys()) + list(config_cmds.keys())
    return sorted(all_commands)

def print_help():
    """Print help information."""
    print("Vibe CLI - Natural language command line interface")
    print("\nUsage:")
    print("  vibe <command> [arguments]")
    print("\nAll commands start with 'vibe' followed by natural language instructions.")
    print("\nExamples:")
    print("  vibe status                  # Check Git status")
    print("  vibe add express             # Install Express package")
    print("  vibe run app.py              # Run a Python script")
    print("  vibe config show             # Show current configuration")
    print("\nAvailable commands:")
    
    # Group commands by type
    all_commands = get_all_commands()
    
    # Filter and group commands
    git_cmds = [cmd for cmd in all_commands if any(x in cmd for x in ["git", "commit", "push", "pull", "branch", "merge"])]
    npm_cmds = [cmd for cmd in all_commands if any(x in cmd for x in ["install", "add", "remove", "npm", "package", "dependency"])]
    python_cmds = [cmd for cmd in all_commands if any(x in cmd for x in ["python", "pip", "env", "venv", "run"])]
    config_cmds = [cmd for cmd in all_commands if cmd.startswith("config")]
    
    # Print a subset of commands in each category
    print("\n  Git commands:")
    for cmd in git_cmds[:5]:
        print(f"    vibe {cmd}")
    print("    ... and more")
    
    print("\n  npm commands:")
    for cmd in npm_cmds[:5]:
        print(f"    vibe {cmd}")
    print("    ... and more")
    
    print("\n  Python commands:")
    for cmd in python_cmds[:5]:
        print(f"    vibe {cmd}")
    print("    ... and more")
    
    print("\n  Configuration commands:")
    for cmd in config_cmds[:5]:
        print(f"    vibe {cmd}")
    print("    ... and more")
    
    print("\nFor more information, visit: https://github.com/yourusername/vibe-cli")

def execute_command(command: str, args: List[str]) -> int:
    """
    Execute a command with arguments.
    
    Args:
        command: The command to execute
        args: List of arguments
    
    Returns:
        Exit code
    """
    # Check for configuration commands
    if command.startswith("config "):
        config_cmd = command[7:]  # Remove "config " prefix
        if config_cmd in config_commands.COMMANDS:
            # Join args with spaces for the config command
            arg_str = " ".join(args) if args else ""
            config_commands.execute_config_command(config_cmd, arg_str)
            return 0
    
    # Get the command registry
    registry = build_command_registry()
    
    # Check if the command exists
    if command in registry:
        cmd_def = registry[command]
        
        # Handle command definition based on type
        if callable(cmd_def):
            # Command is a function that takes arguments
            if args:
                # If multiple args, join them
                if len(args) > 1:
                    arg_str = " ".join(args)
                    cmd_to_run = cmd_def(arg_str)
                else:
                    # Just one arg
                    cmd_to_run = cmd_def(args[0])
            else:
                # No args, call without any
                try:
                    cmd_to_run = cmd_def()
                except TypeError:
                    # Function requires an argument but none provided
                    print(f"Command '{command}' requires an argument.")
                    return 1
        else:
            # Command is a static list or string
            cmd_to_run = cmd_def
        
        # Execute the command
        if isinstance(cmd_to_run, list):
            # Execute as a subprocess with arguments
            try:
                return subprocess.run(cmd_to_run + args).returncode
            except Exception as e:
                print(f"Error executing command: {str(e)}")
                return 1
        elif isinstance(cmd_to_run, str):
            # Execute as a shell command
            try:
                # For shell commands, append any additional args
                full_cmd = f"{cmd_to_run} {' '.join(args)}" if args else cmd_to_run
                return subprocess.run(full_cmd, shell=True).returncode
            except Exception as e:
                print(f"Error executing command: {str(e)}")
                return 1
        else:
            print(f"Invalid command definition for '{command}'")
            return 1
    else:
        # Command not found
        print(f"Command not found: '{command}'")
        print("Run 'vibe help' to see available commands.")
        return 1

def find_closest_command(input_cmd: str, all_commands: List[str]) -> Optional[str]:
    """Find the closest matching command based on input."""
    import difflib
    
    # Get closest matches
    matches = difflib.get_close_matches(input_cmd, all_commands, n=3, cutoff=0.6)
    
    if matches:
        return matches[0]
    return None

def main():
    """Main entry point for the CLI."""
    # Ensure config is loaded
    cli_config = load_cli_config()
    
    # Parse arguments
    args = sys.argv[1:]
    
    if not args or args[0] in ["help", "--help", "-h"]:
        print_help()
        return 0
    
    # The first argument is the command
    command = args[0]
    command_args = args[1:] if len(args) > 1 else []
    
    # Handle version command
    if command in ["version", "--version", "-v"]:
        print("Vibe CLI v1.0.0")
        return 0
    
    # Check if this is a config command
    if command == "config":
        if len(command_args) > 0:
            config_subcmd = command_args[0]
            remaining_args = command_args[1:] if len(command_args) > 1 else []
            
            # Try to execute the config subcommand
            if config_subcmd in config_commands.COMMANDS:
                # Join remaining args with spaces for the config command
                arg_str = " ".join(remaining_args) if remaining_args else ""
                config_commands.execute_config_command(config_subcmd, arg_str)
                return 0
            else:
                print(f"Unknown config command: {config_subcmd}")
                print("Available config commands:", ", ".join(config_commands.COMMANDS.keys()))
                return 1
        else:
            # Default to showing config
            config_commands.execute_config_command("show", "")
            return 0
    
    # Build the command registry
    registry = build_command_registry()
    
    # Try to execute the command
    if command in registry:
        return execute_command(command, command_args)
    else:
        # Try to find a close match
        all_commands = list(registry.keys())
        closest = find_closest_command(command, all_commands)
        
        if closest:
            print(f"Command '{command}' not found. Did you mean 'vibe {closest}'?")
        else:
            print(f"Command '{command}' not found. Run 'vibe help' to see available commands.")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())

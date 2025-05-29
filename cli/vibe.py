#!/usr/bin/env python3
"""
Vibe CLI - Natural language interface for developer tools

A CLI tool that allows developers to use natural language instead of remembering
specific command syntax for common development tools like Git, npm, and Python.

Examples:
  vibe status                 # Check git status
  vibe add everything         # Stage all files in git
  vibe commit "Add feature"   # Commit with a message
  vibe push                   # Push changes to remote
  vibe start node             # Initialize a node project
  vibe add express            # Install an npm package
  vibe create env             # Create a Python virtual environment
"""

import os
import sys
import subprocess
import shlex
import importlib
from pathlib import Path

# Add the parent directory to sys.path to allow importing modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import command modules
from cli.commands import git_commands, npm_commands, python_commands, config_commands
from cli.utils import formatting, shell_detection, telemetry

# Initialize telemetry
telemetry_instance = telemetry.get_telemetry()

# Merge all command dictionaries
ALL_COMMANDS = {
    **git_commands.COMMANDS,
    **npm_commands.COMMANDS,
    **python_commands.COMMANDS,
    **config_commands.COMMANDS
}

def find_command(user_input):
    """Find the closest matching command from user input."""
    user_input = user_input.strip().lower()
    
    # First, try exact matches
    if user_input in ALL_COMMANDS:
        return user_input, ""
    
    # Next, try commands that take arguments
    for cmd in ALL_COMMANDS:
        if user_input.startswith(cmd + " "):
            args = user_input[len(cmd):].strip()
            return cmd, args
    
    # Try partial matches at the beginning
    for cmd in ALL_COMMANDS:
        if user_input.startswith(cmd):
            args = user_input[len(cmd):].strip()
            return cmd, args
    
    # If nothing matches
    return None, None

def execute_command(command, args=""):
    """Execute a command with arguments."""
    # Return error if command is None
    if command is None:
        formatting.print_error(f"Unknown command: {' '.join(sys.argv[1:])}")
        formatting.print_info("Try 'vibe help' to see available commands")
        
        # Track unrecognized command in telemetry
        if telemetry_instance.enabled:
            telemetry_instance.track('command_not_found', {
                'input': ' '.join(sys.argv[1:])
            })
        
        return 1
    
    # Get the command specification
    cmd_spec = ALL_COMMANDS.get(command)
    if not cmd_spec:
        formatting.print_error(f"Command not found: {command}")
        formatting.print_info("Try 'vibe help' for a list of available commands")
        
        # Track unrecognized command in telemetry
        if telemetry_instance.enabled:
            telemetry_instance.track('command_not_found', {
                'input': f"{command} {args}".strip()
            })
        
        return 1
    
    # Track command execution in telemetry
    if telemetry_instance.enabled:
        # Don't track sensitive data like commit messages
        safe_command = command
        # For privacy, don't log argument details for certain commands
        sensitive_commands = ['commit', 'config', 'clone']
        has_sensitive_data = any(cmd in command for cmd in sensitive_commands)
        
        telemetry_instance.track('command_executed', {
            'command': safe_command,
            'has_args': bool(args),
            'contains_sensitive_data': has_sensitive_data
        })
    
    # Process command based on type
    try:
        if callable(cmd_spec):
            # For function-based commands
            if args:
                result = cmd_spec(args)
            else:
                result = cmd_spec()
                
            # Function may return an integer status code
            if isinstance(result, int):
                return result
            return 0
        
        elif isinstance(cmd_spec, list):
            # For list-based commands (direct subprocess calls)
            cmd_display = ' '.join(cmd_spec)
            formatting.print_action(f"Running: {cmd_display}")
            subprocess.run(cmd_spec, shell=False, check=True)
            formatting.print_success("Command completed successfully")
            return 0
        
        else:  # string for shell commands
            # For string-based commands (shell execution)
            formatting.print_action(f"Running: {cmd_spec}")
            subprocess.run(cmd_spec, shell=True, check=True)
            formatting.print_success("Command completed successfully")
            return 0
            
    except subprocess.CalledProcessError as e:
        formatting.print_error(f"Command failed: Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        
        # Track error in telemetry
        if telemetry_instance.enabled:
            telemetry_instance.track('command_error', {
                'command': command,
                'error_type': 'subprocess_error',
                'exit_code': e.returncode
            })
            
        return e.returncode
        
    except FileNotFoundError as e:
        formatting.print_error(f"Command not found: {e}")
        
        # Track error in telemetry
        if telemetry_instance.enabled:
            telemetry_instance.track('command_error', {
                'command': command,
                'error_type': 'file_not_found'
            })
            
        return 1
        
    except Exception as e:
        formatting.print_error(f"Error: {e}")
        
        # Track error in telemetry
        if telemetry_instance.enabled:
            telemetry_instance.track('command_error', {
                'command': command,
                'error_type': type(e).__name__
            })
            
        return 1

def show_help():
    """Display help information about available commands."""
    formatting.print_header("Vibe CLI - Natural language commands for developers")
    print("\nAvailable commands:")
    
    # Git commands
    formatting.print_section("Git Commands:")
    formatting.print_command("vibe status", "Check git status")
    formatting.print_command("vibe add everything", "Add all files")
    formatting.print_command("vibe add file.txt", "Add specific file")
    formatting.print_command("vibe commit \"Your message\"", "Commit with message")
    formatting.print_command("vibe push", "Push changes")
    formatting.print_command("vibe pull", "Pull changes")
    formatting.print_command("vibe start repo", "Initialize a new repository")
    formatting.print_command("vibe get repo URL", "Clone a repository")
    
    # npm commands
    formatting.print_section("npm Commands:")
    formatting.print_command("vibe start node", "Initialize a node project")
    formatting.print_command("vibe add express", "Install a package")
    formatting.print_command("vibe remove lodash", "Uninstall a package")
    formatting.print_command("vibe run build", "Run an npm script")
    formatting.print_command("vibe check updates", "Check for outdated packages")
    
    # Python commands
    formatting.print_section("Python Commands:")
    formatting.print_command("vibe create env", "Create a virtual environment")
    formatting.print_command("vibe run app.py", "Run a Python script")
    formatting.print_command("vibe install requests", "Install a Python package")
    formatting.print_command("vibe save requirements", "Freeze requirements")
    
    # System commands
    formatting.print_section("System Commands:")
    formatting.print_command("vibe version", "Show version information")
    formatting.print_command("vibe help", "Show this help message")
    
    return 0

def show_version():
    """Display version information."""
    from cli import __version__
    formatting.print_header(f"Vibe CLI v{__version__}")
    formatting.print_info("https://github.com/yourusername/vibe-cli")
    return 0

def main():
    """Main entry point for the Vibe CLI."""
    # Handle special arguments
    if len(sys.argv) < 2:
        formatting.print_header("Vibe CLI - Use natural language for development commands")
        formatting.print_info("Try 'vibe help' for a list of available commands")
        return 0
        
    if sys.argv[1] == "help":
        return show_help()
        
    if sys.argv[1] == "version":
        return show_version()
    
    # Process the command with natural language
    user_input = " ".join(sys.argv[1:])
    command, args = find_command(user_input)
    
    # Execute the command
    return execute_command(command, args)

if __name__ == "__main__":
    sys.exit(main())

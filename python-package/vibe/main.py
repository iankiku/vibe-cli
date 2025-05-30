#!/usr/bin/env python3
"""
Vibe CLI - Main entry point for Python package
"""
import os
import sys
import yaml
import shutil
import urllib.parse
import subprocess
from pathlib import Path
import typer

import importlib # For dynamic handler imports

# Import the logger
from vibe.utils.logger import get_logger
from vibe.constants import CLI_VERSION # For version command

# Get a logger instance for this module
logger = get_logger(__name__)

app = typer.Typer()

def get_shared_dir():
    """Get the path to the shared directory containing common files"""
    # In development: Check for local shared directory
    local_shared = Path(__file__).resolve().parent.parent.parent / "shared"
    if local_shared.exists():
        return local_shared
    
    # In installed package: Look in package directory
    package_shared = Path(__file__).parent.parent / "shared"
    if package_shared.exists():
        return package_shared
    
    # Fallback to a copy that should be included in the package
    return Path(__file__).parent / "shared"

def load_commands():
    """Load command definitions from shared YAML file"""
    shared_dir = get_shared_dir()
    commands_file = shared_dir / "commands.yaml"
    
    try:
        with open(commands_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load commands: {e}")
        return {}

def load_natural_language_commands():
    """Load natural language command mappings"""
    shared_dir = get_shared_dir()
    nl_commands_file = shared_dir / "vibe_language_commands.yaml"
    
    try:
        with open(nl_commands_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load natural language commands: {e}")
        return {}

def parse_command_args(args, commands, nl_commands=None):
    """Parse command arguments to determine which command to run"""
    if not args or len(args) == 0:
        return {"show_help": True}

    # Handle special cases
    if args[0] in ["--version", "-v"]:
        return {"type": "system", "command": "version", "args": []}
    
    if args[0] in ["help", "--help", "-h"]:
        return {"show_help": True}
    
    # Check for natural language command
    if nl_commands and len(args) >= 1:
        # Join all args to form a phrase
        phrase = " ".join(args)
        
        # Try to match the phrase to a natural language command
        for tool_name, tool_nl_commands in nl_commands.items():
            for nl_phrase, command_ref in tool_nl_commands.items():
                if phrase.lower() == nl_phrase.lower():
                    # Found a match, parse the reference (e.g., "git.status")
                    ref_parts = command_ref.split('.')
                    if len(ref_parts) == 2:
                        ref_tool, ref_cmd = ref_parts
                        if ref_tool in commands and ref_cmd in commands[ref_tool]:
                            return {
                                "tool": ref_tool,
                                "command": ref_cmd,
                                "config": commands[ref_tool][ref_cmd],
                                "args": [],  # No args for exact phrase matches
                                "natural_language": True
                            }
    
    # Standard command parsing
    tool_name = args[0]
    tool_commands = commands.get(tool_name)
    
    if not tool_commands:
        return {"error": f"Unknown tool: '{tool_name}'. For a list of available tools, run 'vibe help'."}
    
    # If only tool specified, or explicit help for tool
    if len(args) == 1 or (len(args) > 1 and args[1] == "help"):
        return {"tool_help": tool_name, "commands": tool_commands}
    
    command_name = args[1]
    command = tool_commands.get(command_name)
    
    if not command:
        return {"error": f"Unknown command: '{command_name}' for tool '{tool_name}'. For commands in '{tool_name}', run 'vibe {tool_name} help'."}
    
    # Command-specific help
    if len(args) > 2 and args[2] == "help":
        return {"command_help": True, "tool": tool_name, 
                "command": command_name, "config": command}
    
    # Valid command found, return its config and remaining args
    return {
        "tool": tool_name,
        "command": command_name,
        "config": command,
        "args": args[2:]
    }

def format_command(template, args):
    """Format a command template with argument values"""
    result = template
    
    # Simple placeholder replacement
    if "{" in template:
        # Extract placeholder names from template
        import re
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        # Replace each placeholder with its value from args
        for i, placeholder in enumerate(placeholders):
            if i < len(args):
                result = result.replace(f"{{{placeholder}}}", args[i])
    
    return result

def execute_command(command_info):
    """Execute a command based on its configuration"""
    tool = command_info.get("tool")
    command = command_info.get("command")
    config = command_info.get("config")
    args = command_info.get("args", [])
    
    if not config:
        return {"error": "Invalid command configuration"}
    
    if "handler" in config:
        handler_path = config["handler"] # e.g., "vibe.commands.config.set_value"
        module_name, function_name = handler_path.rsplit('.', 1)
        try:
            module = importlib.import_module(module_name)
            handler_function = getattr(module, function_name)
            # Pass the arguments. Handlers are responsible for their own arg parsing.
            handler_result = handler_function(args)
            return {
                "type": "handler",
                "success": True, 
                "result": handler_result
            }
        except ImportError:
            logger.error(f"Handler module {module_name} not found.")
            return {"type": "handler", "success": False, "error": f"Handler module {module_name} not found."}
        except AttributeError:
            logger.error(f"Handler function {function_name} not found in {module_name}.")
            return {"type": "handler", "success": False, "error": f"Handler function {function_name} not found in {module_name}."}
        except Exception as e:
            logger.error(f"Error executing handler {handler_path}: {e}")
            return {"type": "handler", "success": False, "error": f"Error in handler {handler_path}: {str(e)}"}
    
    elif "command" in config:
        # Execute a shell command
        cmd_template = config["command"]
        final_command = format_command(cmd_template, args)
        
        try:
            # Execute the command and capture output
            result = subprocess.run(
                final_command,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            return {
                "type": "shell",
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "type": "shell",
                "success": False,
                "error": str(e),
                "stdout": e.stdout if hasattr(e, 'stdout') else "",
                "stderr": e.stderr if hasattr(e, 'stderr') else ""
            }
    
    return {"error": "Command configuration is invalid"}

def print_general_help(commands):
    """Display general help information"""
    typer.secho("Vibe CLI - Your Friendly Command Companion 🪄", fg=typer.colors.CYAN, bold=True)
    typer.secho("Usage: vibe <tool> <command> [args]", fg=typer.colors.GREEN)
    typer.secho("       vibe <natural language command>", fg=typer.colors.GREEN)
    typer.secho("\n🛠️ Available tools:", fg=typer.colors.YELLOW)
    
    for tool_name in commands:
        typer.secho(f"  {tool_name}", fg=typer.colors.BLUE)
    
    typer.secho("\n🗣️ Natural language examples:", fg=typer.colors.YELLOW)
    typer.secho("  'vibe check status'", fg=typer.colors.WHITE)
    typer.secho("  'vibe add everything'", fg=typer.colors.WHITE)
    typer.secho("  'vibe commit with message \"fix bug\"'", fg=typer.colors.WHITE)
    typer.secho("  'vibe pull latest'", fg=typer.colors.WHITE)
    typer.secho("\nRun 'vibe <tool> help' for commands within a tool", fg=typer.colors.GREEN)
    typer.secho("Run 'vibe help' to see this message", fg=typer.colors.GREEN)

def print_tool_help(tool_name, tool_commands):
    """Display help for a specific tool"""
    typer.secho(f"Vibe CLI - {tool_name} commands 🛠️", fg=typer.colors.CYAN, bold=True)
    typer.secho(f"Usage: vibe {tool_name} <command> [args]", fg=typer.colors.GREEN)
    typer.secho("\nAvailable commands:", fg=typer.colors.YELLOW)
    
    for cmd_name, cmd in tool_commands.items():
        description = cmd.get("description", "")
        typer.secho(f"  {typer.style(cmd_name.ljust(20), fg=typer.colors.BLUE)} {description}")
    
    typer.secho(f"\nRun 'vibe {tool_name} <command> help' for command details", fg=typer.colors.GREEN)

def print_command_help(tool_name, command_name, config):
    """Display help for a specific command"""
    typer.secho(f"Vibe CLI - {tool_name} {command_name} 📜", fg=typer.colors.CYAN, bold=True)
    typer.secho(f"Description: {config.get('description', 'No description')}", fg=typer.colors.WHITE)
    
    if "command" in config:
        typer.secho(f"\nℹ️ Underlying command template: {config['command']}", fg=typer.colors.BLUE)
    
    typer.secho("\n💡 Usage examples:", fg=typer.colors.YELLOW)
    typer.secho(f"  vibe {tool_name} {command_name} [args]", fg=typer.colors.WHITE)

@app.command("install-alias")
def install_alias(shell: str = typer.Option(None, help="Shell type: bash or zsh")):
    """
    Install the Vibe CLI shell alias to your shell configuration file
    """
    # Determine shell type if not specified
    if not shell:
        current_shell = os.environ.get("SHELL", "")
        if "zsh" in current_shell:
            shell = "zsh"
        else:
            shell = "bash"  # Default to bash
    
    # Get the alias script path
    shared_dir = get_shared_dir()
    alias_script = shared_dir / "vibe_alias.sh"
    
    if not alias_script.exists():
        typer.secho(f"⚠️ Alias script not found at {alias_script}", fg=typer.colors.YELLOW)
        typer.secho(f"❌ Error: Alias script not found at {alias_script}", fg=typer.colors.RED)
        return
    
    # Determine RC file path
    home = Path.home()
    if shell == "zsh":
        rc_file = home / ".zshrc"
    else:
        rc_file = home / ".bashrc"
    
    # Create backup
    backup_file = f"{rc_file}.bak"
    shutil.copy(rc_file, backup_file)
    
    # Append alias loader to RC file
    with open(rc_file, "a") as f:
        f.write(f"\n# VibeCLI aliases\nsource {alias_script}\n")
    
    # logger.info(f"Successfully installed Vibe CLI alias to {rc_file}") # Replaced by typer.secho
    typer.secho(f"🎉 Successfully installed Vibe CLI alias to {rc_file}", fg=typer.colors.GREEN)
    typer.secho(f"(Backup saved to {backup_file})", fg=typer.colors.BRIGHT_BLACK)
    typer.secho("Please restart your shell or run:", fg=typer.colors.YELLOW)
    typer.secho(f"  source {rc_file}", fg=typer.colors.WHITE)

    typer.secho("\n📣 Spread the Vibe!", fg=typer.colors.MAGENTA, bold=True)
    tweet_text = "I just installed the Vibe CLI! 🎉 It's making my dev workflow so much smoother. Check it out! #VibeCLI #DevTools @VibeDev"
    tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote_plus(tweet_text)}"
    typer.secho(f"🐦 Tweet about it: {tweet_url}", fg=typer.colors.CYAN)

    typer.secho("\n🤝 Join the Community:", fg=typer.colors.MAGENTA, bold=True)
    typer.secho("💬 Discord (VibeSquad): https://discord.gg/YourVibeDiscord", fg=typer.colors.CYAN)

    typer.secho("\n🔗 Stay Connected:", fg=typer.colors.MAGENTA, bold=True)
    typer.secho("➡️ Twitter: https://twitter.com/VibeDev", fg=typer.colors.CYAN)
    typer.secho("➡️ LinkedIn: https://linkedin.com/company/VibeDev", fg=typer.colors.CYAN)

def main():
    """Main function - called when package is executed"""
    # If run with typer CLI
    if len(sys.argv) > 1 and sys.argv[1] == "install-alias":
        app()
        return
    
    # Normal CLI execution
    cli_args = sys.argv[1:]

    if cli_args and cli_args[0] in ["--version", "-v"]:
        typer.secho(f"✨ Vibe CLI Version: {CLI_VERSION}", fg=typer.colors.MAGENTA)
        # logger.info(f"Vibe CLI Version: {CLI_VERSION}") # Replaced by typer.secho
        sys.exit(0)
    commands = load_commands()
    nl_commands = load_natural_language_commands()
    
    if not commands:
        typer.secho("❌ Failed to load command definitions. Check logs for details.", fg=typer.colors.RED)
        sys.exit(1)
    
    command_info = parse_command_args(cli_args, commands, nl_commands)
    
    # Handle help requests
    if command_info.get("show_help", False):
        print_general_help(commands)
        # logger.debug("Displayed general help") # Help displayed by print_general_help
        sys.exit(0)
    
    if "tool_help" in command_info:
        print_tool_help(command_info["tool_help"], command_info["commands"])
        sys.exit(0)
    
    if command_info.get("command_help", False):
        print_command_help(
            command_info["tool"],
            command_info["command"],
            command_info["config"]
        )
        sys.exit(0)
    
    # Handle errors
    if "error" in command_info:
        typer.secho(f"❌ Error: {command_info['error']}", fg=typer.colors.RED)
        sys.exit(1)
    
    # Execute the command
    typer.secho(f"🚀 Executing: vibe {command_info.get('tool', '')} {command_info.get('command', '')}", fg=typer.colors.BLUE)
    # logger.info(f"Executing command: {command_info.get('tool', '')} {command_info.get('command', '')}")
    result = execute_command(command_info)
    
    if "error" in result:
        typer.secho(f"❌ Command execution failed: {result['error']}", fg=typer.colors.RED)
        sys.exit(1)
    
    if result.get("type") == "shell":
        if result.get("stdout"):
            typer.secho("✅ Command output:", fg=typer.colors.GREEN)
            print(result["stdout"].strip())
        if result.get("stderr"):
            typer.secho("❌ Command error output:", fg=typer.colors.RED, err=True)
            print(result["stderr"].strip(), file=sys.stderr)
        
        if not result.get("success", True):
            sys.exit(1)
    
    elif result.get("type") == "handler":
        if result.get("success"):
            handler_output = result.get("result")
            if handler_output is not None: 
                if isinstance(handler_output, str):
                    print(handler_output)
                elif isinstance(handler_output, dict) and "message" in handler_output:
                    print(handler_output["message"])
                elif isinstance(handler_output, dict):
                    # If it's a dict without 'message', log for debug, don't print by default
                    logger.debug(f"Handler returned dict without 'message': {handler_output}")
                # Other types (like None if handler prints itself) are fine, no explicit print here.
        else:
            error_message = result.get('error', 'Handler execution failed.')
            typer.secho(f"❌ Handler error: {error_message}", fg=typer.colors.RED, err=True)
            # logger.error(f"Handler error: {error_message}") # Replaced by typer.secho
            sys.exit(1)
        
    # If it was a natural language command, provide feedback
    if command_info.get("natural_language", False):
        # logger.info(f"Executed natural language command: '{' '.join(sys.argv[1:])}'") # User feedback is now the primary output
        typer.secho(f"\n✨ Command '{' '.join(cli_args)}' executed as: vibe {command_info['tool']} {command_info['command']}", fg=typer.colors.BRIGHT_GREEN)

if __name__ == "__main__":
    main()

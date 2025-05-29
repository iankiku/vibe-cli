import subprocess
import os  # Used for OS detection in translators
import typer
import shlex
from .translators import git, npm, python

# Core logic in separate functions to enable testing without Typer

# Merge all translator dicts - accessible for testing
ALL_COMMANDS = {**git.commands, **npm.commands, **python.commands}

def find_command_key(input_text):
    """Find matching command key for the input text."""
    for key in ALL_COMMANDS:
        if input_text.startswith(key):
            return key
    return None

def process_command(command_text):
    """Process a command without Typer dependency, returns dict with results."""
    results = {
        'success': False,
        'command_found': False,
        'exit_code': 1,
        'display_message': '',
        'error_message': '',
        'shell_cmd': None,
        'use_shell': False
    }
    
    if not command_text:
        results['error_message'] = '❌ No command provided.'
        return results
        
    text = command_text.lower().strip()
    key = find_command_key(text)
    
    if not key:
        results['error_message'] = '❌ No matching vibe found. Be more specific.'
        return results
    
    results['command_found'] = True
    action = ALL_COMMANDS[key]
    args_str = text[len(key):].strip()
    
    try:
        if callable(action):
            cmd_spec = action(args_str)
        else:
            cmd_spec = action
            
        if isinstance(cmd_spec, list):
            display_cmd = shlex.join(cmd_spec)
            results['display_message'] = f'👉 Running: {display_cmd}'
            results['shell_cmd'] = cmd_spec
            results['use_shell'] = False
        elif isinstance(cmd_spec, str):
            results['display_message'] = f'👉 Running (shell): {cmd_spec}'
            results['shell_cmd'] = cmd_spec
            results['use_shell'] = True
        else:
            results['error_message'] = '❌ Internal error: Command translator returned an unexpected type.'
            return results
        
        results['success'] = True
        results['exit_code'] = 0
        return results
        
    except Exception as e:
        results['error_message'] = f'❌ Error processing command: {e}'
        return results

def execute_command(cmd_spec, use_shell=False):
    """Execute command with subprocess and handle errors."""
    try:
        subprocess.run(cmd_spec, shell=use_shell, check=True)
        return {'success': True, 'exit_code': 0}
    except subprocess.CalledProcessError as e:
        return {
            'success': False, 
            'exit_code': e.returncode,
            'error_message': f'💥 Error executing command: {e}'
        }
    except FileNotFoundError as e:
        cmd_name = cmd_spec[0] if isinstance(cmd_spec, list) and cmd_spec else str(cmd_spec)
        return {
            'success': False, 
            'exit_code': 1,
            'error_message': f'💥 Command not found: {cmd_name}'
        }

# Typer CLI interface
app = typer.Typer(help='🚀 Vibe: speak plain English, run dev commands.')

@app.command()
def run(command: str = typer.Argument(..., help='Your vibe command in quotes')):
    """Interpret natural language and execute the corresponding shell command."""
    # Use the core logic function
    result = process_command(command)
    
    # Handle display and errors
    if result['error_message']:
        typer.secho(result['error_message'], fg=typer.colors.RED)
        raise typer.Exit(code=result['exit_code'])
    
    typer.secho(result['display_message'], fg=typer.colors.GREEN)
    
    # Execute the command
    if result['shell_cmd']:
        exec_result = execute_command(result['shell_cmd'], result['use_shell'])
        if not exec_result['success']:
            typer.secho(exec_result['error_message'], fg=typer.colors.RED)
            raise typer.Exit(code=exec_result['exit_code'])

if __name__ == '__main__':
    app()

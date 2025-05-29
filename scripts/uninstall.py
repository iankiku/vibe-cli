#!/usr/bin/env python3
"""
Vibe CLI Uninstaller

This script uninstalls Vibe CLI from any platform (macOS, Linux, Windows).
It detects the user's shell, removes the installation directory,
and updates shell configuration files appropriately.

Usage:
  python uninstall.py [--force]

Options:
  --force    Skip confirmation prompts
"""

import os
import sys
import shutil
import platform
import subprocess
import argparse
import re
from pathlib import Path

# Colors for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    
    # Disable colors if not in a terminal
    if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
        RESET = BOLD = GREEN = YELLOW = RED = BLUE = ''

# Add the parent directory to the path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from cli.utils.shell_detection import get_shell_info, get_vibe_install_dir
except ImportError:
    # If we can't import, define the functions here
    def get_shell_info():
        """Detect the user's shell and config file."""
        system = platform.system()
        shell_info = {
            'system': system,
            'shell': None,
            'config_file': None,
            'is_powershell': False
        }
        
        if system == 'Windows':
            shell_info['shell'] = 'powershell'
            shell_info['is_powershell'] = True
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 'echo $PROFILE'],
                    capture_output=True, text=True, check=True
                )
                profile_path = result.stdout.strip()
                if profile_path:
                    shell_info['config_file'] = profile_path
                else:
                    documents = os.path.join(str(Path.home()), 'Documents')
                    shell_info['config_file'] = os.path.join(
                        documents, 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1'
                    )
            except (subprocess.SubprocessError, FileNotFoundError):
                documents = os.path.join(str(Path.home()), 'Documents')
                shell_info['config_file'] = os.path.join(
                    documents, 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1'
                )
        else:
            shell_path = os.environ.get('SHELL', '')
            
            if 'zsh' in shell_path:
                shell_info['shell'] = 'zsh'
                shell_info['config_file'] = os.path.join(str(Path.home()), '.zshrc')
            elif 'bash' in shell_path:
                shell_info['shell'] = 'bash'
                if system == 'Darwin':
                    bash_profile = os.path.join(str(Path.home()), '.bash_profile')
                    if os.path.exists(bash_profile):
                        shell_info['config_file'] = bash_profile
                    else:
                        shell_info['config_file'] = os.path.join(str(Path.home()), '.bashrc')
                else:
                    shell_info['config_file'] = os.path.join(str(Path.home()), '.bashrc')
            else:
                shell_info['shell'] = 'bash'
                shell_info['config_file'] = os.path.join(str(Path.home()), '.bashrc')
        
        return shell_info

    def get_vibe_install_dir():
        """Get the installation directory for Vibe CLI."""
        home_dir = str(Path.home())
        install_dir = os.path.join(home_dir, '.vibe-tools', 'cli', 'bin')
        return install_dir

def print_step(text):
    """Print a step in the uninstallation process."""
    print(f"{Colors.BLUE}==>{Colors.RESET} {Colors.BOLD}{text}{Colors.RESET}")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}!{Colors.RESET} {text}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def get_user_confirmation(prompt, force=False):
    """Ask the user for confirmation."""
    if force:
        return True
    
    response = input(f"{prompt} (y/N): ").strip().lower()
    return response in ('y', 'yes')

def remove_installation_dir():
    """Remove the installation directory."""
    install_dir = get_vibe_install_dir()
    cli_dir = os.path.dirname(install_dir)
    vibe_dir = os.path.dirname(cli_dir)
    
    if not os.path.exists(vibe_dir):
        print_warning(f"Installation directory not found: {vibe_dir}")
        return True
    
    try:
        shutil.rmtree(vibe_dir)
        print_success(f"Removed directory: {vibe_dir}")
        return True
    except Exception as e:
        print_error(f"Error removing directory: {e}")
        return False

def update_shell_config(shell_info):
    """Remove Vibe CLI references from shell configuration file."""
    config_file = shell_info['config_file']
    
    if not os.path.exists(config_file):
        print_warning(f"Shell config file not found: {config_file}")
        return True
    
    try:
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        # Remove vibe CLI configuration
        # First, check if vibe config exists
        if 'vibe-tools' not in config_content and 'vibe CLI' not in config_content:
            print_warning(f"No Vibe CLI configuration found in: {config_file}")
            return True
        
        # Define patterns to remove
        patterns = [
            r'# Vibe CLI configuration.*?\n',
            r'function vibe \{.*?\}',
            r'export PATH=".*?vibe-tools.*?"',
            r'alias vibe=.*?\n'
        ]
        
        # Apply all patterns
        new_content = config_content
        for pattern in patterns:
            new_content = re.sub(pattern, '', new_content, flags=re.DOTALL)
        
        # Remove any double blank lines created
        new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
        
        # Write back to file
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        print_success(f"Updated shell config: {config_file}")
        return True
    except Exception as e:
        print_error(f"Error updating shell config: {e}")
        return False

def print_post_uninstall_message(shell_info):
    """Print message after uninstallation."""
    print("\n" + Colors.GREEN + Colors.BOLD + "🎉 Vibe CLI uninstallation complete!" + Colors.RESET)
    print("\nTo finalize the uninstallation, you need to:")
    
    if shell_info['is_powershell']:
        print(f"\n1. Reload your PowerShell profile:")
        print(f"   . $PROFILE")
    elif shell_info['shell'] == 'zsh':
        print(f"\n1. Reload your shell configuration:")
        print(f"   source ~/.zshrc")
    elif shell_info['shell'] == 'bash':
        config = os.path.basename(shell_info['config_file'])
        print(f"\n1. Reload your shell configuration:")
        print(f"   source ~/{config}")
    
    print("\nThanks for trying Vibe CLI! If you had any issues, please let us know on GitHub.")
    print("\n" + Colors.BOLD + "Goodbye! 👋" + Colors.RESET)

def main():
    """Main uninstallation function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Uninstall Vibe CLI")
    parser.add_argument('--force', action='store_true', help='Force uninstallation without confirmation')
    args = parser.parse_args()
    
    print("\n" + Colors.BOLD + "🚀 Uninstalling Vibe CLI..." + Colors.RESET + "\n")
    
    # Confirm uninstallation
    if not args.force:
        if not get_user_confirmation("Are you sure you want to uninstall Vibe CLI?"):
            print_warning("Uninstallation cancelled.")
            return 1
    
    # Detect shell
    print_step("Detecting shell environment")
    shell_info = get_shell_info()
    print_success(f"Detected shell: {shell_info['shell']}")
    print_success(f"Config file: {shell_info['config_file']}")
    
    # Remove installation directory
    print_step("Removing installation directory")
    remove_installation_dir()
    
    # Update shell configuration
    print_step("Updating shell configuration")
    update_shell_config(shell_info)
    
    # Print post-uninstallation message
    print_post_uninstall_message(shell_info)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

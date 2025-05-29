#!/usr/bin/env python3
"""
Vibe CLI Universal Installer

This script installs Vibe CLI on any platform (macOS, Linux, Windows).
It detects the user's shell, creates the necessary directories,
and updates shell configuration files appropriately.

Usage:
  python install.py [--force]

Options:
  --force    Overwrite existing installation if present
"""

import os
import sys
import shutil
import platform
import subprocess
import argparse
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
    """Print a step in the installation process."""
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

def create_installation_dir():
    """Create the installation directory structure."""
    install_dir = get_vibe_install_dir()
    
    try:
        os.makedirs(install_dir, exist_ok=True)
        print_success(f"Created directory: {install_dir}")
        return install_dir
    except Exception as e:
        print_error(f"Error creating directory: {e}")
        sys.exit(1)

def copy_scripts_to_install_dir(install_dir, force=False):
    """Copy the CLI scripts to the installation directory."""
    # Path to the CLI source directory
    cli_dir = os.path.join(parent_dir, 'cli')
    
    # Define target paths
    target_bin = os.path.join(install_dir, 'vibe')
    target_dir = os.path.dirname(install_dir)
    
    if os.path.exists(target_bin) and not force:
        print_warning(f"Vibe CLI is already installed at: {target_bin}")
        print_warning("Use --force to reinstall")
        return False
    
    try:
        # Copy the cli directory to the installation directory
        shutil.copytree(cli_dir, target_dir, dirs_exist_ok=True)
        
        # Make the vibe script executable
        if platform.system() != 'Windows':
            try:
                os.chmod(target_bin, 0o755)
            except Exception as e:
                print_warning(f"Could not make script executable: {e}")
        
        print_success(f"Copied Vibe CLI to: {target_dir}")
        return True
    except Exception as e:
        print_error(f"Error copying files: {e}")
        return False

def generate_config_file(force=False):
    """Generate the vibe.config.json file."""
    print_step("Generating configuration file")
    
    # Path to the installation directory
    install_dir = get_vibe_install_dir()
    config_dir = os.path.dirname(install_dir)
    config_file = os.path.join(config_dir, 'vibe.config.json')
    
    # Check if config already exists
    if os.path.exists(config_file) and not force:
        print_warning(f"Configuration file already exists at: {config_file}")
        print_warning("Use --force to regenerate")
        return True
    
    try:
        # Import or run the config generator
        generate_config_script = os.path.join(parent_dir, 'scripts', 'generate_config.py')
        
        if os.path.exists(generate_config_script):
            # Run the script as a subprocess
            subprocess.run([sys.executable, generate_config_script], check=True)
            print_success(f"Generated configuration file at: {config_file}")
            return True
        else:
            # Create a basic config file manually
            import json
            from datetime import datetime
            
            # Get system information
            system = platform.system()
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            # Try to get npm version
            npm_version = None
            try:
                result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
                npm_version = result.stdout.strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Try to get yarn version
            yarn_version = None
            try:
                result = subprocess.run(["yarn", "--version"], capture_output=True, text=True, check=True)
                yarn_version = result.stdout.strip()
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Basic config data
            config_data = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "system": {
                    "python": python_version,
                    "os": system,
                    "shell": shell_info['shell'] if 'shell' in shell_info else None
                },
                "package_managers": {
                    "npm": npm_version,
                    "yarn": yarn_version
                },
                "mcpServers": {}
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Write config file
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print_success(f"Generated basic configuration file at: {config_file}")
            return True
    except Exception as e:
        print_error(f"Error generating configuration file: {e}")
        return False

def update_shell_config(shell_info, force=False):
    """Add the Vibe CLI to the shell configuration file."""
    config_file = shell_info['config_file']
    install_dir = get_vibe_install_dir()
    
    # Create config directory if it doesn't exist
    config_dir = os.path.dirname(config_file)
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir, exist_ok=True)
            print_success(f"Created config directory: {config_dir}")
        except Exception as e:
            print_error(f"Error creating config directory: {e}")
            return False
    
    # Check if config file exists, create if not
    if not os.path.exists(config_file):
        try:
            with open(config_file, 'w') as f:
                f.write(f"# Shell configuration file created by Vibe CLI installer\n\n")
            print_success(f"Created new config file: {config_file}")
        except Exception as e:
            print_error(f"Error creating config file: {e}")
            return False
    
    # Check if vibe is already configured
    try:
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        if 'vibe-tools' in config_content and not force:
            print_warning(f"Vibe CLI is already configured in: {config_file}")
            print_warning("Use --force to update")
            return False
    except Exception as e:
        print_warning(f"Could not read config file: {e}")
    
    # Add appropriate configuration based on shell
    try:
        with open(config_file, 'a') as f:
            f.write("\n# Vibe CLI configuration - Added by installer\n")
            
            if shell_info['is_powershell']:
                # PowerShell function
                script_path = os.path.join(install_dir, 'vibe').replace('\\', '\\\\')
                f.write(f"""
function vibe {{
    python "{script_path}" $args
}}
                """)
            else:
                # Bash/Zsh alias and PATH
                f.write(f"""
# Add Vibe CLI to PATH
export PATH="$PATH:{install_dir}"

# Vibe CLI alias
alias vibe='python "{os.path.join(install_dir, 'vibe')}"'
                """)
        
        print_success(f"Updated shell config: {config_file}")
        return True
    except Exception as e:
        print_error(f"Error updating shell config: {e}")
        return False

def print_post_install_instructions(shell_info):
    """Print instructions for after installation."""
    print("\n" + Colors.GREEN + Colors.BOLD + "🎉 Vibe CLI installation complete!" + Colors.RESET)
    print("\nTo start using Vibe CLI, you need to:")
    
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
    
    print("\n2. Try using a Vibe CLI command:")
    print("   vibe status")
    print("   vibe help")
    
    print("\nFor more information:")
    print("   vibe help")
    
    print("\n" + Colors.BOLD + "Enjoy using Vibe CLI! {}" + Colors.RESET)

def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install Vibe CLI")
    parser.add_argument('--force', action='store_true', help='Force installation')
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}Vibe CLI Installer{Colors.RESET}")
    print(f"Platform: {platform.system()} {platform.release()}")
    
    # Get shell information
    shell_info = get_shell_info()
    print(f"Detected shell: {shell_info['shell']}")
    print(f"Config file: {shell_info['config_file']}")
    
    # Create installation directory
    install_dir = create_installation_dir()
    
    # Copy scripts to installation directory
    if copy_scripts_to_install_dir(install_dir, args.force):
        # Generate configuration file
        generate_config_file(args.force)
        
        # Update shell configuration
        update_shell_config(shell_info, args.force)
        
        # Print post-installation instructions
        print_post_install_instructions(shell_info)
        
        print(f"\n{Colors.GREEN}Vibe CLI installed successfully!{Colors.RESET}")
        return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main())

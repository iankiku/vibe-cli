"""
Shell detection utilities for Vibe CLI
"""

import os
import platform
import subprocess
from pathlib import Path

def get_shell_info():
    """
    Detect the user's shell and configuration file.
    
    Returns a dictionary with:
    - system: Operating system name
    - shell: Detected shell (zsh, bash, powershell)
    - config_file: Path to shell configuration file
    - is_powershell: Boolean indicating if PowerShell is detected
    """
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
        # Get the PowerShell profile path
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'echo $PROFILE'],
                capture_output=True, text=True, check=True
            )
            profile_path = result.stdout.strip()
            if profile_path:
                shell_info['config_file'] = profile_path
            else:
                # Default location if the command fails
                documents = os.path.join(str(Path.home()), 'Documents')
                shell_info['config_file'] = os.path.join(
                    documents, 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1'
                )
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fallback to default location
            documents = os.path.join(str(Path.home()), 'Documents')
            shell_info['config_file'] = os.path.join(
                documents, 'WindowsPowerShell', 'Microsoft.PowerShell_profile.ps1'
            )
    else:
        # Unix-like systems (macOS, Linux)
        shell_path = os.environ.get('SHELL', '')
        
        if 'zsh' in shell_path:
            shell_info['shell'] = 'zsh'
            shell_info['config_file'] = os.path.join(str(Path.home()), '.zshrc')
        elif 'bash' in shell_path:
            shell_info['shell'] = 'bash'
            # Check for .bash_profile first on macOS, then fall back to .bashrc
            if system == 'Darwin':
                bash_profile = os.path.join(str(Path.home()), '.bash_profile')
                if os.path.exists(bash_profile):
                    shell_info['config_file'] = bash_profile
                else:
                    shell_info['config_file'] = os.path.join(str(Path.home()), '.bashrc')
            else:
                shell_info['config_file'] = os.path.join(str(Path.home()), '.bashrc')
        else:
            # Default to bash if we can't determine the shell
            shell_info['shell'] = 'bash'
            shell_info['config_file'] = os.path.join(str(Path.home()), '.bashrc')
    
    return shell_info

def get_vibe_install_dir():
    """
    Get the installation directory for Vibe CLI.
    
    Returns:
        str: Path to the installation directory
    """
    home_dir = str(Path.home())
    install_dir = os.path.join(home_dir, '.vibe-tools', 'cli', 'bin')
    return install_dir

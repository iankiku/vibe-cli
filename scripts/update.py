#!/usr/bin/env python3
"""
Vibe CLI Update Script

This script checks for updates to Vibe CLI and updates the installation if a new version is available.
"""

import os
import sys
import json
import hashlib
import platform
import subprocess
import argparse
import urllib.request
from datetime import datetime
import shutil
from pathlib import Path

# ANSI colors for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    
    # Disable colors on Windows if not in a supported terminal
    if platform.system() == 'Windows' and not os.environ.get('TERM'):
        RESET = BOLD = BLUE = GREEN = YELLOW = RED = ''

# Configuration
INSTALL_DIR = os.path.expanduser("~/.vibe-tools")
CONFIG_DIR = os.path.join(INSTALL_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "vibe.config.json")
VERSION_FILE = os.path.join(INSTALL_DIR, "version.json")

# GitHub repository information - update with your actual repo
REPO_OWNER = "yourusername"  # Change to your GitHub username
REPO_NAME = "vibe-cli"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

def print_header(message):
    """Print a formatted header message."""
    print(f"\n{Colors.BOLD}🚀 {message}{Colors.RESET}\n")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.RESET}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def get_current_version():
    """Get the current installed version of Vibe CLI."""
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r') as f:
                version_data = json.load(f)
                return version_data.get('version', '0.0.0')
        except (json.JSONDecodeError, IOError):
            pass
    return '0.0.0'  # Default version if not found

def compare_versions(current, latest):
    """Compare version strings and return True if an update is available."""
    current_parts = list(map(int, current.split('.')))
    latest_parts = list(map(int, latest.split('.')))
    
    # Pad versions to ensure equal length
    while len(current_parts) < len(latest_parts):
        current_parts.append(0)
    while len(latest_parts) < len(current_parts):
        latest_parts.append(0)
    
    # Compare each part
    for i in range(len(current_parts)):
        if latest_parts[i] > current_parts[i]:
            return True
        elif latest_parts[i] < current_parts[i]:
            return False
    
    return False  # Versions are equal

def check_for_updates(force=False):
    """Check for updates to Vibe CLI."""
    print_header("Checking for Vibe CLI Updates")
    
    current_version = get_current_version()
    print_info(f"Current version: {current_version}")
    
    try:
        # Create a request with a user agent to avoid GitHub API limitations
        request = urllib.request.Request(
            GITHUB_API_URL,
            headers={'User-Agent': f'Vibe-CLI-Updater/{current_version}'}
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            latest_version = data['tag_name'].lstrip('v')
            
            update_available = compare_versions(current_version, latest_version)
            
            if update_available or force:
                print_info(f"New version available: {latest_version}")
                return True, latest_version, data['zipball_url']
            else:
                print_success(f"Vibe CLI is up to date ({current_version}).")
                return False, current_version, None
    except Exception as e:
        print_error(f"Error checking for updates: {str(e)}")
        return False, current_version, None

def download_update(download_url, target_file):
    """Download the update archive."""
    try:
        print_info(f"Downloading update...")
        
        # Create a request with a user agent
        request = urllib.request.Request(
            download_url,
            headers={'User-Agent': 'Vibe-CLI-Updater'}
        )
        
        with urllib.request.urlopen(request, timeout=30) as response, open(target_file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        return True
    except Exception as e:
        print_error(f"Error downloading update: {str(e)}")
        return False

def backup_config():
    """Backup the user's configuration."""
    if os.path.exists(CONFIG_FILE):
        backup_file = f"{CONFIG_FILE}.backup"
        try:
            shutil.copy2(CONFIG_FILE, backup_file)
            print_info(f"Configuration backed up to {backup_file}")
            return True
        except Exception as e:
            print_error(f"Error backing up configuration: {str(e)}")
    return False

def restore_config():
    """Restore the user's configuration from backup."""
    backup_file = f"{CONFIG_FILE}.backup"
    if os.path.exists(backup_file):
        try:
            shutil.copy2(backup_file, CONFIG_FILE)
            print_info("Configuration restored from backup")
            return True
        except Exception as e:
            print_error(f"Error restoring configuration: {str(e)}")
    return False

def update_vibe_cli(version, download_url):
    """Update Vibe CLI to the latest version."""
    print_header(f"Updating Vibe CLI to version {version}")
    
    # Create temporary directory for the update
    temp_dir = os.path.join(INSTALL_DIR, "update_temp")
    archive_file = os.path.join(temp_dir, "update.zip")
    
    os.makedirs(temp_dir, exist_ok=True)
    
    # Backup user configuration
    backup_config()
    
    try:
        # Download the update
        if not download_update(download_url, archive_file):
            return False
        
        print_info("Extracting update files...")
        
        # Extract the archive
        import zipfile
        with zipfile.ZipFile(archive_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted directory (it will be named something like owner-repo-commit)
        extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_dirs:
            print_error("No extracted directory found")
            return False
        
        extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
        
        # Copy files to installation directory
        print_info("Installing new version...")
        
        # Only update CLI files, keeping config intact
        cli_dir = os.path.join(INSTALL_DIR, "cli")
        if os.path.exists(cli_dir):
            shutil.rmtree(cli_dir)
        
        # Copy the new CLI files
        new_cli_dir = os.path.join(extracted_dir, "cli")
        if os.path.exists(new_cli_dir):
            shutil.copytree(new_cli_dir, cli_dir)
        else:
            print_error("CLI directory not found in update package")
            restore_config()
            return False
        
        # Update version file
        with open(VERSION_FILE, 'w') as f:
            json.dump({
                'version': version,
                'updated_at': datetime.now().isoformat()
            }, f)
        
        # Restore user configuration
        restore_config()
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print_success(f"Vibe CLI has been updated to version {version}!")
        return True
    
    except Exception as e:
        print_error(f"Error updating Vibe CLI: {str(e)}")
        # Attempt to restore configuration
        restore_config()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Vibe CLI Update Tool")
    parser.add_argument('--force', action='store_true', help='Force update even if current version is latest')
    parser.add_argument('--check-only', action='store_true', help='Only check for updates without installing')
    args = parser.parse_args()
    
    update_available, latest_version, download_url = check_for_updates(args.force)
    
    if update_available:
        if args.check_only:
            print_info("Update is available. Run 'vibe update' to install.")
            return 0
        
        user_input = input(f"Do you want to update to version {latest_version}? (y/n): ").lower()
        if user_input.startswith('y'):
            if update_vibe_cli(latest_version, download_url):
                return 0
            else:
                return 1
        else:
            print_info("Update cancelled.")
            return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

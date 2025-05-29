#!/usr/bin/env python3
"""
Generates the initial vibe.config.json file during installation.
This script is executed by the installation scripts to create a default configuration.
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the config utility
from cli.utils.config import (
    generate_default_config, 
    save_config, 
    CONFIG_FILE
)

def main():
    """Generate and save the initial configuration file."""
    print(f"Generating Vibe CLI configuration file at {CONFIG_FILE}...")
    
    # Generate default config
    config = generate_default_config()
    
    # Add installation timestamp
    config["created_at"] = datetime.now().isoformat()
    config["installed_by_script"] = True
    
    # Save the config
    if save_config(config):
        print(f"✅ Configuration file created successfully at {CONFIG_FILE}")
        print(f"System information and package manager versions have been detected.")
        return 0
    else:
        print(f"❌ Failed to create configuration file.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

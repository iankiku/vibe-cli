"""
npm command mappings for Vibe CLI

This module provides natural language mappings for npm commands.
All commands are prefixed with 'vibe' when used in the terminal.
Example: 'vibe add express' instead of 'npm install express'
"""

import shlex
import os
import subprocess

# Detect package manager (npm, yarn, pnpm)
def detect_package_manager():
    """Detect the package manager used in the current project."""
    # Check for yarn.lock
    if os.path.exists('yarn.lock'):
        return "yarn"
    # Check for pnpm-lock.yaml
    elif os.path.exists('pnpm-lock.yaml'):
        return "pnpm"
    # Default to npm
    return "npm"

# Package manager commands mapped to npm equivalents
PM_MAPPINGS = {
    "npm": {
        "install": "install",
        "add": "install",
        "remove": "uninstall",
        "update": "update",
        "global": "-g",
        "dev": "--save-dev",
        "run": "run"
    },
    "yarn": {
        "install": "add",
        "add": "add",
        "remove": "remove",
        "update": "upgrade",
        "global": "global",
        "dev": "--dev",
        "run": ""
    },
    "pnpm": {
        "install": "add",
        "add": "add",
        "remove": "remove",
        "update": "update",
        "global": "-g",
        "dev": "--save-dev",
        "run": "run"
    }
}

# Helper function to use the correct package manager
def pm_command(command, *args):
    pm = detect_package_manager()
    
    if command == "run" and pm == "yarn":
        # For yarn, we don't need the 'run' command for scripts
        return [pm] + list(args)
    elif command == "install" and not args:
        # For 'install' with no args, install all dependencies
        return [pm, command if pm == "npm" else ""]
    else:
        # Map the npm command to the equivalent for the detected package manager
        mapped_command = PM_MAPPINGS[pm].get(command, command)
        cmd_parts = [pm]
        if mapped_command:
            cmd_parts.append(mapped_command)
        cmd_parts.extend(args)
        return [part for part in cmd_parts if part]  # Remove empty strings

# npm command mappings
COMMANDS = {
    # Project initialization
    "init": ["npm", "init", "-y"],
    "start node": ["npm", "init", "-y"],
    "initialize node": ["npm", "init", "-y"],
    "create package": ["npm", "init", "-y"],
    "create node project": ["npm", "init", "-y"],
    "setup node": ["npm", "init", "-y"],
    
    # Package installation
    "add": lambda pkg: pm_command("add", pkg),
    "add package": lambda pkg: pm_command("add", pkg),
    "install": lambda pkg: pm_command("install", pkg) if pkg else pm_command("install"),
    "install package": lambda pkg: pm_command("add", pkg),
    "install all": lambda: pm_command("install"),
    "i": lambda pkg: pm_command("add", pkg),
    "add dev": lambda pkg: pm_command("add", pkg, PM_MAPPINGS[detect_package_manager()]["dev"]),
    "install dev": lambda pkg: pm_command("add", pkg, PM_MAPPINGS[detect_package_manager()]["dev"]),
    "add for development": lambda pkg: pm_command("add", pkg, PM_MAPPINGS[detect_package_manager()]["dev"]),
    "add global": lambda pkg: pm_command("add", PM_MAPPINGS[detect_package_manager()]["global"], pkg),
    "install global": lambda pkg: pm_command("add", PM_MAPPINGS[detect_package_manager()]["global"], pkg),
    "add globally": lambda pkg: pm_command("add", PM_MAPPINGS[detect_package_manager()]["global"], pkg),
    
    # Package removal
    "remove": lambda pkg: pm_command("remove", pkg),
    "remove package": lambda pkg: pm_command("remove", pkg),
    "uninstall": lambda pkg: pm_command("remove", pkg),
    "uninstall package": lambda pkg: pm_command("remove", pkg),
    "delete package": lambda pkg: pm_command("remove", pkg),
    
    # Running scripts
    "run": lambda script: pm_command("run", script),
    "execute": lambda script: pm_command("run", script),
    "start": lambda: pm_command("run", "start"),
    "dev": lambda: pm_command("run", "dev"),
    "develop": lambda: pm_command("run", "dev"),
    "development": lambda: pm_command("run", "dev"),
    "build": lambda: pm_command("run", "build"),
    "test": lambda: pm_command("run", "test"),
    "lint": lambda: pm_command("run", "lint"),
    "format": lambda: pm_command("run", "format"),
    "deploy": lambda: pm_command("run", "deploy"),
    "preview": lambda: pm_command("run", "preview"),
    "serve": lambda: pm_command("run", "serve"),
    
    # Package management
    "update": lambda pkg: pm_command("update", pkg) if pkg else pm_command("update"),
    "update packages": lambda: pm_command("update"),
    "upgrade": lambda pkg: pm_command("update", pkg) if pkg else pm_command("update"),
    "upgrade packages": lambda: pm_command("update"),
    "outdated": ["npm", "outdated"],
    "check updates": ["npm", "outdated"],
    "show outdated": ["npm", "outdated"],
    "list": ["npm", "list", "--depth=0"],
    "list packages": ["npm", "list", "--depth=0"],
    "show packages": ["npm", "list", "--depth=0"],
    "installed packages": ["npm", "list", "--depth=0"],
    
    # Security
    "audit": ["npm", "audit"],
    "check security": ["npm", "audit"],
    "security check": ["npm", "audit"],
    "fix vulnerabilities": ["npm", "audit", "fix"],
    "fix security": ["npm", "audit", "fix"],
    "audit fix": ["npm", "audit", "fix"],
    
    # Publishing
    "publish": ["npm", "publish"],
    "publish package": ["npm", "publish"],
    "release": ["npm", "publish"],
    "version": lambda type: ["npm", "version", type] if type else ["npm", "version"],
    "bump version": lambda type: ["npm", "version", type] if type else ["npm", "version", "patch"],
    "increment version": lambda type: ["npm", "version", type] if type else ["npm", "version", "patch"],
    
    # Info & configuration
    "info": lambda pkg: ["npm", "info", pkg],
    "about": lambda pkg: ["npm", "info", pkg],
    "details": lambda pkg: ["npm", "info", pkg],
    "package info": lambda pkg: ["npm", "info", pkg],
    "whoami": ["npm", "whoami"],
    "who am i": ["npm", "whoami"],
    "login": ["npm", "login"],
    "logout": ["npm", "logout"],
    "config": lambda key: ["npm", "config", "get", key] if key else ["npm", "config", "list"],
    "set config": lambda args: ["npm", "config", "set"] + shlex.split(args),
    
    # Cache management
    "clean": ["npm", "cache", "clean", "--force"],
    "clean cache": ["npm", "cache", "clean", "--force"],
    "clear cache": ["npm", "cache", "clean", "--force"],
    
    # Yarn specific
    "why": lambda pkg: ["yarn", "why", pkg] if detect_package_manager() == "yarn" else ["npm", "explain", pkg],
    
    # Workspace commands (monorepo support)
    "workspaces": lambda cmd: [detect_package_manager(), "workspaces", "run", cmd],
    "run all": lambda cmd: [detect_package_manager(), "workspaces", "run", cmd],
    "version": ["npm", "-v"],
}

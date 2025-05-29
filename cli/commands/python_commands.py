"""
Python command mappings for Vibe CLI

This module provides natural language mappings for Python commands.
All commands are prefixed with 'vibe' when used in the terminal.
Example: 'vibe run app.py' instead of 'python app.py'
"""

import shlex
import os
import sys
import subprocess

# Detect Python virtual environment
def detect_venv():
    """Detect if we're running in a virtual environment."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

# Get the current Python version
def get_python_version():
    """Get the current Python version."""
    return f"python{sys.version_info.major}.{sys.version_info.minor}"

# Detect the appropriate Python command
def get_python_command():
    """Get the appropriate Python command based on the environment."""
    # Check for python3 first
    try:
        subprocess.run(["python3", "--version"], capture_output=True, check=True)
        return "python3"
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fall back to python
        return "python"

# Get the appropriate pip command
def get_pip_command():
    """Get the appropriate pip command based on the environment."""
    # Check for pip3 first
    try:
        subprocess.run(["pip3", "--version"], capture_output=True, check=True)
        return "pip3"
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fall back to pip
        return "pip"

# Python command mappings
COMMANDS = {
    # Running Python scripts
    "run": lambda script: [get_python_command(), script],
    "run python": lambda script: [get_python_command(), script],
    "execute": lambda script: [get_python_command(), script],
    "python": lambda script: [get_python_command(), script],
    "start": lambda script: [get_python_command(), script],
    "run script": lambda script: [get_python_command(), script],
    "run with args": lambda args: [get_python_command()] + shlex.split(args),
    "debug": lambda script: [get_python_command(), "-m", "pdb", script],
    
    # Virtual environment management
    "create env": [get_python_command(), "-m", "venv", "venv"],
    "make env": [get_python_command(), "-m", "venv", "venv"],
    "setup env": [get_python_command(), "-m", "venv", "venv"],
    "new venv": [get_python_command(), "-m", "venv", "venv"],
    "create environment": [get_python_command(), "-m", "venv", "venv"],
    "create virtual environment": [get_python_command(), "-m", "venv", "venv"],
    "activate env": "source venv/bin/activate" if os.name != 'nt' else r'venv\Scripts\activate',
    "activate": "source venv/bin/activate" if os.name != 'nt' else r'venv\Scripts\activate',
    "activate venv": "source venv/bin/activate" if os.name != 'nt' else r'venv\Scripts\activate',
    "use env": "source venv/bin/activate" if os.name != 'nt' else r'venv\Scripts\activate',
    "deactivate": "deactivate",
    "deactivate env": "deactivate",
    "exit env": "deactivate",
    "leave env": "deactivate",
    
    # Package management
    "install": lambda pkg: [get_pip_command(), "install", pkg],
    "add": lambda pkg: [get_pip_command(), "install", pkg],
    "add package": lambda pkg: [get_pip_command(), "install", pkg],
    "install package": lambda pkg: [get_pip_command(), "install", pkg],
    "pip install": lambda pkg: [get_pip_command(), "install", pkg],
    "uninstall": lambda pkg: [get_pip_command(), "uninstall", pkg, "-y"],
    "remove": lambda pkg: [get_pip_command(), "uninstall", pkg, "-y"],
    "remove package": lambda pkg: [get_pip_command(), "uninstall", pkg, "-y"],
    "uninstall package": lambda pkg: [get_pip_command(), "uninstall", pkg, "-y"],
    "update": lambda pkg: [get_pip_command(), "install", "--upgrade", pkg],
    "upgrade": lambda pkg: [get_pip_command(), "install", "--upgrade", pkg],
    "update package": lambda pkg: [get_pip_command(), "install", "--upgrade", pkg],
    "upgrade package": lambda pkg: [get_pip_command(), "install", "--upgrade", pkg],
    
    # Requirements management
    "install requirements": [get_pip_command(), "install", "-r", "requirements.txt"],
    "install deps": [get_pip_command(), "install", "-r", "requirements.txt"],
    "install dependencies": [get_pip_command(), "install", "-r", "requirements.txt"],
    "save requirements": "pip freeze > requirements.txt",
    "freeze requirements": "pip freeze > requirements.txt",
    "generate requirements": "pip freeze > requirements.txt",
    "create requirements": "pip freeze > requirements.txt",
    "export requirements": "pip freeze > requirements.txt",
    
    # Development installation
    "install dev": [get_pip_command(), "install", "-e", "."],
    "install editable": [get_pip_command(), "install", "-e", "."],
    "develop": [get_pip_command(), "install", "-e", "."],
    "dev install": [get_pip_command(), "install", "-e", "."],
    "install self": [get_pip_command(), "install", "-e", "."],
    
    # Package information
    "list": [get_pip_command(), "list"],
    "list packages": [get_pip_command(), "list"],
    "show packages": [get_pip_command(), "list"],
    "installed packages": [get_pip_command(), "list"],
    "outdated": [get_pip_command(), "list", "--outdated"],
    "outdated packages": [get_pip_command(), "list", "--outdated"],
    "check updates": [get_pip_command(), "list", "--outdated"],
    "show package": lambda pkg: [get_pip_command(), "show", pkg],
    "info": lambda pkg: [get_pip_command(), "show", pkg],
    "about": lambda pkg: [get_pip_command(), "show", pkg],
    
    # Version information
    "pip version": [get_pip_command(), "--version"],
    "python version": [get_python_command(), "--version"],
    "version": [get_python_command(), "--version"],
    "check version": [get_python_command(), "--version"],
    
    # Upgrading pip
    "upgrade pip": [get_pip_command(), "install", "--upgrade", "pip"],
    "update pip": [get_pip_command(), "install", "--upgrade", "pip"],
    
    # Testing & linting
    "test": ["pytest"],
    "run tests": ["pytest"],
    "tests": ["pytest"],
    "unit tests": ["pytest"],
    "pytest": ["pytest"],
    "lint": ["flake8"],
    "check style": ["flake8"],
    "flake8": ["flake8"],
    "format": ["black", "."],
    "black": ["black", "."],
    "format code": ["black", "."],
    "mypy": ["mypy", "."],
    "type check": ["mypy", "."],
    "check types": ["mypy", "."],
    
    # Django commands
    "django start": [get_python_command(), "manage.py", "runserver"],
    "django run": [get_python_command(), "manage.py", "runserver"],
    "django server": [get_python_command(), "manage.py", "runserver"],
    "django shell": [get_python_command(), "manage.py", "shell"],
    "django migrate": [get_python_command(), "manage.py", "migrate"],
    "django migrations": [get_python_command(), "manage.py", "makemigrations"],
    "django make migrations": [get_python_command(), "manage.py", "makemigrations"],
    "django admin": lambda name: [get_python_command(), "manage.py", "createsuperuser", "--username", name] if name else [get_python_command(), "manage.py", "createsuperuser"],
    "django superuser": [get_python_command(), "manage.py", "createsuperuser"],
    
    # Flask commands
    "flask run": ["flask", "run"],
    "flask dev": ["flask", "run", "--debug"],
    "flask debug": ["flask", "run", "--debug"],
    "flask shell": ["flask", "shell"],
    
    # Package building & distribution
    "build": [get_python_command(), "-m", "build"],
    "build package": [get_python_command(), "-m", "build"],
    "package": [get_python_command(), "-m", "build"],
    "dist": [get_python_command(), "-m", "build"],
    "create dist": [get_python_command(), "-m", "build"],
    "publish": ["twine", "upload", "dist/*"],
    "upload package": ["twine", "upload", "dist/*"],
    "upload to pypi": ["twine", "upload", "dist/*"],
    "publish to pypi": ["twine", "upload", "dist/*"],
    "test publish": ["twine", "upload", "--repository-url", "https://test.pypi.org/legacy/", "dist/*"],
    "publish to test": ["twine", "upload", "--repository-url", "https://test.pypi.org/legacy/", "dist/*"],
    
    # IPython & Jupyter
    "notebook": ["jupyter", "notebook"],
    "jupyter": ["jupyter", "notebook"],
    "start notebook": ["jupyter", "notebook"],
    "jupyter lab": ["jupyter", "lab"],
    "lab": ["jupyter", "lab"],
    "ipython": ["ipython"],
    "shell": ["ipython"],
    "interactive": ["ipython"],
    
    # Documentation
    "docs": ["sphinx-build", "-b", "html", "docs/source", "docs/build/html"],
    "build docs": ["sphinx-build", "-b", "html", "docs/source", "docs/build/html"],
    "documentation": ["sphinx-build", "-b", "html", "docs/source", "docs/build/html"],
    "sphinx": ["sphinx-build", "-b", "html", "docs/source", "docs/build/html"],
    
    # Utils
    "pycodestyle": ["pycodestyle", "."],
    "autopep8": ["autopep8", "--in-place", "--aggressive", "--aggressive", "."],
    "coverage": ["coverage", "run", "-m", "pytest"],
    "coverage report": ["coverage", "report"],
}

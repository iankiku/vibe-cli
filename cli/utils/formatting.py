"""
Text formatting utilities for Vibe CLI output
"""

import sys
import os
from enum import Enum

# Check if we should use colors (disable for non-interactive terminals)
USE_COLORS = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

# ANSI color codes
class Color:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    UNDERLINE = '\033[4m'
    
    # Check for Windows terminal that doesn't support ANSI colors
    if os.name == 'nt' and not os.environ.get('TERM'):
        # Disable colors for Windows if not in a proper terminal
        RESET = BOLD = BLUE = GREEN = YELLOW = RED = CYAN = MAGENTA = UNDERLINE = ''

# Emoji icons for different message types
class Icon:
    SUCCESS = '✅ '
    ERROR = '❌ '
    INFO = 'ℹ️  '
    WARNING = '⚠️  '
    ACTION = '🔄 '
    HEADER = '🚀 '
    COMMAND = '$ '
    SECTION = '📂 '

def print_colored(text, color='', icon=''):
    """Print text with optional color and icon."""
    if USE_COLORS:
        print(f"{color}{icon}{text}{Color.RESET}")
    else:
        print(f"{icon}{text}")

def print_success(text):
    """Print a success message."""
    print_colored(text, Color.GREEN, Icon.SUCCESS)

def print_error(text):
    """Print an error message."""
    print_colored(text, Color.RED, Icon.ERROR)

def print_warning(text):
    """Print a warning message."""
    print_colored(text, Color.YELLOW, Icon.WARNING)

def print_info(text):
    """Print an informational message."""
    print_colored(text, Color.BLUE, Icon.INFO)

def print_action(text):
    """Print an action message."""
    print_colored(text, Color.CYAN, Icon.ACTION)

def print_header(text):
    """Print a header message."""
    print()
    print_colored(text, Color.BOLD + Color.MAGENTA, Icon.HEADER)
    print()

def print_section(text):
    """Print a section header."""
    print()
    print_colored(text, Color.BOLD + Color.BLUE, Icon.SECTION)

def print_command(command, description=None):
    """Print a command with optional description."""
    if description:
        print(f"  {Icon.COMMAND}{Color.BOLD}{command}{Color.RESET} - {description}")
    else:
        print(f"  {Icon.COMMAND}{Color.BOLD}{command}{Color.RESET}")

"""
Vibe CLI Logger Module

A consistent logging interface for the Vibe CLI application.
"""
import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from enum import IntEnum

# Define LogLevel enum for type safety
class LogLevel(IntEnum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    TRACE = 5

# Log levels
CRITICAL = logging.CRITICAL  # 50
ERROR = logging.ERROR        # 40
WARNING = logging.WARNING    # 30
INFO = logging.INFO          # 20
DEBUG = logging.DEBUG        # 10
TRACE = 5                    # Custom level below DEBUG

# Configure custom TRACE level
logging.addLevelName(TRACE, "TRACE")

# ANSI color codes for terminal output
COLORS = {
    'reset': '\033[0m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bold': '\033[1m'
}

# Define log level colors
LEVEL_COLORS = {
    CRITICAL: COLORS['red'] + COLORS['bold'],
    ERROR: COLORS['red'],
    WARNING: COLORS['yellow'],
    INFO: COLORS['green'],
    DEBUG: COLORS['blue'],
    TRACE: COLORS['magenta']
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages in terminal output"""
    
    def format(self, record):
        levelno = record.levelno
        levelname = record.levelname
        
        # Add color to level name if terminal supports it
        if sys.stdout.isatty():  # Only use colors for terminal output
            color = LEVEL_COLORS.get(levelno, COLORS['reset'])
            record.levelname = f"{color}{levelname}{COLORS['reset']}"
        
        return super().format(record)

class VibeLogger:
    """Vibe CLI Logger class"""
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance exists"""
        if cls._instance is None:
            cls._instance = super(VibeLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Set up the logging configuration"""
        # Get log level from environment or use INFO as default
        log_level_name = os.environ.get('VIBE_LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_name, INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        
        # Create formatter with timestamp, level, and message
        console_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = ColoredFormatter(console_format, date_format)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger('vibe')
        root_logger.setLevel(log_level)
        
        # Clear any existing handlers to avoid duplicate logs
        if root_logger.handlers:
            root_logger.handlers.clear()
        
        root_logger.addHandler(console_handler)
        
        # Create log directory for file logging if enabled
        if os.environ.get('VIBE_LOG_TO_FILE', 'false').lower() == 'true':
            self._setup_file_logging(root_logger, log_level)
    
    def _setup_file_logging(self, root_logger, log_level):
        """Set up file logging if enabled"""
        # Determine log directory
        home_dir = os.path.expanduser('~')
        log_dir = os.path.join(home_dir, '.vibe-cloud', 'logs')
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'vibe_cli_{timestamp}.log')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter for file logs
        file_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        
        # Add file handler to root logger
        root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str = 'vibe') -> logging.Logger:
        """Get a logger instance with the specified name"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            
            # Add trace method to logger
            def trace(msg, *args, **kwargs):
                if logger.isEnabledFor(TRACE):
                    logger._log(TRACE, msg, args, **kwargs)
            logger.trace = trace
            
            self._loggers[name] = logger
        
        return self._loggers[name]

# Convenience functions to get a logger and log messages

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with the specified name"""
    logger_name = name if name else 'vibe'
    return VibeLogger().get_logger(logger_name)

# Global logger instance for direct imports
logger = get_logger()

# Export convenience functions that match the global log levels
def critical(msg, *args, **kwargs):
    """Log a critical message"""
    logger.critical(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    """Log an error message"""
    logger.error(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    """Log a warning message"""
    logger.warning(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    """Log an info message"""
    logger.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    """Log a debug message"""
    logger.debug(msg, *args, **kwargs)

def trace(msg, *args, **kwargs):
    """Log a trace message (more detailed than debug)"""
    logger.trace(msg, *args, **kwargs)

# Set logging level from environment variable
def set_level(level):
    """Set the logging level for the root logger"""
    root_logger = logging.getLogger('vibe')
    root_logger.setLevel(level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level)

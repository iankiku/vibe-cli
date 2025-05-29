#!/usr/bin/env python3
"""
Telemetry module for Vibe CLI

Handles anonymous usage data collection to improve the CLI experience.
User privacy is respected with opt-in telemetry and anonymized data.
"""

import os
import json
import uuid
import platform
import hashlib
import requests
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/.vibe-tools/logs/telemetry.log')
)
logger = logging.getLogger('vibe_telemetry')

# Configuration
INSTALL_DIR = os.path.expanduser("~/.vibe-tools")
CONFIG_DIR = os.path.join(INSTALL_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "vibe.config.json")
TELEMETRY_FILE = os.path.join(CONFIG_DIR, "telemetry.json")
TELEMETRY_ENDPOINT = "https://api.example.com/vibe-cli/telemetry"  # Replace with actual endpoint

class Telemetry:
    """Handles telemetry data collection and reporting."""
    
    def __init__(self):
        """Initialize telemetry module."""
        self.enabled = False
        self.user_id = None
        self.session_id = str(uuid.uuid4())
        self.events = []
        self.load_config()
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.expanduser('~/.vibe-tools/logs'), exist_ok=True)
    
    def load_config(self):
        """Load telemetry configuration."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
                    # Check if telemetry is enabled
                    telemetry_config = config.get('telemetry', {})
                    self.enabled = telemetry_config.get('enabled', False)
                    
                    # Get or generate anonymous user ID
                    self.user_id = telemetry_config.get('user_id')
                    if not self.user_id and self.enabled:
                        self.user_id = self._generate_user_id()
                        self._save_user_id()
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading config: {str(e)}")
    
    def _generate_user_id(self):
        """Generate an anonymous user ID."""
        # Create a hash from system info for an anonymous ID
        system_info = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:16]
    
    def _save_user_id(self):
        """Save the user ID to the config file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                # Update telemetry configuration
                if 'telemetry' not in config:
                    config['telemetry'] = {}
                
                config['telemetry']['user_id'] = self.user_id
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error saving user ID: {str(e)}")
    
    def track(self, event_name, properties=None):
        """Track an event with optional properties."""
        if not self.enabled:
            return
        
        event = {
            'event': event_name,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'properties': properties or {}
        }
        
        self.events.append(event)
        self._save_event(event)
        
        # Send events immediately if appropriate
        if event_name in ['command_executed', 'error', 'update_check']:
            self.send()
    
    def _save_event(self, event):
        """Save an event to the telemetry file."""
        try:
            events = []
            if os.path.exists(TELEMETRY_FILE):
                with open(TELEMETRY_FILE, 'r') as f:
                    try:
                        events = json.load(f)
                    except json.JSONDecodeError:
                        events = []
            
            events.append(event)
            
            # Only keep the most recent 100 events to avoid file size issues
            if len(events) > 100:
                events = events[-100:]
            
            with open(TELEMETRY_FILE, 'w') as f:
                json.dump(events, f)
        except IOError as e:
            logger.error(f"Error saving event: {str(e)}")
    
    def send(self):
        """Send telemetry data to the server."""
        if not self.enabled or not self.events:
            return
        
        # Load any previously saved events
        all_events = []
        if os.path.exists(TELEMETRY_FILE):
            try:
                with open(TELEMETRY_FILE, 'r') as f:
                    all_events = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading telemetry events: {str(e)}")
                all_events = []
        
        # Combine with current session events
        all_events.extend(self.events)
        self.events = []
        
        if not all_events:
            return
        
        # Prepare payload
        payload = {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'app_version': self._get_app_version(),
            'os_info': self._get_os_info(),
            'events': all_events
        }
        
        # Send data
        try:
            response = requests.post(
                TELEMETRY_ENDPOINT, 
                json=payload,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                # Clear sent events
                os.remove(TELEMETRY_FILE)
                logger.info(f"Telemetry data sent successfully: {len(all_events)} events")
            else:
                logger.error(f"Error sending telemetry data: {response.status_code}")
        except Exception as e:
            logger.error(f"Exception sending telemetry data: {str(e)}")
    
    def _get_app_version(self):
        """Get the current app version."""
        version_file = os.path.join(INSTALL_DIR, "version.json")
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                    return version_data.get('version', '0.0.0')
            except (json.JSONDecodeError, IOError):
                pass
        return '0.0.0'
    
    def _get_os_info(self):
        """Get anonymized OS information."""
        return {
            'os': platform.system(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'python_version': platform.python_version()
        }
    
    def enable(self):
        """Enable telemetry."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                # Update telemetry configuration
                if 'telemetry' not in config:
                    config['telemetry'] = {}
                
                config['telemetry']['enabled'] = True
                
                # Generate user ID if not present
                if not config['telemetry'].get('user_id'):
                    config['telemetry']['user_id'] = self._generate_user_id()
                    self.user_id = config['telemetry']['user_id']
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.enabled = True
                logger.info("Telemetry enabled")
                return True
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error enabling telemetry: {str(e)}")
        
        return False
    
    def disable(self):
        """Disable telemetry."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                # Update telemetry configuration
                if 'telemetry' not in config:
                    config['telemetry'] = {}
                
                config['telemetry']['enabled'] = False
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.enabled = False
                logger.info("Telemetry disabled")
                
                # Clear any stored events
                if os.path.exists(TELEMETRY_FILE):
                    os.remove(TELEMETRY_FILE)
                
                return True
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error disabling telemetry: {str(e)}")
        
        return False
    
    def status(self):
        """Get telemetry status information."""
        return {
            'enabled': self.enabled,
            'user_id': self.user_id if self.enabled else None,
            'events_queued': len(self.events) + self._count_stored_events()
        }
    
    def _count_stored_events(self):
        """Count the number of stored events."""
        if os.path.exists(TELEMETRY_FILE):
            try:
                with open(TELEMETRY_FILE, 'r') as f:
                    events = json.load(f)
                    return len(events)
            except (json.JSONDecodeError, IOError):
                pass
        return 0

# Singleton instance
_instance = None

def get_telemetry():
    """Get the telemetry instance."""
    global _instance
    if _instance is None:
        _instance = Telemetry()
    return _instance

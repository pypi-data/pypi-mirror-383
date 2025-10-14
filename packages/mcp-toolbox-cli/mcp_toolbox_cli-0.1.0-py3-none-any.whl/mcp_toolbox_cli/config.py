"""Configuration management for MCP ToolBox CLI"""

import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Manage CLI configuration"""

    def __init__(self):
        self.config_dir = Path.home() / ".mcp-toolbox"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self._data.get(key, default)

    def set(self, key: str, value):
        """Set a configuration value"""
        self._data[key] = value
        self._save()

    @property
    def api_url(self) -> str:
        """Get the API URL"""
        # Check environment variables first, then config file, then default
        return (os.getenv('MCP_TOOLBOX_API_URL') or 
                os.getenv('TOOLBOX_API_URL') or 
                self.get('api_url', 'https://muldercw.com'))

    @api_url.setter
    def api_url(self, value: str):
        """Set the API URL"""
        self.set('api_url', value)

    @property
    def api_token(self) -> Optional[str]:
        """Get the API token"""
        # Check environment variables first, then config file
        return (os.getenv('MCP_TOOLBOX_API_TOKEN') or 
                os.getenv('TOOLBOX_API_TOKEN') or 
                self.get('api_token'))

    @api_token.setter
    def api_token(self, value: str):
        """Set the API token"""
        self.set('api_token', value)

    def clear(self):
        """Clear all configuration"""
        self._data = {}
        self._save()
    
    def get_effective_api_url(self) -> str:
        """Get the effective API URL with source information"""
        if os.getenv('MCP_TOOLBOX_API_URL'):
            return os.getenv('MCP_TOOLBOX_API_URL'), 'MCP_TOOLBOX_API_URL environment variable'
        elif os.getenv('TOOLBOX_API_URL'):
            return os.getenv('TOOLBOX_API_URL'), 'TOOLBOX_API_URL environment variable'
        elif self.get('api_url'):
            return self.get('api_url'), 'configuration file'
        else:
            return 'https://muldercw.com', 'default value'
    
    def get_effective_api_token(self) -> tuple[Optional[str], str]:
        """Get the effective API token with source information"""
        if os.getenv('MCP_TOOLBOX_API_TOKEN'):
            return os.getenv('MCP_TOOLBOX_API_TOKEN'), 'MCP_TOOLBOX_API_TOKEN environment variable'
        elif os.getenv('TOOLBOX_API_TOKEN'):
            return os.getenv('TOOLBOX_API_TOKEN'), 'TOOLBOX_API_TOKEN environment variable'
        elif self.get('api_token'):
            return self.get('api_token'), 'configuration file'
        else:
            return None, 'not set'


config = Config()

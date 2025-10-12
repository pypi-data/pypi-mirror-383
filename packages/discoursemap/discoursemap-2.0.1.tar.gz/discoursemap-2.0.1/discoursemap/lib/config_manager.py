#!/usr/bin/env python3
"""Configuration Manager Module

Manages application configuration from YAML files.
"""

import os
import yaml
from typing import Optional, Dict, Any

class ScanConfig:
    """Scan configuration object"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        config_dict = config_dict or {}
        self.threads = config_dict.get('threads', 10)
        self.timeout = config_dict.get('timeout', 10)
        self.delay = config_dict.get('delay', 0)
        self.verify_ssl = config_dict.get('verify_ssl', True)
        self.max_retries = config_dict.get('max_retries', 3)

class ConfigManager:
    """Configuration manager for the scanner"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to YAML configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.scan_config = ScanConfig(self.config.get('scan', {}))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file or not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

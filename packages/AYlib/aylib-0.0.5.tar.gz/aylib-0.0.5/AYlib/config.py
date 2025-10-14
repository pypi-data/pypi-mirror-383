# -*- coding: utf-8 -*-
"""
Configuration module for AYlib
Provides default configurations and settings management.
"""
__doc__ = 'AYlib configuration module'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import os
import json
import logging
from typing import Dict, Any, Optional

class AYConfig:
    """Configuration management class for AYlib modules."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (JSON format)
        """
        self.config_file = config_file
        self._config = self._load_default_config()
        
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            'database': {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '',
                'database': 'test',
                'charset': 'utf8mb4',
                'autocommit': True
            },
            'socket': {
                'default_host': '127.0.0.1',
                'default_port': 80,
                'timeout': 10,
                'buffer_size': 1024,
                'req_type': 'tcp',
                'req_method': 'queue'
            },
            'serial': {
                'default_port': 'COM1',  # Windows default, will be overridden by system detection
                'default_baudrate': 9600,
                'timeout': 1,
                'send_delay': 0,
                'rx_tx_model': [1, 1]  # [TX, RX] - both enabled by default
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                'file_logging': False,
                'log_file': 'aylib.log'
            }
        }
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self._merge_config(self._config, file_config)
        except Exception as e:
            logging.warning(f"Failed to load config file {config_file}: {e}")
    
    def _merge_config(self, base: Dict, override: Dict) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key (optional, returns entire section if None)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            section_config = self._config.get(section, {})
            if key is None:
                return section_config
            return section_config.get(key, default)
        except Exception:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key
            value: Value to set
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def save(self, config_file: str = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_file: Path to save configuration (uses instance file if None)
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = config_file or self.config_file
        if not file_path:
            return False
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Failed to save config to {file_path}: {e}")
            return False

# Global configuration instance
_global_config = AYConfig()

def get_config(section: str, key: str = None, default: Any = None) -> Any:
    """
    Get configuration value from global config.
    
    Args:
        section: Configuration section name
        key: Configuration key (optional)
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    return _global_config.get(section, key, default)

def set_config(section: str, key: str, value: Any) -> None:
    """
    Set configuration value in global config.
    
    Args:
        section: Configuration section name
        key: Configuration key
        value: Value to set
    """
    _global_config.set(section, key, value)

def load_config_file(config_file: str) -> bool:
    """
    Load configuration from file into global config.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    global _global_config
    try:
        _global_config = AYConfig(config_file)
        return True
    except Exception as e:
        logging.error(f"Failed to load global config from {config_file}: {e}")
        return False

# Auto-detect serial port based on system
def _detect_default_serial_port():
    """Auto-detect default serial port based on operating system."""
    import platform
    system = platform.system().lower()
    
    if system == 'windows':
        return 'COM1'
    elif system == 'darwin':  # macOS
        return '/dev/tty.usbserial'
    else:  # Linux and others
        return '/dev/ttyUSB0'

# Update default serial port based on system
_global_config.set('serial', 'default_port', _detect_default_serial_port())

if __name__ == '__main__':
    # Example usage
    config = AYConfig()
    
    # Get database configuration
    db_config = config.get('database')
    print("Database config:", db_config)
    
    # Get specific value with default
    host = config.get('database', 'host', 'localhost')
    print("Database host:", host)
    
    # Set new value
    config.set('database', 'host', '192.168.1.100')
    
    # Save to file
    config.save('aylib_config.json')
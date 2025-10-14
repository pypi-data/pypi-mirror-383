# -*- coding: utf-8 -*-
"""
AYlib - A comprehensive Python library for socket, serial, and UI operations.
Improved version with better error handling, resource management, and modern Python practices.
"""
__doc__ = 'AYlib module - Improved version with modern Python practices'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

# Import core modules
from . import AYsocket
from . import AYserial
from . import AYui
from . import AYsql
from . import config

# Import improved modules (recommended)
try:
    from .AYserial_improved import AYSerial, AYSerialConfig
    from .AYsql import AYDatabase
    from .config import AYConfig, get_config, set_config, load_config_file
    
    # Make improved classes available at package level
    __all__ = [
        # Original modules (backward compatibility)
        'AYsocket', 'AYserial', 'AYui', 'AYsql', 'config',
        # Improved classes (recommended)
        'AYSerial', 'AYSerialConfig', 'AYDatabase', 'AYConfig',
        # Utility functions
        'get_config', 'set_config', 'load_config_file'
    ]
    
except ImportError as e:
    # Fallback to original modules if improved versions fail
    import warnings
    warnings.warn(f"Failed to import improved modules: {e}. Using original modules.")
    
    __all__ = ['AYsocket', 'AYserial', 'AYui', 'AYsql', 'config']

# Version information
VERSION_INFO = {
    'major': 0,
    'minor': 0,
    'patch': 4,
    'release': 'stable'
}

def get_version():
    """Get formatted version string."""
    return f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"

def get_version_info():
    """Get detailed version information."""
    return VERSION_INFO.copy()
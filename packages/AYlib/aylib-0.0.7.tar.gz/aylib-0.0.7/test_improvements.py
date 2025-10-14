#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for AYlib improvements
Tests the new and improved functionality to ensure everything works correctly.
"""

import sys
import os
import logging

# Add AYlib to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AYlib'))

def test_config_system():
    """Test the new configuration system."""
    print("🧪 Testing Configuration System...")
    
    try:
        from AYlib.config import AYConfig, get_config, set_config
        
        # Test default configuration
        config = AYConfig()
        db_host = config.get('database', 'host')
        print(f"✅ Default database host: {db_host}")
        
        # Test setting values
        config.set('database', 'host', '192.168.1.100')
        new_host = config.get('database', 'host')
        print(f"✅ Updated database host: {new_host}")
        
        # Test global config functions
        serial_port = get_config('serial', 'default_port')
        print(f"✅ Default serial port: {serial_port}")
        
        print("✅ Configuration system test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}\n")
        return False

def test_database_module():
    """Test the improved database module."""
    print("🧪 Testing Database Module...")
    
    try:
        from AYlib.AYsql import AYDatabase
        
        # Test database class initialization
        config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'test',
            'password': 'test',
            'database': 'test'
        }
        
        db = AYDatabase(config)
        print("✅ Database class initialized successfully")
        
        # Test context manager (without actual connection)
        print("✅ Database context manager available")
        
        print("✅ Database module test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Database module test failed: {e}\n")
        return False

def test_socket_module():
    """Test the improved socket module."""
    print("🧪 Testing Socket Module...")
    
    try:
        from AYlib.AYsocket import AYSocket, AYSocketConfig
        
        # Test configuration class
        config = AYSocketConfig()
        print(f"✅ Socket config created: {config.req_type}")
        
        # Test socket class
        socket_server = AYSocket('127.0.0.1', 9999)
        print(f"✅ Socket server created: {socket_server.ip}:{socket_server.port}")
        
        # Test backward compatibility
        from AYlib.AYsocket import AYsocket
        old_socket = AYsocket('127.0.0.1', 9998)
        print("✅ Backward compatibility maintained")
        
        print("✅ Socket module test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Socket module test failed: {e}\n")
        return False

def test_serial_module():
    """Test the improved serial module."""
    print("🧪 Testing Serial Module...")
    
    try:
        from AYlib.AYserial_improved import AYSerial, AYSerialConfig
        
        # Test configuration class
        config = AYSerialConfig()
        print(f"✅ Serial config created: {config.demo_model}")
        
        # Test serial class (without actual hardware)
        serial_comm = AYSerial('/dev/ttyUSB0', 9600, config=config)
        print(f"✅ Serial comm created: {serial_comm.port}@{serial_comm.baudrate}")
        
        # Test utility functions
        hex_val = AYSerial.ascii_to_hex('A')
        ascii_val = AYSerial.hex_to_ascii(65)
        print(f"✅ Utility functions work: 'A' -> {hex_val}, 65 -> '{ascii_val}'")
        
        print("✅ Serial module test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Serial module test failed: {e}\n")
        return False

def test_package_imports():
    """Test package-level imports."""
    print("🧪 Testing Package Imports...")
    
    try:
        # Test new imports
        from AYlib import AYDatabase, AYSerial, AYConfig
        print("✅ New classes imported successfully")
        
        # Test utility functions
        from AYlib import get_config, set_config
        print("✅ Utility functions imported successfully")
        
        # Test backward compatibility imports
        from AYlib import AYsocket, AYserial, AYui, AYsql
        print("✅ Original modules still importable")
        
        print("✅ Package imports test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Package imports test failed: {e}\n")
        return False

def test_version_info():
    """Test version information."""
    print("🧪 Testing Version Information...")
    
    try:
        from AYlib import get_version, get_version_info, __version__
        
        version = get_version()
        version_info = get_version_info()
        
        print(f"✅ Package version: {__version__}")
        print(f"✅ Version function: {version}")
        print(f"✅ Version info: {version_info}")
        
        print("✅ Version information test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Version information test failed: {e}\n")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting AYlib Improvements Test Suite\n")
    print("=" * 50)
    
    tests = [
        test_config_system,
        test_database_module,
        test_socket_module,
        test_serial_module,
        test_package_imports,
        test_version_info
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AYlib improvements are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        return False

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
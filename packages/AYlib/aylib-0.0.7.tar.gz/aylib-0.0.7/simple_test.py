#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for basic AYlib functionality without external dependencies
"""

import sys
import os

# Add AYlib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AYlib'))

def test_basic_imports():
    """Test basic imports without external dependencies."""
    print("🧪 Testing Basic Imports...")
    
    try:
        # Test config system
        from AYlib.config import AYConfig, get_config, set_config
        config = AYConfig()
        print("✅ Config system imported successfully")
        
        # Test socket system
        from AYlib.AYsocket import AYSocket, AYSocketConfig, AYsocket
        socket_config = AYSocketConfig()
        socket_server = AYSocket('127.0.0.1', 9999)
        old_socket = AYsocket('127.0.0.1', 9998)
        print("✅ Socket system imported successfully")
        
        # Test database (without actual connection)
        from AYlib.AYsql import AYDatabase
        print("✅ Database system imported successfully")
        
        # Test package imports
        from AYlib import __version__, get_version
        print(f"✅ Package version: {__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_config_functionality():
    """Test configuration functionality."""
    print("🧪 Testing Configuration Functionality...")
    
    try:
        from AYlib.config import AYConfig
        
        config = AYConfig()
        
        # Test getting values
        db_host = config.get('database', 'host')
        print(f"✅ Database host: {db_host}")
        
        # Test setting values
        config.set('database', 'host', '192.168.1.100')
        new_host = config.get('database', 'host')
        print(f"✅ Updated host: {new_host}")
        
        # Test global functions
        from AYlib.config import get_config, set_config
        serial_port = get_config('serial', 'default_port')
        print(f"✅ Serial port: {serial_port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config functionality test failed: {e}")
        return False

def test_socket_functionality():
    """Test socket functionality."""
    print("🧪 Testing Socket Functionality...")
    
    try:
        from AYlib.AYsocket import AYSocket, AYsocket
        
        # Test new class
        new_socket = AYSocket('127.0.0.1', 8888)
        print(f"✅ New socket: {new_socket.ip}:{new_socket.port}")
        
        # Test backward compatibility
        old_socket = AYsocket('127.0.0.1', 8889)
        print(f"✅ Old socket (backward compatible): {old_socket.ip}:{old_socket.port}")
        
        # Test method availability
        assert hasattr(old_socket, 'AY_OpenTCPServer')
        assert hasattr(old_socket, 'start_tcp_server')
        print("✅ Both old and new methods available")
        
        return True
        
    except Exception as e:
        print(f"❌ Socket functionality test failed: {e}")
        return False

def main():
    """Run simple tests."""
    print("🚀 Starting Simple AYlib Test\n")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_config_functionality,
        test_socket_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
# Welcome to AYlib

[English](https://github.com/AaronYang233/AYlib/blob/main/README.md) | [中文](https://github.com/AaronYang233/AYlib/blob/main/README-CN.md)

<div align="center">

[![GitHub release](https://img.shields.io/badge/release-v0.0.7-blue)](https://github.com/AaronYang233/AYlib/releases)
[![GitHub stars](https://img.shields.io/badge/stars-500-blue)](https://github.com/AaronYang233/AYlib/stargazers)
[![GitHub forks](https://img.shields.io/badge/forks-0-blue)](https://github.com/AaronYang233/AYlib/network)
[![GitHub issues](https://img.shields.io/badge/issuse-1%20open-yellow)](https://github.com/AaronYang233/AYlib/issues)
[![GitHub contributors](https://img.shields.io/badge/contributors-2-yellow)](https://github.com/AaronYang233/AYlib/graphs/contributors)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-GNU--3.0-green)](./LICENSE)
[![PyPI](https://img.shields.io/badge/pip%20install-AYlib-blue)](https://pypi.org/project/AYlib/)
[![](https://img.shields.io/badge/about-aaronyang.cc-red)](https://bbs.aaronyang.cc)

</div>

# AYlib - Python Utility Library

AYlib is a comprehensive Python utility library that provides simplified interfaces for network communication, serial communication, database operations, and data visualization.

## 🎯 Core Features

### 🔌 Network Communication (AYsocket)
- **TCP/UDP Server & Client**: Multi-threaded server implementation with improved error handling
- **HEX & String Data Transmission**: Support for both text and hexadecimal data formats
- **Message Queue Processing**: Asynchronous message handling with queue support
- **Custom Data Processing**: User-defined processor functions for real data manipulation
- **Data Access Methods**: Direct access to queued data for further processing
- **Backward Compatibility**: Legacy `AYsocket` class with original method names
- **Enhanced Logging**: Clean log output without unnecessary line breaks

### 🔧 Serial Communication (AYserial)
- **Serial Port Management**: Robust serial communication with resource management
- **HEX/ASCII Conversion**: Built-in utilities for data format conversion
- **CRC Checksum Calculation**: Support for CRC16-Modbus and other algorithms
- **Threaded Communication**: Background thread support for continuous data exchange
- **Improved Version**: `AYserial_improved.py` with modern Python practices

### 💾 Database Operations (AYsql)
- **MySQL Connectivity**: Database operations with connection pooling
- **Parameterized Queries**: Secure SQL execution with parameter binding
- **Transaction Support**: ACID-compliant transaction management
- **Error Handling**: Comprehensive error handling and resource cleanup

### 📊 Data Visualization (AYui)
- **Interactive Plotting**: Real-time data visualization with matplotlib
- **Custom UI Components**: Extensible UI framework with event handling
- **Multi-language Support**: Chinese font support for better localization
- **Data Management**: Flexible data structures for various visualization needs

### ⚙️ Configuration Management (config)
- **Centralized Configuration**: Unified configuration management system
- **JSON File Support**: External configuration file support
- **Global Access**: Easy access to configuration values across modules
- **Type Safety**: Type-safe configuration access with fallback values

## 🚀 Quick Start

### Installation

#### Option 1: Install via pip (Recommended)
```bash
pip install AYlib
```

#### Option 2: Install from source
```bash
# Install required dependencies
pip install pyserial matplotlib numpy PyMySQL

# Clone and install from source
git clone https://github.com/AaronYang233/AYlib.git
cd AYlib
python setup.py install
```

### Basic Usage Examples

#### TCP Server & Client Communication
```python
from AYlib.AYsocket import AYsocket

# Start TCP server
server = AYsocket('0.0.0.0', 9988)
server.AY_OpenTCPServer()  # Runs in background thread

# Send test messages
client = AYsocket('127.0.0.1', 9988)
client.AY_TCP_SendString("Hello AYlib!")
client.AY_TCP_SendString("测试中文消息")
```

#### Custom Data Processing Example
```python
from AYlib.AYsocket import AYsocket

# Custom data processor function
def my_data_processor(data, data_type):
    """Process incoming data with custom logic"""
    print(f"Processing {data_type} data: {data}")
    
    # Example: Parse JSON, validate data, call external APIs
    if isinstance(data, str):
        # Business logic here
        processed = f"Processed: {data.upper()}"
        # You can: store to database, send to other services, etc.
        return processed
    return data

# Start server with custom processor
server = AYsocket('127.0.0.1', 9988)
server.set_custom_processor(my_data_processor)
server.AY_OpenTCPServer()

# Monitor queued data for further processing
import signal
import sys

# Graceful shutdown handler
def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Safe monitoring with exit condition
max_iterations = 100  # Limit iterations for safety
for i in range(max_iterations):
    if server.has_queued_data():
        data = server.get_queued_data()
        print(f"Retrieved from queue: {data}")
        # Perform additional operations on the data
    
    # Performance monitoring
    stats = server.get_connection_stats()
    print(f"Connection stats: {stats}")
    
    if not server.is_connection_available():
        print("Server is at capacity, cannot accept new connections")
    
    time.sleep(1)

print("Monitoring completed safely")
```

#### Performance Monitoring Example
```python
from AYlib.AYsocket import AYsocket
import asyncio

# Performance monitoring example
server = AYsocket('127.0.0.1', 9988)
server.AY_OpenTCPServer()

async def monitor_performance(max_iterations=20):
    """Monitor server performance asynchronously with safety limits"""
    for i in range(max_iterations):
        # Get connection statistics
        conn_stats = server.get_connection_stats()
        print(f"Active connections: {conn_stats['current_connections']}")
        print(f"Total processed: {conn_stats['processed_messages']}")
        
        # Check connection availability
        if server.is_connection_available():
            print("Server can accept new connections")
        else:
            print("Server at capacity, waiting for connections to free up")
        
        # Asynchronous client example
        client = AYsocket('127.0.0.1', 9988)
        success, response = await client.async_send_tcp_string("Test message")
        if success:
            print(f"Async response: {response}")
        
        await asyncio.sleep(5)
    
    print("Performance monitoring completed")

# Run performance monitoring with safety limit
asyncio.run(monitor_performance())
```

#### Serial Communication
```python
from AYlib.AYserial_improved import AYSerial

# Initialize serial connection
serial = AYSerial('/dev/ttyUSB0', 9600)

# Send and receive data
with serial.connection() as conn:
    serial.send_string("GET_STATUS")
    response = serial.read_data()
    print(f"Received: {response}")
```

#### Database Operations
```python
from AYlib.AYsql import AYDatabase

# Database configuration
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'test'
}

# Execute queries
with AYDatabase(config) as db:
    # Fetch all records
    users = db.fetch_all("SELECT * FROM users WHERE age > ?", (18,))
    
    # Insert data
    db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 25))
```

#### Interactive Data Visualization
```python
from AYlib.AYui import AYui

# Create interactive plot
ui = AYui("interact", head=[0,0], data=[[1,1],[2,1]], end=[8,0])
ui.AY_Plot("Motor Controller", "Time", "Amplitude")
```

#### Configuration Management
```python
from AYlib.config import get_config, set_config

# Get configuration values
db_host = get_config('database', 'host')
serial_port = get_config('serial', 'default_port')

# Set configuration
set_config('database', 'host', '192.168.1.100')
set_config('serial', 'default_port', '/dev/ttyUSB0')
```

## 📚 Module Documentation

### AYSocket Module
**Main Class:** `AYsocket(ip, port, config=None)`

**Server Methods:**
- `AY_OpenTCPServer()` - Start TCP server (backward compatible)
- `start_tcp_server()` - Start TCP server with improved error handling
- `start_tcp_hex_server()` - Start TCP HEX server
- `start_udp_server()` - Start UDP server

**Client Methods:**
- `AY_TCP_SendString(message)` - Send TCP string (backward compatible)
- `AY_TCP_SendHex(message)` - Send TCP HEX data
- `send_tcp_string(message, timeout=10, encoding='utf-8')` - Send TCP string with timeout
- `send_tcp_hex(message, timeout=10)` - Send TCP HEX data with timeout
- `send_udp_string(message, encoding='utf-8')` - Send UDP string

**Configuration:**
- `AYSocketConfig(req_type='tcp', req_method='queue')` - Configuration class

**Data Processing Methods:**
- `set_custom_processor(processor_func)` - Set custom data processor function
- `get_queued_data()` - Get data from processing queue
- `has_queued_data()` - Check if queue contains data

**Performance Monitoring Methods:**
- `get_connection_stats()` - Get current connection statistics
- `get_queue_stats()` - Get queue statistics
- `is_connection_available()` - Check if new connections can be accepted
- `async_send_tcp_string()` - Asynchronous TCP string sending

### AYSerial Module
**Main Classes:** `AYserial(port, baudrate)` and `AYSerial(port, baudrate, send_delay=0, config=None)`

**Communication Methods:**
- `AY_Read_Data_thread()` - Threaded data reading (legacy)
- `AY_Send_Data_thread()` - Threaded data sending (legacy)
- `send_string(data, encoding='utf-8')` - Send string data
- `send_hex(hex_data)` - Send HEX data
- `read_data()` - Read data from serial port
- `read_line()` - Read line with timeout

**Improved Version (AYserial_improved.py):**
- `connection()` - Context manager for serial connection
- `open_port()` - Open serial port with error handling
- `close_port()` - Close serial port safely

### AYDatabase Module
**Main Class:** `AYDatabase(config=None)`

**Query Methods:**
- `fetch_all(sql, params=None)` - Execute SELECT query and return all results
- `fetch_one(sql, params=None)` - Fetch single record
- `execute(sql, params=None)` - Execute INSERT/UPDATE/DELETE
- `execute_many(sql, params_list)` - Execute batch operations
- `call_procedure(proc_name, params=None)` - Call stored procedure

**Connection Management:**
- Context manager support (`with AYDatabase() as db:`)
- Automatic connection pooling
- Transaction support with `begin_transaction()` and `commit()`

### AYui Module
**Main Class:** `AYui(mode, head, data, end)`

**Visualization Methods:**
- `AY_Plot(title, xlabel, ylabel)` - Create interactive plot
- `add_button(label, callback)` - Add custom buttons
- `update_data(new_data)` - Update plot data dynamically
- `set_theme(theme)` - Change plot theme

**Features:**
- Real-time data updates
- Chinese font support
- Custom event handling
- Multiple plot types support

### Configuration Module
**Main Functions:**
- `get_config(section, key, default=None)` - Get configuration value
- `set_config(section, key, value)` - Set configuration value
- `load_config_file(filepath)` - Load configuration from JSON file
- `AYConfig()` - Configuration class with section support

## 🔧 Configuration

Use the configuration system for centralized settings management:

```python
from AYlib.config import get_config, set_config

# Get configuration
db_host = get_config('database', 'host')

# Set configuration
set_config('serial', 'default_port', '/dev/ttyUSB0')
```

## 📋 Requirements

- **Python**: 3.7+
- **Required Packages**:
  - `pyserial` - Serial communication support
  - `matplotlib` - Data visualization
  - `numpy` - Numerical operations
- **Optional Packages**:
  - `PyMySQL` - MySQL database support
  - `crcmod` - CRC calculation support

## 🔄 Recent Updates (v0.0.7)

### 🐛 Bug Fixes
- **Fixed logging line breaks**: Removed unnecessary line breaks in log output
- **Enhanced error handling**: Improved exception handling in socket operations
- **Duplicate log prevention**: Removed global logging configuration conflicts

### ✨ New Features
- **Improved AYserial**: Enhanced serial communication with better resource management
- **Configuration system**: Centralized configuration management with JSON support
- **Backward compatibility**: Legacy method support for existing codebases
- **Custom data processing**: User-defined processor functions for real data manipulation
- **Queue data access**: Direct methods to access and monitor queued data

### 🔧 Code Improvements
- **Modern Python practices**: Updated code to follow current Python standards
- **Better documentation**: Enhanced API documentation with examples
- **Type hints**: Added type annotations for better code clarity
- **Data processing capabilities**: Enhanced MessageProcessor class with custom processor support

### 🚀 Performance Optimizations
- **High Concurrency Support**: Connection pool management with configurable limits
- **Thread Pool Management**: Thread pool size control to prevent resource exhaustion
- **Asynchronous I/O**: Improved I/O handling for better throughput
- **Queue Management**: Efficient message queue processing with custom handlers
- **Performance Monitoring**: Built-in performance metrics and monitoring capabilities
- **Rate Limiting**: Configurable rate limiting to prevent overload

## 📝 Changelog

**v0.0.7** (2025-10-14)
- Fixed logging output formatting in AYsocket and AYserial modules
- Removed duplicate log configuration
- Enhanced error handling and resource management
- Updated documentation with practical examples
- **Performance Optimizations**:
  - High concurrency support with connection pool management
  - Thread pool size control to prevent resource exhaustion
  - Improved asynchronous I/O handling for better throughput
  - Efficient queue management with custom handlers
  - Built-in performance monitoring and rate limiting
  - Performance testing program for validation

**v0.0.5** (Previous version)
- Initial improved version with modern Python practices
- Added configuration management system
- Enhanced serial communication module

**v0.0.4** (Legacy version)
- Original AYlib functionality
- Basic socket, serial, and database operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit Pull Requests or open Issues for any bugs or feature requests.

## 📄 License

This project is licensed under the GNU-3.0 License - see the LICENSE file for details.

> Recommend using the latest version for improved functionality and bug fixes!

# Author

**Aylib** © [AaronYang](http://www.aaronyang.cc), Released under the [GNU-3.0](./LICENSE) License.<br>

> Blog [@Blog](http://bbs.aaronyang.cc) · GitHub [@GitHub](https://github.com/AaronYang233) · Email 3300390005@qq.com

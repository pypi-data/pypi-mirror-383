# Wecome to AYlib

[English](https://github.com/AaronYang233/AYlib/blob/main/README.md) | [chinese](https://github.com/AaronYang233/AYlib/blob/main/README-CN.md)

<div align="center">

[![GitHub release](https://img.shields.io/badge/release-v0.0.1-blue)](https://github.com/AaronYang233/AYlib/releases)
[![GitHub stars](https://img.shields.io/badge/stars-500-blue)](https://github.com/AaronYang233/AYlib/stargazers)
[![GitHub forks](https://img.shields.io/badge/forks-0-blue)](https://github.com/AaronYang233/AYlib/network)
[![GitHub issues](https://img.shields.io/badge/issuse-1%20open-yellow)](https://github.com/AaronYang233/AYlib/issues)
[![GitHub contributors](https://img.shields.io/badge/contributors-2-yellow)](https://github.com/AaronYang233/AYlib/graphs/contributors)
[![](https://img.shields.io/badge/about-aaonyang.cc-red)](https://bbs.aaronyang.cc)

</div>

# AYlib - Python Utility Library

AYlib is a comprehensive Python utility library that provides simplified interfaces for network communication, serial communication, database operations, and data visualization.

## 🎯 Core Features

### 🔌 Network Communication (AYsocket)
- TCP/UDP server and client implementation
- Multi-threaded request handling
- HEX and string data transmission
- Message queue processing

### 🔧 Serial Communication (AYserial)
- Serial port device control
- HEX/ASCII conversion utilities
- CRC checksum calculation
- Threaded communication support

### 💾 Database Operations (AYsql)
- MySQL database connectivity
- Connection pool management
- SQL query execution with parameterization
- Transaction support

### 📊 Data Visualization (AYui)
- Interactive data plotting
- Real-time data visualization
- Customizable UI components
- Multi-language font support

### ⚙️ Configuration Management (config)
- Centralized configuration management
- JSON configuration file support
- Global configuration access

## 🚀 Quick Start

### Installation
```bash
pip install pyserial matplotlib numpy
```

### Basic Usage Examples

#### TCP Server
```python
from AYlib import AYSocket

server = AYSocket('0.0.0.0', 8080)
server.start_tcp_server()
```

#### Serial Communication
```python
from AYlib import AYSerial

serial = AYSerial('/dev/ttyUSB0', 9600)
serial.send_string("GET_STATUS")
response = serial.read_data()
```

#### Database Operations
```python
from AYlib import AYDatabase

config = {'host': 'localhost', 'user': 'root', 'database': 'test'}
with AYDatabase(config) as db:
    users = db.fetch_all("SELECT * FROM users")
```

#### Interactive Plotting
```python
from AYlib import AYui

ui = AYui("interact", head=[0,0], data=[[1,1],[2,1]], end=[8,0])
ui.AY_Plot("Motor Controller", "Time", "Amplitude")
```

## 📚 Module Documentation

### AYSocket Module
- `start_tcp_server()` - Start TCP server
- `start_tcp_hex_server()` - Start TCP HEX server
- `start_udp_server()` - Start UDP server
- `send_tcp_string(message)` - Send TCP string
- `send_tcp_hex(message)` - Send TCP HEX data

### AYSerial Module
- `open_port()` - Open serial port
- `send_string(data)` - Send string data
- `send_hex(hex_data)` - Send HEX data
- `start_threaded_communication()` - Start threaded communication

### AYDatabase Module
- `fetch_all(sql, params)` - Execute SELECT query
- `fetch_one(sql, params)` - Fetch single record
- `execute(sql, params)` - Execute INSERT/UPDATE/DELETE
- `execute_many(sql, params_list)` - Execute batch operations

### AYui Module
- `AY_Plot(title, xlabel, ylabel)` - Create interactive plot
- Customizable buttons and event handlers

## 🔧 Configuration

Use the configuration system for centralized settings management:

```python
from AYlib import get_config, set_config

# Get configuration
db_host = get_config('database', 'host')

# Set configuration
set_config('serial', 'default_port', '/dev/ttyUSB0')
```

## 📋 Requirements

- Python 3.7+
- pyserial (for serial communication)
- matplotlib (for data visualization)
- numpy (for numerical operations)
- PyMySQL (optional, for MySQL database support)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit Pull Requests or open Issues for any bugs or feature requests.

## 📄 License

This project is licensed under the GNU-3.0 License - see the LICENSE file for details.

> Recommend using the latest version for improved functionality and bug fixes!

# Author

**Aylib** © [AaronYang](http://www.aaronyang.cc), Released under the [GNU-3.0](./LICENSE) License.<br>

> Blog [@Blog](http://bbs.aaronyang.cc) · GitHub [@GitHub](https://github.com/AaronYang233) · Email 3300390005@qq.com

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

# AYlib - Python 实用工具库

AYlib 是一个全面的 Python 实用工具库，为网络通信、串口通信、数据库操作和数据可视化提供了简化的接口。

## 🎯 核心功能

### 🔌 网络通信 (AYsocket)
- **TCP/UDP 服务器和客户端**: 多线程服务器实现，改进的错误处理
- **HEX 和字符串数据传输**: 支持文本和十六进制数据格式
- **消息队列处理**: 异步消息处理，支持队列
- **自定义数据处理**: 用户定义的处理器函数，实现真正的数据操作
- **数据访问方法**: 直接访问队列数据，进行后续处理
- **向后兼容性**: 传统 `AYsocket` 类，保留原始方法名
- **增强的日志记录**: 干净的日志输出，无不必要的换行符

### 🔧 串口通信 (AYserial)
- **串口管理**: 稳健的串口通信，资源管理
- **HEX/ASCII 转换**: 内置数据格式转换工具
- **CRC 校验和计算**: 支持 CRC16-Modbus 和其他算法
- **线程通信**: 后台线程支持，持续数据交换
- **改进版本**: `AYserial_improved.py` 采用现代 Python 实践

### 💾 数据库操作 (AYsql)
- **MySQL 连接**: 数据库操作，连接池管理
- **参数化查询**: 安全的 SQL 执行，参数绑定
- **事务支持**: ACID 兼容的事务管理
- **错误处理**: 全面的错误处理和资源清理

### 📊 数据可视化 (AYui)
- **交互式绘图**: 基于 matplotlib 的实时数据可视化
- **自定义 UI 组件**: 可扩展的 UI 框架，事件处理
- **多语言支持**: 中文字体支持，更好的本地化
- **数据管理**: 灵活的数据结构，满足各种可视化需求

### ⚙️ 配置管理 (config)
- **集中式配置**: 统一的配置管理系统
- **JSON 文件支持**: 外部配置文件支持
- **全局访问**: 跨模块轻松访问配置值
- **类型安全**: 类型安全的配置访问，回退值支持

### 🚀 性能优化 (Performance)
- **高并发支持**: 连接池管理，可配置连接限制
- **线程池管理**: 线程池大小控制，防止资源耗尽
- **异步 I/O**: 改进的 I/O 处理，提高吞吐量
- **队列管理**: 高效的消息队列处理，支持自定义处理器
- **性能监控**: 内置性能指标和监控功能
- **速率限制**: 可配置的速率限制，防止系统过载

## 🚀 快速开始

### 安装方式

#### 方式一：使用 pip 安装（推荐）
```bash
pip install AYlib
```

#### 方式二：从源码安装
```bash
# 安装依赖包
pip install pyserial matplotlib numpy PyMySQL

# 从源码安装
git clone https://github.com/AaronYang233/AYlib.git
cd AYlib
python setup.py install
```

### 基础使用示例

#### TCP 服务器和客户端通信
```python
from AYlib.AYsocket import AYsocket

# 启动 TCP 服务器
server = AYsocket('0.0.0.0', 9988)
server.AY_OpenTCPServer()  # 在后台线程中运行

# 发送测试消息
client = AYsocket('127.0.0.1', 9988)
client.AY_TCP_SendString("Hello AYlib!")
client.AY_TCP_SendString("测试中文消息")
```

#### 自定义数据处理示例
```python
from AYlib.AYsocket import AYsocket

# 自定义数据处理函数
def my_data_processor(data, data_type):
    """使用自定义逻辑处理传入数据"""
    print(f"处理 {data_type} 数据: {data}")
    
    # 示例：解析JSON、验证数据、调用外部API等
    if isinstance(data, str):
        # 业务逻辑在这里实现
        processed = f"处理后的数据: {data.upper()}"
        # 可以：存储到数据库、发送到其他服务等
        return processed
    return data

# 启动带自定义处理器的服务器
server = AYsocket('127.0.0.1', 9988)
server.set_custom_processor(my_data_processor)
server.AY_OpenTCPServer()

# 监控队列数据进行进一步处理
import signal
import sys

# 优雅关闭处理器
def signal_handler(sig, frame):
    print("\n正在优雅关闭...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 安全的监控，带退出条件
max_iterations = 100  # 限制迭代次数确保安全
for i in range(max_iterations):
    if server.has_queued_data():
        data = server.get_queued_data()
        print(f"从队列获取数据: {data}")
        # 对数据进行额外操作
    
    # 性能监控
    stats = server.get_connection_stats()
    print(f"连接统计: {stats}")
    
    if not server.is_connection_available():
        print("服务器已达到容量限制，无法接受新连接")
    
    time.sleep(1)

print("监控安全完成")
```

#### 性能监控示例
```python
from AYlib.AYsocket import AYsocket
import asyncio

# 性能监控示例
server = AYsocket('127.0.0.1', 9988)
server.AY_OpenTCPServer()

async def monitor_performance(max_iterations=20):
    """异步监控服务器性能，带安全限制"""
    for i in range(max_iterations):
        # 获取连接统计信息
        conn_stats = server.get_connection_stats()
        print(f"活跃连接数: {conn_stats['current_connections']}")
        print(f"总处理消息数: {conn_stats['processed_messages']}")
        
        # 检查连接可用性
        if server.is_connection_available():
            print("服务器可以接受新连接")
        else:
            print("服务器已达容量限制，等待连接释放")
        
        # 异步客户端示例
        client = AYsocket('127.0.0.1', 9988)
        success, response = await client.async_send_tcp_string("测试消息")
        if success:
            print(f"异步响应: {response}")
        
        await asyncio.sleep(5)
    
    print("性能监控完成")

# 运行性能监控，带安全限制
asyncio.run(monitor_performance())
```

#### 串口通信
```python
from AYlib.AYserial_improved import AYSerial

# 初始化串口连接
serial = AYSerial('/dev/ttyUSB0', 9600)

# 发送和接收数据
with serial.connection() as conn:
    serial.send_string("GET_STATUS")
    response = serial.read_data()
    print(f"收到数据: {response}")
```

#### 数据库操作
```python
from AYlib.AYsql import AYDatabase

# 数据库配置
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'test'
}

# 执行查询
with AYDatabase(config) as db:
    # 获取所有记录
    users = db.fetch_all("SELECT * FROM users WHERE age > ?", (18,))
    
    # 插入数据
    db.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("张三", 25))
```

#### 交互式数据可视化
```python
from AYlib.AYui import AYui

# 创建交互式图表
ui = AYui("interact", head=[0,0], data=[[1,1],[2,1]], end=[8,0])
ui.AY_Plot("电机控制器", "时间", "幅度")
```

#### 配置管理
```python
from AYlib.config import get_config, set_config

# 获取配置值
db_host = get_config('database', 'host')
serial_port = get_config('serial', 'default_port')

# 设置配置
set_config('database', 'host', '192.168.1.100')
set_config('serial', 'default_port', '/dev/ttyUSB0')
```

## 📚 模块文档

### AYSocket 模块
**主类:** `AYsocket(ip, port, config=None)`

**服务器方法:**
- `AY_OpenTCPServer()` - 启动 TCP 服务器（向后兼容）
- `start_tcp_server()` - 启动 TCP 服务器，改进的错误处理
- `start_tcp_hex_server()` - 启动 TCP HEX 服务器
- `start_udp_server()` - 启动 UDP 服务器

**客户端方法:**
- `AY_TCP_SendString(message)` - 发送 TCP 字符串（向后兼容）
- `AY_TCP_SendHex(message)` - 发送 TCP HEX 数据
- `send_tcp_string(message, timeout=10, encoding='utf-8')` - 发送 TCP 字符串，带超时
- `send_tcp_hex(message, timeout=10)` - 发送 TCP HEX 数据，带超时
- `send_udp_string(message, encoding='utf-8')` - 发送 UDP 字符串

**配置:**
- `AYSocketConfig(req_type='tcp', req_method='queue')` - 配置类

**数据处理方法:**
- `set_custom_processor(processor_func)` - 设置自定义数据处理函数
- `get_queued_data()` - 从处理队列获取数据
- `has_queued_data()` - 检查队列是否包含数据

**性能监控方法:**
- `get_connection_stats()` - 获取当前连接统计信息
- `get_queue_stats()` - 获取队列统计信息
- `is_connection_available()` - 检查是否可以接受新连接
- `async_send_tcp_string()` - 异步TCP字符串发送

### AYSerial 模块
**主类:** `AYserial(port, baudrate)` 和 `AYSerial(port, baudrate, send_delay=0, config=None)`

**通信方法:**
- `AY_Read_Data_thread()` - 线程数据读取（传统）
- `AY_Send_Data_thread()` - 线程数据发送（传统）
- `send_string(data, encoding='utf-8')` - 发送字符串数据
- `send_hex(hex_data)` - 发送 HEX 数据
- `read_data()` - 从串口读取数据
- `read_line()` - 读取行，带超时

**改进版本 (AYserial_improved.py):**
- `connection()` - 串口连接的上下文管理器
- `open_port()` - 打开串口，带错误处理
- `close_port()` - 安全关闭串口

### AYDatabase 模块
**主类:** `AYDatabase(config=None)`

**查询方法:**
- `fetch_all(sql, params=None)` - 执行 SELECT 查询，返回所有结果
- `fetch_one(sql, params=None)` - 获取单条记录
- `execute(sql, params=None)` - 执行 INSERT/UPDATE/DELETE
- `execute_many(sql, params_list)` - 执行批量操作
- `call_procedure(proc_name, params=None)` - 调用存储过程

**连接管理:**
- 上下文管理器支持 (`with AYDatabase() as db:`)
- 自动连接池
- 事务支持，带 `begin_transaction()` 和 `commit()`

### AYui 模块
**主类:** `AYui(mode, head, data, end)`

**可视化方法:**
- `AY_Plot(title, xlabel, ylabel)` - 创建交互式图表
- `add_button(label, callback)` - 添加自定义按钮
- `update_data(new_data)` - 动态更新图表数据
- `set_theme(theme)` - 更改图表主题

**特性:**
- 实时数据更新
- 中文字体支持
- 自定义事件处理
- 支持多种图表类型

### 配置管理模块
**主要函数:**
- `get_config(section, key, default=None)` - 获取配置值
- `set_config(section, key, value)` - 设置配置值
- `load_config_file(filepath)` - 从 JSON 文件加载配置
- `AYConfig()` - 带分区支持的配置类

## 🔧 配置管理

使用配置系统进行集中式设置管理：

```python
from AYlib import get_config, set_config

# 获取配置
db_host = get_config('database', 'host')

# 设置配置
set_config('serial', 'default_port', '/dev/ttyUSB0')
```

## 📋 系统要求

- Python 3.7+
- pyserial (用于串口通信)
- matplotlib (用于数据可视化)
- numpy (用于数值运算)
- PyMySQL (可选，用于 MySQL 数据库支持)

## 🤝 贡献指南

欢迎贡献代码！请随时提交 Pull Requests 或为任何错误或功能请求打开 Issues。

## 📄 许可证

本项目采用 GNU-3.0 许可证 - 详情请参阅 LICENSE 文件。

> 推荐使用最新版本以获得改进的功能和错误修复！

## 📝 更新日志

### v0.0.7 (2025-10-14)
**修复和改进：**
- ✅ 修复了AYsocket.py中TCP服务器接收消息的换行符问题
- ✅ 修复了AYserial.py中串口读取数据的换行符问题
- ✅ 移除了重复的全局日志配置，避免日志重复输出
- ✅ 更新了文档，添加了详细的pip安装说明
- ✅ 完善了模块文档和API参考
- ✅ 增强了AYsocket的数据处理能力，支持自定义处理器函数
- ✅ 添加了队列数据访问方法，实现真正的数据操作功能

**性能优化：**
- ✅ 实现了高并发支持，连接池管理防止资源泄露
- ✅ 添加了线程池限制，避免资源耗尽
- ✅ 改进了异步I/O处理，提高系统吞吐量
- ✅ 优化了队列管理机制，支持自定义处理器
- ✅ 添加了性能监控和速率限制功能
- ✅ 创建了性能测试程序，验证高并发处理能力

### v0.0.5 (2024-10-13)
**功能增强：**
- ✅ 添加了AYserial_improved.py模块，提供改进的串口通信功能
- ✅ 优化了日志系统，提供更清晰的调试信息
- ✅ 增强了错误处理和异常管理

### v0.0.4 (2024-10-12)
**基础功能：**
- ✅ 实现了基本的TCP/UDP网络通信
- ✅ 添加了串口通信支持
- ✅ 集成了MySQL数据库操作
- ✅ 提供了数据可视化功能

## 🤝 贡献指南

欢迎贡献代码！请随时提交 Pull Requests 或为任何错误或功能请求打开 Issues。

## 📄 许可证

本项目采用 GNU-3.0 许可证 - 详情请参阅 LICENSE 文件。

# Author

**AYlib** © [AaronYang](http://www.aaronyang.cc), Released under the [GNU-3.0](./LICENSE) License.<br>

> Blog [@Blog](http://bbs.aaronyang.cc) · GitHub [@GitHub](https://github.com/AaronYang233) · Email 3300390005@qq.com

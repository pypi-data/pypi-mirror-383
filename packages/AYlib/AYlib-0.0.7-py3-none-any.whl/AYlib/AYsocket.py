# -*- coding: utf-8 -*-
__doc__ = 'AYlib module'
__version__ = '0.0.7'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import socket
import socketserver
import threading
import time
import asyncio
import concurrent.futures
from threading import Semaphore, BoundedSemaphore

import json

# import requests  # Only import when needed
import logging
import queue

# from binascii import unhexlify
# from crcmod import mkCrcFun
# from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Configuration class to replace global variables
class AYSocketConfig:
    """Configuration class for AYSocket operations"""
    
    # Server response commands
    REQ_END = '{"AYsocket":"end"}'
    REQ_ERROR = '{"AYsocket":"error"}'
    REQ_EXIT = '{"AYsocket":"exit"}'
    
    # Server response hex commands
    REQ_HEX_EXIT = 'FF FB FC FF FD FA'
    REQ_HEX_ERROR = 'FF FF FF FF FF FA'
    
    # Default configuration
    DEFAULT_TYPE = 'tcp'
    DEFAULT_METHOD = 'queue'
    
    # Performance configuration
    MAX_CONNECTIONS = 1000
    MAX_THREADS = 100
    CONNECTION_TIMEOUT = 30
    QUEUE_MAX_SIZE = 10000
    
    def __init__(self, req_type='tcp', req_method='queue', max_connections=1000, max_threads=100):
        self.req_type = req_type
        self.req_method = req_method
        self.max_connections = max_connections
        self.max_threads = max_threads

# Default configuration instance
_default_config = AYSocketConfig()

''' logging config '''
# 移除全局basicConfig，避免重复日志输出
# logging.basicConfig(#filename="INFO.log",
#             level=logging.INFO,
#             format='%(asctime)s -%(levelname)s: %(message)s')

# Performance optimized queues and pools
QueueData = queue.Queue(maxsize=_default_config.QUEUE_MAX_SIZE)
ConnectionPool = {}
ThreadPool = concurrent.futures.ThreadPoolExecutor(max_workers=_default_config.max_threads)
ConnectionSemaphore = Semaphore(_default_config.max_connections)

class AYSocket:
    """
    AYSocket class for TCP/UDP server and client operations.
    Improved with better error handling and resource management.
    Performance optimized for high concurrency scenarios.
    """
    
    def __init__(self, ip='127.0.0.1', port=80, config=None):
        """
        Initialize AYSocket instance.
        
        Args:
            ip: Server IP address
            port: Server port number
            config: AYSocketConfig instance for custom configuration
        """
        self.ip = ip
        self.port = port
        self.config = config or _default_config
        self.logger = self._setup_logger()
        self.active_connections = 0
        self.connection_stats = {
            'total_connections': 0,
            'current_connections': 0,
            'failed_connections': 0,
            'processed_messages': 0
        }
        
    def _setup_logger(self):
        """Setup logger for socket operations."""
        logger = logging.getLogger('AYSocket')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _acquire_connection(self):
        """Acquire connection slot with semaphore."""
        if ConnectionSemaphore.acquire(blocking=False):
            self.active_connections += 1
            self.connection_stats['current_connections'] = self.active_connections
            self.connection_stats['total_connections'] += 1
            return True
        else:
            self.connection_stats['failed_connections'] += 1
            self.logger.warning(f"Connection limit reached: {self.active_connections}/{self.config.max_connections}")
            return False
    
    def _release_connection(self):
        """Release connection slot."""
        if self.active_connections > 0:
            self.active_connections -= 1
            self.connection_stats['current_connections'] = self.active_connections
            ConnectionSemaphore.release()
    
    def get_connection_stats(self):
        """Get current connection statistics."""
        return self.connection_stats.copy()
    
    def is_connection_available(self):
        """Check if new connections can be accepted."""
        return self.active_connections < self.config.max_connections
    
    async def async_send_tcp_string(self, message="hello AYlib", timeout=10, encoding='utf-8'):
        """
        Asynchronously send string data via TCP client.
        
        Args:
            message: String message to send
            timeout: Connection timeout in seconds
            encoding: Text encoding
            
        Returns:
            tuple: (success: bool, response: str or None)
        """
        loop = asyncio.get_event_loop()
        try:
            # Use thread pool for blocking socket operations
            result = await loop.run_in_executor(
                ThreadPool, 
                self.send_tcp_string, 
                message, timeout, encoding
            )
            return result
        except Exception as e:
            self.logger.error(f'Async TCP Client string send error: {e}')
            return False, None
    
    def start_tcp_server(self):
        """
        Start TCP server with improved error handling and performance optimization.
        
        Returns:
            bool: True if server started successfully
        """
        try:
            socketserver.TCPServer.allow_reuse_address = True
            server = ThreadedTCPServer((self.ip, self.port), ThreadedTCPRequestHandler, server_instance=self)
            
            # Set socket options for better performance
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle's algorithm
            
            self.logger.info(f"Starting TCP server on {self.ip}:{self.port}")
            self.logger.info(f"Max connections: {self.config.max_connections}")
            self.logger.info(f"Max threads: {self.config.max_threads}")
            
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            self.logger.info(f"TCP Server running in thread: {server_thread.name}")
            self.logger.info("Waiting for connections...")
            
            # Start connection monitoring in background
            monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
            monitor_thread.start()
            
            server.serve_forever()
            return True
            
        except Exception as e:
            self.logger.error(f"TCP Server error: {e}")
            if 'server' in locals():
                server.shutdown()
            return False
    
    def _monitor_connections(self):
        """Monitor connection statistics in background."""
        while True:
            time.sleep(60)  # Log every minute
            stats = self.get_connection_stats()
            self.logger.info(f"Connection stats: {stats}")
            
            # Log warning if approaching limits
            if self.active_connections > self.config.max_connections * 0.8:
                self.logger.warning(f"High connection usage: {self.active_connections}/{self.config.max_connections}")
    def start_tcp_hex_server(self):
        """
        Start TCP HEX server with improved error handling.
        
        Returns:
            bool: True if server started successfully
        """
        try:
            socketserver.TCPServer.allow_reuse_address = True
            server = ThreadedTCPServer((self.ip, self.port), ThreadedTCPHEXRequestHandler)
            
            self.logger.info(f"Starting TCP HEX server on {self.ip}:{self.port}")
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            self.logger.info(f"TCP HEX Server running in thread: {server_thread.name}")
            self.logger.info("Waiting for connections...")
            
            server.serve_forever()
            return True
            
        except Exception as e:
            self.logger.error(f"TCP HEX Server error: {e}")
            if 'server' in locals():
                server.shutdown()
            return False

    def start_udp_server(self):
        """
        Start UDP server with improved error handling.
        
        Returns:
            bool: True if server started successfully
        """
        try:
            server = socketserver.UDPServer((self.ip, self.port), ThreadedUDPRequestHandler)
            
            self.logger.info(f"Starting UDP server on {self.ip}:{self.port}")
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            self.logger.info(f"UDP Server running in thread: {server_thread.name}")
            self.logger.info("Waiting for connections...")
            
            server.serve_forever()
            return True
            
        except Exception as e:
            self.logger.error(f"UDP Server error: {e}")
            if 'server' in locals():
                server.shutdown()
            return False
            
    def send_tcp_hex(self, message="aa bb cc", timeout=10):
        """
        Send HEX data via TCP client.
        
        Args:
            message: HEX string to send (space-separated)
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((self.ip, self.port))
                hex_data = bytes.fromhex(message.replace(' ', ''))
                sock.sendall(hex_data)
                self.logger.info(f'TCP Client sent HEX: {message}')
                return True
        except Exception as e:
            self.logger.error(f'TCP Client HEX send error: {e}')
            return False

    def send_tcp_string(self, message="hello AYlib", timeout=10, encoding='utf-8'):
        """
        Send string data via TCP client.
        
        Args:
            message: String message to send
            timeout: Connection timeout in seconds
            encoding: Text encoding
            
        Returns:
            tuple: (success: bool, response: str or None)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((self.ip, self.port))
                sock.sendall(message.encode(encoding))
                self.logger.info(f'TCP Client sent data: {message}')
                
                # Try to receive response
                try:
                    response = sock.recv(1024).decode(encoding)
                    self.logger.info(f'TCP Client received: {response}')
                    return True, response
                except socket.timeout:
                    return True, None
                    
        except Exception as e:
            self.logger.error(f'TCP Client string send error: {e}')
            return False, None

    def send_udp_string(self, message="hello AYlib", encoding='utf-8'):
        """
        Send string data via UDP client.
        
        Args:
            message: String message to send
            encoding: Text encoding
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                data = message.encode(encoding)
                sock.sendto(data, (self.ip, self.port))
                self.logger.info(f'UDP Client sent data: {message}')
                return True
        except Exception as e:
            self.logger.error(f'UDP Client send error: {e}')
            return False

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    """Improved UDP request handler with better error handling."""
    
    def handle(self):
        """Handle UDP request with improved error handling."""
        addr = self.client_address
        logger = logging.getLogger('AYSocket.UDP')
        
        try:
            data = self.request[0].decode('utf-8')
            logger.info(f'UDP Server received from {addr}: {data}')
            
            # Process the message
            response = process_message(data, 'udp', _default_config.req_method)
            logger.info(f'UDP Server processed data from {addr}: {response}')
            
        except UnicodeDecodeError as e:
            logger.warning(f'UDP Server decode error from {addr}: {e}')
        except Exception as e:
            logger.error(f'UDP Server error from {addr}: {e}')

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Improved TCP request handler with better error handling and performance optimization."""
    
    def setup(self):
        """Setup connection with resource management."""
        self.addr = self.client_address
        self.logger = logging.getLogger('AYSocket.TCP')
        self.server_instance = self.server.server_instance if hasattr(self.server, 'server_instance') else None
        
        # Acquire connection slot
        if self.server_instance and not self.server_instance._acquire_connection():
            self.logger.warning(f"Connection rejected from {self.addr}: limit reached")
            self.request.close()
            return
        
        self.logger.info(f"Connection established from {self.addr}")
    
    def handle(self):
        """Handle TCP request with improved error handling and performance optimization."""
        try:
            while True:
                data = self.request.recv(4096)  # Increased buffer size for better performance
                if not data:
                    break
                    
                try:
                    message = data.decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.warning(f'TCP Server decode error from {self.addr}')
                    self.request.sendall(AYSocketConfig.REQ_ERROR.encode('utf-8'))
                    continue
                
                # Handle special commands
                if message == AYSocketConfig.REQ_END:
                    self.logger.info(f'TCP Device end signal from {self.addr}')
                    break
                elif message == AYSocketConfig.REQ_EXIT:
                    self.logger.info(f'TCP Device exit signal from {self.addr}')
                    raise ConnectionAbortedError("Client requested exit")
                
                # Process message in thread pool for better concurrency
                future = ThreadPool.submit(self._process_message, message)
                try:
                    response = future.result(timeout=5)  # 5 second timeout
                    if response:
                        self.request.sendall(response.encode('utf-8'))
                except concurrent.futures.TimeoutError:
                    self.logger.error(f'Message processing timeout from {self.addr}')
                    self.request.sendall(AYSocketConfig.REQ_ERROR.encode('utf-8'))
                    
        except ConnectionAbortedError:
            self.logger.info(f'TCP connection aborted by client {self.addr}')
        except Exception as e:
            self.logger.error(f'TCP Server error from {self.addr}: {e}')
            try:
                self.request.sendall(AYSocketConfig.REQ_ERROR.encode('utf-8'))
            except:
                pass
        finally:
            self._cleanup()
    
    def _process_message(self, message):
        """Process message in separate thread."""
        # 去除消息中的换行符后再记录日志
        clean_message = message.strip()
        self.logger.info(f'TCP Server received from {self.addr}: {clean_message}')
        
        # Update statistics
        if self.server_instance:
            self.server_instance.connection_stats['processed_messages'] += 1
        
        # Process message based on configuration
        if _default_config.req_method == 'client':
            response = process_message(message, _default_config.req_type, 'client')
            if response:
                self.logger.info(f'TCP Server sent to {self.addr}: {response}')
            return response
        elif _default_config.req_method == 'queue':
            response = process_message(message, _default_config.req_type, 'queue')
            # 去除响应中的换行符后再记录日志
            clean_response = str(response).strip()
            self.logger.info(f'TCP Server queued data from {self.addr}: {clean_response}')
            return clean_response
    
    def _cleanup(self):
        """Cleanup connection resources."""
        try:
            self.request.close()
        except:
            pass
        finally:
            # Release connection slot
            if self.server_instance:
                self.server_instance._release_connection()
            self.logger.info(f"Connection closed from {self.addr}")

class ThreadedTCPHEXRequestHandler(socketserver.BaseRequestHandler):
    """Improved TCP HEX request handler with better error handling."""
    
    def handle(self):
        """Handle TCP HEX request with improved error handling."""
        addr = self.client_address
        logger = logging.getLogger('AYSocket.TCP_HEX')
        
        try:
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                
                # Handle exit command
                if data == bytes.fromhex(AYSocketConfig.REQ_HEX_EXIT.replace(' ', '')):
                    logger.info(f'TCP HEX Server exit signal from {addr}')
                    raise ConnectionAbortedError("Client requested exit")
                
                logger.info(f'TCP HEX Server received from {addr}: {data.hex()}')
                
                # Process message based on configuration
                if _default_config.req_method == 'client':
                    response = process_message(data, _default_config.req_type, 'client')
                    if response and isinstance(response, (bytes, bytearray)):
                        self.request.sendall(response)
                        logger.info(f'TCP HEX Server sent to {addr}: {response.hex()}')
                elif _default_config.req_method == 'queue':
                    response = process_message(data, _default_config.req_type, 'queue')
                    logger.info(f'TCP HEX Server queued data from {addr}: {response}')
                    
        except ConnectionAbortedError:
            logger.info(f'TCP HEX connection aborted by client {addr}')
        except Exception as e:
            logger.error(f'TCP HEX Server error from {addr}: {e}')
            try:
                error_bytes = bytes.fromhex(AYSocketConfig.REQ_HEX_ERROR.replace(' ', ''))
                self.request.sendall(error_bytes)
            except:
                pass
        finally:
            try:
                self.request.close()
            except:
                pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Threaded TCP server with performance optimization."""
    
    def __init__(self, server_address, request_handler_class, bind_and_activate=True, server_instance=None):
        super().__init__(server_address, request_handler_class, bind_and_activate)
        self.server_instance = server_instance

class MessageProcessor:
    """
    Improved message processor with better error handling and performance optimization.
    Override tcp_processing and udp_processing methods for custom protocol resolution.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('AYSocket.MessageProcessor')
        self.custom_processor = None
        self.batch_size = 100  # Process messages in batches for better performance
        self.batch_buffer = []
        self.last_batch_time = time.time()
    
    def set_custom_processor(self, processor_func):
        """
        Set a custom processor function for handling incoming data.
        
        Args:
            processor_func: Function that takes (data, data_type) and returns processed data
        """
        self.custom_processor = processor_func
    
    def tcp_processing(self, data):
        """
        Process TCP data. Override this method for custom TCP protocol handling.
        
        Args:
            data: Raw data received from TCP client
            
        Returns:
            Processed data
        """
        if self.custom_processor:
            return self.custom_processor(data, 'tcp')
        return data
    
    def udp_processing(self, data):
        """
        Process UDP data. Override this method for custom UDP protocol handling.
        
        Args:
            data: Raw data received from UDP client
            
        Returns:
            Processed data
        """
        if self.custom_processor:
            return self.custom_processor(data, 'udp')
        return data
    
    def batch_process(self, data, data_type="tcp"):
        """
        Process data in batches for better performance.
        
        Args:
            data: Raw data to process
            data_type: Type of connection
            
        Returns:
            Processed data or None if batched
        """
        self.batch_buffer.append((data, data_type))
        current_time = time.time()
        
        # Process batch if buffer is full or timeout reached
        if (len(self.batch_buffer) >= self.batch_size or 
            current_time - self.last_batch_time > 1.0):  # 1 second timeout
            
            processed_batch = self._process_batch()
            self.batch_buffer.clear()
            self.last_batch_time = current_time
            return processed_batch
        
        return None
    
    def _process_batch(self):
        """Process a batch of messages."""
        if not self.batch_buffer:
            return None
            
        # Use thread pool for batch processing
        futures = []
        for data, data_type in self.batch_buffer:
            future = ThreadPool.submit(self._single_process, data, data_type)
            futures.append(future)
        
        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=2.0)  # 2 second timeout per message
                if result:
                    results.append(result)
            except concurrent.futures.TimeoutError:
                self.logger.warning("Batch processing timeout")
            except Exception as e:
                self.logger.error(f"Batch processing error: {e}")
        
        return results if results else None
    
    def _single_process(self, data, data_type):
        """Process single message."""
        if data_type == "tcp":
            return self.tcp_processing(data)
        elif data_type == "udp":
            return self.udp_processing(data)
        return data
    
    def get_queued_data(self, batch_size=10):
        """
        Get data from queue in batches for better performance.
        
        Args:
            batch_size: Number of items to retrieve at once
            
        Returns:
            List of data items or None if empty
        """
        try:
            items = []
            for _ in range(min(batch_size, QueueData.qsize())):
                if not QueueData.empty():
                    items.append(QueueData.get_nowait())
            return items if items else None
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f'Queue get error: {e}')
        return None
    
    def has_queued_data(self):
        """
        Check if there is data in the queue.
        
        Returns:
            bool: True if queue has data, False otherwise
        """
        return not QueueData.empty()
    
    def get_queue_stats(self):
        """
        Get queue statistics.
        
        Returns:
            dict: Queue statistics
        """
        return {
            'queue_size': QueueData.qsize(),
            'max_size': _default_config.QUEUE_MAX_SIZE,
            'is_full': QueueData.full(),
            'is_empty': QueueData.empty()
        }

# Global message processor instance
_message_processor = MessageProcessor()

def process_message(data, data_type="tcp", request_type="client"):
    """
    Process incoming message data.
    
    Args:
        data: Raw message data
        data_type: Type of connection ('tcp' or 'udp')
        request_type: Processing type ('client' or 'queue')
        
    Returns:
        Processed data or None on error
    """
    logger = logging.getLogger('AYSocket.MessageProcessor')
    logger.debug('Processing message...')
    
    try:
        # Process based on connection type
        if data_type == "tcp":
            processed_data = _message_processor.tcp_processing(data)
        elif data_type == "udp":
            processed_data = _message_processor.udp_processing(data)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        logger.debug('Message processing completed')
        
        # Handle response based on request type
        if request_type == "client":
            return processed_data
        elif request_type == "queue":
            # Add to queue if data is substantial
            if processed_data and len(str(processed_data)) > 1:
                QueueData.put(processed_data)
            return _message_processor.get_queued_data()
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
            
    except Exception as e:
        logger.error(f'Message processing error: {e}')
        return None

# Backward compatibility
AY_Message_processing = process_message
Message_processing = MessageProcessor

# Backward compatibility class alias
class AYsocket(AYSocket):
    """Backward compatibility alias for AYSocket."""
    
    def AY_OpenTCPServer(self):
        """Backward compatibility method."""
        return self.start_tcp_server()
    
    def AY_OpenTCPHEXServer(self):
        """Backward compatibility method."""
        return self.start_tcp_hex_server()
    
    def AY_OpenUDPServer(self):
        """Backward compatibility method."""
        return self.start_udp_server()
    
    def AY_TCP_SendHex(self, message="aa bb cc"):
        """Backward compatibility method."""
        return self.send_tcp_hex(message)
    
    def AY_TCP_SendString(self, message="hello AYlib"):
        """Backward compatibility method."""
        success, response = self.send_tcp_string(message)
        return success
    
    def AY_UDP_SendString(self, message="hello AYlib"):
        """Backward compatibility method."""
        return self.send_udp_string(message)
    
    def set_custom_processor(self, processor_func):
        """
        Set a custom processor function for handling incoming data.
        
        Args:
            processor_func: Function that takes (data, data_type) and returns processed data
        """
        _message_processor.set_custom_processor(processor_func)
    
    def get_queued_data(self):
        """
        Get data from queue.
        
        Returns:
            Data from queue or None if empty
        """
        return _message_processor.get_queued_data()
    
    def has_queued_data(self):
        """
        Check if there is data in the queue.
        
        Returns:
            bool: True if queue has data, False otherwise
        """
        return _message_processor.has_queued_data()

if __name__ == '__main__':
    a = AYsocket('127.0.0.1',9988)
    
    ''' TCP RX/TX '''
    # TCP_Server START
    a.AY_OpenTCPServer()

    # TCP_Client send data
    #a.AY_TCP_SendString("hello\n")

    # TCP_HEX_Server START
    #a.AY_OpenTCPHEXServer()

    # TCP_HEX_Client send data
    #a.AY_TCP_SendHex("AA BB CC DD")

    ''' TCP_ModBus_RTU '''

    ''' UDP RX/TX'''
    # UDP_Server START
    #a.AY_OpenUDPServer()

    # UDP_Client send data
    #a.AY_UDP_SendString("hello")
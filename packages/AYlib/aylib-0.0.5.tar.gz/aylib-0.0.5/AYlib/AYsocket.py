# -*- coding: utf-8 -*-
__doc__ = 'AYlib module'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import socket
import socketserver
import threading
import time

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
    
    def __init__(self, req_type='tcp', req_method='queue'):
        self.req_type = req_type
        self.req_method = req_method

# Default configuration instance
_default_config = AYSocketConfig()

''' logging config '''
logging.basicConfig(#filename="INFO.log",
            level=logging.INFO,
            format='%(asctime)s -%(levelname)s: %(message)s')

QueueData = queue.Queue(maxsize=0)

class AYSocket:
    """
    AYSocket class for TCP/UDP server and client operations.
    Improved with better error handling and resource management.
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
    
    def start_tcp_server(self):
        """
        Start TCP server with improved error handling.
        
        Returns:
            bool: True if server started successfully
        """
        try:
            socketserver.TCPServer.allow_reuse_address = True
            server = ThreadedTCPServer((self.ip, self.port), ThreadedTCPRequestHandler)
            
            self.logger.info(f"Starting TCP server on {self.ip}:{self.port}")
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            self.logger.info(f"TCP Server running in thread: {server_thread.name}")
            self.logger.info("Waiting for connections...")
            
            server.serve_forever()
            return True
            
        except Exception as e:
            self.logger.error(f"TCP Server error: {e}")
            if 'server' in locals():
                server.shutdown()
            return False
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
    """Improved TCP request handler with better error handling."""
    
    def handle(self):
        """Handle TCP request with improved error handling."""
        addr = self.client_address
        logger = logging.getLogger('AYSocket.TCP')
        
        try:
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                    
                try:
                    message = data.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f'TCP Server decode error from {addr}')
                    self.request.sendall(AYSocketConfig.REQ_ERROR.encode('utf-8'))
                    continue
                
                # Handle special commands
                if message == AYSocketConfig.REQ_END:
                    logger.info(f'TCP Device end signal from {addr}')
                    break
                elif message == AYSocketConfig.REQ_EXIT:
                    logger.info(f'TCP Device exit signal from {addr}')
                    raise ConnectionAbortedError("Client requested exit")
                
                logger.info(f'TCP Server received from {addr}: {message}')
                
                # Process message based on configuration
                if _default_config.req_method == 'client':
                    response = process_message(message, _default_config.req_type, 'client')
                    if response:
                        self.request.sendall(response.encode('utf-8'))
                        logger.info(f'TCP Server sent to {addr}: {response}')
                elif _default_config.req_method == 'queue':
                    response = process_message(message, _default_config.req_type, 'queue')
                    logger.info(f'TCP Server queued data from {addr}: {response}')
                    
        except ConnectionAbortedError:
            logger.info(f'TCP connection aborted by client {addr}')
        except Exception as e:
            logger.error(f'TCP Server error from {addr}: {e}')
            try:
                self.request.sendall(AYSocketConfig.REQ_ERROR.encode('utf-8'))
            except:
                pass
        finally:
            try:
                self.request.close()
            except:
                pass

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
    pass

class MessageProcessor:
    """
    Improved message processor with better error handling.
    Override tcp_processing and udp_processing methods for custom protocol resolution.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('AYSocket.MessageProcessor')
    
    def tcp_processing(self, data):
        """
        Process TCP data. Override this method for custom TCP protocol handling.
        
        Args:
            data: Raw data received from TCP client
            
        Returns:
            Processed data
        """
        return data
    
    def udp_processing(self, data):
        """
        Process UDP data. Override this method for custom UDP protocol handling.
        
        Args:
            data: Raw data received from UDP client
            
        Returns:
            Processed data
        """
        return data
    
    def get_queued_data(self):
        """
        Get data from queue.
        
        Returns:
            Data from queue or None if empty
        """
        try:
            if not QueueData.empty():
                return QueueData.get_nowait()
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f'Queue get error: {e}')
        return None

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
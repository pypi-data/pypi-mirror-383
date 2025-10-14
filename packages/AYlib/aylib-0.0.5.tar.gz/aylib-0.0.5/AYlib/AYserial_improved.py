# -*- coding: utf-8 -*-
"""
AYserial - Improved serial communication module for AYlib
Provides robust serial communication with better error handling and resource management.
"""
__doc__ = 'AYlib serial module'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import serial
import threading
import time
import logging
import queue
from typing import Optional, Dict, Any, Tuple, Callable
from contextlib import contextmanager

try:
    from binascii import unhexlify
    from crcmod import mkCrcFun
    CRC_AVAILABLE = True
except ImportError:
    CRC_AVAILABLE = False
    logging.warning("crcmod not available. CRC functions will be disabled.")

from .config import get_config

class AYSerialConfig:
    """Configuration class for AYSerial operations."""
    
    def __init__(self):
        self.demo_model = 'C'  # A: String, B: HEX, C: Thread mode
        self.send_flag = 0  # 0: auto, 1: manual
        self.rx_tx_model = get_config('serial', 'rx_tx_model', [1, 1])  # [TX, RX]
        self.user_data = {"{'hello':1}": 95, 'Lisa': 85, 'Bart': 59, 'Paul': 74}
        self.user_error = {'value': -1}

class AYSerial:
    """
    Improved serial communication class with better error handling and resource management.
    """
    
    def __init__(self, port: str = None, baudrate: int = None, send_delay: float = 0, 
                 config: Optional[AYSerialConfig] = None):
        """
        Initialize AYSerial instance.
        
        Args:
            port: Serial port name
            baudrate: Baud rate for communication
            send_delay: Delay between sends in seconds
            config: AYSerialConfig instance for custom settings
        """
        self.port = port or get_config('serial', 'default_port', '/dev/ttyUSB0')
        self.baudrate = baudrate or get_config('serial', 'default_baudrate', 9600)
        self.send_delay = send_delay
        self.config = config or AYSerialConfig()
        
        # Serial connection
        self.serial_conn = serial.Serial()
        self.serial_conn.port = self.port
        self.serial_conn.baudrate = self.baudrate
        self.serial_conn.timeout = get_config('serial', 'timeout', 1)
        
        # Threading control
        self.alive = False
        self.wait_end = None
        self.thread_read = None
        self.thread_send = None
        
        # Data queues
        self.read_data_queue = queue.Queue(maxsize=0)
        self.send_data_queue = queue.Queue(maxsize=0)
        
        # Logger setup
        self.logger = self._setup_logger()
        
        # Callbacks
        self.data_received_callback: Optional[Callable[[str], None]] = None
        self.error_callback: Optional[Callable[[Exception], None]] = None
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for serial operations."""
        logger = logging.getLogger('AYSerial')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def set_data_received_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback function for received data."""
        self.data_received_callback = callback
    
    def set_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Set callback function for errors."""
        self.error_callback = callback
    
    def echo_config(self) -> None:
        """Display current serial configuration."""
        self.logger.info("-" * 40)
        self.logger.info(f"Serial Port: {self.port}")
        self.logger.info(f"Baud Rate: {self.baudrate}")
        self.logger.info(f"Send Delay: {self.send_delay}s")
        self.logger.info(f"RX/TX Model: {self.config.rx_tx_model}")
        self.logger.info("-" * 40)
    
    @contextmanager
    def connection(self):
        """Context manager for serial connection."""
        try:
            self.open_port()
            yield self.serial_conn
        finally:
            self.close_port()
    
    def open_port(self) -> bool:
        """
        Open serial port.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.serial_conn.is_open:
                self.serial_conn.open()
            self.logger.info(f"Serial port {self.port} opened successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open serial port {self.port}: {e}")
            if self.error_callback:
                self.error_callback(e)
            return False
    
    def close_port(self) -> None:
        """Close serial port."""
        try:
            if self.serial_conn.is_open:
                self.serial_conn.close()
            self.logger.info(f"Serial port {self.port} closed")
        except Exception as e:
            self.logger.warning(f"Error closing serial port: {e}")
    
    def start_threaded_communication(self) -> bool:
        """
        Start threaded communication.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.open_port():
            return False
        
        self.wait_end = threading.Event()
        self.alive = True
        
        # Start read thread if RX is enabled
        if self.config.rx_tx_model[1]:
            self.logger.info('Starting serial read thread')
            self.thread_read = threading.Thread(target=self._read_thread, daemon=True)
            self.thread_read.start()
        
        # Start send thread if TX is enabled
        if self.config.rx_tx_model[0]:
            self.logger.info('Starting serial send thread')
            self.thread_send = threading.Thread(target=self._send_thread, daemon=True)
            self.thread_send.start()
        
        if not any(self.config.rx_tx_model):
            self.logger.error('Both RX and TX are disabled. Please enable at least one.')
            self.alive = False
            return False
        
        return True
    
    def stop_threaded_communication(self) -> None:
        """Stop threaded communication."""
        self.alive = False
        if self.wait_end:
            self.wait_end.set()
        self.close_port()
    
    def wait_for_threads(self) -> None:
        """Wait for communication threads to finish."""
        if self.wait_end:
            self.wait_end.wait()
    
    def _read_thread(self) -> None:
        """Thread function for reading serial data."""
        while self.alive:
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.readline().decode('utf-8').strip()
                    if data:
                        self.logger.info(f'Received: {data}')
                        
                        # Handle quit command
                        if data.endswith('qqqqq'):
                            self.logger.info('Quit command received')
                            break
                        
                        # Add to queue
                        if self.config.send_flag == 0:
                            self.read_data_queue.put(data)
                        
                        # Call callback if set
                        if self.data_received_callback:
                            self.data_received_callback(data)
                            
            except Exception as e:
                self.logger.error(f'Read thread error: {e}')
                if self.error_callback:
                    self.error_callback(e)
                break
        
        self.alive = False
        if self.wait_end:
            self.wait_end.set()
    
    def _send_thread(self) -> None:
        """Thread function for sending serial data."""
        while self.alive:
            try:
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
                data = None
                if self.config.send_flag == 0:
                    data = self._handle_automatic_send()
                elif self.config.send_flag == 1:
                    # Manual mode - get from queue
                    try:
                        data = self.send_data_queue.get_nowait()
                    except queue.Empty:
                        continue
                
                if data:
                    self.send_string(data)
                    
            except Exception as e:
                self.logger.error(f'Send thread error: {e}')
                if self.error_callback:
                    self.error_callback(e)
                break
        
        self.alive = False
        if self.wait_end:
            self.wait_end.set()
    
    def _handle_automatic_send(self) -> Optional[str]:
        """Handle automatic sending based on received data."""
        try:
            if not self.read_data_queue.empty():
                received_data = self.read_data_queue.get_nowait()
                
                # Look up response in user data
                for key, value in self.config.user_data.items():
                    if key == received_data:
                        return str(value)
                        
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f'Automatic send handling error: {e}')
        
        return None
    
    def send_string(self, data: str, encoding: str = 'utf-8') -> bool:
        """
        Send string data via serial port.
        
        Args:
            data: String data to send
            encoding: Text encoding
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.send_delay > 0:
                time.sleep(self.send_delay)
            
            bytes_sent = self.serial_conn.write(data.encode(encoding))
            self.logger.info(f'Sent {bytes_sent} bytes: {data}')
            return True
            
        except Exception as e:
            self.logger.error(f'String send error: {e}')
            return False
    
    def send_hex(self, hex_data: str) -> bool:
        """
        Send HEX data via serial port.
        
        Args:
            hex_data: HEX string (space-separated)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.send_delay > 0:
                time.sleep(self.send_delay)
            
            # Clean and convert hex string
            clean_hex = hex_data.replace(' ', '').replace('-', '')
            binary_data = bytes.fromhex(clean_hex)
            
            bytes_sent = self.serial_conn.write(binary_data)
            self.logger.info(f'Sent {bytes_sent} bytes HEX: {hex_data}')
            return True
            
        except Exception as e:
            self.logger.error(f'HEX send error: {e}')
            return False
    
    def queue_send_data(self, data: str) -> None:
        """Add data to send queue for manual mode."""
        self.send_data_queue.put(data)
    
    def read_data(self) -> Optional[str]:
        """
        Read data from serial port (blocking).
        
        Returns:
            str: Received data or None on error
        """
        try:
            data = self.serial_conn.readline().decode('utf-8').strip()
            self.logger.info(f'Read data: {data}')
            return data
        except Exception as e:
            self.logger.error(f'Read error: {e}')
            return None
    
    def get_queued_data(self) -> Optional[str]:
        """Get data from read queue."""
        try:
            return self.read_data_queue.get_nowait()
        except queue.Empty:
            return None
    
    # CRC and utility functions
    def calculate_crc16_modbus(self, hex_data: str, invert_bytes: bool = False) -> str:
        """
        Calculate CRC16 Modbus for hex data.
        
        Args:
            hex_data: HEX data string
            invert_bytes: Whether to invert byte order
            
        Returns:
            str: CRC16 value as hex string
        """
        if not CRC_AVAILABLE:
            raise ImportError("crcmod not available. Install with: pip install crcmod")
        
        crc16 = mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        clean_data = hex_data.replace(' ', '').replace('-', '')
        
        crc_value = crc16(unhexlify(clean_data))
        crc_hex = f"{crc_value:04X}"
        
        if invert_bytes:
            return f"{crc_hex[2:4]} {crc_hex[0:2]}"
        else:
            return f"{crc_hex[0:2]} {crc_hex[2:4]}"
    
    @staticmethod
    def hex_to_ascii(hex_value: int) -> str:
        """Convert hex value to ASCII character."""
        return chr(hex_value)
    
    @staticmethod
    def ascii_to_hex(char: str) -> str:
        """Convert ASCII character to hex string."""
        return hex(ord(char))
    
    @staticmethod
    def ascii_to_dec(char: str) -> int:
        """Convert ASCII character to decimal."""
        return ord(char)
    
    @staticmethod
    def dec_to_ascii(dec_value: int) -> str:
        """Convert decimal value to ASCII character."""
        return chr(dec_value)
    
    def calculate_checksum(self, data: list, count: int) -> int:
        """
        Calculate simple checksum for data array.
        
        Args:
            data: List of integer values
            count: Number of elements to process
            
        Returns:
            int: Checksum value
        """
        if count <= 0:
            return 0
        return data[count - 1] + self.calculate_checksum(data, count - 1)
    
    def __enter__(self):
        """Context manager entry."""
        self.open_port()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_threaded_communication()

# Backward compatibility alias
AYserial = AYSerial

if __name__ == '__main__':
    # Example usage
    config = AYSerialConfig()
    config.demo_model = 'C'  # Thread mode
    
    serial_comm = AYSerial('/dev/ttyUSB0', 9600, 0.2, config)
    serial_comm.echo_config()
    
    # Set up callbacks
    def on_data_received(data):
        print(f"Received: {data}")
    
    def on_error(error):
        print(f"Error: {error}")
    
    serial_comm.set_data_received_callback(on_data_received)
    serial_comm.set_error_callback(on_error)
    
    try:
        if config.demo_model == 'A':
            # String mode
            with serial_comm:
                serial_comm.send_string('This is test data for AYSerial Library')
                
        elif config.demo_model == 'B':
            # HEX mode
            with serial_comm:
                hex_data = '00 01 20 10'
                if CRC_AVAILABLE:
                    crc = serial_comm.calculate_crc16_modbus(hex_data, False)
                    serial_comm.send_hex(f"{hex_data} {crc}")
                else:
                    serial_comm.send_hex(hex_data)
                    
        elif config.demo_model == 'C':
            # Thread mode
            if serial_comm.start_threaded_communication():
                serial_comm.wait_for_threads()
            else:
                serial_comm.stop_threaded_communication()
                
    except Exception as e:
        serial_comm.logger.error(f'Application error: {e}')
        serial_comm.stop_threaded_communication()
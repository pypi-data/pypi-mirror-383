# -*- coding: utf-8 -*-
__doc__ = 'AYlib module'
__version__ = '0.0.4'
__author__ = 'Aaron Yang <3300390005@qq.com>'
__website__ = 'https://github.com/AaronYang233/AYlib/'
__license__ = 'Copyright © 2015 - 2021 AaronYang.'

import threading
import time
import logging
import string
import queue

from binascii import unhexlify

# Optional imports with fallback
try:
    import serial
    from crcmod import mkCrcFun
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    # Mock serial for when pyserial is not available
    class MockSerial:
        def __init__(self):
            self.port = None
            self.baudrate = None
            self.timeout = 1
            self.is_open = False
            
        def open(self):
            self.is_open = True
            
        def close(self):
            self.is_open = False
            
        def isOpen(self):
            return self.is_open
            
        def write(self, data):
            return len(data)
            
        def readline(self):
            return b""
    
    serial = MockSerial()
    mkCrcFun = lambda *args, **kwargs: lambda data: 0

# Default configuration constants
DEFAULT_MODEL = 'C'
DEFAULT_SEND_FLAG = 0
DEFAULT_RXTX_MODEL = [1, 1]
DEFAULT_USER_DATA = { "{'hello':1}": 95, 'Lisa': 85, 'Bart': 59, 'Paul': 74 }
DEFAULT_USER_ERROR = {'value': -1}

class AYserial:
    def __init__(self, uart_port, uart_baudrate, send_delay=0, 
                 model=DEFAULT_MODEL, send_flag=DEFAULT_SEND_FLAG, 
                 rxtx_model=DEFAULT_RXTX_MODEL, user_data=DEFAULT_USER_DATA):
        if not SERIAL_AVAILABLE:
            self.logger.warning("pyserial not available, using mock serial")
        
        self.my_serial = serial.Serial() if SERIAL_AVAILABLE else serial.MockSerial()
        self.my_serial.port = uart_port
        self.my_serial.baudrate = uart_baudrate
        self.my_serial.timeout = 1
        self.__send_delay = send_delay
        
        # Configuration parameters
        self.model = model
        self.send_flag = send_flag
        self.rxtx_model = rxtx_model
        self.user_data = user_data
        self.read_data_queue = queue.Queue(maxsize=0)

        self.alive = False
        self.waitEnd = None
        
        self.thread_read = None
        self.thread_send = None

        # Setup logging once
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('AYserial.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger('AYserial')

    def AY_Waiting_thread(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()

    def AY_Echo_uartcfg(self):
        print('-----------------')
        print('串口号:%s\n波特率:%d\n发送延时:%d'% (self.my_serial.port,self.my_serial.baudrate,self.__send_delay))
        print('-----------------\n')
    
    def AY_ClosePort_thread(self):
        self.alive = False
        if self.my_serial.isOpen():
            self.my_serial.close()

    def AY_OpenPort_thread(self):
        self.my_serial.open()

        if self.my_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            
            if 1 == self.rxtx_model[1]:
                self.logger.info('AYserial Read Msg Open!')
                self.thread_read = threading.Thread(target=self.AY_Read_Data_thread)
                self.thread_read.setDaemon(True)
                self.thread_read.start()

            if 1 == self.rxtx_model[0]:
                self.logger.info('AYserial Send Msg Open!')
                self.thread_send = threading.Thread(target=self.AY_Send_Data_thread)
                self.thread_send.setDaemon(True)
                self.thread_send.start()

            if 0 == self.rxtx_model[0] and 0 == self.rxtx_model[1]:
                self.logger.info('Serial Msg All Close, Please Open one!')
                self.alive = False
                return False
            return True
        else:
            self.logger.info('AYserial Open Port Error!')
            return False
 
    def AY_Read_Data_thread(self):
        while self.alive:
            try:
                data=self.my_serial.readline().decode('utf-8')
                if data:           
                    self.logger.info('Read Data: %s', data)
                    # recv "qqqqq" quit
                    if len(data) == 5 and ord(data[len(data)-1]) == 113:
                        break
                    if 0 == self.send_flag:
                        self.read_data_queue.put(data)
            except Exception as e:
                self.logger.error('Read Error: %s', e)
                self.waitEnd.set()
                self.alive = False
        self.waitEnd.set()
        self.alive = False

    def AY_Send_Data_thread(self):
        while self.alive:
            try:
                time.sleep(0.1)
                if 0 == self.send_flag:
                    data = self.AY_handle_task()
                if 1 == self.send_flag:
                    data = input("Input Data:")
                if data:
                    self.my_serial.write(data.encode('utf-8'))
                    self.logger.info('Send Data: %s', data)

            except Exception as e:
                self.logger.error('Send Error: %s', e)
                self.waitEnd.set()
                self.alive = False
        self.waitEnd.set()
        self.alive = False

    def AY_OpenPort(self):
        self.my_serial.open()

    def AY_ClosePort(self):
        self.my_serial.close()

    def AY_Read_Data(self):
        data = self.my_serial.readline()
        self.logger.info('AY_Read_Data: %s', data)

    def AY_Send_String_Data(self,Data):
        self.data = Data
        time.sleep(self.__send_delay)
        success_str = self.my_serial.write(self.data.encode())
        self.logger.info('Send len %s, Data: %s', success_str, self.data.encode())

    def AY_Send_Hex_Data(self,Data,check_mode=None,invert=None):
        self.data = Data
        self.check = check_mode
        self.invert = invert

        time.sleep(self.__send_delay)
        buff = self.my_serial.write(bytes.fromhex(self.data))
        self.logger.info('Send len %s, Hex Data: %s', buff, self.data)

    ''' checkes msg'''
    # print(Hex_to_ASCII(0x61))
    # print(ASCII_to_Hex('A'))
    # print(ASCII_to_DEC("!"))
    # print(DEC_to_ASCII(101))

    # data = [0x25,0x30,0x30,0x30,0x38]
    # print(hex(data_sum_checks(data,len(data))))

    def AY_Crc16_Modbus(self,Data,invert):
        self.data = Data
        crc16 = mkCrcFun(0x18005, rev=True, initCrc=0xFFFF,xorOut=0x0000)
        data = self.data.replace(' ', '')
        crc_out = hex(crc16(unhexlify(data))).upper()
        str_list = list(crc_out)
        if len(str_list) == 5:
            str_list.insert(2,'0') 
        crc_data = ''.join(str_list[2:])
        return crc_data[2:]+' '+crc_data[:2] if invert == True else crc_data[:2]+' '+crc_data[2:]

    def AY_Hex_to_ASCII(self,data):
        return chr(data)

    def AY_ASCII_to_Hex(self,data):
        return hex(ord(data))

    def AY_ASCII_to_DEC(self,data):
        return ord(data)

    def AY_DEC_to_ASCII(self,data):
        return chr(data)

    def AY_data_sum_checks(self,data,count):
        if(count ==0 ):
            return 0
        else:
            return data[count - 1] + self.AY_data_sum_checks(data, count - 1)

    """ heartbeat """
    def AY_handle_task(self):
        try:
            while not self.read_data_queue.empty():
                data = self.read_data_queue.get()            
                for k, v in self.user_data.items():
                    if k == data:
                        data = v
                        return str(data)
            pass
        except Exception as e:
            self.logger.error('AY_Handle_Task Error: %s', e)
            pass

if __name__ == '__main__':    
    ser = AYserial('COM4', 9600, 0.2)
    ser.AY_Echo_uartcfg()

    try:
        if not ser.model:
            print("AYserial Class. AaronYang All Rights Reserved")
        else:
            if ser.model == 'A':
                ser.AY_OpenPort()
                ser.AY_Send_String_Data('This is test data for AYserial Library')
                ser.AY_ClosePort()
            if ser.model == 'B':
                ser.AY_OpenPort()
                a = ('00 01 20 10')
                ser.AY_Send_Hex_Data(a + ' ' + ser.AY_Crc16_Modbus(a, 0))
                ser.AY_ClosePort()
            if ser.model == 'C':
                if ser.AY_OpenPort_thread():
                    ser.AY_Waiting_thread()
                    ser.AY_ClosePort_thread()
                else:
                    if ser.alive:
                        ser.AY_ClosePort_thread()
    except Exception as e:
        print(f"Class Exit Error: {e}")

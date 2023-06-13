import socket
import threading
from threading import Event
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import traceback

#threading.Thread
from conf.logconfig import logger

event = Event()

class SocketClient(QThread, QObject):
    ip = ''
    port = 0
    type = ''
    scType = ''
    isRun = False
    client_socket = None

    # 수신 메시지 바인딩
    reciveData = pyqtSignal(bytearray)

    # 연결 상태 log 바인딩
    statLogMsg = pyqtSignal(str)

    # Error log 바인딩
    errorLogMsg = pyqtSignal(str)

    def __init__(self, ip, port, type, scType):
        super().__init__()
        self.name = '{}:{}'.format(ip, port)# 스레드 명
        self.ip = ip
        self.port = port
        self.type = type
        self.scType = scType


    def run(self):
          self.initClient()
          print("Client thread start ", threading.current_thread())


    def initClient(self):
        print('run Thread :: ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))

        logger.info('Client thread start ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, int(self.port)))
            self.isRun = True
            self.statLog('Connection Success')
            # 서버로 부터 메세지 받기
            while self.isRun:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                #self.reciveMsgMethod(data.decode())
                byte_array = bytearray(data)
                self.reciveMsgMethod(byte_array)
        except:
            self.errorLog(traceback.format_exc())


    def sendMsg(self, msg):
        try:
            self.client_socket.send(msg)
        except:
            self.errorLog(traceback.format_exc())

    def reciveMsgMethod(self, msg):
        self.reciveData.emit(msg)

    def closeSocket(self):
        self.isRun = False
        self.client_socket.close()

    def statLog(self, log):
        self.statLogMsg.emit(str(log))

    def errorLog(self, log):
        self.errorLogMsg.emit(str(log))
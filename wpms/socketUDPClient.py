import socket
import threading
from threading import Event
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import traceback
from conf.logconfig import logger

#threading.Thread

event = Event()

class SocketUDPClient(QThread, QObject):
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
          print("Client UDP thread start ", threading.current_thread())


    def initClient(self):
        print('run Thread :: ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))
        logger.info('Client UDP thread start ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))
        try:
            # 클라이언트 쪽에서 UDP 소켓 생성
            self.client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        except:
            self.errorLog(traceback.format_exc())


    def sendMsg(self, msg):
        try:
            self.client_socket.sendto(msg, (self.ip, int(self.port)))
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
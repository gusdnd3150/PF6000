import socket
import threading
from _thread import *
import select
from threading import Event
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random
from conf.logconfig import logger

import traceback

#threading.Thread


event = Event()

class SocketServer(QThread, QObject):
    ip = ''
    port = 0
    type = ''
    scType = ''
    isRun = False
    server_socket = None
    socketClient = None
    client_list = []
    error_list = []
    clientInstance = None
    test = None

    # 수신 메시지 바인딩
    serverReciveData = pyqtSignal(bytearray, str)

    # 송신 메시지 바인딩
    serverSendData = pyqtSignal(str, str)

    # 연결 상태 log 바인딩
    serverStatLogMsg = pyqtSignal(str, str)

    # Error log 바인딩
    serverErrorLogMsg = pyqtSignal(str, str)

    def __init__(self, ip, port, type, scType):
        super().__init__()
        self.name = '{}:{}'.format(ip, port)# 스레드 명
        self.ip = ip
        self.port = port
        self.type = type
        self.scType = scType
        self.client_list = []
        self.client_Obj_list = []



    def run(self):
          self.initServer()
          # print("Server thread start ", threading.current_thread())


    def initServer(self):
        print('run Thread :: ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))
        #logger.info('Server thread start ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))
        try:
            tempClient = {}
            if self.type == 'TCP':
                self.isRun = True

                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind((self.ip, int(self.port)))
                server.listen()
                self.server_socket = server
                self.client_list = [server]
                self.error_list = [server]

                temp = []

                try:
                    newClient = None
                    while self.isRun:
                        readables, writeables, excpetions = select.select(self.client_list, [], self.error_list)

                        for sock in readables:
                            if sock == server:  # 신규 클라이언트 접속
                                newClient, addr = server.accept()

                                self.client_Obj_list.append(newClient)

                                t = threading.Thread(target=self.handle_client, args=(newClient, addr))
                                t.start()
                        for error in excpetions:
                            print(error)

                except:
                    traceback.print_exc()

                    #self.serverErrorLog('Close Server ', '{}:{}'.format(self.ip, str(self.port)))

            elif self.type == 'UDP':
                print('preparing')

        except:
            print('222222222222')
            traceback.print_exc()
            #self.serverErrorLog(traceback.format_exc(), '{}:{}'.format(self.ip, str(self.port)))


    def serverReviceMsgMethod(self, msg, ipPort):
        # self.serverReciveData.emit(msg, ipPort)
        self.serverReciveData.emit(msg, ipPort)


    def serverStatLog(self, log, ipPort):
        self.serverStatLogMsg.emit(str(log),ipPort)

    def serverErrorLog(self, log, ipPort):
        self.serverErrorLogMsg.emit(str(log), ipPort)

    def handle_client(self, conn, addr):
        tempClient = {}
        with conn:
            #self.serverStatLog('Connected',  '{}:{}'.format(addr[0], str(addr[1])))
            #logger.info('New Client Connected',  '{}:{}'.format(addr[0], str(addr[1])))
            while self.isRun:
                try:
                    # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
                    data = conn.recv(1024)
                    if not data:
                        break
                    byte_array = bytearray(data)
                    self.serverReviceMsgMethod(byte_array, '{}:{}'.format(addr[0], str(addr[1])))
                except:
                    conn.close()
                    #self.serverErrorLog('Disconnected ', '{}:{}'.format(addr[0], str(addr[1])))


    def closeSocket(self):

        # for i in range(0, len(self.client_list)):
        #     runningClient = self.client_list.pop(0)
        #     runningClient.close()

        for index in range(0, len(self.client_Obj_list)):
            # if index != 0:  # 0 인덱스는 자기 자신의 주소값이기 때문에 건너뜀
            if self.client_Obj_list[index]._closed == False:
                self.client_Obj_list[index].close()

        self.client_Obj_list.clear()
        self.server_socket.close()
        self.isRun = False
        # self.client_socket.close()
        # self.server_socket.close()

    def sendToClientAll(self, msg):

        try:
            #print(len(self.client_Obj_list))
            #print(self.client_Obj_list)
            for index in range(0, len(self.client_Obj_list)):
                # if index != 0:  # 0 인덱스는 자기 자신의 주소값이기 때문에 건너뜀
                if self.client_Obj_list[index]._closed == False:
                    self.client_Obj_list[index].send(msg)
                    # print(self.client_Obj_list[index].getpeername())
                    ip, port = self.client_Obj_list[index].getpeername()
                    # self.serverSendData.emit(str(''.join(chr(byte) for byte in msg)), ip+":"+str(port))
        except:
            traceback.print_exc()





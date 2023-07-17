import socket
import threading
from _thread import *
import select
from threading import Event
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random

import traceback
from conf.logconfig import logger

#threading.Thread


event = Event()

class SocketUDPServer(QThread, QObject):
    ip = ''
    port = 0
    type = ''
    scType = ''
    isRun = False
    server_socket = None
    socketClient = None
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




    def run(self):
          self.initServer()
          print("Server thread start ", threading.current_thread())


    def initServer(self):
        print('run UDP server Thread :: ip={}, port={}, type={}, scType={}'.format(self.ip, self.port, self.type, self.scType))
        try:

            self.isRun = True

            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.bind((self.ip, int(self.port)))

            self.server_socket = server
            temp = []
            while (True):
                bytesAddressPair = server.recvfrom(1024)
                message = bytesAddressPair[0]
                address = bytesAddressPair[1]

                # Sending a reply to client
                byte_array = bytearray(message)
                self.serverReviceMsgMethod(byte_array, '{}:{}'.format(address, ''))
                #server.sendto('', address)

        except:
            print('UDP SERVER make eception')
            traceback.print_exc()
            self.serverErrorLog('UDP SERVER CLOSED', '{}:{}'.format(self.ip, str(self.port)))


    def serverReviceMsgMethod(self, msg, ipPort):
        print('tttttt1')
        # self.serverReciveData.emit(str(msg), ipPort)
        self.serverReciveData.emit(msg, ipPort)


    def serverStatLog(self, log, ipPort):
        self.serverStatLogMsg.emit(str(log),ipPort)

    def serverErrorLog(self, log, ipPort):
        self.serverErrorLogMsg.emit(str(log), ipPort)

    def handle_client(self, client_socket, client_address):
        self.serverStatLog('UDP CLIENT is Connected', '{}:{}'.format(client_address[0], str(client_address[1])))
        # while True:
        #     data = client_socket.recvfrom(1024)  # 데이터 수신
        #
        #     # 클라이언트로부터 'quit' 메시지를 받으면 클라이언트 소켓 종료
        #     if not data:
        #         break
        #
        #     print(data)
        #     byte_array = bytearray(data)
        #     self.serverReviceMsgMethod(byte_array, '{}:{}'.format(client_address[0], str(client_address[1])))
        #     client_socket.sendto(data, client_address)
        #
        # client_socket.close()

        while True:
            data, address = client_socket.recvfrom(1024)  # 데이터 수신

            # 클라이언트로부터 'quit' 메시지를 받으면 클라이언트 소켓 종료
            if not data:
                break

            print(data)
            byte_array = bytearray(data)
            self.serverReviceMsgMethod(byte_array, '{}:{}'.format(client_address[0], str(client_address[1])))
            client_socket.sendto(data, address)

        client_socket.close()

    def closeSocket(self):

        # for i in range(0, len(self.client_list)):
        #     runningClient = self.client_list.pop(0)
        #     runningClient.close()

        # for index in range(0, len(self.client_list)):
        #     # if index != 0:  # 0 인덱스는 자기 자신의 주소값이기 때문에 건너뜀
        #     self.client_list[index].close()

        self.server_socket.close()
        self.client_list.clear()
        self.isRun = False
        # self.client_socket.close()
        # self.server_socket.close()

    def sendToClientAll(self, msg):

        print(len(self.client_Obj_list))
        print(self.client_Obj_list)

        for index in range(0, len(self.client_Obj_list)):
            #if index != 0:  # 0 인덱스는 자기 자신의 주소값이기 때문에 건너뜀
                if self.client_Obj_list[index]._closed == False:
                    self.client_Obj_list[index].send(msg)
                    print(self.client_Obj_list[index].getpeername())
                    ip, port = self.client_Obj_list[index].getpeername()
                    self.serverSendData.emit(str(msg), ip+":"+str(port))


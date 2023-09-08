
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer

from time import sleep
import sys
import os
import traceback
import json

from conf.logconfig import logger
from wpms.socketClient import SocketClient
from wpms.methodUtils import MethodUtils
from wpms.socketServer import SocketServer
from wpms.socketUDPClient import SocketUDPClient
from wpms.socketUDPServer import SocketUDPServer
from wpms.messageLenDecoder import MessageLenDecoder
import struct


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

print(resource_path('test.ui'))
form = resource_path('test.ui')
form_class = uic.loadUiType(form)[0]



# 콤보 영역
scCombo = ['CLIENT', 'SERVER']
typeCombo = ['TCP', 'UDP']

width = 580
height = 500


class InitWindow(QMainWindow, form_class):

    colorSuccess = QColor(57, 110, 255)
    colorFail = QColor(255, 11, 64)
    colorWhite = QColor(255, 255, 255)
    sendMsg = []
    reciveMsg = ''
    socketList = []
    methodUtils = None

    timer = None

    isRunClient = False
    isRunServer = False
    msgDecoder = None

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setFixedSize(width, height)
        self.initUI()
        self.setWindowTitle("PF6000 테스터")
        self.show()


    # 이벤트, 변수 바인딩
    def initUI(self):

    
        self.START.clicked.connect((self.uiStart))
        self.setComboMethod()
        #         # Button/chk box등 기능 연결
        # self.pingBt.clicked.connect((self.pingBtMethod))
        # self.bindBt.clicked.connect((self.bindBtMethod))
        # # self.msgAddBt.clicked.connect((self.msgAddBtMethod))
        # self.sendBt.clicked.connect((self.sendBtMethod))
        # self.cleanMsgBtn.clicked.connect(self.cleanMsgMethod)
        # self.clearBt2.clicked.connect(self.cleanMsgMethod2)
        #
        # self.msgReload.clicked.connect((self.reloadMsg))
        # self.deletesaveMsg.clicked.connect((self.deleteMsg))
        #
        # # 메시지 추가 버튼들
        # self.btnString.clicked.connect(self.addString)
        # self.btnInt.clicked.connect(self.addInt)
        # self.btnShort.clicked.connect(self.addShort)
        # self.btnByte.clicked.connect(self.addByte)
        # self.btnDouble.clicked.connect(self.addDouble)
        # self.btnJson.clicked.connect(self.addJson)
        #
        #
        #
        # self.saveMsg.clicked.connect((self.saveMsgMethod))
        #
        # # ComboBox에 기능 연결
        # self.typeCombo.currentIndexChanged.connect((self.onchangeType))
        # self.scCombo.currentIndexChanged.connect((self.onchangeScType))
        # self.msgSavedList.currentIndexChanged.connect((self.onChangeSaveMsgCombo))
        # self.qtMsgList.currentIndexChanged.connect((self.changeMsgListCombo))
        #
        # self.nullCheckBox.stateChanged.connect((self.nullCheckBoxMethod))
        # self.decodeYn.stateChanged.connect((self.decodeYnMethod))
        #
        #
        # # onChange 기능 연결
        # self.msgArea.textChanged.connect(self.textChange)


    # start 버튼
    def uiStart(self):
        ip = self.IP.text()
        port = self.PORT.text()
        flag = self.START.text().upper()
        protocol = self.TYPES.currentText()
        skInfo = {}

        try:
            if flag == 'START':
                self.START.setText('End')
                if self.isRunServer == True:
                    return

                if protocol == 'TCP':
                    toolSk = SocketServer(ip, port, protocol, flag)
                    toolSk.damon = True
                    toolSk.start()
                    toolSk.serverReciveData.connect(self.serverReciveDataMethod)

                    skInfo['SK_INFO'] = toolSk
                    skInfo['SK_TYPE'] = 'SERVER'
                    self.socketList.append(skInfo)
                    self.isRunServer = True
                    self.lockTargetYn('Y')
                    self.timer = QTimer()
                    self.timer.start(2000)
                    self.timer.timeout.connect(self.fnKeepalive)  # 스케줄링할 작업을 연결합니다

                   
                elif protocol =='UDP':
                    toolSk = SocketUDPServer(ip, port, protocol, flag)
                    toolSk.damon = True
                    toolSk.start()
                    skInfo['SK_INFO'] = toolSk
                    skInfo['SK_TYPE'] = 'SERVER'
                    self.socketList.append(skInfo)
                    self.isRunServer = True
                    self.lockTargetYn('Y')
                    self.timer = QTimer()
                    self.timer.setInterval(2000)
                    self.timer.timeout.connect(self.fnKeepalive)  # 스케줄링할 작업을 연결합니다
                    self.timer.start(0)



            elif flag == 'END':
                for i in range(0, len(self.socketList)):
                    item = self.socketList.pop(0)
                    item['SK_INFO'].closeSocket()
                self.START.setText('Start')
                self.isRunServer = False
                self.lockTargetYn('N')
                self.timer.stop()
            
        except:
            self.START.setText('Start')
            self.isRunServer = False
            self.timer.stop()
            self.lockTargetYn('N')
            traceback.print_exc()
        


    def setComboMethod(self): # 콤보 세팅
        for i in typeCombo:
            self.TYPES.addItem(i)



    # 킵어라이브 송신
    def fnKeepalive(self):
        msgEncoded = '00209999001000000000'
        msg = bytearray(msgEncoded, 'utf-8')
        self.sendMsgForAllClient(msg)


    def sendMsgForAllClient(self, msgBytes):
        msgBytes.append(0x00) # 딜리미터 추가
        for item in self.socketList:
            if item['SK_TYPE'] == 'SERVER':
                item['SK_INFO'].sendToClientAll(msgBytes)

    def msgAddBtMethod(self):
        msgTy = self.msgTyCombo.currentText()
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:

            if msgTy == 'JSON':
                jsonDataList = json.loads(msg)
                for i in range(0, len(jsonDataList)):
                    msgObj = {'MSG_TY': jsonDataList[i]['MSG_TY'], 'VALUE': jsonDataList[i]['VALUE'],  'VAL_LEN': jsonDataList[i]['VAL_LEN']}
                    self.msgList.append(str(jsonDataList[i]['VALUE']))
                    self.sendMsg.append(msgObj)
            else:
                msgTemp = {}
                msgTemp['MSG_TY'] = msgTy
                msgTemp['VALUE'] = msg

                self.sendMsg.append(msgTemp)
                self.msgList.append(msg)
        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR', ' ',' Msg Type error'])


    def converForSend(self, msgTy, msg):
        temp = []
        print('msg::' + msg)
        if msgTy == 'string':
            for i in range(len(str(msg))):
                temp.append(ord(msg[i]))
                print('string')
                print(temp)
            return temp

        elif msgTy == 'int':
            value = int(msg)
            intBytes = value.to_bytes(4, byteorder='big')
            for i in range(0, len(intBytes)):
                temp.append(intBytes[i])
            print('int')
            print(intBytes)
            return temp

        elif msgTy == 'short':
            value = int(msg)
            shortValue = value & 0xffff
            shortBytes = shortValue.to_bytes(2,byteorder='big', signed=True)
            for i in range(0, len(shortBytes)):
                temp.append(shortBytes[i])
            print('short')
            print(temp)
            return temp

        elif msgTy == 'byte':
            temp.append(int(msg))
            print('byte')
            print(temp)
            return temp

        elif msgTy == 'double':
            # doubleVal = None
            print('더블 변수 체크')
            print(type(msg))
            if type(msg) == str:
                doubleVal = float(msg)
            else:
                doubleVal = int(msg)

            print('더블 변수 체크')
            print(float(msg))

            # 자바는 64비트 IEEE 754 표준을 사용하여 double 값을 표현하고, 파이썬은 64비트 부동 소수점 형식을 사용합니다.
            # 따라서 자바와 통신할때에는 아래 포맷을 거쳐야한다.
            bytes_data = struct.pack('!d', float(doubleVal))
            #bytes_data = struct.pack('!d', float(doubleVal)) 파이선끼리 통신할 경우
            print(bytes_data)
            for i in range(0, len(bytes_data)):
                temp.append(bytes_data[i])

            return temp

        elif msgTy == 'long':
            doubleVal = None
            if type(msg) == str:
                doubleVal = float(msg)
            else:
                doubleVal = msg
            bytes_data = struct.pack('d', doubleVal)
            print(bytes_data)
            for i in range(0, len(bytes_data)):
                temp.append(bytes_data[i])

            return temp

    def converForSend22(self, msgTy, msg):
        temp = []
        #print('msg::' + msg)

        try:

            if msgTy == 'STRING':
                return msg.encode('utf-8')

            elif msgTy == 'INT':
                value = 0
                if type(msg) == str:
                    value = int(msg)
                else:
                    value = msg
                return value.to_bytes(4, byteorder='big')

            elif msgTy == 'SHORT':
                if type(msg) == str:
                    value = int(msg)
                else:
                    value = msg

                shortValue = value & 0xffff
                return shortValue.to_bytes(2,byteorder='big', signed=True)

            elif msgTy == 'BYTE':
                if type(msg) == int:
                    decimal_value = msg
                    byte_array = decimal_value.to_bytes(1, byteorder='big')
                    return byte_array
                # elif msg.isdigit():  # 입력값이 숫자인 경우
                #     decimal_value = int(msg)
                #     byte_array = decimal_value.to_bytes(4, byteorder='big')
                #     return byte_array
                else:  # 입력값이 문자열인 경우
                    return msg.encode('utf-8')



            elif msgTy == 'DOUBLE':
                try:
                    fval = float(msg)
                    return struct.pack('!d', fval)
                except ValueError:
                    return struct.pack('!d', msg)

                # fval = float(msg)
                # # 자바는 64비트 IEEE 754 표준을 사용하여 double 값을 표현하고, 파이썬은 64비트 부동 소수점 형식을 사용합니다.
                # # 따라서 자바와 통신할때에는 아래 포맷을 거쳐야한다.
                # # bytes_data = struct.pack('!d', fval)
                # # bytes_data = struct.pack('d', float(doubleVal)) 파이선끼리 통신할 경우
                #
                # return struct.pack('!d', fval)

            elif msgTy == 'LONG':
                doubleVal = None
                if type(msg) == str:
                    doubleVal = float(msg)
                else:
                    doubleVal = msg
                bytes_data = struct.pack('d', doubleVal)
                print(bytes_data)
                for i in range(0, len(bytes_data)):
                    temp.append(bytes_data[i])

                return temp

        except:
            logger.info('PARSING MSG JSON FORMAT ERROR !!!')

    def sendBtMethod(self):
        # msgEncoded = []
        msgEncoded = bytearray()
        msg = []
        try:
            # HTTP 통신일 경우========================
            if self.typeCombo.currentText() == 'REST':
                temp = json.loads(self.msgList.toPlainText())
                if temp['METHOD'] == 'POST':

                    if temp['HEADER']['Content-Type'] == 'multipart/form-data;':
                        # response = self.methodUtils.requestPostMultiPartForm(self.msgList.toPlainText(), self.ipInput.text(), self.fileObj)
                        # self.inputTableRow(['RESPONSE', self.ipInput.text(), response])
                        return
                    else:
                        # response = self.methodUtils.requestPost(self.msgList.toPlainText(), self.ipInput.text())
                        # self.inputTableRow(['RESPONSE', self.ipInput.text(), response])
                        return
                elif temp['METHOD'] == 'GET':
                    # response = self.methodUtils.requestGet(self.msgList.toPlainText(), self.ipInput.text())
                    # self.inputTableRow(['RESPONSE', self.ipInput.text(), response])
                    return


            # TCP 통신일 경우========================
            if len(self.sendMsg) > 0:
                for i in range(0, len(self.sendMsg)):
                    indexItem = self.sendMsg[i]
                    msg.append(indexItem['VALUE'])
                    temp = self.converForSend22(indexItem['MSG_TY'], indexItem['VALUE'])

                    msgEncoded.extend(temp)
                    print('msgEncoded', msgEncoded)


            if len(msgEncoded) < 0:
                return

            # 딜리미터 자동 삽입 0x00
            if self.nullCheckBox.isChecked():
                nullDelemeter = 0
                msgEncoded.extend(nullDelemeter.to_bytes(1, byteorder='big'))

            # 클라리언트 시 전송
            if self.isRunClient:


                self.sk.sendMsg(msgEncoded)

                #self.inputTableRow(['OUT', '{}:{}'.format(self.ipInput.text(), self.portInput.text()), str(self.sendMsg)])
                self.inputTableRow(['OUT', '{}:{}'.format(self.ipInput.text(), self.portInput.text()), str(''.join(chr(byte) for byte in msgEncoded))])

                logger.info('SEND TO SERVER BYTE:' + str(''.join(chr(byte) for byte in msgEncoded)))
                #self.inputTableRow(['OUT', '{}:{}'.format(self.ipInput.text(), self.portInput.text()), " ".join(map(str, msg))])


            # 서버 바인드 시 전송
            elif self.isRunServer:
                serverTemp = []
                for item in self.socketList:
                    if item['SK_TYPE'] == 'SERVER':
                        serverTemp.append(item['SK_INFO'])

                for item in serverTemp:
                    print('send data')
                    item.sendToClientAll(msgEncoded)

                logger.info('SEND TO CLIENT BYTE:' + str(''.join(chr(byte) for byte in msgEncoded)))
                #self.inputTableRow(['OUT', '{}:{}'.format(self.ipInput.text(), self.portInput.text()), str(self.sendMsg)])
                # self.sk.sendMsg(bytes(msgEncoded))




        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR','{}:{}'.format(self.ipInput.text(), self.portInput.text()), traceback.format_exc()])
            print('send exception')
            if self.isRunClient:
                self.inputTableRow(['ERROR', '{}:{}'.format(self.ipInput.text(), self.portInput.text()),                                    'Check the IP/PORT conection status'])

            elif self.isRunServer:
                print()

        finally:
            self.sendMsg.clear()
            self.cleanMsgMethod2()




    def bindBtMethod(self):
        ip = self.ipInput.text()
        port = self.portInput.text()
        type = self.typeCombo.currentText()
        scType = self.scCombo.currentText()
        btnText  = self.bindBt.text()




        if self.isRunClient:
            try:
                for i in range(0, len(self.socketList)):
                    item = self.socketList.pop(0)
                    item['SK_INFO'].closeSocket()
            except:
                traceback.print_exc()
            finally:
                self.isRunClient = False
                self.bindBt.setText('Connect')
                self.lockTargetYn('N')
            return


        elif self.isRunServer:
            try:
                for i in range(0, len(self.socketList)):
                    item = self.socketList.pop(0)
                    item['SK_INFO'].closeSocket()
            except:
                traceback.print_exc()
            finally:
                self.isRunServer = False
                self.bindBt.setText('Bind')
                self.lockTargetYn('N')
            return


        logger.info('ip={}, port={}, type={}, scType={}'.format(ip, port, type, scType))
        skInfo = {}
        self.socketList.clear()

        if scType == 'CLIENT':
            try:
                # 소켓리스트 확인


                # 소켓 클라이언트 인스턴스 생성
                if type == 'UDP':
                    self.sk = SocketUDPClient(ip, port, type, scType)
                elif type == 'TCP':
                    self.sk = SocketClient(ip, port, type, scType)

                #self.sk = SocketClient(ip, port, type, scType)
                # thread 시작
                self.sk.damon = True
                self.sk.start()

                # 소켓 인스턴스 저장
                skInfo['SK_INFO'] = self.sk
                skInfo['SK_TYPE'] = scType
                self.socketList.append(skInfo)

                # 클라이언트 이벤트 바인딩
                self.sk.reciveData.connect(self.reciveData)
                self.sk.statLogMsg.connect(self.statLog)
                self.sk.errorLogMsg.connect(self.errLog)
                self.lockTargetYn('Y')

                # running 상태 수정
                self.isRunClient = True
                self.bindBt.setText('Close')
                
            except:
                traceback.print_exc()
                self.socketList.clear()
                self.lockTargetYn('N')
                self.inputTableRow(['ERROR', '{}:{}'.format(self.ipInput.text(), self.portInput.text()) ,'Connection Error'])

        elif scType == 'SERVER':

            try:

                if type == 'UDP':
                    self.sk = SocketUDPServer(ip, port, type, scType)
                elif type == 'TCP':
                    self.sk = SocketServer(ip, port, type, scType)

                # thread 시작
                self.sk.damon = True
                self.sk.start()

                # 소켓 인스턴스 저장
                skInfo['SK_INFO'] = self.sk
                skInfo['SK_TYPE'] = scType
                self.socketList.append(skInfo)

                # 서버 이벤트 바인딩
                self.sk.serverReciveData.connect(self.serverReciveDataMethod)
                self.sk.serverStatLogMsg.connect(self.serverStatLogMethod)
                self.sk.serverErrorLogMsg.connect(self.serverErrorLogMethod)
                self.sk.serverSendData.connect(self.serverSendDataMethod)

                self.lockTargetYn('Y')

                # running 상태 수정
                self.isRunServer = True
                self.bindBt.setText('Close')

            except:
                traceback.print_exc()
                self.socketList.clear()
                #self.inputTableRow(['ERROR', '{}:{}'.format(self.ipInput.text(), self.portInput.text()) , 'Bind Error'])


    def lockTargetYn(self, Yn):
        if Yn == 'Y':
            self.IP.setReadOnly(True)
            self.PORT.setReadOnly(True)
            self.TYPES.setEnabled(False)

            self.KEEPALIVE.setReadOnly(True)
            self.MINANG.setReadOnly(True)
            self.MAXANG.setReadOnly(True)
            self.MINTOR.setReadOnly(True)
            self.MAXTOR.setReadOnly(True)
        else:
            self.IP.setReadOnly(False)
            self.PORT.setReadOnly(False)
            self.TYPES.setEnabled(True)
            self.KEEPALIVE.setReadOnly(False)
            self.MINANG.setReadOnly(False)
            self.MAXANG.setReadOnly(False)
            self.MINTOR.setReadOnly(False)
            self.MAXTOR.setReadOnly(False)


    @pyqtSlot(bytearray)  # 클라이언트 커넥션 후 메시지 invoke 함수
    def reciveData(self, msgBytes):

        # 해더 기준으로
        if self.decodeYn.isChecked():
            result = self.msgDecoder.decodeByHeader(msgBytes, self.headerCombo.currentText())
            logger.info('RECIVE FROM SERVER BYTE:' + str(result))
            self.inputTableRow(['IN', self.portInput.text(), str(result)])

            return
        
        # json 포맷 기준으로
        if self.readHeader.isChecked():
            self.parsingReciveData(msgBytes, self.portInput.text())
            # jsonDataList = json.loads(self.msgArea.toPlainText())
            # result = self.msgDecoder.decodeByJsonFormat(msgBytes, jsonDataList)
        else:
            # self.inputTableRow(['IN', '{}:{}'.format(self.ipInput.text(), self.portInput.text()) , str(msgBytes)])
            logger.info('RECIVE FROM SERVER BYTE:' + str(''.join(chr(byte) for byte in msgBytes)))
            self.inputTableRow(['IN', self.portInput.text(), str(''.join(chr(byte) for byte in msgBytes))])

    @pyqtSlot(str)  # 클라이언트 커넥션 후 상태메시지 invoke 함수
    def statLog(self, test):
        self.isRunClient = True
        self.bindBt.setText('Close')
        now = datetime.now()
        self.inputTableRow(['LOG','{}:{}'.format(self.ipInput.text(), self.portInput.text()) , test])

        #self.reciveMsgArea.append('[ {} ]  {}'.format(now.strftime('%H:%M:%S'), test))

    @pyqtSlot(str)  # 클라이언트 커넥션 후 상태메시지 invoke 함수
    def errLog(self, test):
        self.isRunClient = False
        self.bindBt.setText('Connect')
        self.lockTargetYn('N')
        now = datetime.now()
        self.inputTableRow(['ERROR', '{}:{}'.format(self.ipInput.text(), self.portInput.text()), test])

        # self.reciveMsgArea.append('[ {} ]  {}'.format(now.strftime('%H:%M:%S'), test))


    def sendPf6000Msg(self,mid,bytes):

        if(mid=='0061'):
            print('최신작업결과 송신')
            # 슬레쉬 기준으로 각 데이터 파싱 필요
            #             0            1    2       3     4   5 ...
            msg0061 = '023100610010/010000/0200/030000000/04/0500/06000/070000/080000/091/101/111/12000000/13000000/14000000/15000000/1600000/1700000/1800000/1900000/202023-09-06:08:34:21/210000-00-00:00:00:00/222/230000004346'
            # 0:해더영역,  1:cellId , 2:channelId , 3: 컨트롤러이름
            temp = msg0061.split('/')



        elif(mid=='0000'):
            print('')
    @pyqtSlot(bytearray, str)
    def serverReciveDataMethod(self, msgBytes, ipPort):

        start_index = 4
        length = 4
        midBytes = msgBytes[start_index:start_index + length]
        byte_data = bytes(midBytes)
        strMid = byte_data.decode('utf-8') # MID 추출

        self.LOG.append(strMid)
        if(strMid == '0060'): # 마지막 작업결과 구독 요청   리턴: 0005 + mid 0060
            print('request MID ::'+strMid)
            msgEncoded = '002400050010000000000060'
            msg = bytearray(msgEncoded, 'utf-8')
            self.sendMsgForAllClient(msg)

        elif(strMid == '0062'): # 작업결과 송신응답
            print('request MID ::'+strMid)

        elif (strMid == '0064'):  # 특정 작업결과 요청  리턴: 0065
            print('request MID ::' + strMid)

        elif (strMid == '0001'):  # 통신시작 응답   리턴: 0002
            print('request MID ::' + strMid)
            msgEncoded = '00200002000000000000'
            msg = bytearray(msgEncoded, 'utf-8')
            self.sendMsgForAllClient(msg)

        elif (strMid == '0080'):  # 시간 동기화 리턴:0005 + mid
            print('request MID ::' + strMid)

        elif (strMid == '0082'):  # 시간 동기화 리턴:0005 + mid
            print('request MID ::' + strMid)

        elif (strMid == '9999'):  # 킵어라이브 수신   리턴:
            print('request MID ::' + strMid)


    @pyqtSlot(str, str)
    def serverStatLogMethod(self, revicevLog, ipPort):
        self.isRunServer = True
        self.bindBt.setText('Close')
        now = datetime.now()
        self.inputTableRow(['LOG', ipPort, revicevLog])

    @pyqtSlot(str, str)
    def serverSendDataMethod(self, msg , ipPort):
        self.inputTableRow(['OUT',ipPort,  msg ])


    @pyqtSlot(str, str)
    def serverErrorLogMethod(self,revicevLog ,ipPort):
        self.isRunServer = False
        self.bindBt.setText('Bind')
        self.lockTargetYn('N')
        now = datetime.now()
        self.inputTableRow(['ERROR', ipPort, revicevLog])


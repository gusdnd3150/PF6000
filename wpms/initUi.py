
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
from datetime import datetime

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
typeCombo = ['TCP']

width = 1107
height = 430


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
    isDone = False

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setFixedSize(width, height)
        self.initUI()
        self.setWindowTitle("[아틀라스 콥코] PF6000 테스터")
        self.show()


    # 이벤트, 변수 바인딩
    def initUI(self):

    
        self.START.clicked.connect((self.uiStart))
        #self.btnByte.clicked.connect(self.addByte)  # 전송 버튼
        self.setComboMethod()
        self.RESULTSEND.clicked.connect((self.sendRslt))


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
        #self.LOG.append('[OUT]    :: ' + msgEncoded)
        #self.sendMsgForAllClient(msg)


    def sendMsgForAllClient(self, msgBytes):
        msgBytes.append(0x00) # 딜리미터 추가
        for item in self.socketList:
            if item['SK_TYPE'] == 'SERVER':
                item['SK_INFO'].sendToClientAll(msgBytes)

    # 체결결과 송신 버튼
    def sendRslt(self, bytes):
        if(self.isRunServer == False):
            return

        curBody = self.BODY.text()
        curJob = self.JOB.text()
        print('CURRENT  :: ' + curBody +'///'+ curJob)
        self.sendPf6000Msg('0061')

        if(curBody == ''):
            return
        elif(curJob == ''):
            return


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



    def lockTargetYn(self, Yn):
        if Yn == 'Y':
            self.IP.setReadOnly(True)
            self.PORT.setReadOnly(True)
            self.TYPES.setEnabled(False)

            #self.KEEPALIVE.setReadOnly(True)
            self.BATCHSIZE.setReadOnly(True)
            self.MINANG.setReadOnly(True)
            self.MAXANG.setReadOnly(True)
            self.MINTOR.setReadOnly(True)
            self.MAXTOR.setReadOnly(True)
        else:
            self.IP.setReadOnly(False)
            self.PORT.setReadOnly(False)
            self.TYPES.setEnabled(True)
            #self.KEEPALIVE.setReadOnly(False)
            self.BATCHSIZE.setReadOnly(False)
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

    def lpad(self, input_string, length, padding_char):
        if len(input_string) >= length:
            return input_string
        else:
            padding_length = length - len(input_string)
            padding = padding_char * padding_length
            return padding + input_string


    def rpad(self, input_string, length, padding_char):
        if len(input_string) >= length:
            return input_string
        return input_string + (padding_char * (length - len(input_string)))

    # 아틀라스콥코 응답 처리
    def sendPf6000Msg(self,mid):
        try:

            minAng = self.MINANG.value()
            maxAng = self.MAXANG.value()
            minTorque = int(self.MINTOR.value()*100)
            maxTorque = int(self.MAXTOR.value()*100)
            ang = self.ANGLE.value()
            tor = int(self.TORQUE.value()*100)


            isPass = True

            if(mid=='0061'):
                print('최신작업결과 송신')
                # 슬레쉬 기준으로 각 데이터 파싱 필요
                #             0                     1    2       3                               4                      5 ...
                #msg0061 = '023100610010        /010000/0200/030000000                  /04                         /0500/06000/070000/080000/091/101/111/12000000/13000000/14000000/15000000/1600000/1700000/1800000/1900000/202023-09-06:08:34:21/210000-00-00:00:00:00/222/230000004346'

                header_0 = '023100610010        '
                cellId_1 = '01'+self.rpad('0000', 4, ' ')
                channelId_2 = '02'+self.rpad('00', 2, ' ')
                ctrlName_3 = '03'+self.rpad(self.IP.text(), 25, ' ')

                vinStr = ''
                jobStr = '1'
                batCntStr = '0'
                if(self.BODY.text() != ''):
                    vinStr = self.BODY.text()
                if(self.JOB.text() != ''):
                    jobStr = self.JOB.text()

                if (self.BATCHCNT.text() == ''):
                    batCntStr = '01'
                    print('ddddd' + batCntStr)
                else:
                    print('sssss' + batCntStr)
                    batCntStr = self.BATCHSIZE.text()


                vinNo_4 = '04'+self.rpad(vinStr, 25, ' ')
                jobId_5 = '05'+self.rpad(jobStr, 2, '0')
                # parameterSet_6 = '06' + self.rpad('000', 3, ' ')   # pset_id
                parameterSet_6 = '06' + self.lpad(str(self.PSET.value()), 3, '0')  # pset_id
                batchSize_7 = '07' + self.lpad(self.BATCHSIZE.text(), 4, '0')
                batchCnt_8  = '08' + self.lpad(batCntStr, 4, '0')



                torStat_10 = ''
                if(tor >= minTorque and tor <= maxTorque):
                    torStat_10 = '101'
                elif(tor < minTorque):
                    torStat_10 = '100'
                    isPass = False
                elif (tor > maxTorque):
                    torStat_10 = '102'
                    isPass = False
                else:
                    torStat_10= '100'
                    isPass = False

                angStat_11 = ''
                if (ang >= minAng and ang <= maxAng):
                    angStat_11 = '111'
                elif (ang < minAng):
                    angStat_11 = '110'
                    isPass = False
                elif (ang > maxAng):
                    angStat_11 = '112'
                    isPass = False
                else:
                    angStat_11 = '110'
                    isPass = False

                if(isPass == False):
                    tighteningRslt_9 = '090'  # 확인필요
                else:
                    tighteningRslt_9 = '091'  # 확인필요

                minTorque_12 = '12'+self.lpad(str(minTorque), 6, '0')
                maxTorque_13 = '13'+self.lpad(str(maxTorque), 6, '0')

                torqueFnTarget_14 = '14000000'  # 확인필요

                tor_15 = '15'+self.lpad(str(tor), 6, '0')

                minAng_16 = '16' + self.lpad(str(minAng), 5, '0')
                maxAng_17 = '17' + self.lpad(str(maxAng), 5, '0')

                angFnTarget_18 = '1800000'  # 확인필요

                ang_19 = '19' + self.lpad(str(ang), 5, '0')

                now = datetime.now()
                timeStamp_20 = '20'+now.strftime("%Y-%m-%d:%H:%M:%S")
                timeStamp_21 = '21'+now.strftime("%Y-%m-%d:%H:%M:%S")
                batchStat_22 = ''

                if(int(batCntStr) == int(self.BATCHSIZE.value()) and isPass == True):
                    batchStat_22 = '221'
                else:
                    batchStat_22 = '220'

                # 마이크로초 정보를 추가합니다.
                microseconds = now.microsecond
                # 마이크로초를 6자리로 맞춰줍니다.
                microseconds_str = str(microseconds).zfill(10)
                tighteningId_23 = '23'+str(microseconds_str)


                rlstMsg = header_0+cellId_1+channelId_2+ctrlName_3+vinNo_4+jobId_5+parameterSet_6+batchSize_7+batchCnt_8+tighteningRslt_9\
                          +torStat_10+angStat_11+minTorque_12+maxTorque_13+torqueFnTarget_14+tor_15+minAng_16+maxAng_17+angFnTarget_18+ang_19+timeStamp_20\
                            +timeStamp_21+batchStat_22+tighteningId_23
                print(rlstMsg)
                msgByte = bytearray(rlstMsg, 'utf-8')
                print(len(msgByte))
                self.LOG.append('[OUT]    :: ' + rlstMsg)
                self.sendMsgForAllClient(msgByte)

                logger.info('체결결과 Send :: ' + rlstMsg)
                batchSize = int(self.BATCHSIZE.value())
                batchCnt = int(batCntStr)
                print('배치 비교 ::'+ str(batchSize))
                print('배치 비교 ::' + str(batchCnt))

                if (batchSize != batchCnt and isPass == True):
                    print('잡수정 패스 :: ')
                    self.BATCHCNT.setText(self.lpad(str(int(batCntStr) + 1), 2, '0'))

                print('잡 패스 :: '+ str(isPass))

            elif(mid=='0005'):
                print('')
                msgEncoded = '00240005001000000000' + mid
                msg = bytearray(msgEncoded, 'utf-8')
                self.sendMsgForAllClient(msg)
        except:
            traceback.print_exc()

    def convertPf6000Msg(self, mid, bytes):

        defaultHdLen = 20  # 해더 길이
        reuslt = ""

        if (mid == '0050'):  # 25자리 BODY_NO 파싱
            reuslt = bytes[defaultHdLen:defaultHdLen+10].decode('utf-8')
        elif (mid == '0038' or mid == '0039'): # 2자리 JOB_ID 파싱
            reuslt = bytes[defaultHdLen:defaultHdLen+2].decode('utf-8')

        return reuslt.strip()


    #0005는 요청에대한 응답 메시지
    @pyqtSlot(bytearray, str)
    def serverReciveDataMethod(self, msgBytes, ipPort):
        try:
            self.LOG.append('[IN]    :: ' + msgBytes.decode('utf-8'))
            retunr0005 = False
            start_index = 4
            length = 4
            midBytes = msgBytes[start_index:start_index + length]
            byte_data = bytes(midBytes)
            strMid = byte_data.decode('utf-8') # MID 추출


            if(strMid == '0060'): # 마지막 작업결과 구독 요청   리턴: 0005 + mid 0060
                print('request MID ::'+strMid)
                retunr0005 = True

            elif(strMid == '0062'): # 작업결과 송신 응답
                print('request MID ::'+strMid)
                # print('request body ::' + msgBytes)

            elif (strMid == '0064'):  # 특정 작업결과 요청  리턴: 0065
                print('request MID ::' + strMid)

            elif (strMid == '0001'):  # 통신시작 응답   리턴: 0002
                print('request MID ::' + strMid)
                msgEncoded = '00200002001000000000'  # //PF6000
                #msgEncoded = '00200002   000000000' #//PF6000
                # msgEncoded = '00200002000000000000' #//PF4000

                msg = bytearray(msgEncoded, 'utf-8')
                self.LOG.append('[OUT] : ' + msgEncoded)
                self.sendMsgForAllClient(msg)

            elif (strMid == '0080'):  # 시간 동기화 리턴:0005 + mid
                print('request MID ::' + strMid)

            elif (strMid == '0082'):  # 시간 동기화 리턴:0005 + mid
                print('request MID ::' + strMid)

            elif (strMid == '0050'):  # BODY_NO 수신
                print('request MID ::' + strMid)
                self.TORQUE.setValue(0.0)
                self.ANGLE.setValue(50)
                retunr0005 = True
                self.isDone = False

                bodyNO = self.convertPf6000Msg(strMid,msgBytes)
                self.BODY.setText(bodyNO)

            elif (strMid == '0038' or strMid == '0039' ):  # JOB_ID 수신
                print('request MID ::' + strMid)
                self.TORQUE.setValue(0.0)
                self.ANGLE.setValue(50)
                self.isDone = False
                self.BATCHCNT.setText(self.lpad('1', 2 ,'0'))
                retunr0005 = True

                jobId = self.convertPf6000Msg(strMid, msgBytes)
                self.JOB.setText(jobId)

            elif (strMid == '9999'):  # 킵어라이브 수신   리턴:
                msgEncoded = '00209999001000000000'
                msg = bytearray(msgEncoded, 'utf-8')
                self.LOG.append('[OUT]    :: ' + msgEncoded)
                self.sendMsgForAllClient(msg)



            if(retunr0005):
                msgEncoded = '00240005001000000000' + strMid
                msg = bytearray(msgEncoded, 'utf-8')
                self.LOG.append('[OUT] :: ' + str(msgEncoded))
                self.sendMsgForAllClient(msg)
        except:
            traceback.print_exc()

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


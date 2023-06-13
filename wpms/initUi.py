
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
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
typeCombo = ['TCP', 'UDP', 'WEBSOCKET']
msgTyCombo = ['STRING','INT','SHORT','DOUBLE','BYTE','JSON']
headerList = ['H4','H6']
contentTyCombo = ['application/json']


h6Form= [
        {'msgTy':'string','value':''}
    ]

defaultForm = {
    'METHOD':'POST',
    'HEADER': {
        'Content-Type': 'application/json'
    },
    'BODY': {
        'test': ''
    }
}

multipartForm = {
    'METHOD':'POST',
    'HEADER': {
        'Content-Type': 'multipart/form-data;'
    },
    'BODY': {
        'test': ''
    },
    'FILE':{

    }
}

width = 1000
height = 800


class InitWindow(QMainWindow, form_class):

    colorSuccess = QColor(57, 110, 255)
    colorFail = QColor(255, 11, 64)
    colorWhite = QColor(255, 255, 255)
    sendMsg = []
    reciveMsg = ''
    socketList = []
    methodUtils = None

    isRunClient = False
    isRunServer = False
    rowCount = 0
    maxRowCount = 23
    fileObj = {'fileNm':'', 'file':''}

    targetJson = []

    jsonList = []
    targetHeaer=[]

    msgHdList = []
    msgIdList = []

    msgDecoder = None

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.setFixedSize(width, height)
        self.initUI()
        self.setWindowTitle("무슈캉 v1.0.0")
        self.show()


    # 이벤트, 변수 바인딩
    def initUI(self):

        print()
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



    def addString(self):
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:
                msgTemp = {}
                msgTemp['MSG_TY'] = 'STRING'
                msgTemp['VALUE'] = msg

                self.sendMsg.append(msgTemp)
                self.msgList.append(msg)
                self.msgArea.clear()
        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR', ' ', ' Msg Type error'])


    def addInt(self):
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:
                msgTemp = {}
                msgTemp['MSG_TY'] = 'INT'
                msgTemp['VALUE'] = msg

                self.sendMsg.append(msgTemp)
                self.msgList.append(msg)
                self.msgArea.clear()
        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR', ' ', ' Msg Type error'])

    def addShort(self):
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:
            msgTemp = {}
            msgTemp['MSG_TY'] = 'SHORT'
            msgTemp['VALUE'] = msg

            self.sendMsg.append(msgTemp)
            self.msgList.append(msg)
            self.msgArea.clear()
        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR', ' ', ' Msg Type error'])

    def addByte(self):
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:
            msgTemp = {}
            msgTemp['MSG_TY'] = 'BYTE'
            msgTemp['VALUE'] = int(msg)

            self.sendMsg.append(msgTemp)
            self.msgList.append(msg)
            self.msgArea.clear()
        except:
            msgTemp = {}
            msgTemp['MSG_TY'] = 'BYTE'
            msgTemp['VALUE'] = msg

            self.sendMsg.append(msgTemp)
            self.msgList.append(msg)
            self.msgArea.clear()
            #traceback.print_exc()
            #self.inputTableRow(['ERROR', ' ', ' Msg Type error'])

    def addDouble(self):
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:
            msgTemp = {}
            msgTemp['MSG_TY'] = 'DOUBLE'
            msgTemp['VALUE'] = msg

            self.sendMsg.append(msgTemp)
            self.msgList.append(msg)
            self.msgArea.clear()
        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR', ' ', ' Msg Type error'])

    def addJson(self):
        msg = self.msgArea.toPlainText()
        if msg == '':
            return
        try:
            jsonDataList = json.loads(msg)
            for i in range(0, len(jsonDataList)):
                msgObj = {'MSG_TY': jsonDataList[i]['MSG_TY'], 'VALUE': jsonDataList[i]['VALUE'],
                          'VAL_LEN': jsonDataList[i]['VAL_LEN']}
                self.msgList.append(str(jsonDataList[i]['VALUE']))
                self.sendMsg.append(msgObj)
        except:
            traceback.print_exc()
            self.inputTableRow(['ERROR', ' ', ' Msg Type error'])

    def decodeYnMethod(self):

        if self.decodeYn.isChecked():
            self.readHeader.setChecked(False)
            # self.headerCombo.currentText()

    def reloadMsg(self):
        print('준비중')
        # self.msgDecoder.resetMsgList()


    def deleteMsg(self): # 저장 메시지 삭제
        alias = self.msgSavedList.currentText()
        if alias == '-':
            return

        self.msgDecoder.deleteSaveMsg(alias)
        newList = self.msgDecoder.comboSaveMsg
        self.msgSavedList.clear()
        self.msgSavedList.addItem('-')
        for i in self.msgDecoder.comboSaveMsg:
            self.msgSavedList.addItem(i)


    def onChangeSaveMsgCombo(self):

        if self.msgSavedList.currentText() == '-':
            return

        alias = self.msgSavedList.currentText()
        self.aliaisText.setText(alias)

        try:
            msg = self.msgDecoder.getSaveData(alias)
            self.msgArea.clear()
            self.msgArea.append(msg)
        except:
            traceback.print_exc()



    def saveMsgMethod(self):
        print('click!!!!!')
        alias = self.aliaisText.text()
        msg = self.msgArea.toPlainText()
        if alias == '':
            return
        elif msg == '':
            return
        saveMsg = {
            "ALIAS": alias,
            "MSG" : msg
        }

        newCombo = self.msgDecoder.saveMsg(saveMsg)

        self.msgSavedList.clear()
        self.msgSavedList.addItem('-')
        for i in newCombo:
            self.msgSavedList.addItem(i)




    def formatChange(self):
        print()
        # if self.readFormat.isChecked():
        #     print('2222')
        #     self.readHeader.setChecked(False)
        #
        # elif self.readHeader.isChecked():
        #     self.readFormat.setChecked(False)

    def readLoggerFile(self):
        print('chekc')
        roofYn = False
        if self.loggerReadYn.isChecked():
            roofYn = True
            with open("./logs/appslog.log", "r") as f:
                while roofYn:
                    where = f.tell()
                    line = f.readline().strip()
                    if not line:
                        sleep(4)
                        delay_time += 1
                        f.seek(where)
                        # if delay_time > 30.0:  # 30초 이상 지연되면 파일 출력이 끝난 것으로 간주
                        #     print("check")
                        #     break
                        # print('대기중')
                    else:
                        delay_time = 0.  # reset delay time
                        print(type(line))
                        print(line)
                        # self.loggerArea.append(str(line))
        else:
            roofYn = False

    def autoSendSecMethod(self):
        print(self.autoSendSec.value())

    def nullCheckBoxMethod(self):
        print('asdassd')

    def cleanRevMsgMethod(self):
        self.reciveMsgArea.clear()
    def cleanSendMsgMethod(self):
        self.sendMsgArea.clear()


    def textChange(self):
        msgLeng = str(len(self.msgArea.toPlainText()))
        #self.len_label.setText('Msg Length({})'.format(msgLeng))

    def chkItemClicked(self):
        pass

    def chkItemDoubleClicked(self):
        pass

    def chkCurrentItemChanged(self):
        pass

    def cleanMsgMethod(self):
        self.rowCount = 0
        self.table.clearContents()


    def cleanMsgMethod2(self):
        self.msgList.clear()
        self.sendMsg.clear()

    def setComboMethod(self): # 콤보 세팅

        self.qtMsgList.addItem('-')
        for i in self.msgIdList:
            self.qtMsgList.addItem(i)

        for i in typeCombo:
            self.typeCombo.addItem(i)
        for i in scCombo:
            self.scCombo.addItem(i)
        # for i in msgTyCombo:
        #     self.msgTyCombo.addItem(i)

        for i in headerList:
            self.headerCombo.addItem(i)

        self.msgSavedList.addItem('-')
        for i in self.msgDecoder.comboSaveMsg:
            self.msgSavedList.addItem(i)


    def changeMsgListCombo(self):

        if self.qtMsgList.currentText() != '-' :
            self.msgArea.clear()
            msgId = self.qtMsgList.currentText()
            form = self.msgDecoder.makeForm( msgId)
            self.msgArea.append(json.dumps(form, indent=1))

    def comboBoxMethod(self):
        if self.msgTyCombo.currentText() == 'file':

            if self.typeCombo.currentText() == 'REST':
                try:
                    fileInfo = QFileDialog.getOpenFileName(self, 'test', './')
                    device = str(fileInfo[0]).split('/')
                    fileName = device[len(device)-1]
                    fileType = fileName.split('.')[1]

                    temp = multipartForm
                    temp['HEADER']['Content-Type'] = 'multipart/form-data;'
                    temp['FILE']['fileNm'] = fileName

                    self.fileObj['fileNm'] = fileName
                    self.fileObj['file'] = fileInfo[0]


                    self.msgArea.clear()
                    #self.msgArea.append(self.methodUtils.jsonFormat(temp))

                    if fileInfo[0]:
                        realFile = open(fileInfo[0], 'rb')  # 바이너리로 읽음

                except:
                    traceback.print_exc()


        elif self.qtMsgList.currentText() != '-' :
            self.msgArea.clear()
            msgId = self.qtMsgList.currentText()
            form = self.msgDecoder.makeForm( msgId)
            self.msgArea.append(json.dumps(form, indent=1))


        else:
            if self.typeCombo.currentText() == 'REST':
                self.msgArea.clear()
                # self.msgArea.append(self.methodUtils.jsonFormat(defaultForm))




    def hdComboBoxMethod(self):
        self.msgArea.clear()
        self.msgList.clear()
        self.sendMsg.clear()

        # if self.headerList.currentText() == 'H6':
        #     self.msgArea.append(self.methodUtils.jsonFormat(h6Form))

    def onchangeScType(self):

        if self.scCombo.currentText() == 'CLIENT':
            self.bindBt.setText('Connect')
        else:
            self.bindBt.setText('Bind')

    def onchangeType(self):
        self.msgArea.clear()
        self.msgList.clear()
        self.sendMsg.clear()

        if self.typeCombo.currentText() == 'REST':
            # self.msgArea.append(self.methodUtils.jsonFormat(defaultForm))
            self.ip_label.setText('Url')
        elif self.typeCombo.currentText() == 'REST(GET)':
            # self.msgArea.append(self.methodUtils.jsonFormat(defaultForm))
            self.ip_label.setText('Url')
        else:
            self.ip_label.setText('Ip')


    # 인도 H6 포맷
    def makeH6Form(self,jsonString):

        datas = json.loads(jsonString)

        print(datas)

        msgTemp1 = {'msgTy': 'int', 'msg': datas['TOTAL_LENGTH']}
        msgTemp2 = {'msgTy': 'byte', 'msg': datas['HD_ID']}
        msgTemp3 = {'msgTy': 'int', 'msg': datas['DATA_TOTAL_LENGTH']}
        msgTemp4 = {'msgTy': 'short', 'msg': datas['DATA_CNT']}
        msgTemp5 = {'msgTy': 'string', 'msg': datas['REV']}
        msgTemp6 = {'msgTy': 'string', 'msg': datas['SPARE']}
        #msgTemp7 = {'msgTy': 'string', 'msg': datas['DATA']}





        # if self.removeChkBox.isChecked():
        #     self.msgArea.clear()

        self.sendMsg.append(msgTemp1)
        self.msgList.append(msgTemp1['msg'])
        self.sendMsg.append(msgTemp2)
        self.msgList.append(msgTemp2['msg'])
        self.sendMsg.append(msgTemp3)
        self.msgList.append(msgTemp3['msg'])
        self.sendMsg.append(msgTemp4)
        self.msgList.append(msgTemp4['msg'])
        self.sendMsg.append(msgTemp5)
        self.msgList.append(msgTemp5['msg'])
        self.sendMsg.append(msgTemp6)
        self.msgList.append(msgTemp6['msg'])
        jsonDataList = datas['DATA']
        print(jsonDataList)
        for i in range(0, len(jsonDataList)):
            msgObj = {'msgTy': jsonDataList[i]['msgTy'], 'msg': jsonDataList[i]['val']}
            self.msgList.append(jsonDataList[i]['val'])
            self.sendMsg.append(msgObj)

        # self.sendMsg.append(msgTemp7)
        # self.msgList.append(msgTemp7['msg'])


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



    # 받은 메시지를 json 포맷 바탕으로 재구성하여 노출
    def parsingReciveData(self, msgBytes, ipPort):


        try:
            jsonDataList = json.loads(self.msgArea.toPlainText())
            parsed_data = {}
            index = 0
            result = []

            print('바이트 길이')
            print(len(msgBytes))
            for i in range(0, len(jsonDataList)):
                msg_type = jsonDataList[i]["MSG_TY"]
                value = jsonDataList[i]["VALUE"]
                length = int(jsonDataList[i]["VAL_LEN"])

                print(length)
                if msg_type == "INT":
                    sub_array = msgBytes[index:index + 4]  # 맨 앞 4바이트만 자르기
                    value = int.from_bytes(sub_array, byteorder='big')
                    # parsed_data[msg_type + str(i)] = value
                    result.append(value)
                    index += 4

                elif msg_type == "BYTE":
                    size = length
                    sub_array = msgBytes[index:index + size]
                    #value = int.from_bytes(sub_array, byteorder='big')
                    result.append(str(''.join(chr(byte) for byte in sub_array)))
                    index += size

                elif msg_type == "SHORT":
                    sub_array = msgBytes[index:index + 2]  # 맨 앞 4바이트만 자르기
                    value = int.from_bytes(sub_array, byteorder='big', signed=True)
                    # parsed_data[msg_type + str(i)] = value
                    result.append(value)
                    index += 2

                elif msg_type == "STRING":
                    size = length
                    # parsed_data[msg_type+str(i)] = msgBytes[index:index + size].decode('utf-8').strip()
                    result.append(msgBytes[index:index + size].decode('utf-8-sig').strip())
                    index += size

                elif msg_type == "DOUBLE":
                    print(index, index + 8)
                    # size = int(value)
                    # parsed_data[msg_type+str(i)] = struct.unpack('!d', msgBytes[index:index + 8])[0]
                    result.append(struct.unpack('!d', msgBytes[index:index + 8])[0])
                    index += 8


            logger.info('RECIVE JSON BYTE:' + str(result))
            self.inputTableRow(['IN', ipPort, str(result)])
        except:
            traceback.print_exc()
            logger.info('RECIVE MSG JSON FORMAT ERROR !!!')



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
            self.ipInput.setReadOnly(True)
            self.ipInput.setStyleSheet("background:gray;")
            self.portInput.setReadOnly(True)
            self.typeCombo.setEnabled(False)
            self.scCombo.setEnabled(False)
            self.portInput.setStyleSheet("background:gray;")
        else:
            self.typeCombo.setEnabled(True)
            self.scCombo.setEnabled(True)
            self.ipInput.setReadOnly(False)
            self.ipInput.setStyleSheet( "background:rgb(122, 122, 122);""color:white;")
            self.portInput.setReadOnly(False)
            self.portInput.setStyleSheet("background:rgb(122, 122, 122);""color:white;")



    def inputSendMsgArea(self, test):
        now = datetime.now()
        self.sendMsgArea.append('[ {} ]  {}'.format(now.strftime('%H:%M:%S'), test))

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


    @pyqtSlot(bytearray, str)
    def serverReciveDataMethod(self, msgBytes, ipPort):

        # 해더 기준으로
        if self.decodeYn.isChecked():
            result = self.msgDecoder.decodeByHeader(msgBytes, self.headerCombo.currentText())
            logger.info('RECIVE FROM CLIENT BYTE:' + str(result))
            self.inputTableRow(['IN', ipPort, str(result)])

            return

        if self.readHeader.isChecked():
            print('포멧팅')
            self.parsingReciveData(msgBytes, ipPort)
        else:

            logger.info('RECIVE FROM CLIENT BYTE:' + str(''.join(chr(byte) for byte in msgBytes)))
            self.inputTableRow(['IN', ipPort, str(''.join(chr(byte) for byte in msgBytes))])

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



    def inputTableRow(self,arr):
        #  파라미터 :: ['OUT','MSG']
        now = datetime.now()
        now.strftime('%H:%M:%S')

        self.table.setRowCount(self.rowCount + 1)

        # item = QTableWidgetItem(arr[0])
        bg_color = QColor(204, 229, 255)  # 빨간색 배경색

        if arr[0] == 'IN':
            item = QTableWidgetItem(now.strftime('%H:%M:%S'))
            item.setBackground(bg_color)
            self.table.setItem(self.rowCount, 0, item)

            item2 = QTableWidgetItem(arr[2])
            item2.setBackground(bg_color)
            self.table.setItem(self.rowCount, 1, item2)

        else:
            self.table.setItem(self.rowCount, 0, QTableWidgetItem(now.strftime('%H:%M:%S')))
            self.table.setItem(self.rowCount, 1, QTableWidgetItem(arr[2]))





        # self.table.setItem(self.rowCount, 0, QTableWidgetItem(now.strftime('%H:%M:%S')))
        # self.table.setItem(self.rowCount, 1, item)  # 로그타입
        # self.table.setItem(self.rowCount, 2, QTableWidgetItem(arr[1])) # target
        # self.table.setItem(self.rowCount, 3, QTableWidgetItem(arr[2]))  # 메시지

        self.table.scrollToBottom()

        self.rowCount = self.rowCount+1
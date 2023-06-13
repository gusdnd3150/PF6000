

import traceback
import struct

import json
from conf.logconfig import logger

class MessageLenDecoder():

    headerList = []
    msgIdList = []
    savedMsgList = []

    comboHeader = []
    comboMsg = []
    comboSaveMsg = []

    def __init__(self):
        self.init()
        logger.info('message decoder init start')
    def init(self):
        try:
            with open('./config.json') as f:
                data = json.load(f)
                self.headerList = data['HD_ID_LIST']
                self.msgIdList = data['MSG_ID_LIST']
                self.savedMsgList = data['SAVE_LIST']

            logger.info('HD_ID_LIST ')
            logger.info(self.headerList)
            logger.info('MSG_ID_LIST ')
            logger.info(self.msgIdList)
            logger.info('SAVE_LIST ')
            logger.info(self.savedMsgList)

            for item in self.headerList:
                if item['HD_ID'] not in self.comboHeader:
                    self.comboHeader.append(item['HD_ID'])

            for item in self.msgIdList:
                if item['MSG_ID'] not in self.comboMsg:
                    self.comboMsg.append(item['MSG_ID'])

            for item in self.savedMsgList:
                if item['ALIAS'] not in self.savedMsgList:
                    self.comboSaveMsg.append(item['ALIAS'])

            logger.info(self.comboHeader)
            logger.info(self.comboMsg)
        except:
            traceback.print_exc()


    def makeForm(self,msgId):

        result = []
        hdId = ''
        headerList = []
        msgIdList = []
        delimeter =[
            {
                "MSG_DT_ID": "DELIMITER",
                "MSG_TY": "BYTE",
                "VAL_LEN": 1,
                "VALUE": 0
            }
        ]


        totalLen = 0
        headerLen = 0


        # BODY 구성
        for item in self.msgIdList:
            if item['MSG_ID'] == msgId:
                nObj = {
                      "MSG_DT_ID": item['MSG_DT_ID'],
                      "MSG_TY": item['MSG_TY'],
                      "VAL_LEN":item['VAL_LEN'],
                      "VALUE":""
                }
                totalLen = totalLen+item['VAL_LEN']
                hdId = item['HD_ID']
                msgIdList.append(nObj)

        # HEADER 구성
        for item in self.headerList:
            if item['HD_ID'] == hdId:
                nObj = {
                    "MSG_DT_ID": item['MSG_DT_ID'],
                    "MSG_TY": item['MSG_TY'],
                    "VAL_LEN": item['VAL_LEN'],
                    "VALUE": self.setHeaderDefaultVal(item['MSG_TY'],item['VAL_LEN'])
                }
                totalLen = totalLen + item['VAL_LEN']
                headerLen = headerLen + item['VAL_LEN']
                headerList.append(nObj)

        print('길이 체크')
        print(totalLen)
        print(headerLen)

        result.extend(headerList)
        result.extend(msgIdList)
        result.extend(delimeter)
        return result




    def getSaveData(self, alias):

        for item in  self.savedMsgList:
            if item['ALIAS'] == alias:
                return item['MSG']

    def setHeaderDefaultVal(self, type,length ):
        print('시작')

        return ''

    def setMsgListCombo(self, hdId):
        for item in self.msgIdList:
            if item['HD_ID'] == hdId and item['MSG_ID'] not in self.comboMsg:
                self.comboMsg.append(item['MSG_ID'])


    def saveMsg(self, nMsg):

        try:
            with open('./config.json', 'r') as file:
                data = json.load(file)

            # 데이터 수정

            dupCheck = False
            for item in data['SAVE_LIST']:
                if item['ALIAS'] == nMsg['ALIAS']:
                    item['MSG'] = nMsg['MSG']
                    dupCheck = True

            if dupCheck == False:
                data['SAVE_LIST'].append(nMsg)

            # 수정된 데이터를 JSON 파일에 쓰기
            with open('./config.json', 'w') as file:
                json.dump(data, file, indent=2)


            newList = data['SAVE_LIST']

            self.savedMsgList.clear()
            self.comboSaveMsg.clear()

            self.savedMsgList = newList
            for item in self.savedMsgList:
                if item['ALIAS'] not in self.savedMsgList:
                    self.comboSaveMsg.append(item['ALIAS'])

            return self.comboSaveMsg

        except:
            traceback.print_exc()

    def decodeByJsonFormat(self, msgBytes,jsonDataList, msgId):

        try:
            # jsonDataList = json.loads(self.msgArea.toPlainText())
            parsed_data = {}
            index = 0
            result = []

            totalByte = str(len(msgBytes))

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
                    # value = int.from_bytes(sub_array, byteorder='big')
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

            result = msgId+'-BYTE LEN('+totalByte+')' + str(result)
        except:
            traceback.print_exc()
            logger.info('RECIVE MSG JSON FORMAT ERROR !!!')

        return result



    # 해더 id 바이트 어레이 파싱후 포맷 디코드
    def decodeByHeader(self, msgBytes, header):

        try:
            result = []
            headerList = []
            msgIdList = []

            sub_array = msgBytes[4:5]  # 헤더 아이디만 짜름
            hdId = header
            msgIntVal = int.from_bytes(sub_array, byteorder='big')
            msgId = ""

            # BODY 구성
            for item in self.msgIdList:
                if item['MSG_INT_VAL'] == msgIntVal and item['HD_ID'] == hdId:
                    nObj = {
                        "MSG_DT_ID": item['MSG_DT_ID'],
                        "MSG_TY": item['MSG_TY'],
                        "VAL_LEN": item['VAL_LEN'],
                        "VALUE": ""
                    }
                    msgId = item['MSG_ID']
                    msgIdList.append(nObj)

            # HEADER 구성
            for item in self.headerList:
                if item['HD_ID'] == hdId:
                    nObj = {
                        "MSG_DT_ID": item['MSG_DT_ID'],
                        "MSG_TY": item['MSG_TY'],
                        "VAL_LEN": item['VAL_LEN'],
                        "VALUE": self.setHeaderDefaultVal(item['MSG_TY'], item['VAL_LEN'])
                    }
                    headerList.append(nObj)

            result.extend(headerList)
            result.extend(msgIdList)


            if len(msgIdList) < 1:
                return 'there"s no MSG_ID in config.json file :BYTE('+ str(str(''.join(chr(byte) for byte in msgBytes)))+')'

            stre = self.decodeByJsonFormat(msgBytes ,result, msgId)
            return stre
        except:
            return traceback.print_exc()


    def deleteSaveMsg(self, alias):

        try:
            with open('./config.json', 'r') as file:
                data = json.load(file)

            for i, item in enumerate(data['SAVE_LIST']):
                if item['ALIAS'] == alias:
                    del data['SAVE_LIST'][i]

            # 수정된 데이터를 JSON 파일에 쓰기
            with open('./config.json', 'w') as file:
                json.dump(data, file, indent=2)

            newList = data['SAVE_LIST']

            self.savedMsgList.clear()
            self.comboSaveMsg.clear()

            self.savedMsgList = newList
            for item in self.savedMsgList:
                if item['ALIAS'] not in self.savedMsgList:
                    self.comboSaveMsg.append(item['ALIAS'])
        except:
            traceback.print_exc()





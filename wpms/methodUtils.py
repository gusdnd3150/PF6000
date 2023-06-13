import traceback
import struct

import json


class MethodUtils():

    def __init__(self):
        print()

    def jsonFormat(self, jsonString):  # OBJ -> STR
        return json.dumps(jsonString, indent=3)




    # string, 혹은 double 값을 byte array로 반환
    def doubleToBytes(self, val):
        print('doubleVal :'+val)
        # doubleVal = None
        # if type(val) == str:
        #     doubleVal = float(val)
        # else:
        #     doubleVal = val

        bytes_data = struct.pack('d', float(val))
        return bytes_data

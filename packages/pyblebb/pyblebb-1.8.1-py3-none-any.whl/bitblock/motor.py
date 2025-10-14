from .bitblock import * 
from .constants import *

__all__ = [
    "DCMotor",
]

class DCMotor():
    def __init__(self, controler, pin=PIN.P16):
        self.__controller = controler
        self.__pin = pin
         
    def set(self, value):

        value = max(0, min(255, value))  # 범위 제한
        value = int(50 + (value * 205 / 255))

        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ANALOG
        command[BBPACKET.DATA0] = ACTION_MODE.ANALOG_OUTPUT
        command[BBPACKET.DATA1] = self.__pin
        # 0 ~ 1023
        ah = (value >> 8) & 0xff      # 상위 바이트
        al = value & 0xff
        command[BBPACKET.DATA2] = al    # 펌웨어에서 readShort 함수를 사용할려면 상위와 하위를 조심
        command[BBPACKET.DATA3] = ah
        self.__controller.send(command)


    


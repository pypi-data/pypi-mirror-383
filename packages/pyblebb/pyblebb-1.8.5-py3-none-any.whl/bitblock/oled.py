from .bitblock import * 
from .constants import *

__all__ = [
    "OLED",
]

class OLED():
    def __init__(self, controler):
        self.__controller = controler

         
    def set(self, x, y, size, text):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.OLED
        command[BBPACKET.DATA0] = ACTION_MODE.OLED_TEXT_XY
        command[BBPACKET.DATA1] = x
        command[BBPACKET.DATA2] = y
        command[BBPACKET.DATA3] = 1
        command[BBPACKET.DATA4] = size
        DATA_INDEX = 10
        for i, char in enumerate(text):
            command[i+DATA_INDEX] = ord(char)
        self.__controller.send(command)


    def clear(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.OLED
        command[BBPACKET.DATA0] = ACTION_MODE.OLED_CLEAR
        self.__controller.send(command);

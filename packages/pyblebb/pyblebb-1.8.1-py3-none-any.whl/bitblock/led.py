from .bitblock import * 
from .constants import *

__all__ = [
    "LED",
]

class LED():
    def __init__(self, controler, pin):
        self.__controller = controler
        self.__pin = pin
         
    def on(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.DIGITAL
        command[BBPACKET.DATA0] = ACTION_MODE.DIGITAL_OUTPUT
        command[BBPACKET.DATA1] = self.__pin
        command[BBPACKET.DATA2] = 1
        self.__controller.send(command)


    def off(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.DIGITAL
        command[BBPACKET.DATA0] = ACTION_MODE.DIGITAL_OUTPUT
        command[BBPACKET.DATA1] = self.__pin
        command[BBPACKET.DATA2] = 0
        self.__controller.send(command)


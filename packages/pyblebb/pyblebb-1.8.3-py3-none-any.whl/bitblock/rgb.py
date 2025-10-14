from .bitblock import * 
from .constants import *

__all__ = [
    "RGB",
]

class RGB():
    def __init__(self, controler, pin):
        self.__controller = controler
        self.__pin = pin
         
    def on(self, r, g, b):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.COLORLED
        command[BBPACKET.DATA0] = ACTION_MODE.COLORLED_ON;
        command[BBPACKET.DATA1] = self.__pin;
        command[BBPACKET.DATA2] = r;
        command[BBPACKET.DATA3] = g;
        command[BBPACKET.DATA4] = b;
        self.__controller.send(command)


    def off(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.COLORLED
        command[BBPACKET.DATA0] = ACTION_MODE.COLORLED_OFF;
        command[BBPACKET.DATA1] = self.__pin;
        self.__controller.send(command)


    def set_brightness(self, value):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.COLORLED
        command[BBPACKET.DATA0] = ACTION_MODE.COLORLED_BRIGHT;
        command[BBPACKET.DATA1] = self.__pin;
        command[BBPACKET.DATA2] = value;
        self.__controller.send(command)

    
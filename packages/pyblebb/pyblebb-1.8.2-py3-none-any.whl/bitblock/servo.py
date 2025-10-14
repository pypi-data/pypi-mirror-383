from .bitblock import * 
from .constants import *

__all__ = [
    "Servo",
]

class Servo():
    def __init__(self, controler, pin):
        self.__controller = controler
        self.__pin = pin
         
    def set(self, value):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.SERVO
        command[BBPACKET.DATA0] = self.__pin;
        command[BBPACKET.DATA1] = value;
        self.__controller.send(command)


    


from .bitblock import * 
from .constants import *

__all__ = [
    "PIR",
]

# PIR은 디지털 입력
class PIR():
    def __init__(self, controler, pin):
        self.__controller = controler
        self.__pin = pin

    def get(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.DIGITAL
        command[BBPACKET.DATA0] = ACTION_MODE.DIGITAL_INPUT
        command[BBPACKET.DATA1] = self.__pin
        self.__controller.send(command)
        packet = self.__controller.read_data()
        if self.__controller._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        val = packet[5]
        return val


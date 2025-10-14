from .bitblock import * 
from .constants import *

__all__ = [
    "CDS",
]

class CDS():
    def __init__(self, controler, pin):
        self.__controller = controler
        self.__pin = pin



    def get(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__controller.get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ANALOG;
        command[BBPACKET.DATA0] = ACTION_MODE.ANALOG_INPUT;
        command[BBPACKET.DATA1] = self.__pin;
        self.__controller.send(command)
        packet = self.__controller.read_data()
        if self.__controller._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return

        # 5, 6
        al = packet[5]
        ah = packet[6]
        val = (ah << 8) | al;
        return val


  
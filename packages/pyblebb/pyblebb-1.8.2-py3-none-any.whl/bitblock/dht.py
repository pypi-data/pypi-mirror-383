from .bitblock import * 
from .constants import *

__all__ = [
    "DHT",
]

class DHT():
  def __init__(self, controler, pin):
      self.__controller = controler
      self.__pin = pin

  def get(self):
    command = NULL_COMMAND_PACKET[:]
    command[BBPACKET.INDEX] = self.__controller.get_index()
    command[BBPACKET.ACTION] = ACTION_CODE.TMPHUM
    command[BBPACKET.DATA0] = self.__pin
    self.__controller.send(command)

    packet = self.__controller.read_data()
    if self.__controller._packetIndex != packet[BBRETURN.INDEX]:
        print(ERROR.WRONG_PACKET_INDEX)
        return
    temp = packet[5]
    humi = packet[6]
    return temp, humi

from .bitblock import * 
from .constants import *

__all__ = [
    "Ultrasonic",
]

class Ultrasonic():
  def __init__(self, controler, trig=PIN.P13, echo=PIN.P14):
      self.__controller = controler
      self.__trig = trig
      self.__echo = echo

  def get(self):
      command = NULL_COMMAND_PACKET[:]
      command[BBPACKET.INDEX] = self.__controller.get_index()
      command[BBPACKET.ACTION] = ACTION_CODE.ULTRASONIC
      command[BBPACKET.DATA0] = self.__trig
      command[BBPACKET.DATA1] = self.__echo
      self.__controller.send(command)
      packet = self.__controller.read_data()
      if self.__controller._packetIndex != packet[BBRETURN.INDEX]:
          print(ERROR.WRONG_PACKET_INDEX)
          return
      return packet[5]

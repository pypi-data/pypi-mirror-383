import nest_asyncio
import asyncio
from asyncio import Queue
import time
# import struct
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from bleak import BleakClient, BleakScanner
from .constants import *
from .utils import * 
from .board_wrapper import *
from termcolor import cprint

__all__ = [
    "ble_list",
    "Bitblock",
]

nest_asyncio.apply()


class Bitblock():
    """일반 IDE와 주피터노트북에서 사용가능한 클래스 
    """
    def __init__(self, address=None, timeout=5, verbose=False):
        self.__verbose = verbose
        self.__address = address
        self.__client = None
        self._packetIndex = 1;
        self.display = self.Display(self)
        self.pin = self.PIN()

        self.__sensors = {
            'switch': [0, 0],
            'mic': 0,
            'lightSensor': [0, 0],
            'touchSensor': [0, 0, 0],
            'mpuSensor': [0, 0, 0, 0], # left, right, top, bottom
        };

    # def _run_async(self, coro):
    #     try:
    #         # 이미 실행 중인 이벤트 루프가 있는지 확인
    #         loop = asyncio.get_running_loop()
    #     except RuntimeError:
    #         loop = None

    #     if loop and loop.is_running():
    #         # 이미 실행 중인 이벤트 루프가 있으면 태스크로 실행
    #         # return asyncio.create_task(coro)
    #         return loop.run_until_complete(coro)
    #     else:
    #         # 새 이벤트 루프를 생성하여 실행
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #         try:
    #             return loop.run_until_complete(coro)
    #         finally:
    #             loop.close()

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)             

    def connect(self):
        if self.__address and not self.__client:
            cprint(f'👽 Connect {self.__address}', "green")
            
            self.__client = BoardWrapper(self.__address)
        # return self.__client.connect()
        # return asyncio.run(self.__client.connect())
        return self._run_async(self.__client.connect())

    def disconnect(self):
        if self.__client:
            try:
                cprint(f'🔥 Disconnect {self.__address}', 'red')
                # return asyncio.run(self.__client.disconnect())
                #  에러가 발생해서 호출 안하는 것으로 수정 2024.11.05
                # self._run_async(self.__client.disconnect())

                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.__client.disconnect())


            except Exception as e:
                pass

    
    
    def send_command(self, data):
        if self.__client :
            # return asyncio.run(self.__client.send_command(data))
            return self._run_async(self.__client.send_command(data))


    def read_data(self):
        if self.__client :
            # packet = asyncio.run(self.__client.read_data())
            packet = self._run_async(self.__client.read_data())
            return packet
        

    def __processReportPacket(self, packet):
        self.__sensors['switch'] = [packet[2], packet[3]];

        # 5, 6
        al = packet[4]; # low byte
        ah = packet[5]; # hight byte
        light1 = (ah << 8) | al;

        # 6, 7
        al = packet[6];
        ah = packet[7];
        light2 = (ah << 8) | al;

        self.__sensors['lightSensor'] = [light1, light2];

        # 8, 9
        al = packet[8];
        ah = packet[9];
        touch0 = (ah << 8) | al;

        # 10, 11
        al = packet[10];
        ah = packet[11];
        touch1 = (ah << 8) | al;

        # 12, 13
        al = packet[12];
        ah = packet[13];
        touch2 = (ah << 8) | al;

        self.__sensors['touchSensor'] = [touch0, touch1, touch2];
        
        p = packet[14];
        self.__sensors['mpuSensor'] = [
            (p >> 3) & 0x01,
            (p >> 2) & 0x01,
            (p >> 1) & 0x01,
            p & 0x01,
        ];

        # 15, 16
        al = packet[15];
        ah = packet[16];
        self.__sensors['mic'] = (ah << 8) | al;

    def __send(self, command):
        if self.__client:
            if isinstance(command, list):
                command = bytes(command)
                # command = bytes(command)
                # return asyncio.run(self.__client.send_command(command))
                return self._run_async(self.__client.send_command(command))

    def send(self, command):
        if self.__client:
            if isinstance(command, list):
                command = bytes(command)
                # command = bytes(command)
                # return asyncio.run(self.__client.send_command(command))
                return self._run_async(self.__client.send_command(command))
            
    def __get_index(self):
        self._packetIndex = (self._packetIndex + 1) % 256  # 0~255 사이에서 순환
        return self._packetIndex
    
    def get_index(self):
        self._packetIndex = (self._packetIndex + 1) % 256  # 0~255 사이에서 순환
        return self._packetIndex
    
    # def __send_read(self, command):
    #     self.__send(command)
    #     wait(100)
    #     packet = self.read_data()
    #     self.__processReportPacket(packet)

    
    
    # -------------------------------------------------------
    #   BOARD PINS
    # -------------------------------------------------------
    class PIN:
        def __init__(self):
            self.P0 = 10 
            self.P1 = 4
            self.P2 = 8
            self.P3 = 2
            self.P4 = 9
            self.P7 = 39
            self.P11 = 7
            self.P12 = 18
            self.SERVO = 16
            self.DCMOTOR = 46

    # -------------------------------------------------------
    #   DISPLAY (LED MATRIX)
    # -------------------------------------------------------
    class Display():
        def __init__(self, controler=None):
            self.__controller = controler
            # print(dir(self.__controller))
            # self.__init()

        def __color(self, color):
            if isinstance(color, str):
                r, g, b = (0, 0, 0)
                # Hex 색상 코드인 경우
                if color.startswith("#") and len(color) == 7:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                else:
                    raise ValueError("Invalid color string format. Expected format: '#RRGGBB'")
            elif (isinstance(color, list) or isinstance(color, tuple)) and len(color) == 3:
                # RGB 리스트인 경우
                r, g, b = color
                if not all(0 <= val <= 255 for val in (r, g, b)):
                    raise ValueError("RGB values must be between 0 and 255.")
            else:
                raise TypeError("Color must be a string in '#RRGGBB' format or a list [R, G, B].")
            return r, g, b

        def color(self, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_COLOR
            command[BBPACKET.DATA1] = r
            command[BBPACKET.DATA2] = g
            command[BBPACKET.DATA3] = b
            self.__controller._Bitblock__send(command)

        def symbol(self, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_SYMBOL
            command[BBPACKET.DATA1] = symbol[0]
            command[BBPACKET.DATA2] = symbol[1]
            command[BBPACKET.DATA3] = symbol[2]
            command[BBPACKET.DATA4] = symbol[3]
            command[BBPACKET.DATA5] = symbol[4]
            command[BBPACKET.DATA6] = r
            command[BBPACKET.DATA7] = g
            command[BBPACKET.DATA8] = b
            self.__controller._Bitblock__send(command)

        def row(self, row, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_ROW
            command[BBPACKET.DATA1] = symbol
            command[BBPACKET.DATA2] = r
            command[BBPACKET.DATA3] = g
            command[BBPACKET.DATA4] = b
            command[BBPACKET.DATA5] = row
            self.__controller._Bitblock__send(command)

        def bright(self, bright):
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_BRIGHT
            command[BBPACKET.DATA1] = bright
            self.__controller._Bitblock__send(command)

        def char(self, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_CHAR
            command[BBPACKET.DATA1] = ord(symbol)
            command[BBPACKET.DATA2] = r
            command[BBPACKET.DATA3] = g
            command[BBPACKET.DATA4] = b
            self.__controller._Bitblock__send(command)


        def num(self, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED;
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_NUM;
            command[BBPACKET.DATA1] = int(symbol);
            command[BBPACKET.DATA2] = r;
            command[BBPACKET.DATA3] = g;
            command[BBPACKET.DATA4] = b;
            self.__controller._Bitblock__send(command)

        def xy(self, coordX, coordY, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED;
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_XY;
            command[BBPACKET.DATA1] = r;
            command[BBPACKET.DATA2] = g;
            command[BBPACKET.DATA3] = b;
            command[BBPACKET.DATA4] = coordX;
            command[BBPACKET.DATA5] = coordY;
            self.__controller._Bitblock__send(command)

        def effect(self, no):
            """
            정해진 효과를 표시한다.
            
            Parameters:
                no (int): 효과 번호 (e.g., 0, 1, 2).
            Returns:
                0: 무지개 효과 
                1: 폭포 효과
                2: 와이퍼 효과 

            Example:
                None
            """
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_EFFECT
            command[BBPACKET.DATA1] = no
            command[BBPACKET.DATA2] = 1     # 아두이노에서 사용하는 값
            self.__controller._Bitblock__send(command)

        def clear(self):
            self.color("#000000")
    # --- END OF DIAPLAY ------------------------------------
    # -------------------------------------------------------
    # BUZZER
    # -------------------------------------------------------
    def note(self, note, time):
        # time 은 미리초 단위로 넘어온다.
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.BUZZER;
        command[BBPACKET.DATA0] = ACTION_MODE.BUZZER_NOTE;
        command[BBPACKET.DATA1] = note;

        ah = (time >> 8) & 0xff; # 상위 바이트
        al = time & 0xff;
        command[BBPACKET.DATA2] = ah;
        command[BBPACKET.DATA3] = al;
        self.__send(command)

    def melody(self, melody):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.BUZZER;
        command[BBPACKET.DATA0] = ACTION_MODE.BUZZER_MELODY;
        command[BBPACKET.DATA1] = melody;
        self.__send(command)

    def beep(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.BUZZER;
        command[BBPACKET.DATA0] = ACTION_MODE.BUZZER_BEEP;
        self.__send(command)

    # -------------------------------------------------------
    # BUTTON
    # -------------------------------------------------------    
    def button(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.BUTTON
        self.__send(command)
        packet = self.read_data()

        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        # print(self._packetIndex, ' ## ', packet[BBRETURN.INDEX])
        # print(split_and_join(packet))
        # A, B 버튼 동시 리턴 
        return packet[BBRETURN.DATA1]==1, packet[BBRETURN.DATA2]==1
       

    # -------------------------------------------------------
    # TOUCH SENSOR
    # -------------------------------------------------------    
    # def touch_init(self):
    #     '''사용하지 않음'''
    #     command = NULL_COMMAND_PACKET[:]
    #     command[BBPACKET.INDEX] = self.__get_index()
    #     command[BBPACKET.ACTION] = ACTION_CODE.TOUCH;
    #     command[BBPACKET.DATA0] = ACTION_MODE.TOUCH_INIT;
    #     self.__send(command)

    
    def touch(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.TOUCH;
        command[BBPACKET.DATA0] = ACTION_MODE.TOUCH_VALUES;
        self.__send(command)
        packet = self.read_data()

        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return

        # 5, 6
        al = packet[5]
        ah = packet[6]
        p0 = (ah << 8) | al;

        # 7, 8
        al = packet[7]
        ah = packet[8]
        p1 = (ah << 8) | al;

        # 9, 10
        al = packet[9]
        ah = packet[10]
        p2 = (ah << 8) | al;

        return p0==1, p1==1, p2==1

    # -------------------------------------------------------
    # MPU
    # -------------------------------------------------------    
    def tilt(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.MPU_ACTION;
        self.__send(command)
        packet = self.read_data()
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        return packet[13]==1,packet[14]==1,packet[15]==1,packet[16]==1
    # -------------------------------------------------------
    # 밝기 센서
    # -------------------------------------------------------   
    def light(self):
        # 0 ~ 1023
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        # print("self.__get_index() -> ", command[BBPACKET.INDEX])

        command[BBPACKET.ACTION] = ACTION_CODE.LIGHT_SENSOR;
        self.__send(command)
        packet = self.read_data()

        # print(self.bytearray_to_hex(packet, sep=' '))

        # print(self._packetIndex, "  ===  ",packet[BBRETURN.INDEX])
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        # 5, 6
        al = packet[5]
        ah = packet[6]
        l1 = (ah << 8) | al;

        # 7, 8
        al = packet[7]
        ah = packet[8]
        l2 = (ah << 8) | al;
        return l1, l2
    
    # -------------------------------------------------------
    # 소리 센서
    # -------------------------------------------------------   
    def mic(self):
       # 0 ~ 1023
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.MIC_SENSOR;
        self.__send(command)
        packet = self.read_data()
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        # 5, 6
        al = packet[5]
        ah = packet[6]
        val = (ah << 8) | al;
        return val

    # -------------------------------------------------------
    # 디지털 입출력
    # -------------------------------------------------------   
    def digital_write(self, pin, val):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.DIGITAL
        command[BBPACKET.DATA0] = ACTION_MODE.DIGITAL_OUTPUT
        command[BBPACKET.DATA1] = pin
        command[BBPACKET.DATA2] = val
        self.__send(command)
    

    def digital_read(self, pin):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.DIGITAL
        command[BBPACKET.DATA0] = ACTION_MODE.DIGITAL_PULLUP    #디지털 풀업
        command[BBPACKET.DATA1] = pin
        self.__send(command)
        packet = self.read_data()
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        val = packet[5]
        return val

    # -------------------------------------------------------
    # 아날로그 입출력
    # -------------------------------------------------------   
    def analog_write(self, pin, val):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ANALOG;
        command[BBPACKET.DATA0] = ACTION_MODE.ANALOG_OUTPUT;
        command[BBPACKET.DATA1] = pin;

        # 0 ~ 1023
        # val 값을 상위 바이트와 하위 바이트로 분리
        ah = (val >> 8) & 0xff  # 상위 바이트
        al = val & 0xff         # 하위 바이트

        command[BBPACKET.DATA2] = al; # 펌웨어에서 readShort 함수를 사용할려면 상위와 하위를 조심
        command[BBPACKET.DATA3] = ah;
        self.__send(command)

    def analog_read(self, pin):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ANALOG;
        command[BBPACKET.DATA0] = ACTION_MODE.ANALOG_INPUT;
        command[BBPACKET.DATA1] = pin;
        self.__send(command)
        packet = self.read_data()
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        
        # 5, 6
        al = packet[5]
        ah = packet[6]
        val = (ah << 8) | al;
        return val


    def dcmotor(self, pin, val):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ANALOG
        command[BBPACKET.DATA0] = ACTION_MODE.ANALOG_OUTPUT
        command[BBPACKET.DATA1] = pin
        # 0 ~ 1023
        ah = (val >> 8) & 0xff      # 상위 바이트
        al = val & 0xff
        command[BBPACKET.DATA2] = al    # 펌웨어에서 readShort 함수를 사용할려면 상위와 하위를 조심
        command[BBPACKET.DATA3] = ah
        self.__send(command)

    # 메인보드의 서버도 핀번호로 동작시키자 
    def servo(self, pin, val):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        if pin == self.pin.SERVO:
            command[BBPACKET.ACTION] = ACTION_CODE.MAIN_SERVO
        else:
            command[BBPACKET.ACTION] = ACTION_CODE.SERVO
        command[BBPACKET.DATA0] = pin;
        command[BBPACKET.DATA1] = val;
        self.__send(command)
    #  -------------------------------------------------------
    #  -------------------------------------------------------
    def ultrasonic(self, trig, echo):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ULTRASONIC
        command[BBPACKET.DATA0] = trig
        command[BBPACKET.DATA1] = echo
        self.__send(command)
        packet = self.read_data()
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        return packet[5]
    
    def dht11(self, pin):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.TMPHUM
        command[BBPACKET.DATA0] = pin
        self.__send(command)
        packet = self.read_data()
        if self._packetIndex != packet[BBRETURN.INDEX]:
            print(ERROR.WRONG_PACKET_INDEX)
            return
        temp = packet[5]
        humi = packet[6]
        return temp, humi
    # -----------------------------------------------------------------
    # 🔥 UTIL 함수
    # -----------------------------------------------------------------
    def delay(self, sec):
        """기다리기

        Args:
            sec (float): 초
        Returns:
            None
        """
        time.sleep(sec)

    def delayms(self,ms):
            """기다리기

            Args:
                ms (float): 밀리초
            Returns:
                None
            """
            self.delay(ms/1000)


    def wait(self, ms):
            """기다리기

            Args:
                ms (float): 밀리초
            Returns:
                None
            """
            self.delay(ms/1000)
    
    def bytearray_to_hex(self, data: bytearray, sep: str = '') -> str:
            """
            bytearray를 16진수 문자열로 변환합니다.

            Args:
                data (bytearray): 변환할 바이트 배열
                sep (str): 각 바이트 사이에 넣을 구분자 (기본값: '')

            Returns:
                str: 16진수 문자열
            """
            return sep.join(f"{b:02X}" for b in data)
    # -----------------------------------------------------------------
    # 🔥 Bitblock 내부 클래스로 정의
    # -----------------------------------------------------------------
    def rccar_init(self):
        return self.RCCar(self)

    class RCCar():
        def __init__(self, controler=None):
            self.__controller = controler
            # print(dir(self.__controller))
            self.__init()

        def __init(self):
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_INITIALIZE
            self.__controller._Bitblock__send(command)

        def __rlspeed(self, dir_l, speed_l, dir_r, speed_r):
            """
            RCCar의 왼쪽 오른쪽 바퀴의 회전 속도와 방향을 설정해서 동작시킨다.
            
            Parameters:
                dir_l (int): 왼쪽 바퀴의 방향 (e.g., forward(0), or reverse(1)).
                speed_l (int): 왼쪽 바퀴의 속도 (e.g., 0 ~ 255).
                dir_r (int): 오른쪽 바퀴의 방향 (e.g., forward(0), or reverse(1)). 
                speed_r (int): 오른쪽 바퀴의 방향 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                    self.rlspeed(dir_l=1, speed_l=50, dir_r=1, speed_r=50)
            """
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_RLSPEED
            command[BBPACKET.DATA1] = dir_l;
            command[BBPACKET.DATA2] = speed_l;
            command[BBPACKET.DATA3] = dir_r;
            command[BBPACKET.DATA4] = speed_r;
            self.__controller._Bitblock__send(command)

        def move_forward(self, speed=100):
            """
            주어진 속도(speed)로 앞으로 이동한다.
            
            Parameters:
                speed (int): 속도 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                None
            """
            self.__rlspeed(0, int(abs(speed)), 0, int(abs(speed)))
        
        def move_backward(self, speed=100):
            """
            주어진 속도(speed)로 뒤로 이동한다.
            
            Parameters:
                speed (int): 속도 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                None
            """
            self.__rlspeed(1, int(abs(speed)), 1, int(abs(speed)))
        
        def turn_left(self, speed=100):
            """
            주어진 속도(speed)로 왼쪽으로 회전한다. 왼쪽 바퀴의 속도는 speed * 0.5로 설정된다.
            
            Parameters:
                speed (int): 속도 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                None
            """
            self.__rlspeed(0, int(abs(speed)/2), 0, int(abs(speed)))

        def turn_right(self, speed=100):
            """
            주어진 속도(speed)로 오른으로 회전한다. 오른쪽 바퀴의 속도는 speed * 0.5로 설정된다.
            
            Parameters:
                speed (int): 속도 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                None
            """
            self.__rlspeed(0, int(abs(speed)), 0, int(abs(speed)/2))

        def pivot_left(self, speed=100):
            """
            왼쪽으로 제자리 돌기
            
            Parameters:
                speed (int): 회전 속도 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                None
            """
            self.__rlspeed(1, int(abs(speed)), 0, int(abs(speed)))
        
        def pivot_right(self, speed=100):
            """
            오른쪽으로 제자리 돌기
            
            Parameters:
                speed (int): 회전 속도 (e.g., 0 ~ 255).

            Returns:
                None

            Example:
                None
            """
            self.__rlspeed(0, int(abs(speed)), 1, int(abs(speed)))
        
        
        def wheels(self, lspeed=100, rspeed=100):
            """
            RCCar의 왼쪽 오른쪽 바퀴의 회전 속도와 방향을 설정해서 동작시킨다.
            
            Parameters:
                lspeed (int): 왼쪽 바퀴의 속도. 음수값이면 역회전 (e.g., -255 ~ 255).
                rspeed (int): 오른쪽 바퀴의 속도. 음수값이면 역회전 (e.g., -255 ~ 255).

            Returns:
                None

            Example:
                    self.wheels(50, -50)
            """
            ldir = 0 if lspeed >= 0 else 1
            rdir = 0 if rspeed >= 0 else 1
            self.__rlspeed(ldir , int(abs(lspeed)), rdir, int(abs(rspeed)))

        def stop(self):
            """
            RCCar 바퀴의 동작을 멈춥니다.
            
            Parameters:
                None

            Returns:
                None

            Example:
                    self.stop()
            """
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_STOP
            self.__controller._Bitblock__send(command)


        def distance(self):
            """
            RCCar의 거리센서(초음파센서)값을 반환한다.

            Returns:
                int: 앞의 장애물과의 거리 (cm)

            Example:
                val = self.distance()

            Note:
                None

            """
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_DISTANCE
            command[BBPACKET.DATA1] = 39 #P7
            command[BBPACKET.DATA2] = 5  #P9
            self.__controller._Bitblock__send(command)
            packet = self.__controller.read_data()
            if self.__controller._packetIndex != packet[BBRETURN.INDEX]:
                print(ERROR.WRONG_PACKET_INDEX)
                return
            return packet[6]
        

        def line(self):
            """
            RCCar의 라인 센서값을 반환한다.

            Returns:
                tuple: 3개의 라인센서 값을 포함한다. (왼쪽, 중간, 오른쪽)값을 나타낸다.

            Example:
                l1, l2, l3 = self.line()
                print(f"Sensor values: {l1}, {l2}, {l3}")

            Note:
                None

            """
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_LINESENSOR
            self.__controller._Bitblock__send(command)
            packet = self.__controller.read_data()
            if self.__controller._packetIndex != packet[BBRETURN.INDEX]:
                print(ERROR.WRONG_PACKET_INDEX)
                return
            # 6, 7
            al = packet[6]
            ah = packet[7]
            l1 = (ah << 8) | al;

            # 8, 9
            al = packet[8]
            ah = packet[9]
            l2 = (ah << 8) | al;

            # 10, 11
            al = packet[10]
            ah = packet[11]
            l3 = (ah << 8) | al;
            return l1, l2, l3

        # 메인보드의 서버도 핀번호로 동작시키자 
        def servo(self, pin, val):
            """
            RCCar의 뒷쪽 커넥터에 연결된 서보모터를 동작시킨다.

            Returns:
                pin (int): P3, P4 3개의 핀 중 하나.

            Example:
                l1, l2, l3 = self.linesensor()
                print(f"Sensor values: {l1}, {l2}, {l3}")

            Note:
                비트블록 1.x 버전은 P3 사용 가능 
                비트블록 2.x 이상은 P3, P4 사용 가능 

            """
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._Bitblock__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.SERVO
            command[BBPACKET.DATA0] = pin
            command[BBPACKET.DATA1] = clamp(val)
            self.__controller._Bitblock__send(command)

        

# END CLASS

# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.


# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# BLE 리스트 출력 
async def __scan(show=True):
    """
    BLE 디바이스를 검색

    Returns:
        list : 검색된 디바이스의 정보를 담은 리스트 
    """
    devices = await BleakScanner.discover()

    l = []
    for device in devices:
        if device.name and device.name.lower().startswith("bitblock"):
            l.append([device.name, device.address, device.rssi])
    # 마지막 숫자를 기준으로 내림차순 정렬
    l = sorted(l, key=lambda x: x[-1], reverse=True)
    if show:
        print("""
__________.__  __ __________.__                 __    
\______   \\__|/  |\\______   \\  |   ____   ____ |  | __
 |    |  _/  \\   __\    |  _/  |  /  _ \\_/ ___\\|  |/ /
 |    |   \\  ||  | |    |   \\  |_(  <_> )  \\___|    < 
 |______  /__||__| |______  /____/\\____/ \\___  >__|_ \\
        \\/                \\/                 \\/     \\/
              """)
        print("#Bitblock BLE device list")
        for i, device in enumerate(l):
            print(f"✔️  {i+1} name({device[0]}), address({device[1]}), rssi({device[2]})")
        print("")
        print("")
    return l
    

# 동기적으로 호출할 수 있는 헬퍼 함수
def ble_list():
    try:
        # 이미 실행 중인 이벤트 루프가 있는지 확인
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # print("# 실행 중인 루프가 있을 경우")
        # 실행 중인 루프가 있을 경우 Task를 만들어 실행
        # loop = asyncio.get_event_loop()
        return loop.run_until_complete(__scan())
    else:
        # 새로운 이벤트 루프에서 실행
        # print("# 새로운 이벤트 루프에서 실행")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(__scan())
        finally:
            loop.close()



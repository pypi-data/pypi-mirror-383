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
    "BitblockAsync"
]

nest_asyncio.apply()

class BitblockAsync:
    """헬로AI(HelloAI)와 함께 사용하기 위한 비트블록 랩핑 클래스  
    """
    def __init__(self, address=None):
        self.__address = address
        
        self.client = None
        self.loop = None
        self.stop_event = threading.Event()
        self.robot_done_event = threading.Event()  # 로봇 완료 신호를 전달할 이벤트
        self.robot_done_event.set()                # 초기 상태를 완료 상태로 설정

        self.thread = None
        self.command_queue = Queue()  # BLE 명령을 보관하는 큐
        self.__received_data = None
        self.display = self.Display(self)
        self.pin = self.PIN()
        self._packetIndex = 0
        self.__sensors = {
            'switch': [0, 0],
            'mic': 0,
            'lightSensor': [0, 0],
            'touchSensor': [0, 0, 0],
            'mpuSensor': [0, 0, 0, 0], # left, right, top, bottom
        };
    

    # BLE 스캐닝 함수 (비동기)
    async def scan_devices(self):
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        for device in devices:
            print(f"Device found: {device.name}, Address: {device.address}")

    # BLE 장치 연결 함수 (비동기)
    async def connect_to_device(self):
        if not self.__address:
            print("No address specified for connection.")
            return

        print(f"Attempting to connect to {self.__address}...")
        self.client = BleakClient(self.__address)
        try:
            await self.client.connect()
            if self.client.is_connected:
                # print(f"Connected to {self.__address}.")
                print(f'👽 Connect {self.__address}')
        except Exception as e:
            print(f"Failed to connect to {self.__address}: {e}")

    def connect(self):
        self.start()  # BLE 스레드 시작

    async def ble_task(self):
        while not self.stop_event.is_set():
            try:
                # BLE 연결 상태 확인
                if self.client and self.client.is_connected:

                    # 큐에서 데이터를 가져와 BLE로 전송
                    if not self.command_queue.empty():
                        data = await self.command_queue.get()
                        await self.client.write_gatt_char(BLEUUID.CHARACTERISTIC_UUID_RX, data)

                        # 약간의 대기 
                        await asyncio.sleep(0.01)

                         # BLE로부터 데이터 읽기
                        # self.__received_data = await self.read_data()
                        # if self.__received_data:
                            # print(f"Received data from BLE: {' '.join(f'{byte:02X}' for byte in self.__received_data)}")
                            # self.__processReportPacket(self.__received_data)
                            # pass

                        self.command_queue.task_done()  # 작업 완료
                        self.robot_done_event.set()

                await asyncio.sleep(0.01)  # 1초 대기

            except Exception as e:
                print(f"Error in BLE task: {e}")


    # BLE 작업 실행 함수 (스레드용)
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            # self.loop.run_until_complete(self.scan_devices())
            self.loop.run_until_complete(self.connect_to_device())
            self.loop.run_until_complete(self.ble_task())
        finally:
            print(f'🔥 Disconnect {self.__address}')
            if self.client and self.client.is_connected:
                self.loop.run_until_complete(self.client.disconnect())
                # print("Disconnected from BLE device.")
            self.loop.close()

    # 스레드 시작
    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def disconnect(self):
        self.stop()
    
    def close(self):
        self.stop()

    # 스레드 종료
    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

    # LED ON 명령을 보내는 함수 (비동기)
    async def send_command(self, data):
        if self.client and self.client.is_connected:
            print("Sending LED ON command...")
            try:
                await self.client.write_gatt_char(BLEUUID.CHARACTERISTIC_UUID_RX, data) 
                print("LED ON command sent.")
            except Exception as e:
                print(f"Failed to send LED ON command: {e}")

    
    async def read_data(self):
        """
        BLE 장치로부터 데이터를 읽어오는 함수
        """
        if self.client and self.client.is_connected:
            try:
                print("Reading data from BLE device...")
                data = await self.client.read_gatt_char(BLEUUID.CHARACTERISTIC_UUID_TX)
                return data
            except Exception as e:
                print(f"Failed to read data from BLE: {e}")
        return None
    
   

    def __processReportPacket(self, packet):
        """리포터 패킷 파싱하는 함수. 하나의 명령씩 실행하기 때문에 사용 안함 
        """
        print('💧 RETURN : ', ' '.join(f'{byte:02X}' for byte in packet))

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

        
    

    def __get_index(self):
        self._packetIndex = (self._packetIndex + 1) % 256  # 0~255 사이에서 순환
        return self._packetIndex
    

    def __send(self, command):
        # print('🐸🐸🐸', command)
        if isinstance(command, list):
            command = bytes(command)
            if self.loop and self.client and self.client.is_connected:
                if self.robot_done_event.is_set():
                    self.loop.call_soon_threadsafe(self.command_queue.put_nowait, command)
                    self.robot_done_event.clear()
        
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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_COLOR
            command[BBPACKET.DATA1] = r
            command[BBPACKET.DATA2] = g
            command[BBPACKET.DATA3] = b
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True


        def symbol(self, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
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
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True


        def row(self, row, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_ROW
            command[BBPACKET.DATA1] = symbol
            command[BBPACKET.DATA2] = r
            command[BBPACKET.DATA3] = g
            command[BBPACKET.DATA4] = b
            command[BBPACKET.DATA5] = row
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True
            

        def bright(self, bright):
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_BRIGHT
            command[BBPACKET.DATA1] = bright
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True
            
        
        def char(self, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_CHAR
            command[BBPACKET.DATA1] = ord(symbol)
            command[BBPACKET.DATA2] = r
            command[BBPACKET.DATA3] = g
            command[BBPACKET.DATA4] = b
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True
            

        def num(self, symbol, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED;
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_NUM;
            command[BBPACKET.DATA1] = int(symbol);
            command[BBPACKET.DATA2] = r;
            command[BBPACKET.DATA3] = g;
            command[BBPACKET.DATA4] = b;
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True
            

        def xy(self, coordX, coordY, color):
            r, g, b = self.__color(color)
            command = NULL_COMMAND_PACKET[:]
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED;
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_XY;
            command[BBPACKET.DATA1] = r;
            command[BBPACKET.DATA2] = g;
            command[BBPACKET.DATA3] = b;
            command[BBPACKET.DATA4] = coordX;
            command[BBPACKET.DATA5] = coordY;
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True


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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.MATRIX_LED
            command[BBPACKET.DATA0] = ACTION_MODE.DISPLAY_EFFECT
            command[BBPACKET.DATA1] = no
            command[BBPACKET.DATA2] = 1     # 아두이노에서 사용하는 값
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True
            

        def clear(self):
            self.color("#000000")
        
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
        if self.robot_done_event.set(): 
            return True


    def melody(self, melody):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.BUZZER;
        command[BBPACKET.DATA0] = ACTION_MODE.BUZZER_MELODY;
        command[BBPACKET.DATA1] = melody;
        self.__send(command)
        if self.robot_done_event.set(): 
            return True


    def beep(self):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.BUZZER;
        command[BBPACKET.DATA0] = ACTION_MODE.BUZZER_BEEP;
        self.__send(command)
        if self.robot_done_event.set(): 
            return True

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
        if self.robot_done_event.set(): 
            return packet[BBRETURN.DATA1]==1, packet[BBRETURN.DATA2]==1


    # -------------------------------------------------------
    # TOUCH SENSOR
    # -------------------------------------------------------   
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

        if self.robot_done_event.set(): 
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
        
        if self.robot_done_event.set(): 
            return packet[13]==1,packet[14]==1,packet[15]==1,packet[16]==1


    # -------------------------------------------------------
    # 밝기 센서
    # -------------------------------------------------------   
    def light(self):
        # 0 ~ 1023
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.LIGHT_SENSOR;
        self.__send(command)
        packet = self.read_data()
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

        if self.robot_done_event.set(): 
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

        if self.robot_done_event.set(): 
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
        if self.robot_done_event.set(): 
            return None

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

        if self.robot_done_event.set(): 
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
        if self.robot_done_event.set(): 
            return None


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
        if self.robot_done_event.set(): 
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
        if self.robot_done_event.set():
            return None

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
        if self.robot_done_event.set():
            return None
    
    def ultrasonic(self, trig, echo):
        command = NULL_COMMAND_PACKET[:]
        command[BBPACKET.INDEX] = self.__get_index()
        command[BBPACKET.ACTION] = ACTION_CODE.ULTRASONIC
        command[BBPACKET.DATA0] = trig
        command[BBPACKET.DATA1] = echo
        self.__send(command)
        if self.robot_done_event.set():
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
        if self.robot_done_event.set():
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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_INITIALIZE
            self.__controller._BitblockAsync__send(command)


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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_RLSPEED
            command[BBPACKET.DATA1] = dir_l;
            command[BBPACKET.DATA2] = speed_l;
            command[BBPACKET.DATA3] = dir_r;
            command[BBPACKET.DATA4] = speed_r;
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return True

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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_STOP
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return None
            
        
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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_DISTANCE
            command[BBPACKET.DATA1] = 39 #P7
            command[BBPACKET.DATA2] = 5  #P9
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.RCCAR
            command[BBPACKET.DATA0] = ACTION_MODE.RCCAR_LINESENSOR
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
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
            command[BBPACKET.INDEX] = self.__controller._BitblockAsync__get_index()
            command[BBPACKET.ACTION] = ACTION_CODE.SERVO
            command[BBPACKET.DATA0] = pin
            command[BBPACKET.DATA1] = clamp(val)
            self.__controller._BitblockAsync__send(command)
            if self.__controller.robot_done_event.set(): 
                return None

# END CLASS (Async)
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
# -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

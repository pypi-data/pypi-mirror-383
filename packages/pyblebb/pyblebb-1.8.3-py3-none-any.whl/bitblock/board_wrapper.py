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
from termcolor import cprint

__all__ = [
    "BoardWrapper"
]

class BoardWrapper:
    def __init__(self, address=None, timeout=5, verbose=False):
        self.__verbose = verbose
        self.__address = address
        # self.__disconnected_event = None
        self.__device = None
        self.__client = None

    def __disconnected_callback(self, client, event=None):
        print("Disconnected callback called!")
        # self.__disconnected_event.set()

    async def __scan(self, parts):
        """
        BLE 디바이스를 검색

        Returns:
            list : 검색된 디바이스의 정보를 담은 리스트 
        """
        devices = await BleakScanner.discover()
        address = None
        for device in devices:
            if device.address.endswith(parts):
                address = device.address
        return address


    async def connect(self):
        if len(self.__address) == 5:
            self.__address = await self.__scan(self.__address)
            if self.__address is None:
                return False

        self.__device = await BleakScanner.find_device_by_address(self.__address)
        if self.__device is None:
            print(f"Could not find device with address {self.__address}")
            return False
        # self.__disconnected_event = asyncio.Event()
        self.__client = BleakClient(self.__device, disconnected_callback=self.__disconnected_callback)
        try:
            await self.__client.connect()
            if self.__verbose:
                print("Connected to device.")
            
        except Exception as e:
            return False

        if self.__client.is_connected:
            return True
        else:
            return False

    # async def disconnect(self):
    #     try:
    #         if self.__client and self.__client.is_connected:
    #             await self.__client.disconnect()
    #     except Exception as e:  # 모든 예외를 포괄하여 처리
    #         pass

    def disconnect(self):
        try:
            if self.__client and self.__client.is_connected:
                self.__client.disconnect()
        except Exception as e:  # 모든 예외를 포괄하여 처리
            pass    
            
    async def get_services(self):
        services = await self.__client.get_services()
        print(services)


    async def send_command(self, data):
        if self.__client:
            await self.__client.write_gatt_char(BLEUUID.CHARACTERISTIC_UUID_RX, data)
            # print(f"Sent command: {data}")


    async def read_data(self):
        if self.__client :
            data = await self.__client.read_gatt_char(BLEUUID.CHARACTERISTIC_UUID_TX)
            # print(f"Received data: {data}")
            return data
       
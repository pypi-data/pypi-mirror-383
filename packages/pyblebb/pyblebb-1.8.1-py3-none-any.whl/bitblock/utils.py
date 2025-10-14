import sys
import time
import math
import asyncio

__all__ = [
    "split_and_join",
    "delay",
    'delayms',
    "wait",
    "clamp",
]

def split_and_join(msg, separator=','):
    """바이트 배열을 문자열러 표시해서 확인하는 용도로 사용 

        Args:
            msg (bytearray): 확인할 바이트 배열 
        Returns:
            str
    """
    hex_string = msg.hex()
    if len(hex_string) % 2 != 0:
        print("주의: 문자열의 길이가 분할 단위로 나누어 떨어지지 않습니다.")
    split_str = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    return separator.join(split_str)


def delay(sec):
        """기다리기

        Args:
            sec (float): 초
        Returns:
            None
        """
        time.sleep(sec)

def delayms(ms):
        """기다리기

        Args:
            ms (float): 밀리초
        Returns:
            None
        """
        delay(ms/1000)


def wait(ms):
        """기다리기

        Args:
            ms (float): 밀리초
        Returns:
            None
        """
        delay(ms/1000)

def clamp(value, mval=0, xval=180):
    """
    주어진 최대값과 최소값 사이의 범위로 조정하여 값을 반환 

    Parameters:
        value (int or float): 조정할 값
        mval  (int or float): 최소값
        xval  (int or float): 최대값

    Returns:
        int or float: 조정된 값 

    Example:
        result = clamp(200, 0, 180)
        print(result)  # Output: 180

        result = clamp(-50, 0, 180)
        print(result)  # Output: 0
    """
    return max(mval, min(xval, value))
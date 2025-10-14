import threading
import queue

__all__ = [
    "BoardControl"
]


class BoardControl:
    def __init__(self, robot, que, coro):
        """파이썬 IDE에서 로봇을 동작시키기 위한 스레드 랩핑 

        Args:
            robot: The robot's control robot object, which has methods to control the display, etc.
        """
        self.__robot = robot  # 로봇 제어 보드 객체
        self.__MSG_QUEUE = que  # 손모양 인식 결과를 저장할 큐
        self.__SENSOR_VALUES = queue.Queue()  # 카미봇에서 리턴되는 값을 저장하기 위한 큐 
        self.__ROBOT_DONE_EVENT = threading.Event()  # 로봇 동작 완료 신호를 위한 이벤트
        self.__ROBOT_DONE_EVENT.set()    # 완료 상태로 셋팅 

        self.__STOP_EVENT = threading.Event()  # 스레드 종료 이벤트
        self.__thread = threading.Thread(target=self._control_robot, daemon=True)  # 로봇 제어 스레드
        self.__coro = coro

    def _control_robot(self):
        """
        Internal method to control the robot based on gestures in the queue.
        """
        while not self.__STOP_EVENT.is_set():
            try:
                # 큐에서 손모양 인식 결과를 기다림
                message = self.__MSG_QUEUE.get(timeout=0.5)  # 0.5초 대기 후 타임아웃 발생
                self.__coro(message, self.__SENSOR_VALUES)

                # 로봇 동작 완료 알림
                self.__MSG_QUEUE.task_done()   # 작업 완료
                self.__ROBOT_DONE_EVENT.set()  # 완료 이벤트 설정
            except queue.Empty:
                continue  # 큐가 비어 있으면 다음 루프로 이동

    def start(self):
        self.__thread.start()
        print("BoardControl started.")

    def stop(self):
        """
        Stop the robot control thread.
        """
        self.__STOP_EVENT.set()
        self.__thread.join()
        print("BoardControl stopped.")

    def add_command(self, message):
        """
        Add a message to the queue for robot control.

        Args:
            message: The recognized message to be processed.
        """
        if self.__ROBOT_DONE_EVENT.is_set():  # 로봇이 준비 상태일 때만 큐에 추가
            self.__MSG_QUEUE.put(message)
            self.__ROBOT_DONE_EVENT.clear()
            print(f"'{message}' added to queue.")
        else:
            print(f"Robot not ready. Message '{message}' ignored.")

    def is_ready(self):
        return self.__ROBOT_DONE_EVENT.is_set()
    
    def get_return(self):
        """큐에서 센서 값을 가져옴"""
        if self.__SENSOR_VALUES.empty():
            return None
        else:
            try:
                value = self.__SENSOR_VALUES.get()
                self.__SENSOR_VALUES.task_done()
                return value
            except queue.Empty:
                return None  # 큐가 비어 있을 경우
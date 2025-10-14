from a2y_kcom import create_serial_instance
from enum import Enum as _Enum
from threading import Thread as _Thread
from time import sleep as _sleep
from typing import Optional as _Optional


class Status(_Enum):
	Closed = 0
	Bad = 1
	Good = 2


class DT1309:
	def __init__(self, port: str):
		self.__serial = create_serial_instance(port=port, baudrate=9600, timeout=0.3)
		self.__value: float = -1
		self.__interval = 0.2

		self.__stop_flag = False
		self.last_frame = ''
		self.__status = Status.Closed

		self.__checking_thread: _Optional[_Thread] = None
		self.start()

	@property
	def interval(self) -> float:
		return self.__interval

	@interval.setter
	def interval(self, value: float):
		self.__interval = value

	@property
	def serial(self):
		return self.__serial

	def start(self):
		assert self.__checking_thread is None, 'Device has started.'
		self.__stop_flag = False
		self.__status = Status.Bad
		self.__checking_thread = _Thread(target=self.__checker)
		self.__checking_thread.start()

	def stop(self):
		if self.__checking_thread is not None:
			self.__stop_flag = True
			self.__checking_thread.join()
			self.__status = Status.Closed
			self.__checking_thread = None

	def close(self):
		self.stop()
		self.__serial.close()

	def open(self):
		if not self.__serial.is_open:
			self.__serial.open()
			self.start()

	def __checker(self):
		while not self.__stop_flag:
			self.__serial.flushInput()
			self.__serial.write(b'\x00\x00')
			char = self.__serial.read()
			timeout = False
			while char != b'\xCE':
				if char == b'':
					timeout = True
					break
				else:
					char = self.__serial.read()
			if timeout:
				self.__status = Status.Bad
				continue
			data = self.__serial.read(4)
			hex_items = [hex(c)[2:].upper().zfill(2) for c in data]
			hex_str = ' '.join(hex_items)
			self.last_frame = f'CE {hex_str}'
			if len(data) != 4 or data[0] not in [0, 1, 2] or data[1] not in [0x80, 0x88]:
				self.__status = Status.Bad
				continue
			high = int(hex(data[2])[2:])
			low = int(hex(data[3])[2:])
			value = high * 100 + low
			for i in range(data[0]):
				value = value / 10
			if data[1] == 0x88:
				value = value * 1000

			self.__value = value
			self.__status = Status.Good

			_sleep(self.interval)

	@property
	def status(self) -> Status:
		return self.__status

	@property
	def good(self) -> bool:
		return self.status == Status.Good

	@property
	def lux(self) -> _Optional[float]:
		if self.good:
			return self.__value
		return 0

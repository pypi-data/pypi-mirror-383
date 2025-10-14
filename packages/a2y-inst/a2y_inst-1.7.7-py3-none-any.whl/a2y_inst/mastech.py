from serial import Serial as _Serial
from threading import Thread
from time import sleep, time as now
from typing import Optional


class MS6701(_Serial):
	"""A Digital Sound Level Meter"""

	InvalidValue = -1.0

	def __init__(self, port: str, baudrate=2400, timeout=0.1):
		_Serial.__init__(self, port, baudrate=baudrate, timeout=timeout)
		self.Value: float = MS6701.InvalidValue
		self.RealTime = False
		self.Range = 6
		self.Minimum = 30
		self.Maximum = 130
		self.OverRange = False
		self.UnderRange = False
		self.Slow = False
		self.Weighting = 'C'
		self.MemoryFull = False
		self.MaxMode = False
		self.BatteryLow = False
		self.__stop_flag = False
		self.__thread: Optional[Thread] = None

		self.Start()

	def Start(self):
		assert self.__thread is None, 'Device has been started.'

		if not self.is_open:
			self.open()

		self.__thread = Thread(target=self.__ReadingThread)
		self.__thread.start()

	def Stop(self):
		assert(self.__thread is not None)

		self.__stop_flag = True
		self.__thread.join()
		self.__thread = None

		self.close()

	def ReadFrame(self, timeout: float = 3, use_stop_flag: bool = False) -> bytes:
		if timeout is None or timeout <= 0:
			end = float('inf')
		else:
			end = now() + timeout
		frame = b''
		while now() < end:
			if use_stop_flag and self.__stop_flag:
				break

			if self.in_waiting == 0:
				sleep(0.1)
				continue
			else:
				sleep(0.1)
				frame = self.read(18)
				for idx, c in enumerate(frame):
					if (c & 0x80) != 0:
						if idx > 0:
							frame = frame[idx:] + self.read(idx)
				if len(frame) == 18:
					break
		return frame

	def ParseFrame(self, frame: bytes):
		# 不知从何时起，frame[8] 的值变成了 0x0C，超过了 10。
		# 而其后的数据看起来像墙钟时间（与仪器屏幕显示一致），目前我们不关心。
		for i in range(2, 8):
			if frame[i] >= 10:
				raise ValueError('Data format invalid from MS6701')
		byte0 = frame[0]
		self.RealTime = (byte0 & 0x20) != 0
		self.Range = (byte0 & 0x7)
		if self.Range == 6:
			self.Minimum = 30
			self.Maximum = 130
		else:
			self.Minimum = 30 + self.Range * 10
			self.Maximum = 80 + self.Range * 10
		flags = frame[1]
		self.OverRange = (flags & 1) != 0
		self.UnderRange = (flags & 2) != 0
		self.Slow = (flags & 4) != 0
		self.Weighting = 'A' if (flags & 8) != 0 else 'C'
		self.MemoryFull = (flags & 0x10) != 0
		self.MaxMode = (flags & 0x20) != 0
		self.BatteryLow = (flags & 0x40) != 0
		self.Value = frame[2] * 100 + frame[3] * 10 + frame[4] + frame[5] * 0.1

		return self.Value

	def GetValueString(self) -> str:
		if self.Value < 0:
			return 'N/A'
		if self.OverRange:
			return '> %.1f' % self.Value
		if self.UnderRange:
			return '< %.1f' % self.Value
		return '%.1f' % self.Value

	def __ReadingThread(self):
		while not self.__stop_flag:
			frame = self.ReadFrame(use_stop_flag=True)
			if len(frame) != 18:
				self.Value = MS6701.InvalidValue
			else:
				try:
					self.ParseFrame(frame)
				except Exception as _e:
					import traceback
					traceback.print_exc()
					self.Value = MS6701.InvalidValue

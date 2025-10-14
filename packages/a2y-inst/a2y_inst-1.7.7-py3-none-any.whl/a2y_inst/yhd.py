"""
深圳市誉恒达科技有限公司产品驱动
"""
from serial import Serial as _Serial
from threading import Thread as _Thread
from time import sleep as _sleep, time as _now
from typing import Union as _Union


class M300D:
	ACK = 0x6
	NACK = 0x15
	CmdStartScan = '\x1B\x31'
	CmdStopScan = '\x1B\x30'

	"""
	M300D 条码扫码枪驱动。M300D 除了能识别一维码外，还能识别 QRCode、DataMatrix 等二维码。
	"""
	def __init__(self, port: str, baudrate: int = 9600, *args, **kwargs):
		self.__serial = _Serial(port, baudrate, *args, **kwargs)
		self.__listening = False
		self.__stop_flag = False
		self.__scan_thread: _Union[_Thread, None] = None
		self.__code = ''
		self.__serial_timeout = 1
		self.__scan_timeout = 3  # 扫码超时设定值
		self.__postfix = '\r'

	@property
	def postfix(self):
		return self.__postfix

	@postfix.setter
	def postfix(self, value: str):
		assert value in ['', '\r', '\r\n']
		if value == '':
			command = 'DJ000'
		elif value == '\r':
			command = 'DK010'
		else:
			command = 'DK020'
		if value == '':
			if self.postfix != '':
				self.execute(command)
		elif value != self.postfix:
			self.execute(command)
			if self.postfix == '':
				self.execute('DJ010')
		self.__postfix = value

	@property
	def scan_timeout(self) -> float:
		return self.__scan_timeout

	@scan_timeout.setter
	def scan_timeout(self, value: float):
		assert value > 0
		self.__scan_timeout = value

	def execute(self, command: str):
		"""
		执行指令。对于那些像“开始扫码”指令这类带有返回数据的指令，调用者需要在执行完这条指令后自行读取返回数据。
		本函数仅判断 M300D 是否已经收到并“理解”了所发出的指令，也就是说仅接收 NACK 或 ACK 响应，不对返回数据进行接收或解析。
		"""
		self.__serial.reset_input_buffer()
		if command != M300D.CmdStartScan and command != M300D.CmdStopScan:
			if not command.startswith('R'):
				command = f'R{command}'
			if not command.endswith(';'):
				command = f'{command};'
		cmd = command.encode('latin')
		self.__serial.write(cmd)
		end = _now() + self.__serial_timeout
		while self.__serial.in_waiting == 0 and end >= _now():
			_sleep(0.05)
		if self.__serial.in_waiting == 0:
			raise IOError('Error: Communicate with M300D timeout: Device no response')

		fb = self.__serial.read(1)
		if fb[0] == M300D.NACK:
			raise ValueError('Error: Invalid command for M300D')
		elif fb[0] != M300D.ACK:
			raise IOError(f'Error: Unknown M300D feedback: {fb[0]:02X}H')

	def __read_until_linefeed(self) -> bytes:
		data = b''
		postfix = self.postfix.encode('latin')
		while self.__serial.in_waiting > 0:
			char = self.__serial.read(1)
			data += char
			if postfix and data.endswith(postfix):
				break
		return data

	def __scan_function(self) -> str:
		self.execute(M300D.CmdStopScan)
		self.execute(M300D.CmdStartScan)

		end = _now() + self.scan_timeout
		code = b''
		postfix = self.postfix.encode('latin')
		sleep_count = 0
		while not self.__stop_flag and end >= _now():
			if self.__serial.in_waiting > 0:
				code += self.__read_until_linefeed()
				if postfix:
					if code.endswith(postfix):
						break
				else:
					sleep_count = 0
			else:
				_sleep(0.01)
				if code:
					sleep_count += 1
					if sleep_count > 5:
						break

		return code.decode('latin').rstrip(self.postfix)

	def reset_factory_default(self):
		self.execute('AB160')
		self.__postfix = '\r'

	def scan(self) -> str:
		return self.__scan_function()

	def __scan_thread_function(self):
		code = ''
		try:
			code = self.__scan_function()
		except ValueError as _e:
			pass
		except IOError as _e:
			pass
		except Exception as _e:
			pass
		if not self.__stop_flag:
			self.__code = code
		self.__stop_flag = False

	def start_scan(self):
		if self.__scan_thread is not None:
			raise ValueError('Error: Scanning has been started. Wait for it')

		self.__code = ''
		self.__scan_thread = _Thread(target=self.__scan_thread_function)
		self.__scan_thread.start()

	def wait(self) -> str:
		if self.__scan_thread is None:
			raise ValueError('Error: Scanning has NOT been started. Start it first')
		self.__scan_thread.join()
		self.__scan_thread = None
		return self.__code

	def cancel(self):
		if self.__scan_thread is None:
			raise ValueError('Error: Scanning has NOT been started. No scanning to cancel')

		self.__stop_flag = True
		self.__scan_thread.join()
		self.__scan_thread = None

		self.execute(M300D.CmdStopScan)

	def close(self):
		if self.__scan_thread is not None:
			self.cancel()
		self.__serial.close()

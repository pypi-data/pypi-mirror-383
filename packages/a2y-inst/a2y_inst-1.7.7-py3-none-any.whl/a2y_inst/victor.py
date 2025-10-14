from serial import Serial as _Serial
from threading import Lock as _Lock
from time import sleep as _sleep
from enum import Enum as _Enum
from typing import Tuple as _Tuple


class Function(_Enum):
	DCV = '0'
	ACV = '1'
	DCI = '2'
	ACI = '3'
	OHM_2W = '4'
	OHM_4W = '5'
	CONT = '6'
	DIODE = '7'
	FREQ = '8'
	DUTY = '8'
	CAP = '9'
	TEMP = '\x3A'
	RTD = '\x3B'
	dBm = '\x3C'


class Range(_Enum):
	DCV_50mV = '0'
	DCV_500mV = '1'
	DCV_5V = '2'
	DCV_50V = '3'
	DCV_500V = '4'
	DCV_1000V = '5'

	DCI_500uA = '0'
	DCI_5000uA = '1'
	DCI_50mA = '2'
	DCI_500mA = '3'
	DCI_5A = '4'
	DCI_10A = '5'

	# TODO: 补充完善其他的量程值


class Speed(_Enum):
	Slow = '0'
	Fast = '1'


class VC8246:
	# 如果你想用 USB 虚拟串口，需要先在仪器上修改一下设置。设置方法：
	# 按一下“Utility”键，这时屏幕上显示“rS232”，表示当前通信接口是 DB9 的 RS232 接口。
	# 按一下向下的小三角方向键，屏幕上显示 USB。按一下“AUTO”按键，保存。设置完成，可以断电重启仪器。
	Head = '#*'
	Tail = '\r\n'

	def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1):
		"""
		在使用频率测试功能时，根据仪器文档，最好把 timeout 参数设置为比 3 稍大的值。
		"""
		self.__serial = _Serial(port, baudrate=baudrate, timeout=timeout)
		self.__lock = _Lock()

	def close(self):
		self.__serial.close()

	def open(self):
		self.__serial.open()

	@property
	def timeout(self) -> float:
		return self.__serial.timeout

	@timeout.setter
	def timeout(self, value: float):
		self.__serial.timeout = value

	@property
	def is_open(self) -> bool:
		return self.__serial.is_open

	@staticmethod
	def construct_data_frame(data: str) -> str:
		frame = f'{VC8246.Head}{data}{VC8246.Tail}'
		return frame

	def send_command(self, command: str):
		"""
		根据通信协议，把指令 command 包装成一个完整的数据帧，然后发送给仪器。
		通信时没有加锁，不能用在多线程环境。也不接收数据，调用者应当随后调用 recv_feedback 来收取仪器的响应数据。
		设计上调用者不应当直接使用此函数。
		"""
		frame = VC8246.construct_data_frame(command)
		data = frame.encode('latin')
		self.__serial.write(data)

	def recv_feedback(self) -> str:
		"""
		收取仪器返回的响应数据。根据通信协议，做最基本的解析，从数据帧中抽取出有用的数据，返回给调用者。
		通信时没有加锁，不能用在多线程环境。
		设计上调用者不应当直接使用此函数。
		"""
		raw_data = self.__serial.readline()
		data = raw_data.decode('latin')
		if data == '':
			raise TimeoutError('Receive from VC8246 timeout')
		if not data.startswith(VC8246.Head):
			raise IOError(f'Data received from VC8246 format invalid: "{data}"')
		if not data.endswith(VC8246.Tail):
			raise IOError(f'Data received from VC8246 format invalid: "{data}"')
		feedback = data[2:-2]
		return feedback

	def query(self, command: str) -> str:
		with self.__lock:
			self.__serial.reset_input_buffer()
			self.send_command(command)
			feedback = self.recv_feedback()
		return feedback

	def query_ack(self, command: str):
		feedback = self.query(command)
		if feedback == '\x15\x00':
			raise IOError(f'NAK from VC8246')
		if feedback != '\x06\x00':
			raise IOError(f'Feedback of command "{command}" from VC8246 invalid: "{feedback}"')

	def reset(self):
		"""
		复位仪器。之后，想再次远程控制仪器，需要先调用 connect 函数。
		"""
		self.query_ack('RST')

	def connect(self, timeout: float = 2):
		"""
		发送“ONL”指令，使得仪器进入远程控制状态。
		麻烦的是，如果仪器在收到此指令前已经处于远程控制状态时，它将不响应。我们无法知道是通信出了问题？还是原本就处于远控状态？
		为此，我们如果超时没有收到响应，就先发一个“RST”指令，复位仪器，然后再发送一次“ONL”指令。
		据观测，仪器复位大概需要 2 秒，这就是 timeout 参数的默认值的来源。
		"""
		try:
			self.query_ack('ONL')
		except TimeoutError:
			self.reset()
			_sleep(timeout)
			self.query_ack('ONL')

	def config(self, function: Function, measuring_range: Range, speed: Speed = Speed.Fast):
		"""
		配置仪器的测量功能、量程，以及速率。
		测量功能、量程，以及速率存在一定的对应关系。这个函数里面没有执行任何的检查。没有做过无效实验。
		请调用者自行保证使用对应功能有效的量程和速率。
		"""
		command = f'INS{function.value}{measuring_range.value}{speed.value}'
		self.query_ack(command)

	def fetch(self) -> _Tuple[float, float]:
		"""
		读取仪器当前读数。
		目前对返回数据的格式检查比较严格，对不同型号的仪器可能会不兼容。这需要开发者在出现问题时补充修正。
		返回值包括两项数据，第 0 项是测量值，第 1 项意义不明。待到明白时再做说明。
		频率测试跟占空比测试的功能码是一样的（8），那么，这两项数据是否一项是频率值，另一项是占空比值？有待验证。
		TODO: 如上所述
		"""
		feedback = self.query('RD?')
		if not feedback.startswith('RD'):
			raise IOError(f'Feedback of command "RD?" from VC8246 invalid: "{feedback}"')
		if len(feedback) != 2+7+7:
			raise IOError(f'Feedback of command "RD?" from VC8246 is unsupported: "{feedback}"')

		value_str = feedback[2:9]
		temp_str = feedback[9:-1]
		try:
			if value_str == '+FFFFFF':  # 超出量程
				value = float('inf')
			else:
				value = float(value_str)
			temp = float(temp_str)
		except ValueError:
			raise IOError(f'Value feedback from VC8246 is invalid: "{feedback}"')
		return value, temp

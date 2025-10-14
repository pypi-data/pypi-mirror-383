from enum import Enum as _Enum
from serial import Serial as _Serial
from time import sleep as _sleep
from typing import List as _List, Optional


class GPP4323Exception(IOError):
	pass


class GPP4323(_Serial):
	"""
	为访问、控制固纬 GPP 系列多通道程控直流电源提供便利。
	"""
	def __init__(self, port: str, baudrate: int = 115200):
		_Serial.__init__(self, port=port, baudrate=baudrate, timeout=0.5)
		self.__last_sent = ''
		self.__last_recv = ''

	def write_command(self, command: str):
		if not command.endswith('\n'):
			command = f'{command}\n'
		cmd = command.encode('ascii')
		self.__last_sent = cmd
		self.write(cmd)

	def read_feedback(self) -> str:
		fb = self.read_until()
		try:
			feedback = fb.decode('ascii')
		except UnicodeDecodeError:
			feedback = fb.decode('latin')
			self.__last_recv = feedback
			raise IOError(f'GPP 仪器返回数据编码异常：[{feedback}]')
		self.__last_recv = feedback
		if not feedback.endswith('\n'):
			raise GPP4323Exception(f'GPP仪器数据接收超时')

		return feedback.strip()

	def query(self, command: str) -> str:
		self.write_command(command)
		return self.read_feedback()

	def set_voltage(self, channel: int, voltage: float):
		"""
		设置输出电压值，单位：伏特
		"""
		cmd = f':source{channel}:voltage {voltage}\n'
		self.write_command(cmd)

	def set_current(self, channel: int, current: float):
		"""
		设置输出电流限制值，单位：安培
		"""
		cmd = f':source{channel}:current {current}\n'
		self.write_command(cmd)

	def get_voltage(self, channel: int) -> float:
		"""
		获取当前的输出电压设定值，单位：伏特
		"""
		feedback = self.query(f':source{channel}:voltage?\n')
		voltage = float(feedback)
		return voltage

	def get_current(self, channel: int) -> float:
		"""
		获取当前的输出电流限值设定值，单位：安培
		"""
		feedback = self.query(f':source{channel}:current?\n')
		current = float(feedback)
		return current

	def turn_off(self, channel: int):
		cmd = f':output{channel}:state off\n'
		self.write_command(cmd)

	def turn_on(self, channel: int):
		cmd = f':output{channel}:state on\n'
		self.write_command(cmd)

	def turn_off_all(self):
		cmd = ':alloutoff\n'
		self.write_command(cmd)

	def turn_on_all(self):
		self.write_command(':allouton\n')

	def measure_current(self, channel: int) -> float:
		"""
		测量指定通道的输出电流实际值，单位：安培
		"""
		feedback = self.query(f':measure{channel}:current?\n')
		current = float(feedback)
		return current

	def measure_voltage(self, channel: int) -> float:
		"""
		测量指定通道的输出电压实际值，单位：伏特
		"""
		feedback = self.query(f':measure{channel}:voltage?\n')
		voltage = float(feedback)
		return voltage

	def measure_power(self, channel: int) -> float:
		"""
		测量指定通道的输出功率实际值，单位：瓦特
		"""
		feedback = self.query(f':measure{channel}:power?\n')
		power = float(feedback)
		return power

	def measure_all_currents(self) -> _List[float]:
		"""
		测量所有通道的输出电流实际值，单位：安培
		"""
		feedback = self.query(f':measure:current:all?\n')
		tokens = feedback.split(',')
		currents = [float(token) for token in tokens]
		return currents


class HVTMode(_Enum):
	ACW = 'ACW'
	DCW = 'DCW'
	IR = 'IR'
	GB = 'GB'


class HVTResult:
	def __init__(self, mode: HVTMode, result: bool, voltage: float, value: float, test_time: float):
		self.mode = mode
		self.result = result
		self.voltage = voltage
		self.value = value
		self.test_time = test_time

		self.__raw = ''

	@property
	def raw(self) -> str:
		return self.__raw

	@staticmethod
	def parse_result(result_str: str):
		items = result_str.split(',')
		assert len(items) >= 5, f'GPT9900 测试结果格式错误，逗号分隔至少 5 项：[{result_str}]'
		mode = HVTMode(items[0].strip())
		ok = items[1].strip() == 'PASS'
		voltage = float(items[2].strip()[:-2])
		value = float(items[3].strip()[:-2])
		test_time = float(items[4].strip()[2:-1])

		result = HVTResult(
			mode=mode,
			result=ok,
			voltage=voltage,
			value=value,
			test_time=test_time
		)
		result.__raw = result_str.strip()
		return result


class GPT9900:
	VerifyWaitTime = 0.1

	def __init__(self, port: str, baudrate: int, timeout: float = 1):
		self.__serial = _Serial(port=port, baudrate=baudrate, timeout=timeout)

	def close(self):
		self.__serial.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def query(self, command: str):
		in_waiting = self.__serial.in_waiting
		if in_waiting > 0:
			self.__serial.read(in_waiting)
		self.__serial.write(command.encode('latin'))
		if not command.endswith('\n'):
			self.__serial.write(b'\n')
		feedback = self.__serial.readline().strip()
		if not feedback:
			raise IOError('GPT9904 通信超时')
		return feedback.decode('latin')

	@property
	def rise_time(self) -> float:
		feedback = self.query('MANU:RTime?').lower()
		assert feedback.endswith(' s'), f'GPT9904 上升时间反馈格式错误，没有以“ S”结尾：[{feedback}]'
		result = float(feedback[:-2])
		return round(result, 1)

	def send(self, command: str):
		self.__serial.write(command.encode('latin'))
		if not command.endswith('\n'):
			self.__serial.write(b'\n')

	@rise_time.setter
	def rise_time(self, value: float):
		value = round(value, 1)
		self.send(f'MANU:RTime {value}')

		_sleep(GPT9900.VerifyWaitTime)
		rtime = self.rise_time
		assert abs(rtime-value) <= 0.01, f'设置上升时间失败。当前值：{rtime}；目标值：{value}'

	@property
	def mode(self) -> HVTMode:
		feedback = self.query('MANU:EDIT:MODE?')
		return HVTMode(feedback)

	@mode.setter
	def mode(self, mode: HVTMode):
		command = f'MANU:EDIT:MODE {mode.value}'
		self.send(command)

		_sleep(GPT9900.VerifyWaitTime)
		assert self.mode == mode, f'测试模式设置失败。当前值：{self.mode.value}；目标值：{mode.value}'

	@property
	def voltage(self) -> float:
		mode = self.mode
		command = f'MANU:{mode.value}:VOLTAGE?'
		feedback = self.query(command).lower()
		assert feedback.endswith('kv'), f'GPT9904 测试电压反馈格式错误，没有以“ kV”结尾：[{feedback}]'
		result = float(feedback[:-2])
		return round(result, 3)

	@voltage.setter
	def voltage(self, value: float):
		mode = self.mode
		voltage = round(value, 3)
		command = f'MANU:{mode.value}:VOLTAGE {voltage}'
		self.send(command)

		_sleep(GPT9900.VerifyWaitTime)
		volt = self.voltage
		assert abs(volt - voltage) < 0.001, f'测试电压设置失败。当前值：{volt}；目标值：{voltage}'

	@property
	def test_time(self) -> float:
		mode = self.mode
		command = f'MANU:{mode.value}:TTime?'
		feedback = self.query(command).lower()
		if 'off' in feedback:
			return float('inf')
		assert feedback.endswith(' s'), f'GPT9904 测试时间反馈格式错误，没有以“ S”结尾：[{feedback}]'
		result = float(feedback[:-2])
		return round(result, 1)

	@test_time.setter
	def test_time(self, value: float):
		mode = self.mode
		test_time = round(value, 1)
		command = f'MANU:{mode.value}:TTime {test_time}'
		self.send(command)

		_sleep(GPT9900.VerifyWaitTime)
		ttime = self.test_time
		assert abs(ttime - test_time) < 0.1, f'测试时间设置失败。当前值：{ttime}；目标值：{test_time}'

	@property
	def current_upper(self) -> float:
		mode = self.mode
		command = f'MANU:{mode.value}:CHISet?'
		feedback = self.query(command).lower()
		assert feedback.endswith('ma'), f'GPT9904 电流上限反馈格式错误，没有以“mA”结尾：[{feedback}]'
		result = float(feedback[:-2])
		return round(result, 3)

	@current_upper.setter
	def current_upper(self, value: float):
		mode = self.mode
		current_upper = round(value, 3)
		command = f'MANU:{mode.value}:CHISet {current_upper}'
		self.send(command)

		_sleep(GPT9900.VerifyWaitTime)
		upper = self.current_upper
		assert abs(upper - current_upper) < 0.001, f'电流上限设置失败。当前值：{upper}；目标值：{current_upper}'

	@property
	def current_lower(self) -> float:
		mode = self.mode
		command = f'MANU:{mode.value}:CLOSet?'
		feedback = self.query(command).lower()
		assert feedback.endswith('ma'), f'GPT9904 电流下限反馈格式错误，没有以“mA”结尾：[{feedback}]'
		result = float(feedback[:-2])
		return round(result, 3)

	@current_lower.setter
	def current_lower(self, value: float):
		mode = self.mode
		current_lower = round(value, 3)
		command = f'MANU:{mode.value}:CLOSet {current_lower}'
		self.send(command)

		_sleep(GPT9900.VerifyWaitTime)
		lower = self.current_lower
		assert abs(lower - current_lower) < 0.001, f'电流下限设置失败。当前值：{lower}；目标值：{current_lower}'

	def prepare(
			self,
			mode: HVTMode, voltage: float, test_time: float,
			current_upper: Optional[float] = None,
			current_lower: Optional[float] = None
	):
		self.mode = mode
		self.voltage = voltage
		self.test_time = test_time
		if current_upper is not None:
			self.current_upper = current_upper
		if current_lower is not None:
			self.current_lower = current_lower

	def start(self):
		command = 'FUNCTION:TEST ON'
		self.send(command)

	def stop(self):
		command = 'FUNCTION: TEST OFF'
		self.send(command)

	@property
	def is_testing(self) -> bool:
		command = 'FUNCTION:TEST?'
		feedback = self.query(command)
		fb = feedback.lower()
		assert 'on' in fb or 'off' in fb, f'测试状态反馈格式错误：[{feedback}]'
		return 'on' in fb

	@property
	def measurement(self) -> HVTResult:
		result_str = self.query('MEASURE?')
		return HVTResult.parse_result(result_str)

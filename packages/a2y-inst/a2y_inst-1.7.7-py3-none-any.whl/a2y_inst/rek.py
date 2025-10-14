from a2y_handy import make_enum_instance_from_name
from a2y_kcom import create_serial_instance as _create_serial_instance
from enum import Enum
from threading import Lock as _Lock
from time import sleep as _sleep
from typing import Optional as _Optional


class HVTMode(Enum):
	AC = 1
	DC = 2
	IR = 3


class HVTResult:
	def __init__(
			self, mode: HVTMode, result_desc: str, voltage: float, value: float,
			step: int, upper: float, lower: float, unit: str
	):
		self.mode = mode
		self.result_desc = result_desc
		self.voltage = voltage
		self.value = value
		self.step = step
		self.upper = upper
		self.lower = lower
		self.unit = unit

		self.__raw = ''

	@staticmethod
	def convert_limit(data: str, direction):
		data = data.strip()
		if data == 'OFF':
			return direction * float('inf')
		return float(data[:-2])

	@property
	def raw(self) -> str:
		return self.__raw

	@property
	def is_testing(self) -> bool:
		return self.result_desc == 'ON PROGRESS'

	@property
	def ok(self) -> bool:
		return self.result_desc == 'PASS'

	@staticmethod
	def parse_result(result_str: str):
		items = result_str.split(',')
		assert len(items) >= 7, f'RK9900 测试结果格式错误，逗号分隔项目数必须为 7 项：[{result_str}]'
		step = int(items[0].strip())
		mode = make_enum_instance_from_name(HVTMode, items[1].strip())
		voltage = float(items[2].strip()[:-2])
		upper = HVTResult.convert_limit(items[3], 1)
		lower = HVTResult.convert_limit(items[4], -1)
		value = float(items[5].strip()[:-2])
		unit = items[5].strip()[-2:]
		result_desc = items[6].strip()

		result = HVTResult(
			mode=mode,
			result_desc=result_desc,
			voltage=voltage,
			value=value,
			step=step,
			upper=upper,
			lower=lower,
			unit=unit
		)
		result.__raw = result_str.strip()
		return result


class RK9920:
	VerifyWaitTime = 0.1

	def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
		self.__serial = _create_serial_instance(port=port, baudrate=baudrate, timeout=timeout)
		self.__lock = _Lock()
		self.__last_command_sent = ''
		self.__last_feedback_received = ''
		self.__step = 1
		self.__mode: _Optional[HVTMode] = None

	@property
	def step(self) -> int:
		return self.__step

	@step.setter
	def step(self, value: int):
		assert isinstance(value, int) and value > 0
		self.__step = value

	@property
	def last_command_sent(self) -> str:
		return self.__last_command_sent

	@property
	def last_feedback_received(self) -> str:
		return self.__last_feedback_received

	def close(self):
		self.__serial.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def query(self, command: str, retry_count: int = 2, interval: float = 0.5):
		counter = 0
		with self.__lock:
			while counter <= retry_count:
				in_waiting = self.__serial.in_waiting
				if in_waiting > 0:
					self.__serial.read(in_waiting)
				self.__send(command)
				feedback = self.__serial.readline().strip()
				if feedback and b'ERROR' not in feedback:
					break
				elif counter < retry_count:
					_sleep(interval)
					counter += 1
		if not feedback:
			raise IOError(f'Rek 仪器[{self.__serial.port}]通信超时')
		# 返回的数据中含有 UTF8 字符“Ω”，需要用“utf8”来解码
		self.__last_feedback_received = feedback.decode('utf8')
		return self.__last_feedback_received

	def __send(self, command: str):
		self.__last_feedback_received = ''
		self.__serial.write(command.encode('utf8'))
		if not command.endswith('\n'):
			self.__serial.write(b'\n')
		self.__last_command_sent = command

	def send(self, command: str):
		with self.__lock:
			self.__send(command)

	@property
	def mode(self) -> HVTMode:
		if self.__mode is None:
			feedback = self.query(f'FUNCTION:SOURCE:STEP{self.step}:MODE?')
			try:
				mode_int = int(feedback)
				assert 1 <= mode_int <= 3
			except Exception as _e:
				raise IOError(f'读取测试模式时 Rek 返回数据格式有误：{feedback}')
			self.__mode = HVTMode(mode_int)
		return self.__mode

	@mode.setter
	def mode(self, value: HVTMode):
		self.__mode = value

	def __make_setting_command(self, name: str, value):
		return f'FUNCTION:SOURCE:STEP{self.step}:MODE:{self.mode.name}:{name} {value}\n'

	def __make_query_command(self, name: str):
		return f'FUNCTION:SOURCE:STEP{self.step}:MODE:{self.mode.name}:{name}?\n'

	def __query_float_setting_item(self, name: str, digit_count: int):
		cmd = self.__make_query_command(name)
		feedback = self.query(cmd)
		try:
			result = float(feedback)
		except Exception as _e:
			raise IOError(f'读取[{name}]时仪器返回数据格式有误：{feedback}')
		return round(result, digit_count)

	def __set_float_setting_item(self, name: str, value, digit_count: int):
		value = round(value, digit_count)
		cmd = self.__make_setting_command(name, value)
		self.send(cmd)

		_sleep(RK9920.VerifyWaitTime)
		feedback_value = self.__query_float_setting_item(name, digit_count)
		min_diff = 1 / pow(10, digit_count + 1)
		assert abs(feedback_value - value) <= min_diff, f'设置[{name}]失败。当前值：{feedback_value}；目标值：{value}'

	@property
	def rise_time(self) -> float:
		return self.__query_float_setting_item('RTIME', 1)

	@rise_time.setter
	def rise_time(self, value: float):
		self.__set_float_setting_item('RTIME', value, 1)

	@property
	def fall_time(self) -> float:
		return self.__query_float_setting_item('FTIME', 1)

	@fall_time.setter
	def fall_time(self, value: float):
		self.__set_float_setting_item('FTIME', value, 1)

	@property
	def test_time(self) -> float:
		return self.__query_float_setting_item('TTIME', 1)

	@test_time.setter
	def test_time(self, value: float):
		self.__set_float_setting_item('TTIME', value, 1)

	@property
	def voltage(self) -> float:
		return self.__query_float_setting_item('VOLTAGE', 3)

	@voltage.setter
	def voltage(self, value: float):
		self.__set_float_setting_item('VOLTAGE', value, 3)

	@property
	def upper(self) -> float:
		digit_count = 1 if self.mode == HVTMode.IR else 3
		return self.__query_float_setting_item('UPLM', digit_count)

	@upper.setter
	def upper(self, value: float):
		digit_count = 1 if self.mode == HVTMode.IR else 3
		self.__set_float_setting_item('UPLM', value, digit_count)

	@property
	def lower(self) -> float:
		digit_count = 1 if self.mode == HVTMode.IR else 3
		return self.__query_float_setting_item('DNLM', digit_count)

	@lower.setter
	def lower(self, value: float):
		digit_count = 1 if self.mode == HVTMode.IR else 3
		self.__set_float_setting_item('DNLM', value, digit_count)

	def start(self):
		cmd = 'FUNC:START\n'
		feedback = self.query(cmd)
		if not feedback.startswith('Testing'):
			raise IOError('RK 启动测试失败')

	def stop(self):
		self.send('FUNC:STOP\n')

	@property
	def measurement(self) -> HVTResult:
		result_str = self.query('FETCH?')
		return HVTResult.parse_result(result_str)

	@property
	def is_testing(self) -> bool:
		result = self.measurement
		return result.is_testing

	@property
	def display_page(self) -> int:
		cmd = 'DISPLAY:PAGE?\n'
		feedback = self.query(cmd)
		page = int(feedback)
		return page

	@display_page.setter
	def display_page(self, value: int):
		assert 1 <= value <= 4, f'RK9920 display page [{value}] out of range [1, 4]'
		cmd = f'DISPLAY:PAGE {value}\n'
		self.send(cmd)

		_sleep(RK9920.VerifyWaitTime)

		real_page = self.display_page
		assert real_page == value, f'设置仪器[{self.__serial.port}]显示页面失败。目标页[{value}，当前页[{real_page}]'

	def turn_to_test_page(self):
		self.display_page = 1

	def disable_result_auto_upload(self):
		cmd = 'FETCH:AUTO 0\n'
		self.send(cmd)

	def enable_result_auto_upload(self):
		cmd = 'FETCH:AUTO 1\n'
		self.send(cmd)

	def prepare(
			self,
			mode: HVTMode, voltage: float, test_time: float,
			current_upper: _Optional[float] = None,
			current_lower: _Optional[float] = None
	):
		"""
		为了方便可能出现的老代码维护工作，提供此接口。这个接口出现在 gwinstek.GPT9900 的 API 中。
		由于 GPT9900 缺乏跌落时间（FTime）的控制功能，客户将逐渐淘汰该仪器，改用 RK9920。
		在新项目代码中应尽量避免使用该接口。
		"""
		self.mode = mode
		self.voltage = voltage
		self.test_time = test_time
		if current_upper is not None:
			self.upper = current_upper
		if current_lower is not None:
			self.lower = current_lower

	# 以下四个“current”相关接口，类似“prepare”，仅用于旧代码维护，不宜在新项目中使用。
	@property
	def current_upper(self) -> float:
		return self.upper

	@current_upper.setter
	def current_upper(self, value: float):
		self.upper = value

	@property
	def current_lower(self) -> float:
		return self.lower

	@current_lower.setter
	def current_lower(self, value: float):
		self.lower = value

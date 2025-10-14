""" 提供汉晟普源直流程控电源的驱动"""

from a2y_modbus import FixMaster as _Bus
from enum import Enum


class Mode(Enum):
	CV = 0
	CC = 1
	CP = 2


class DCSource:
	def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
		# 电源的站号，出厂设置默认值为 0
		self.__bus = _Bus(station=0, port=port, baudrate=baudrate, timeout=timeout)
		self.__voltage_decimal_digit_count = 1
		self.__current_decimal_digit_count = 3

		self.__mode = Mode.CV

	@property
	def station(self):
		return self.__bus.station

	@station.setter
	def station(self, value: int):
		self.__bus.station = value

	@property
	def setting_voltage(self) -> float:
		vol_int = self.__bus.read_uint16(0)
		voltage = round(vol_int / pow(10, self.__voltage_decimal_digit_count), self.__voltage_decimal_digit_count)
		return voltage

	@setting_voltage.setter
	def setting_voltage(self, value: float):
		assert value >= 0, f'The setting voltage value is out of range: {value}, it must be not less than 0.'
		vol_int = int(round(value * pow(10, self.__voltage_decimal_digit_count), 0))
		assert vol_int <= 65535, f'The setting voltage value is out of range: {value}, too large.'

		self.__bus.write_register(0, vol_int)

	@property
	def setting_current(self) -> float:
		cur_int = self.__bus.read_uint16(1)
		current = round(cur_int / pow(10, self.__current_decimal_digit_count), self.__current_decimal_digit_count)
		return current

	@setting_current.setter
	def setting_current(self, value: float):
		assert value >= 0, f'The setting current value is out of range: {value}, it must be not less than 0.'
		cur_int = int(round(value * pow(10, self.__current_decimal_digit_count), 0))
		assert cur_int <= 65535, f'The setting current value is out of range: {value}, too large.'

		self.__bus.write_register(1, cur_int)

	@property
	def real_voltage(self) -> float:
		vol_int = self.__bus.read_uint16(2)
		voltage = round(vol_int / pow(10, self.__voltage_decimal_digit_count), self.__voltage_decimal_digit_count)
		return voltage

	@property
	def real_current(self) -> float:
		cur_int = self.__bus.read_uint16(3)
		current = round(cur_int / pow(10, self.__current_decimal_digit_count), self.__current_decimal_digit_count)
		return current

	@property
	def mode(self) -> Mode:
		mode_value = self.__bus.read_uint16(9)
		mode = Mode(mode_value)
		return mode

	@mode.setter
	def mode(self, value: Mode):
		mode_value = value.value
		self.__bus.write_register(9, mode_value)

	def output_on(self):
		self.__bus.write_register(4, 1)

	def output_off(self):
		self.__bus.write_register(4, 0)

	def close(self):
		self.__bus.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

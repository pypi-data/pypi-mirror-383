from serial import Serial as Serial
from threading import Lock as _Lock
from typing import Union as _Union
from enum import Enum


class LoadMode(Enum):
	CC = 0
	CV = 1
	CW = 2
	CR = 3


class IT8500plus:
	def __init__(self, port: str, baudrate: int = 9600):
		self.__serial = Serial(port, baudrate=baudrate, timeout=0.5)
		self.__lock = _Lock()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	@staticmethod
	def checksum(data: _Union[bytearray, bytes]) -> int:
		assert len(data) >= 25
		crc = 0
		for i in range(25):
			crc += data[i]
		return crc & 0xFF

	# def read_frame(self):
	# 	frame = self.__serial.read(26)
	# 	if len(frame) != 26:
	# 		raise IOError('Communicate with IT8500plus timeout.')
	# 	if frame[0] != 0xAA:
	# 		raise IOError('IT8500plus frame header invalid.')
	# 	if IT8500plus.checksum(frame) != frame[25]:
	# 		raise IOError('IT8500plus frame checksum error.')
	#
	# 	return frame

	def __query(self, frame: _Union[bytearray, bytes]):
		with self.__lock:
			self.__serial.flush()
			self.__serial.write(frame)
			feedback = self.__serial.read(26)
		if len(feedback) != 26:
			raise IOError('Communicate with IT8500plus timeout.')
		if feedback[0] != 0xAA:
			raise IOError('IT8500plus frame header invalid.')
		if IT8500plus.checksum(feedback) != feedback[25]:
			raise IOError('IT8500plus frame checksum error.')

		return feedback

	def __set_something(self, frame):
		feedback = self.__query(frame)
		if feedback[2] != 0x12:
			raise IOError(f'IT8500plus Setting Feedback frame format invalid: command byte is not 0x12: {feedback[2]}.')
		if feedback[3] != 0x80:
			raise IOError(f'IT58500plus says that you have make some mistakes on your command: {feedback[3]:02X}H.')

	def __get_one_byte(self, frame) -> int:
		feedback_frame = self.__query(frame)
		cmd = frame[2]
		if feedback_frame[2] != cmd:
			raise IOError(f'IT8500plus feedback command byte is not matched. Send: {cmd:02X}H, Recv: {feedback_frame[2]:02X}H.')
		return feedback_frame[3]

	def __get_uint16(self, frame) -> int:
		feedback_frame = self.__query(frame)
		cmd = frame[2]
		if feedback_frame[2] != cmd:
			raise IOError(f'IT8500plus feedback command byte is not matched. Send: {cmd:02X}H, Recv: {feedback_frame[2]:02X}H.')
		return (feedback_frame[4] << 8) | feedback_frame[3]

	def __get_uint32(self, frame) -> int:
		feedback_frame = self.__query(frame)
		cmd = frame[2]
		if feedback_frame[2] != cmd:
			raise IOError(f'IT8500plus feedback command byte is not matched. Send: {cmd:02X}H, Recv: {feedback_frame[2]:02X}H.')
		return feedback_frame[3] | (feedback_frame[4] << 8) | (feedback_frame[5] << 16) | (feedback_frame[6] << 24)

	@staticmethod
	def build_frame(station: int, cmd: int, data: _Union[bytearray, bytes, list]):
		assert len(data) <= 22
		frame = bytearray(26)
		frame[0] = 0xAA
		frame[1] = station
		frame[2] = cmd
		for idx, byte in enumerate(data):
			frame[idx+3] = byte
		frame[-1] = IT8500plus.checksum(frame)
		return frame

	def set_control_mode(self, station: int, mode: _Union[str, bool, int]):
		"""
		设置负载仪的控制模式：通过本地面板控制的本地模式，或者是通过通信端口控制的远程模式（remote mode）。
		"""
		if isinstance(mode, str):
			mode_value = 1 if mode == 'remote' else 0
		elif isinstance(mode, bool):
			mode_value = 1 if mode else 0
		elif isinstance(mode, int):
			mode_value = 0 if mode == 0 else 1
		else:
			raise ValueError(f'Unknown mode: {mode} with type {type(mode)}.')
		frame = IT8500plus.build_frame(station, 0x20, [mode_value])
		self.__set_something(frame)

	def set_remote_mode(self, station: int):
		"""
		设置负载仪为远程模式。只有在远程模式下，负载仪才会响应从通信端口传入的其他的设置、控制命令。
		"""
		self.set_control_mode(station, mode=1)

	def set_load_mode(self, station: int, mode: LoadMode):
		frame = IT8500plus.build_frame(station, 0x28, [mode.value])
		self.__set_something(frame)

	def get_load_mode(self, station: int):
		frame = IT8500plus.build_frame(station, 0x29, [])
		feedback = self.__get_one_byte(frame)
		return LoadMode(feedback)

	def __set_float_value(self, station: int, cmd: int, value: float, coe: int):
		value_int = int(round(value * coe, 0))
		data = [0] * 4
		data[0] = value_int & 0xFF
		data[1] = (value_int >> 8) & 0xFF
		data[2] = (value_int >> 16) & 0xFF
		data[3] = (value_int >> 24) & 0xFF
		frame = IT8500plus.build_frame(station, cmd, data)
		self.__set_something(frame)

	def __get_float_value(self, station: int, cmd: int, coe: int) -> float:
		frame = IT8500plus.build_frame(station, cmd, [])
		value = self.__get_uint32(frame)
		return value / coe

	def set_max_voltage(self, station: int, voltage: float):
		self.__set_float_value(station, 0x22, voltage, 1000)

	def get_max_voltage(self, station: int):
		return self.__get_float_value(station, 0x23, 1000)

	def set_max_current(self, station: int, current: float):
		self.__set_float_value(station, 0x24, current, 10000)

	def get_max_current(self, station: int):
		return self.__get_float_value(station, 0x25, 10000)

	def set_max_power(self, station: int, power: float):
		self.__set_float_value(station, 0x26, power, 1000)

	def get_max_power(self, station: int):
		return self.__get_float_value(station, 0x27, 1000)

	def set_cc_current(self, station: int, current: float):
		self.__set_float_value(station, 0x2A, current, 10000)

	def get_cc_current(self, station: int) -> float:
		return self.__get_float_value(station, 0x2B, 10000)

	def set_cv_voltage(self, station: int, voltage: float):
		self.__set_float_value(station, 0x2C, voltage, 1000)

	def get_cv_voltage(self, station: int) -> float:
		return self.__get_float_value(station, 0x2D, 1000)

	def set_cw_power(self, station: int, power: float):
		self.__set_float_value(station, 0x2E, power, 1000)

	def get_cw_power(self, station: int) -> float:
		return self.__get_float_value(station, 0x2F, 1000)

	def set_cr_resistance(self, station: int, resistance: float):
		self.__set_float_value(station, 0x30, resistance, 1000)

	def get_cr_resistance(self, station: int):
		return self.__get_float_value(station, 0x31, 1000)

	def get_load_status(self, station: int) -> dict:
		status = dict()
		frame = IT8500plus.build_frame(station, 0x5F, [])
		feedback = self.__query(frame)
		cmd, count = 0x5F, 26-3-1
		if feedback[2] != cmd:
			raise IOError(f'IT8500plus feedback command byte is not matched. Send: {cmd:02X}H, Recv: {feedback[2]:02X}H.')
		data = feedback[3:3+count]
		for idx, name in enumerate(['voltage', 'current', 'power']):
			start = idx * 4
			value = data[start] | (data[start+1] << 8) | (data[start+2] << 16) | (data[start+3] << 24)
			status[name] = value
		status['operation_status'] = data[12]
		status['query_status'] = data[13] | (data[14] << 8)
		# TODO: 保存其他那些“散热器温度”等数据
		return status

	def get_real_current(self, station: int) -> float:
		status = self.get_load_status(station)
		return status['current'] / 10000

	def get_real_voltage(self, station: int) -> float:
		status = self.get_load_status(station)
		return status['voltage'] / 1000

	def get_real_power(self, station: int) -> float:
		status = self.get_load_status(station)
		return status['power'] / 1000

	def set_input_state(self, station: int, state: _Union[bool, str]):
		if isinstance(state, str):
			if state.upper() in ['ON', '1']:
				i_state = 1
			else:
				i_state = 0
		else:
			i_state = 1 if state else 0
		frame = IT8500plus.build_frame(station, 0x21, [i_state])
		self.__set_something(frame)

	def turn_on(self, station: int):
		self.set_input_state(station, True)

	def turn_off(self, station: int):
		self.set_input_state(station, False)

	def close(self):
		self.__serial.close()

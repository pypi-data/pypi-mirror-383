from a2y_kcom import create_serial_instance
from a2y_modbus import ModbusStatic
from threading import Lock
from time import sleep as _wait, time as _now
from typing import Sequence


class ADSException(Exception):
	pass


class ADS906:
	MinDuration = 0.05
	CMD_Code_Read = 0x10
	CMD_Code_Write = 0x11
	FuncCode_Map_DataLength = {
		0x01: 0x1C,
		0x02: 0x06,
		0x08: 0x0F,
		0xB3: 0x19,
		0xFF: 0x03,
	}

	def __init__(self, station: int, port: str, baudrate: int = 115200, timeout: float = 0.5, **kwargs):
		self.__station = station
		self.__serial = create_serial_instance(port=port, baudrate=baudrate, timeout=timeout, **kwargs)
		self.__lock = Lock()
		self.__last_data_sent = []
		self.__last_data_recv = []
		self.__last_write_time = 0

	def close(self):
		self.__serial.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	@property
	def station(self):
		return self.__station

	@property
	def last_data_sent(self):
		return list(self.__last_data_sent)

	@property
	def last_data_recv(self):
		return list(self.__last_data_recv)

	@staticmethod
	def construct_command(station: int, cmd_code: int, func_code: int, data: Sequence[int]):
		command = [station, cmd_code, func_code, len(data)]
		command.extend(data)
		crc = ModbusStatic.calculate_crc(command)
		command.extend(crc)
		return command

	def __recv_helper(self):
		head_str = self.__serial.read(4)
		frame = list(head_str)
		if len(frame) == 4 and frame[0] == self.station and frame[1] == 0x12:
			data_len = frame[3]
			data_str = self.__serial.read(data_len)
			data = [c for c in data_str]
			frame.extend(data)
			if len(data) == data_len:
				crc = self.__serial.read(2)
				crc_calc = ModbusStatic.calculate_crc(frame)
				frame.extend(crc)
				self.__last_data_recv = frame
				frame_str = [f'{c:02X}' for c in frame]
				if len(crc) == 2:
					if crc_calc[0] == crc[0] and crc_calc[1] == crc[1]:
						return data
					else:
						desc = f'ADS906 CRC Error: [{', '.join(frame_str)}]'
				else:
					desc = f'ADS906 Invalid Frame: [{', '.join(frame_str)}]'
			else:
				self.__last_data_recv = frame
				frame_str = [f'{c:02X}' for c in frame]
				desc = f'ADS906 Invalid Frame: [{', '.join(frame_str)}]'
		else:
			self.__last_data_recv = frame
			frame_str = [f'{c:02X}' for c in frame]
			desc = f'ADS906 Invalid Frame: [{', '.join(frame_str)}]'

		raise ADSException(desc)

	def query(self, func_code: int, data: Sequence[int]):
		cmd_code = ADS906.CMD_Code_Write if data else ADS906.CMD_Code_Read
		command = ADS906.construct_command(self.station, cmd_code, func_code, data)
		with self.__lock:
			self.__serial.flushInput()
			duration = _now() - self.__last_write_time
			if duration < ADS906.MinDuration:
				_wait(ADS906.MinDuration - duration)
			self.__serial.write(command)
			self.__last_data_sent = command
			data = self.__recv_helper()

		if cmd_code == ADS906.CMD_Code_Read:
			data_len_needed = ADS906.FuncCode_Map_DataLength.get(func_code, 0)
			if data_len_needed > 0:
				if data_len_needed != len(data):
					raise ADSException(f'ADS906 Feedback Data Length Incorrect: {data_len_needed} wanted, get {len(data)}')
		return data

	def out_on(self):
		self.query(4, (1, 0, 0))

	def out_off(self):
		self.query(4, (0, 0, 0))

	def set_voltage(self, voltage: float):
		"""
		voltage: 单位：伏特（V）
		"""
		volt = int(round(voltage * 1000, 0))  # mV
		data = (0, ((volt >> 8) & 0xFF), (volt & 0xFF), 0, 0, 0, 0, 0)
		self.query(0x10, data)

	def get_values(self) -> dict[str, float]:
		data = self.query(0xB3, [])
		voltage_uv = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | (data[3])
		current_ua = (data[4] << 24) | (data[5] << 16) | (data[6] << 8) | (data[7])
		voltage = voltage_uv / 1000000
		current = current_ua / 1000000
		return dict(voltage=voltage, current=current)

	def get_average_values(self):
		data = self.query(0x08, [])
		voltage_raw = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | (data[3])
		volt_unit = data[4]
		current_raw = (data[5] << 24) | (data[6] << 16) | (data[7] << 8) | (data[8])
		curr_unit = data[9]
		curr_direction = -1 if data[10] == 1 else 1
		voltage = voltage_raw / pow(10, (volt_unit - 1) * 3)
		current = current_raw / pow(10, (curr_unit - 1) * 3) * curr_direction
		return dict(voltage=voltage, current=current)

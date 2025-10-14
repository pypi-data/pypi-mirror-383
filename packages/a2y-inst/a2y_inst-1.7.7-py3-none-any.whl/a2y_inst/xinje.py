from a2y_modbus import Master as _Modbus, ModbusTCPMaster as _ModbusTCPMaster
import struct
from threading import Lock as _Lock
from typing import List as _List, Sequence as _Sequence


class XCPlc:
	def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.3):
		self.__modbus = _Modbus(port, baudrate=baudrate, timeout=timeout)
		self.__lock = _Lock()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.__modbus.close()

	def set_coil(self, station: int, name: str, value: bool):
		coil_type = name[0]
		if coil_type == 'Y':
			start_address = 0x4800
		elif coil_type == 'X':
			raise TypeError(f'Writing readonly coil: "{name}".')
		else:
			raise TypeError(f'Coil type "{coil_type}" is not supported yet.')
		shift = int(name[1:], 8)
		with self.__lock:
			self.__modbus.write_coil(station=station, address=start_address + shift, value=value)

	def get_coils(self, station: int, name: str, count: int) -> _List[bool]:
		assert 0 < count <= 16
		coil_type = name[0]
		if coil_type == 'X':
			start_address = 0x4000
		elif coil_type == 'Y':
			start_address = 0x4800
		else:
			raise TypeError(f'Coil type "{coil_type}" is not supported yet.')
		shift = int(name[1:], 8)
		with self.__lock:
			values = self.__modbus.read_coils(station=station, address=start_address + shift, count=count)
		return values

	def get_coil(self, station: int, name: str) -> bool:
		return self.get_coils(station, name, 1)[0]

	@staticmethod
	def register_name_to_address(name: str) -> int:
		num_start_idx = -1
		for idx, char in enumerate(name):
			if str.isdigit(char):
				num_start_idx = idx
				break
		assert num_start_idx > 0
		register_type = name[:num_start_idx]
		if register_type != 'D':
			raise TypeError(f'Register type "{register_type}" is not supported yet.')
		address = int(name[num_start_idx:])
		return address

	def set_uint16(self, station: int, name: str, value: int):
		address = XCPlc.register_name_to_address(name)
		with self.__lock:
			self.__modbus.write_uint16(station, address, value)

	def get_uint16(self, station: int, name: str) -> int:
		address = XCPlc.register_name_to_address(name)
		with self.__lock:
			return self.__modbus.read_register(station, address)

	def get_multi_uint16(self, station: int, name: str, count: int) -> _List[int]:
		address = XCPlc.register_name_to_address(name)
		with self.__lock:
			return self.__modbus.read_registers(station, address, count)


class XD5E:
	def __init__(self, host: str, port: int = 502, station: int = 1, timeout: float = 0.5):
		self.__modbus = _ModbusTCPMaster(host=host, port=port, station=station, timeout=timeout)

	def close(self):
		self.__modbus.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	@property
	def station(self):
		return self.__modbus.station

	@station.setter
	def station(self, value: int):
		self.__modbus.station = value

	@staticmethod
	def register_name_to_address(name: str) -> int:
		upper = name.upper()
		if upper.startswith('D'):
			address = int(upper[1:])
			assert 0 <= address < 20480, f'D register out of range [0, 20480)'
		elif upper.startswith('HD'):
			address = int(upper[2:])
			assert 0 <= address < 6144, f'HD register out of range [0, 6144)'
			address += 0xA080
		else:
			raise ValueError(f'Register type {upper} not supported yet')

		return address

	@staticmethod
	def coil_name_to_address(name: str) -> int:
		upper = name.upper()
		if upper[0] == 'M':
			address = int(upper[1:])
			assert 0 <= address < 20480, f'M coil out of range [0, 20480): {name}'
		else:
			raise ValueError(f'Coil type [{name}] not supported yet.')
		return address

	def get_multi_coils(self, name: str, count: int) -> _List[bool]:
		address = XD5E.coil_name_to_address(name)
		return self.__modbus.read_coils(address, count)

	def set_coil(self, name: str, value: bool):
		address = XD5E.coil_name_to_address(name)
		self.__modbus.write_coil(address, value)

	def get_uint16(self, name: str):
		address = XD5E.register_name_to_address(name)
		return self.__modbus.read_register(address)

	def get_int16(self, name: str):
		u_value = self.get_uint16(name)
		package = struct.pack('<H', u_value)
		return struct.unpack('<h', package)[0]

	def set_uint16(self, name: str, value: int):
		address = XD5E.register_name_to_address(name)
		self.__modbus.write_registers(address, [value])

	def set_int16(self, name: str, value: int):
		package = struct.pack('<h', value)
		u_value = struct.unpack('<H', package)[0]
		self.set_uint16(name, u_value)

	def get_multi_uint16(self, name: str, count: int):
		address = XD5E.register_name_to_address(name)
		return self.__modbus.read_registers(address, count)

	def get_multi_int16(self, name: str, count: int):
		u_values = self.get_multi_uint16(name, count)
		values = list()
		for u_value in u_values:
			package = struct.pack('<H', u_value)
			value = struct.unpack('<h', package)[0]
			values.append(value)
		return values

	def set_multi_uint16(self, name: str, values: _List[int]):
		address = XD5E.register_name_to_address(name)
		self.__modbus.write_registers(address, values)

	def set_multi_int16(self, name: str, values: _List[int]):
		u_values = list()
		for value in values:
			package = struct.pack('<h', value)
			u_value = struct.unpack('<H', package)[0]
			u_values.append(u_value)
		self.set_multi_uint16(name, u_values)

	def __get_multi_number_32(self, name: str, count: int, value_type: str) -> list:
		units = self.get_multi_uint16(name, count*2)
		values = list()
		for i in range(count):
			low, high = units[i*2], units[i*2+1]
			p = struct.pack('<HH', low, high)
			tuple_values: _Sequence = struct.unpack(f'<{value_type}', p)
			value = tuple_values[0]
			values.append(value)
		return values

	def __set_multi_number_32(self, name: str, values: _Sequence, value_type: str):
		units = list()
		for value in values:
			p = struct.pack(f'<{value_type}', value)
			low, high = struct.unpack('<HH', p)
			units.extend((low, high))
		self.set_multi_uint16(name, units)

	def set_multi_int32(self, name: str, values: _List[int]):
		self.__set_multi_number_32(name, values, 'i')

	def set_multi_uint32(self, name: str, values: _List[int]):
		self.__set_multi_number_32(name, values, 'I')

	def get_multi_int32(self, name: str, count: int) -> list[int]:
		return self.__get_multi_number_32(name, count, 'i')

	def get_multi_uint32(self, name: str, count: int) -> list[int]:
		return self.__get_multi_number_32(name, count, 'I')

	def get_float32(self, name: str) -> float:
		low, high = self.get_multi_uint16(name, 2)
		p = struct.pack('<HH', low, high)
		f_value = struct.unpack('<f', p)[0]
		return f_value

	def get_multi_float32(self, name: str, count: int) -> list[float]:
		return self.__get_multi_number_32(name, count, 'f')

	def set_float32(self, name: str, value: float):
		p = struct.pack('<f', value)
		low, high = struct.unpack('<HH', p)
		self.set_multi_uint16(name, [low, high])

	def set_multi_float32(self, name: str, values: _Sequence[float]):
		self.__set_multi_number_32(name, values, 'f')

	def set_string(self, value: str, name: str, register_count: int, encoding: str = 'latin'):
		data = value.encode(encoding=encoding)
		max_len = register_count * 2
		items = list(data[:max_len])
		register_values = []
		if len(items) % 2 != 0:
			items.append(0)

		for i in range(0, len(items), 2):
			register = (items[i+1] << 8) | items[i]
			register_values.append(register)

		register_values.extend([0] * (register_count - len(register_values)))
		self.set_multi_uint16(name, register_values)

	@staticmethod
	def convert_registers_to_string(registers: list[int], encoding: str = 'latin') -> str:
		items = []
		for register in registers:
			back, front = ((register >> 8) & 0xFF), (register & 0xFF)
			if front == 0:
				break
			items.append(front)
			if back != 0:
				items.append(back)
		b_str = bytes(items)
		string = b_str.decode(encoding=encoding)
		return string

	def get_string(self, name: str, register_count: int, encoding: str = 'latin'):
		register_values = self.get_multi_uint16(name, register_count)
		items = []
		for register in register_values:
			back, front = ((register >> 8) & 0xFF), (register & 0xFF)
			if front == 0:
				break
			items.append(front)
			if back != 0:
				items.append(back)
		b_str = bytes(items)
		string = b_str.decode(encoding=encoding)
		return string


XDME = XD5E
XL5E = XD5E
XLME = XD5E

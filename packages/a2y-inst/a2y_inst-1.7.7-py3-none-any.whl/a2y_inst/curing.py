from a2y_modbus import FixMaster
from threading import Lock
from typing import List


class CuringRTU:
	"""固化机（最初来自众人行-华工科技项目，品牌未知）简单包装。使用 RS232 波特率 9600 通信，Modbus RTU 协议。"""

	ResourceLock = Lock()

	def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5, station: int = 1):
		CuringRTU.ResourceLock.acquire()
		try:
			self.modbus = FixMaster(station, port, baudrate, timeout)
		except Exception as e:
			CuringRTU.ResourceLock.release()
			raise e

	def read_system_registers(self, address: int, count: int) -> List[int]:
		assert 0 <= address < 0xA and count > 0 and address + count <= 0xA, 'Address or count out of range'
		return self.modbus.read_registers(address, count)

	def read_channel_registers(self, address: int, count: int, channel: int = 1) -> List[int]:
		assert 0 <= address < 0x2B and count > 0 and address + count <= 0x2B, 'Address or count out of range'
		assert 0 < channel <= 8, 'Channel out of range (0, 8]'
		addr = address | (channel << 8)
		return self.modbus.read_registers(addr, count)

	def write_channel_registers(self, address: int, values: List[int], channel: int = 1):
		count = len(values)
		assert 0 <= address < 0x2B and count > 0 and address + count <= 0x2B, 'Address or count out of range'
		assert 0 < channel <= 8, 'Channel out of range (0, 8]'
		addr = address | (channel << 8)
		self.modbus.write_registers(addr, values)

	def read_error_states(self) -> tuple:
		error_code = self.read_system_registers(9, 1)[0]
		alarm_state = self.read_channel_registers(5, 1)
		return error_code, alarm_state

	def close(self):
		self.modbus.close()
		CuringRTU.ResourceLock.release()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def get_all_plc_needs(self) -> List[int]:
		values = self.read_system_registers(9, 1)  # [error_code]
		channel_values = self.read_channel_registers(0x5, 14)
		values.extend([channel_values[0], channel_values[4], channel_values[13]])  # 报警状态，自动强度，自动点亮时间
		return values

	def set_all_plc_wants(self, values: List[int]):
		assert len(values) == 2, f'必须是“自动模式下的强度(0x9)”、“自动模式下的点亮时间(0x12)”这两个参数'
		strength, duration = values
		self.write_channel_registers(0x9, [strength])
		self.write_channel_registers(0x12, [duration])

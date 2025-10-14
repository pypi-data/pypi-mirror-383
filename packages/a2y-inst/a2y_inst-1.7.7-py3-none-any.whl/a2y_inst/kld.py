from a2y_modbus import Master as _Master
import struct


class K4:
	"""凯利德K4系列数显电测仪表 RS485 Modbus 通信接口"""
	def __init__(self, port, baudrate=4800, timeout: float = 0.5):
		self.__master = _Master(port, baudrate, timeout=timeout)

	def close(self):
		self.__master.close()

	@property
	def master(self) -> _Master:
		return self.__master

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def __read_float(self, station, address):
		low, high = self.__master.read_registers(station, address, 2)
		package = struct.pack('HH', high, low)
		return struct.unpack('f', package)[0]

	def Read(self, station=1):
		self.__master.serial.flushInput()
		return self.__read_float(station, 0)

	def ReadUA(self, station=1):
		"""读取A相电压"""
		return self.__read_float(station, 3)

	def ReadUB(self, station=1):
		"""相电压"""
		return self.__read_float(station, 5)

	def ReadUC(self, station=1):
		"""相电压"""
		return self.__read_float(station, 7)

	def ReadIA(self, station=1):
		"""相电流"""
		return self.__read_float(station, 9)

	def ReadIB(self, station=1):
		"""相电流"""
		return self.__read_float(station, 11)

	def ReadIC(self, station=1):
		"""相电流"""
		return self.__read_float(station, 13)

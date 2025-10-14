# 搜索国内品牌的可程控交流电源，发现几个品牌使用的外观（按键布局、显示屏类型）极为类似，
# 而且都同样的功率为 350VA 的型号都默认不带通讯口，价格也都基本一致（可以说一分不差）。
# 可合理怀疑这几个品牌的产品全都来自同一个祖宗。估计通信协议也不会有啥区别。
# 这个驱动为它而作。希望它们能够真的互相兼容，和平相处。
from a2y_modbus import FixMaster as _MBMaster


class ACPowerSource:
	def __init__(self, port: str, station: int = 1, baudrate: int = 9600, timeout: float = 0.3):
		self.__mb = _MBMaster(station=station, port=port, baudrate=baudrate, timeout=timeout)

	@property
	def modbus_master(self):
		return self.__mb

	def set_frequency(self, hz: float):
		"""
		设置交流电源输出的频率。传入参数的单位是赫兹（Hz），传给仪器时需要使用 16bit 整数，单位是 0.1Hz。
		"""
		value = int(round(hz * 10, 0))
		self.__mb.write_register(7, value)

	def set_voltage(self, volt: float):
		"""
		设置交流电源的输出电压。传入参数的单位是伏（V），传给仪器时需要使用 16bit 整数，单位是 0.1V。
		"""
		value = int(round(volt * 10, 0))
		self.__mb.write_register(8, value)

	def out_on(self):
		self.__mb.write_register(9, 1)

	def out_off(self):
		self.__mb.write_register(9, 0)

	def close(self):
		self.__mb.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

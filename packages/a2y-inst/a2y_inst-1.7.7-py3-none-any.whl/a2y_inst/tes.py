from serial import Serial as _Serial
from time import sleep


class TES1336A(_Serial):
	def __init__(self, port):
		_Serial.__init__(self, port, baudrate=9600)
		self.timeout = 0.5

	def read_data_frame(self) -> bytes:
		c = self.read()
		while c != b'':
			if c == b'\x02':
				break
			c = self.read()
		fb = c
		if fb == b'':
			return fb
		c = self.read()
		while c != b'':
			fb += c
			if c == b'\x03' and len(fb) == 5:
				break
			c = self.read()
		if c != b'\x03':
			raise IOError('TES1336A IO Error')

		if len(fb) != 5:
			raise IOError('Invalid feedback format from TES1336A')

		return fb

	def send_read_data_command(self):
		sleep(0.05)
		self.reset_input_buffer()
		self.write(b' ')
		sleep(0.25)
		self.write(b' ')

	def shift_range(self):
		sleep(0.05)
		self.write(b' ')
		sleep(0.2)
		self.write(b'F')
		sleep(0.2)
		self.write(b'\x10')

		sleep(3)

	def set_unit_lux(self):
		sleep(0.05)
		self.write(b' ')
		sleep(0.2)
		self.write(b'F')
		sleep(0.2)
		self.write(b'\x00')

	def try_read_data(self) -> bytes:
		self.send_read_data_command()
		return self.read_data_frame()

	def read_data(self, try_count: int = 3) -> bytes:
		fb = b''
		i = 0
		while i != try_count:
			try:
				fb = self.try_read_data()
				if len(fb) == 5:
					break
			except Exception as _e:
				pass
			i += 1

		if i == try_count:
			raise IOError('Read data from TES1336A timeout')

		return fb

	@staticmethod
	def parse_range(fb: bytes) -> int:
		rg = ((fb[1] >> 4) & 0x3)
		return [20, 200, 2000, 20000][rg]

	@staticmethod
	def parse_unit(fb: bytes):
		return (fb[1] >> 3) & 0x1

	@staticmethod
	def is_battery_low(fb: bytes):
		return (fb[1] & 1) != 0

	@staticmethod
	def is_hold(fb: bytes):
		return ((fb[1] >> 2) & 1) != 0

	@staticmethod
	def out_of_range(fb: bytes):
		return fb[3] == 0xFF

	@staticmethod
	def parse_value(fb: bytes):
		if TES1336A.out_of_range(fb):
			return -1
		rg = TES1336A.parse_range(fb)
		bcd = ((fb[2] & 0x1F) << 8) + fb[3]
		value = 0
		for i in range(4):
			value += ((bcd >> (4*i)) & 0xF) * (10**i)

		if rg == 20:
			value /= 100.0
		elif rg == 200:
			value /= 10.0
		elif rg == 20000:
			value *= 10.0

		return value

	@staticmethod
	def under_range(fb: bytes):
		rg = TES1336A.parse_range(fb)
		value = TES1336A.parse_value(fb)
		if value < 0 or rg == 20:
			return False
		return (rg * 1.0 / value) >= 20

	@staticmethod
	def absolute_out_of_range(fb: bytes):
		rg = TES1336A.parse_range(fb)
		return TES1336A.out_of_range(fb) and rg == 20000

	@staticmethod
	def is_best_range(fb: bytes):
		return (not TES1336A.out_of_range(fb)) and (not TES1336A.under_range(fb))

	def set_best_range(self, fb: bytes):
		i = 0
		while (not TES1336A.is_best_range(fb)) and (i != 9):
			if TES1336A.absolute_out_of_range(fb):
				raise OverflowError('TES1336A value too large to be represented')
			self.shift_range()
			fb = self.read_data()
			i += 1

		if not TES1336A.is_best_range(fb):
			raise IOError('Fail to set TES1336A range')

		return fb

	def read_value(self):
		fb = self.read_data()
		fb = self.set_best_range(fb)
		return TES1336A.parse_value(fb)

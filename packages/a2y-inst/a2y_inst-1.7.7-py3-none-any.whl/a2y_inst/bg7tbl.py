from serial import Serial as _Serial


class FrequencyCounter(_Serial):
	def __init__(self, port: str, baudrate: int = 9600):
		_Serial.__init__(self, port, baudrate=baudrate)

	def measure(self, fresh: bool = False) -> float:
		in_waiting = self.in_waiting
		if in_waiting > 0:
			self.read(in_waiting)
		data = self.readline().strip()
		if fresh or (b'FA' not in data and b'FB' not in data):
			data = self.readline().strip()

		index = data.find(b'F')
		assert index >= 0, f'Data invalid: [{data}]'

		value = float(data[index+2:])
		return value

	def select_ch1_frequency(self):
		cmd = b'$E2121*\r\n'
		self.write(cmd)

	def ch1_imp_50(self):
		cmd = b'$E3030*\r\n'
		self.write(cmd)

	def ch1_imp_1M(self):
		cmd = b'$E3131*\r\n'
		self.write(cmd)

	def beep_on(self):
		cmd = b'$E3232*\r\n'
		self.write(cmd)

	def beep_off(self):
		cmd = b'$E3333*\r\n'
		self.write(cmd)

	def high_precision_on(self):
		cmd = b'$E3434*\r\n'
		self.write(cmd)

	def high_precision_off(self):
		cmd = b'$E3535*\r\n'
		self.write(cmd)

	def ch1_lpf_on(self):
		cmd = b'$E3636*\r\n'
		self.write(cmd)

	def ch1_lpf_off(self):
		cmd = b'$E3737*\r\n'
		self.write(cmd)

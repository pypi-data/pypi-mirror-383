from serial import Serial
from threading import Lock
from typing import List


class DispenserGK:
	"""点胶机（最初来自众人行-华工科技项目，品牌未知）简单包装，采用 RS232 通信，自定义（ASCII）协议通信，供应商文档称之为“GK通信协议”。"""

	ParamLen = {
		0x10: [1],
		0x11: [1],
		0x12: [4],
		0x13: [1],
		0x19: [2],  # 文档中说用于一次读取9个参数，实际只回来2个字节的数据，不知道对应啥参数
		0x40: [4],
		0x54: [4]
	}
	ResourceLock = Lock()

	def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
		DispenserGK.ResourceLock.acquire()
		try:
			self.__serial = Serial(port=port, baudrate=baudrate, timeout=timeout)
		except Exception as e:
			DispenserGK.ResourceLock.release()
			raise e
		self.__last_command_sent = b''
		self.__last_feedback_received = b''

	def close(self):
		if self.__serial.is_open:
			self.__serial.close()
		DispenserGK.ResourceLock.release()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	@property
	def last_command_sent(self) -> bytes:
		return self.__last_command_sent

	@property
	def last_feedback_received(self) -> bytes:
		return self.__last_feedback_received

	@property
	def last_command(self) -> str:
		return self.last_command_sent.decode('latin')

	@property
	def last_feedback(self) -> str:
		return self.last_feedback_received.decode('latin')

	@staticmethod
	def cal_crc(data: bytes) -> int:
		crc = 0
		length = len(data)
		assert length % 2 == 0, f'Data length must be multiple of 2'
		for i in range(0, length, 2):
			content = data[i:i+2]
			value = int(content, 16)
			crc += value
		return crc & 0xFF

	@staticmethod
	def check_crc(data: bytes) -> bool:
		assert data.startswith(b':'), f'Data frame must start with ":"'
		assert data.endswith(b'\r\n'), f'Data frame must end with CRLN'
		content = data[1:-4]
		crc = DispenserGK.cal_crc(content)
		crc2 = int(data[-4:-2], 16)
		return crc == crc2

	@staticmethod
	def add_head_tail(command: str) -> bytes:
		crc = DispenserGK.cal_crc(command.encode())
		whole = f':{command}{crc:02X}\r\n'
		return whole.encode('latin')

	@staticmethod
	def para_len(para: int) -> List[int]:
		default = [2]
		return DispenserGK.ParamLen.get(para, default)

	def read_para(self, para: int) -> int:
		para_lens = DispenserGK.para_len(para)
		assert len(para_lens) == 1, f'函数 read_para 仅用于读取单一参数的值。'
		values = self.do_read_paras(para)
		return values[0]

	def read_multi_parameters(self, para: int) -> List[int]:
		return self.do_read_paras(para)

	def do_read_paras(self, para: int) -> List[int]:
		command = b':00%02X%02X\r\n' % (para, para)
		self.__last_command_sent = command
		self.__serial.write(command)
		para_lens = DispenserGK.para_len(para)
		para_total = sum(para_lens) * 2
		total = 1 + 2 + 2 + 2 + para_total + 2 + 2
		feedback = self.__serial.read_until(size=total)
		self.__last_feedback_received = feedback
		assert feedback.endswith(b'\n'), f'Read from dispenser timeout'
		assert DispenserGK.check_crc(feedback), 'Frame CRC invalid'
		para_data = feedback[7:7+para_total]
		idx = 0
		start = 0
		result = list()
		while idx < len(para_lens):
			item_len = para_lens[idx] * 2
			item = para_data[start:start+item_len]
			value = int(item, 16)
			result.append(value)
			start += item_len
			idx += 1
		return result

	def write_para(self, para: int, value: int):
		data_lens = DispenserGK.para_len(para)
		assert len(data_lens) == 1, f'函数 write_para 仅用于设置单一参数。'
		data_len = data_lens[0]
		data = f'{value:X}'.rjust(data_len * 2, '0')
		command = f'01{para:02X}{data_len:02X}{data}'
		whole_command = DispenserGK.add_head_tail(command)
		self.__serial.write(whole_command)
		self.__last_command_sent = whole_command
		feedback = self.__serial.read_until()
		self.__last_feedback_received = feedback
		assert feedback.endswith(b'\n'), 'Read from dispenser timeout'
		error_code = int(feedback[3:5], 16)
		assert error_code == 0, f'参数设置出错，错误码：{error_code:02X}'

	def action_control(self, action: int, start: int):
		command = f'02{action:02X}{start:02X}'
		whole_command = DispenserGK.add_head_tail(command)
		self.__serial.write(whole_command)
		self.__last_command_sent = whole_command
		feedback = self.__serial.read_until()
		self.__last_feedback_received = feedback
		assert feedback.endswith(b'\n'), 'Read from dispenser timeout'
		error_code = int(feedback[3:5], 16)
		assert error_code == 0, f'动作控制出错，错误码：{error_code:02X}'

	def start_nozzle_heater(self):
		self.action_control(action=0x2, start=1)

	def stop_nozzle_heater(self):
		self.action_control(action=0x2, start=0)

	def get_nozzle_setting_temperature(self) -> int:
		return self.read_para(0x20)

	def get_nozzle_temperature(self) -> int:
		return self.read_para(0x52)

	def get_what_you_need(self):
		"""
		这个函数用于给通信调试助手使用
		"""
		needle_shift = self.read_para(0x13)
		raising_time = self.read_para(0x14) / 100
		open_time = self.read_para(0x15) / 100
		falling_time = self.read_para(0x16) / 100
		close_time = self.read_para(0x17) / 100
		nozzle_temperature = self.get_nozzle_setting_temperature() / 10
		alarm_state = f'{self.get_alarm_state():04X}'
		result = dict(
			needle_shift=needle_shift,
			needle_raising_time=raising_time,
			open_time=open_time,
			needle_falling_time=falling_time,
			close_time=close_time,
			nozzle_temperature=nozzle_temperature,
			alarm_state=alarm_state
		)
		return result

	def get_alarm_state(self) -> int:
		return self.read_para(0x30)

	def set_what_you_want(self, values: List[int]):
		assert len(values) == 6, '必须是“撞针行程、撞针上升时间、开阀时间、撞针下降时间、关阀时间、喷嘴加热温度”这6个参数'
		paras = [0x13, 0x14, 0x15, 0x16, 0x17, 0x20]
		for value, para in zip(values, paras):
			self.write_para(para, value)

	def get_all(self) -> List[int]:
		"""
		这个函数主要给自动程序使用
		"""
		paras = [0x13, 0x14, 0x15, 0x16, 0x17, 0x20, 0x30]
		values = []
		for para in paras:
			value = self.read_para(para)
			values.append(value)
		return values

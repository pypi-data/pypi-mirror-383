from serial import Serial as _Serial
from typing import Optional as _Optional, Tuple as _Tuple, Dict as _Dict


class LB1905(_Serial):
	def __init__(self, port: str, baudrate: int = 57600, timeout: float = 1):
		_Serial.__init__(self, port=port, baudrate=baudrate, timeout=timeout)

	def query(self, command: str) -> str:
		if not command.endswith('\n'):
			command += '\n'
		cmd = command.encode('ascii')
		self.write(cmd)
		feedback = self.readline()
		result = feedback.decode('ascii')
		if not result.endswith('\n'):
			raise IOError('与LED分析仪通信超时。')
		return result.strip()

	def capture(self, time_level: int = 2):
		command = f'capture{time_level}'
		ack = self.query(command)
		if ack.upper() != 'OK':
			raise IOError(f'LED分析仪“capture”命令返回数据格式错误：{ack}。')

	def __get_values(self, channel: _Optional[int], cmd_for_all: str, cmd_for_single: str, names: _Tuple, types: _Tuple) -> _Dict[int, _Dict[str, float]]:
		if channel is None:
			command = cmd_for_all
		else:
			command = f'{cmd_for_single}{channel}'
		result = self.query(command)
		value_strs = result.split()
		if len(value_strs) % len(names) != 0:
			raise ValueError(f'LED分析仪”{command}“命令返回数据格式错误：{result}。')
		channel_count = len(value_strs) // 3
		if channel is not None and channel_count != 1:
			raise ValueError(f'LED分析仪”{command}“命令返回数据格式错误：{result}。')
		value_index = 0
		channel_index = 0
		if channel is not None:
			channel_index = channel
		value_dict = None
		all_values = dict()
		while value_index != len(value_strs):
			if value_index % len(names) == 0:
				value_dict = dict()
				all_values[channel_index] = value_dict
			value = types[value_index % len(types)](value_strs[value_index])
			name = names[value_index % len(names)]
			value_dict[name] = value
			value_index += 1
			if value_index % len(names) == 0:
				channel_index += 1

		return all_values

	def get_rgbi(self, channel: _Optional[int] = None):
		return self.__get_values(
			channel,
			cmd_for_all='getallrgbi',
			cmd_for_single='getrgbi',
			names=('red', 'green', 'blue', 'intensity'),
			types=(int, int, int, int)
		)

	def get_hsi(self, channel: _Optional[int] = None):
		return self.__get_values(
			channel,
			cmd_for_all='getallhsi',
			cmd_for_single='gethsi',
			names=('hue', 'saturation', 'intensity'),
			types=(float, int, int)
		)

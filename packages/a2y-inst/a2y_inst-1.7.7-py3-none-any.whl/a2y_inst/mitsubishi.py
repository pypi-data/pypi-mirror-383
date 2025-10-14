import serial as _serial
import gzip as _gzip
import uuid as _uuid
import socket as _socket
from socket import create_connection as _create_connection
import struct
from enum import Enum
from time import time as _now
from threading import Lock as _Lock
from a2y_handy import int_2_bool_list, bool_list_2_int
from typing import Union as _Union, List as _List, Optional as _Optional


class FX(_serial.Serial):
	VALID_CHARS = b'0123456789ABCDEF'

	def __init__(self, port, baudrate=9600):
		_serial.Serial.__init__(self, port, baudrate=baudrate, parity=_serial.PARITY_EVEN, bytesize=7, timeout=0.5)

	@staticmethod
	def to_valid_chars(value, length=2):
		vcs = FX.VALID_CHARS
		result = bytearray()
		if isinstance(value, int):
			for i in range(length):
				result.append(vcs[value & 0xF])
				value = (value >> 4)
			result.reverse()

		return result

	@staticmethod
	def to_bytes(values):
		values = bytes(values)
		length = len(values)
		i = 0
		result = []
		while i < length:
			d = int(values[i:i+2], 16)
			result.append(d)
			i += 2
		return result

	@staticmethod
	def to_d(values):
		byte_str = FX.to_bytes(values)
		length = len(byte_str)
		i = 0
		result = []
		while i < length:
			value = byte_str[i] + (byte_str[i+1] << 8)
			result.append(value)
			i += 2

		return result

	@staticmethod
	def calculate_crc(msg, append_etx=True, skip_stx=True):
		crc = 0
		meet_etx = False
		for c in msg:
			c &= 0x7F
			if c != 2 or (not skip_stx):
				crc += c
			if c == 3:
				meet_etx = True
				break
		if (not meet_etx) and append_etx:
			crc += 3
		crc &= 0xFF
		return FX.to_valid_chars(crc)

	@staticmethod
	def add_head(msg):
		msg.insert(0, 2)

	@staticmethod
	def append_tail(msg):
		msg.append(3)
		crc = FX.calculate_crc(msg)
		msg.extend(crc)

	@staticmethod
	def make_msg(body):
		msg = bytearray(body)
		FX.add_head(msg)
		FX.append_tail(msg)
		return msg

	@staticmethod
	def make_read_bytes_msg(address, count):
		if count > 0x40:
			raise ValueError('Read too much')
		body = bytearray(b'0')
		if isinstance(address, int):
			address = FX.to_valid_chars(address, 4)
		elif isinstance(address, str):
			address = address.upper().encode()
		elif isinstance(address, bytes):
			address = address.upper()
		body.extend(address)
		body.extend(FX.to_valid_chars(count))
		return FX.make_msg(body)

	@staticmethod
	def make_write_bytes_msg(address, values, cmd=b'1'):
		count = len(values)
		if count > 0x40:
			raise ValueError('Write too much')
		body = bytearray(cmd)
		if isinstance(address, int):
			address = FX.to_valid_chars(address, 4)
		elif isinstance(address, str):
			address = address.upper().encode()
		elif isinstance(address, bytes):
			address = address.upper()
		body.extend(address)
		body.extend(FX.to_valid_chars(count))
		for value in values:
			body.extend(FX.to_valid_chars(value))
		return FX.make_msg(body)

	@staticmethod
	def make_force_msg(address, shift, value):
		address = FX.to_valid_chars((address + shift), 4)
		m_address = bytearray(4)
		m_address[0] = address[2]
		m_address[1] = address[3]
		m_address[2] = address[0]
		m_address[3] = address[1]
		body = bytearray(b'7' if value else b'8')
		body.extend(m_address)
		return FX.make_msg(body)

	@staticmethod
	def make_set_m_msg(address, value=True):
		if address >= 1024:
			raise ValueError('M address out of range')
		return FX.make_force_msg(address, 0x800, value)

	@staticmethod
	def make_set_y_msg(address, value=True):
		if address >= 0x80:
			raise ValueError('Y address out of range')
		return FX.make_force_msg(address, 0x500, value)

	@staticmethod
	def make_read_d_msg(address, count):
		if count > 0x20:
			raise ValueError('Read too much D')
		if address >= 8256 or (1024 <= address < 8000) or address < 0:
			raise ValueError('D address out of range')
		if address >= 8000:
			shift = 0xE00
			address -= 8000
			if address + count > 256:
				raise ValueError('D last address out of range')
		else:
			shift = 0x1000
			if address + count > 1024:
				raise ValueError('D last address out of range')
		address = shift + address * 2
		count *= 2
		return FX.make_read_bytes_msg(address, count)

	@staticmethod
	def make_write_d_msg(address, values):
		if address >= 512:
			raise ValueError('D address out of range')
		count = len(values)
		if count > 0x20:
			raise ValueError('Read too much D')
		if address + count > 512:
			raise ValueError('D last address out of range')
		address = 0x1000 + address * 2
		Vs = []
		for value in values:
			Vs.append(value & 0xFF)
			Vs.append((value >> 8) & 0xFF)
		return FX.make_write_bytes_msg(address, Vs)

	@staticmethod
	def _make_set_multi_coil_uint8_message(address, addr_shift, values):
		return FX.make_write_bytes_msg(address + addr_shift, values)

	@staticmethod
	def _make_set_multi_coil_uint16_message(address, addr_shift, values: _Union[list, tuple]):
		address *= 2
		uint8_values = list()
		for value in values:
			uint8_values.append(value & 0xFF)
			uint8_values.append(value >> 8)

		return FX._make_set_multi_coil_uint8_message(address, addr_shift, uint8_values)

	def set_multi_coil_uint8(self, name, values):
		assert name[0] == 'B'
		assert name[1] in 'XYM'
		address = int(name[2:], 8)
		addr_shift = [0x80, 0xA0, 0x100]['XYM'.index(name[1])]
		msg = FX._make_set_multi_coil_uint8_message(address, addr_shift, values)
		self.write(msg)
		self.receive_ack()

	def set_multi_coil_uint16(self, name, values: list):
		assert name[0] == 'W'
		assert name[1] in 'XYM'
		address = int(name[2:], 8)
		addr_shift = [0x80, 0xA0, 0x100]['XYM'.index(name[1])]
		msg = FX._make_set_multi_coil_uint16_message(address, addr_shift, values)
		self.write(msg)
		self.receive_ack()

	def set_coil_uint8(self, name, value: int):
		self.set_multi_coil_uint8(name, [value])

	def set_coil_uint16(self, name, value: int):
		self.set_multi_coil_uint16(name, [value])

	@staticmethod
	def MakeProgramMsg(address, values):
		Vs = []
		for value in values:
			Vs.append(value & 0xFF)
			Vs.append((value >> 8) & 0xFF)
		return FX.make_write_bytes_msg(address * 2, Vs, b'P')

	def read_one(self):
		data = self.read()
		if len(data) == 0:
			raise IOError('Read FX timeout')
		if isinstance(data, str):
			c = ord(data)
		else:
			c = data[0]
		if c == 0x15:  # NAK
			raise IOError('FX NAK')
		return c

	def Read(self, size):
		data = self.read(size)
		if len(data) != size:
			raise IOError('Read FX timeout')
		msg = bytearray()
		for c in data:
			if isinstance(c, str):
				c = ord(c)
			if c == 0x15:  # NACK
				raise IOError('FX NAK')
			msg.append(c)
		return msg

	def receive(self):
		c = self.read_one()
		while c != 2:
			c = self.read_one()

		msg = bytearray()
		c = self.read_one()
		while c != 3:
			msg.append(c)
			c = self.read_one()

		crc = self.Read(2)
		CRC = FX.calculate_crc(msg)
		if crc != CRC:
			raise IOError('FX CRC error')

		return msg

	def receive_ack(self):
		c = self.read_one()
		while c != 6:
			c = self.read_one()

	def read_d(self, address, count):
		msg = FX.make_read_d_msg(address, count)
		self.write(msg)
		feedback = self.receive()
		result = FX.to_d(feedback)
		return result

	def get_multi_uint16(self, name, count):
		assert name[0] == 'D'
		address = int(name[1:])
		return self.read_d(address, count)

	def read_one_d(self, address):
		return self.read_d(address, 1)[0]

	def read_uint32(self, address):
		low, high = self.read_d(address, 2)
		return (high << 16) | low

	def write_d(self, address, values):
		msg = FX.make_write_d_msg(address, values)
		self.write(msg)
		self.receive_ack()

	def set_multi_uint16(self, name, values):
		assert name[0] == 'D'
		address = int(name[1:])
		self.write_d(address, values)

	def write_one_d(self, address, value):
		self.write_d(address, [value])

	def write_uint32(self, address, value):
		high = (value >> 16) & 0xFFFF
		low = (value & 0xFFFF)
		return self.write_d(address, [low, high])

	def program(self, address, values):
		msg = FX.MakeProgramMsg(address, values)
		self.write(msg)
		self.receive_ack()

	def stop_plc(self):
		msg = FX.make_msg(bytearray(b'S'))
		self.write(msg)
		self.receive_ack()

	def start_plc(self):
		msg = FX.make_msg(bytearray(b'R'))
		self.write(msg)
		self.receive_ack()

	def erase(self, kb_index):
		body = bytearray(b'e')
		body.extend(FX.to_valid_chars(kb_index))
		msg = FX.make_msg(body)
		self.write(msg)
		self.receive_ack()

	def read_m(self, address):
		if address >= 1024:
			raise ValueError('M address out of range')
		major = 0x100 + address // 8
		minor = address % 8
		msg = FX.make_read_bytes_msg(major, 1)
		self.write(msg)
		feedback = self.receive()
		value = FX.to_bytes(feedback)[0]
		return (value & (1 << minor)) != 0

	def read_m_group(self, group_index):
		if group_index >= 1024 / 8:
			raise ValueError('M Group Index out of range. Only 0~127 are accepted.')
		msg = FX.make_read_bytes_msg(0x100 + group_index, 1)
		self.write(msg)
		feedback = self.receive()
		values = FX.to_bytes(feedback)[0]
		result = [False]*8
		for i in range(8):
			result[i] = ((values & (1 << i)) != 0)
		return result

	def set_m(self, address):
		msg = FX.make_set_m_msg(address)
		self.write(msg)
		self.receive_ack()

	def reset_m(self, address):
		msg = FX.make_set_m_msg(address, False)
		self.write(msg)
		self.receive_ack()

	def read_x_byte(self, address):
		if address >= (0xA0 - 0x80) // 8:
			raise ValueError('X address out of range')
		major = 0x80 + address * 8
		msg = FX.make_read_bytes_msg(major, 1)
		self.write(msg)
		feedback = self.receive()
		value = FX.to_bytes(feedback)[0]
		return value

	def _read_coil_bytes(self, address, count, addr_shift):
		major = addr_shift + address * 8
		msg = FX.make_read_bytes_msg(major, count)
		self.write(msg)
		feedback = self.receive()
		values = FX.to_bytes(feedback)
		return values

	def read_x_bytes(self, address, count):
		return self._read_coil_bytes(address, count, 0x80)

	def read_x_byte_as_bool_list(self, address):
		value = self.read_x_byte(address)
		return int_2_bool_list(value, 8)

	def _read_coil(self, address, addr_shift):
		major = addr_shift + address // 8
		minor = address % 8
		msg = FX.make_read_bytes_msg(major, 1)
		self.write(msg)
		feedback = self.receive()
		value = FX.to_bytes(feedback)[0]
		return (value & (1 << minor)) != 0

	def ReadX(self, address):
		if address >= (0xA0 - 0x80):
			raise ValueError('X address out of range')

		return self._read_coil(address, 0x80)

	def ReadY(self, address):
		if address >= 0xC0 - 0xA0:
			raise ValueError('X address out of range')

		return self._read_coil(address, 0xA0)

	def ReadYBytes(self, address, count):
		return self._read_coil_bytes(address, count, 0xA0)

	def ReadMBytes(self, address, count):
		return self._read_coil_bytes(address, count, 0x100)

	def SetY(self, address):
		msg = FX.make_set_y_msg(address)
		self.write(msg)
		self.receive_ack()

	def ResetY(self, address):
		msg = FX.make_set_y_msg(address, False)
		self.write(msg)
		self.receive_ack()

	def get_coil(self, name):
		address = int(name[1:], 8)
		if name[0] == 'X':
			value = self.ReadX(address)
		elif name[0] == 'Y':
			value = self.ReadY(address)
		elif name[0] == 'M':
			value = self.read_m(address)
		else:
			raise ValueError('Coil name not supported yet...')
		return value

	def reset_coil(self, name):
		address = int(name[1:], 8)
		if name[0] == 'Y':
			self.ResetY(address)
		elif name[0] == 'M':
			self.reset_m(address)
		else:
			raise ValueError('Coil name not supported yet...')

	def set_coil(self, name: str, value: bool = True):
		if not value:
			self.reset_coil(name)
			return

		address = int(name[1:], 8)
		if name[0] == 'Y':
			self.SetY(address)
		elif name[0] == 'M':
			self.set_m(address)
		else:
			raise ValueError('Coil name not supported yet...')

	def get_multi_coil_uint8(self, name: str, count: int):
		if name[0] != 'B':
			raise ValueError('Not a valid name for coil uint8: %s. It should start with a "B".' % name)

		coil_type = name[1]
		address = int(name[2:], 8)
		if coil_type == 'X':
			result = self.read_x_bytes(address, count)
		elif coil_type == 'Y':
			result = self.ReadYBytes(address, count)
		elif coil_type == 'M':
			result = self.ReadMBytes(address, count)
		else:
			raise ValueError('Coil name not supported yet...')
		return result

	def get_coil_uint8(self, name: str):
		return self.get_multi_coil_uint8(name, 1)[0]

	def get_multi_coil_uint16(self, name: str, count: int):
		if name[0] != 'W':
			raise ValueError('Not a valid name for coil uint16: %s. It should start with a "W"' % name)

		address = int(name[2:], 8) * 2
		name = 'B' + name[1] + oct(address)[2:]
		byte_result = self.get_multi_coil_uint8(name, count*2)
		result = list()
		for i in range(count):
			idx = i * 2
			word = byte_result[idx] + (byte_result[idx+1] << 8)
			result.append(word)

		return result

	def get_coil_uint16(self, name):
		return self.get_multi_coil_uint16(name, 1)[0]


class DefaultLanguage(object):
	"""系统的语言基类，默认也即是中文版本"""
	AuthorizationFailed = "系统授权失败，需要使用激活码授权，谢谢支持。"
	ConnectedFailed = "连接失败："
	ConnectedSuccess = "连接成功！"
	UnknownError = "未知错误"
	ErrorCode = "错误代号"
	TextDescription = "文本描述"
	ExceptionMessage = "错误信息："
	ExceptionSource = "错误源："
	ExceptionType = "错误类型："
	ExceptionStackTrace = "错误堆栈："
	ExceptionTargetSite = "错误方法："
	ExceptionCustomer = "用户自定义方法出错："
	SuccessText = "成功"
	TwoParametersLengthIsNotSame = "两个参数的个数不一致"
	NotSupportedFunction = "当前的功能逻辑不支持"
	NotSupportedDataType = "输入的类型不支持，请重新输入"
	DataLengthIsNotEnough = "接收的数据长度不足，应该值:{0},实际值:{1}"
	ReceiveDataTimeout = "接收数据超时："
	ReceiveDataLengthTooShort = "接收的数据长度太短："
	MessageTip = "消息提示："
	Close = "关闭"
	Time = "时间："
	SoftWare = "软件："
	BugSubmit = "Bug提交"
	MailServerCenter = "邮件发送系统"
	MailSendTail = "邮件服务系统自动发出，请勿回复！"
	IpAddressError = "Ip地址输入异常，格式不正确"
	Send = "发送"
	Receive = "接收"
	# 系统相关的错误信息
	SystemInstallOperater = "安装新系统：IP为"
	SystemUpdateOperater = "更新新系统：IP为"
	# 套接字相关的信息描述
	SocketIOException = "套接字传送数据异常："
	SocketSendException = "同步数据发送异常："
	SocketHeadReceiveException = "指令头接收异常："
	SocketContentReceiveException = "内容数据接收异常："
	SocketContentRemoteReceiveException = "对方内容数据接收异常："
	SocketAcceptCallbackException = "异步接受传入的连接尝试"
	SocketReAcceptCallbackException = "重新异步接受传入的连接尝试"
	SocketSendAsyncException = "异步数据发送出错:"
	SocketEndSendException = "异步数据结束挂起发送出错"
	SocketReceiveException = "异步数据发送出错:"
	SocketEndReceiveException = "异步数据结束接收指令头出错"
	SocketRemoteCloseException = "远程主机强迫关闭了一个现有的连接"
	# 文件相关的信息
	FileDownloadSuccess = "文件下载成功"
	FileDownloadFailed = "文件下载异常"
	FileUploadFailed = "文件上传异常"
	FileUploadSuccess = "文件上传成功"
	FileDeleteFailed = "文件删除异常"
	FileDeleteSuccess = "文件删除成功"
	FileReceiveFailed = "确认文件接收异常"
	FileNotExist = "文件不存在"
	FileSaveFailed = "文件存储失败"
	FileLoadFailed = "文件加载失败"
	FileSendClientFailed = "文件发送的时候发生了异常"
	FileWriteToNetFailed = "文件写入网络异常"
	FileReadFromNetFailed = "从网络读取文件异常"
	FilePathCreateFailed = "文件夹路径创建失败："
	FileRemoteNotExist = "对方文件不存在，无法接收！"
	# 服务器的引擎相关数据
	TokenCheckFailed = "接收验证令牌不一致"
	TokenCheckTimeout = "接收验证超时:"
	CommandHeadCodeCheckFailed = "命令头校验失败"
	CommandLengthCheckFailed = "命令长度检查失败"
	NetClientAliasFailed = "客户端的别名接收失败："
	NetEngineStart = "启动引擎"
	NetEngineClose = "关闭引擎"
	NetClientOnline = "上线"
	NetClientOffline = "下线"
	NetClientBreak = "异常掉线"
	NetClientFull = "服务器承载上限，收到超出的请求连接。"
	NetClientLoginFailed = "客户端登录中错误："
	NetHeartCheckFailed = "心跳验证异常："
	NetHeartCheckTimeout = "心跳验证超时，强制下线："
	DataSourseFormatError = "数据源格式不正确"
	ServerFileCheckFailed = "服务器确认文件失败，请重新上传"
	ClientOnlineInfo = "客户端 [ {0} ] 上线"
	ClientOfflineInfo = "客户端 [ {0} ] 下线"
	ClientDisableLogin = "客户端 [ {0} ] 不被信任，禁止登录"
	# Client 相关
	ReConnectServerSuccess = "重连服务器成功"
	ReConnectServerAfterTenSeconds = "在10秒后重新连接服务器"
	KeyIsNotAllowedNull = "关键字不允许为空"
	KeyIsExistAlready = "当前的关键字已经存在"
	KeyIsNotExist = "当前订阅的关键字不存在"
	ConnectingServer = "正在连接服务器..."
	ConnectFailedAndWait = "连接断开，等待{0}秒后重新连接"
	AttemptConnectServer = "正在尝试第{0}次连接服务器"
	ConnectServerSuccess = "连接服务器成功"
	GetClientIpaddressFailed = "客户端IP地址获取失败"
	ConnectionIsNotAvailable = "当前的连接不可用"
	DeviceCurrentIsLoginRepeat = "当前设备的id重复登录"
	DeviceCurrentIsLoginForbidden = "当前设备的id禁止登录"
	PasswordCheckFailed = "密码验证失败"
	DataTransformError = "数据转换失败，源数据："
	RemoteClosedConnection = "远程关闭了连接"
	# 日志相关
	LogNetDebug = "调试"
	LogNetInfo = "信息"
	LogNetWarn = "警告"
	LogNetError = "错误"
	LogNetFatal = "致命"
	LogNetAbandon = "放弃"
	LogNetAll = "全部"
	# Modbus相关
	ModbusTcpFunctionCodeNotSupport = "不支持的功能码"
	ModbusTcpFunctionCodeOverBound = "读取的数据越界"
	ModbusTcpFunctionCodeQuantityOver = "读取长度超过最大值"
	ModbusTcpFunctionCodeReadWriteException = "读写异常"
	ModbusTcpReadCoilException = "读取线圈异常"
	ModbusTcpWriteCoilException = "写入线圈异常"
	ModbusTcpReadRegisterException = "读取寄存器异常"
	ModbusTcpWriteRegisterException = "写入寄存器异常"
	ModbusAddressMustMoreThanOne = "地址值在起始地址为1的情况下，必须大于1"
	ModbusAsciiFormatCheckFailed = "Modbus的ascii指令检查失败，不是modbus-ascii报文"
	ModbusCRCCheckFailed = "Modbus的CRC校验检查失败"
	ModbusLRCCheckFailed = "Modbus的LRC校验检查失败"
	ModbusMatchFailed = "不是标准的modbus协议"
	# Melsec PLC 相关
	MelsecPleaseReferToManulDocument = "请查看三菱的通讯手册来查看报警的具体信息"
	MelsecReadBitInfo = "读取位变量数组只能针对位软元件，如果读取字软元件，请调用Read方法"
	MelsecCurrentTypeNotSupportedWordOperate = "当前的类型不支持字读写"
	MelsecCurrentTypeNotSupportedBitOperate = "当前的类型不支持位读写"
	MelsecFxReceiveZero = "接收的数据长度为0"
	MelsecFxAckNagative = "PLC反馈的数据无效"
	MelsecFxAckWrong = "PLC反馈信号错误："
	MelsecFxCrcCheckFailed = "PLC反馈报文的和校验失败！"
	# Siemens PLC 相关
	SiemensDBAddressNotAllowedLargerThan255 = "DB块数据无法大于255"
	SiemensReadLengthMustBeEvenNumber = "读取的数据长度必须为偶数"
	SiemensWriteError = "写入数据异常，代号为："
	SiemensReadLengthCannotLargerThan19 = "读取的数组数量不允许大于19"
	SiemensDataLengthCheckFailed = "数据块长度校验失败，请检查是否开启put/get以及关闭db块优化"
	SiemensFWError = "发生了异常，具体信息查找Fetch/Write协议文档"
	SiemensReadLengthOverPlcAssign = "读取的数据范围超出了PLC的设定"
	# Panasonic PLC 相关
	PanasonicReceiveLengthMustLargerThan9 = "接收数据长度必须大于9"
	PanasonicAddressParameterCannotBeNull = "地址参数不允许为空"
	PanasonicMewStatus20 = "错误未知"
	PanasonicMewStatus21 = "NACK错误，远程单元无法被正确识别，或者发生了数据错误。"
	PanasonicMewStatus22 = "WACK 错误:用于远程单元的接收缓冲区已满。"
	PanasonicMewStatus23 = "多重端口错误:远程单元编号(01 至 16)设置与本地单元重复。"
	PanasonicMewStatus24 = "传输格式错误:试图发送不符合传输格式的数据，或者某一帧数据溢出或发生了数据错误。"
	PanasonicMewStatus25 = "硬件错误:传输系统硬件停止操作。"
	PanasonicMewStatus26 = "单元号错误:远程单元的编号设置超出 01 至 63 的范围。"
	PanasonicMewStatus27 = "不支持错误:接收方数据帧溢出. 试图在不同的模块之间发送不同帧长度的数据。"
	PanasonicMewStatus28 = "无应答错误:远程单元不存在. (超时)。"
	PanasonicMewStatus29 = "缓冲区关闭错误:试图发送或接收处于关闭状态的缓冲区。"
	PanasonicMewStatus30 = "超时错误:持续处于传输禁止状态。"
	PanasonicMewStatus40 = "BCC 错误:在指令数据中发生传输错误。"
	PanasonicMewStatus41 = "格式错误:所发送的指令信息不符合传输格式。"
	PanasonicMewStatus42 = "不支持错误:发送了一个未被支持的指令。向未被支持的目标站发送了指令。"
	PanasonicMewStatus43 = "处理步骤错误:在处于传输请求信息挂起时,发送了其他指令。"
	PanasonicMewStatus50 = "链接设置错误:设置了实际不存在的链接编号。"
	PanasonicMewStatus51 = "同时操作错误:当向其他单元发出指令时,本地单元的传输缓冲区已满。"
	PanasonicMewStatus52 = "传输禁止错误:无法向其他单元传输。"
	PanasonicMewStatus53 = "忙错误:在接收到指令时,正在处理其他指令。"
	PanasonicMewStatus60 = "参数错误:在指令中包含有无法使用的代码,或者代码没有附带区域指定参数(X, Y, D), 等以外。"
	PanasonicMewStatus61 = "数据错误:触点编号,区域编号,数据代码格式(BCD,hex,等)上溢出, 下溢出以及区域指定错误。"
	PanasonicMewStatus62 = "寄存器错误:过多记录数据在未记录状态下的操作（监控记录、跟踪记录等。)。"
	PanasonicMewStatus63 = "PLC 模式错误:当一条指令发出时，运行模式不能够对指令进行处理。"
	PanasonicMewStatus65 = "保护错误:在存储保护状态下执行写操作到程序区域或系统寄存器。"
	PanasonicMewStatus66 = "地址错误:地址（程序地址、绝对地址等）数据编码形式（BCD、hex 等）、上溢、下溢或指定范围错误。"
	PanasonicMewStatus67 = "丢失数据错误:要读的数据不存在。（读取没有写入注释寄存区的数据。。"

	def __setattr__(self, f, v):
		"""强制所有的属性为只读的，无法进行更改和设置"""
		raise AttributeError('{}.{} is READ ONLY'.format(type(self).__name__, f))


class StringResources:
	"""系统的资源类，System String Resouces"""
	Language = DefaultLanguage()


class OperateResult:
	"""结果对象类，可以携带额外的数据信息"""
	def __init__(self, err: int = 0, msg: str = ""):
		"""
		实例化一个IsSuccess为False的默认对象，可以指定错误码和错误信息 -> OperateResult
		Parameter
			err: int 错误码
			msg: str 错误信息
		Return
			OperateResult: 结果对象
		"""
		self.ErrorCode = err
		self.Message = msg
		self.IsSuccess = False
		self.Content = None
		self.Content1 = None
		self.Content2 = None
		self.Content3 = None
		self.Content4 = None
		self.Content5 = None
		self.Content6 = None
		self.Content7 = None
		self.Content8 = None
		self.Content9 = None
		self.Content10 = None

	def CopyErrorFromOther(self, result):
		"""从另一个结果类中拷贝错误信息"""
		if result is not None:
			self.ErrorCode = result.ErrorCode
			self.Message = result.Message

	@staticmethod
	def CreateFailedResult(result):
		"""
		创建一个失败的结果对象，将会复制拷贝result的值 -> OperateResult
		Parameter
			result: OperateResult 继承自该类型的其他任何数据对象
		Return
			OperateResult: 新的一个IsSuccess为False的对象
		"""
		failed = OperateResult()
		if result is not None:
			failed.ErrorCode = result.ErrorCode
			failed.Message = result.Message
		return failed

	@staticmethod
	def CreateSuccessResult(
			content1=None,
			content2=None,
			content3=None,
	):
		"""
		创建一个成功的对象

		可以指定内容信息，当然也可以不去指定，就是单纯的一个成功的对象
		"""
		success = OperateResult()
		success.IsSuccess = True
		success.Message = StringResources.Language.SuccessText
		if content2 is None and content3 is None:
			success.Content = content1
		else:
			success.Content1 = content1
			success.Content2 = content2
			success.Content3 = content3
		return success


class HslTimeOut:
	def __init__(self):
		self.IsSuccessful = False
		self.IsTimeout = False
		self.DelayTime = 0
		self.StartTime = _now()
	WaitHandleTimeOut = []
	interactiveLock = _Lock()

	@staticmethod
	def AddHandleTimeOutCheck(timeout):
		HslTimeOut.interactiveLock.acquire()
		HslTimeOut.WaitHandleTimeOut.append(timeout)
		HslTimeOut.interactiveLock.release()

	@staticmethod
	def HandleTimeOutCheck(socket: _socket, timeout):
		hslTimeOut = HslTimeOut()
		hslTimeOut.DelayTime = timeout
		hslTimeOut.WorkSocket = socket
		if timeout > 0:
			HslTimeOut.AddHandleTimeOutCheck(hslTimeOut)
		return hslTimeOut


class INetMessage:
	"""数据消息的基本基类"""

	def __init__(self):
		self.HeadBytes: _Optional[bytearray] = None
		self.ContentBytes: _Optional[bytearray] = None
		self.SendBytes: _Optional[bytearray] = None

	def ProtocolHeadBytesLength(self):
		"""协议头数据长度，也即是第一次接收的数据长度"""
		return 0

	def GetContentLengthByHeadBytes(self):
		"""二次接收的数据长度"""
		return 0

	def CheckHeadBytesLegal(self, toke):
		"""令牌检查是否成功"""
		return False


class SoftBasic:
	"""系统运行的基础方法，提供了一些基本的辅助方法"""

	@staticmethod
	def GetSizeDescription(size: int):
		"""获取指定数据大小的文本描述字符串"""
		if size < 1000:
			return str(size) + " B"
		elif size < (1000 * 1000):
			data = float(size) / 1024
			return '{:.2f}'.format(data) + " Kb"
		elif size < (1000 * 1000 * 1000):
			data = float(size) / 1024 / 1024
			return '{:.2f}'.format(data) + " Mb"
		else:
			data = float(size) / 1024 / 1024 / 1024
			return '{:.2f}'.format(data) + " Gb"

	@staticmethod
	def IsTwoBytesEqual(b1, start1, b2, start2, length):
		"""判断两个字节的指定部分是否相同"""
		if b1 is None or b2 is None:
			return False
		for ii in range(length):
			if b1[ii + start1] != b2[ii + start2]:
				return False
		return True

	@staticmethod
	def TokenToBytes(token):
		"""将uuid的token值转化成统一的bytes数组，方便和java，C#通讯"""
		buffer = bytearray(token.bytes)
		buffer[0], buffer[1], buffer[2], buffer[3] = buffer[3], buffer[2], buffer[1], buffer[0]
		buffer[4], buffer[5] = buffer[5], buffer[4]
		buffer[6], buffer[7] = buffer[7], buffer[6]
		return buffer

	@staticmethod
	def ArrayExpandToLength(value, length):
		"""将数组扩充到指定的长度"""
		buffer = bytearray(length)
		if len(value) >= length:
			buffer[0:] = value[0:len(value)]
		else:
			buffer[0:len(value)] = value
		return buffer

	@staticmethod
	def StringToUnicodeBytes(value):
		"""获取字符串的unicode编码字符"""
		if value is None:
			return bytearray(0)

		buffer = value.encode('utf-16')
		if len(buffer) > 1 and buffer[0] == 255 and buffer[1] == 254:
			buffer = buffer[2:len(buffer)]
		return buffer


class HslSecurity:
	@staticmethod
	def ByteEncrypt(enBytes):
		"""加密方法，只对当前的程序集开放"""
		if enBytes is None:
			return None
		result = bytearray(len(enBytes))
		for i in range(len(enBytes)):
			result[i] = enBytes[i] ^ 0xB5
		return result

	@staticmethod
	def ByteDecrypt(deBytes):
		"""解密方法，只对当前的程序集开放"""
		return HslSecurity.ByteEncrypt(deBytes)


class SoftZipped:
	"""一个负责压缩解压数据字节的类"""

	@staticmethod
	def CompressBytes(inBytes):
		"""压缩字节数据"""
		if inBytes is None:
			return None
		return _gzip.compress(inBytes)

	@staticmethod
	def Decompress(inBytes):
		"""解压字节数据"""
		if inBytes is None:
			return None
		return _gzip.decompress( inBytes )


class HslProtocol:
	"""用于本程序集访问通信的暗号说明"""

	@staticmethod
	def HeadByteLength():
		"""规定所有的网络传输指令头都为32字节"""
		return 32

	@staticmethod
	def ProtocolBufferSize():
		"""所有网络通信中的缓冲池数据信息"""
		return 1024

	@staticmethod
	def ProtocolCheckSecends():
		"""用于心跳程序的暗号信息"""
		return 1

	@staticmethod
	def ProtocolClientQuit():
		"""客户端退出消息"""
		return 2

	@staticmethod
	def ProtocolClientRefuseLogin():
		"""因为客户端达到上限而拒绝登录"""
		return 3

	@staticmethod
	def ProtocolClientAllowLogin():
		"""允许客户端登录到服务器"""
		return 4

	@staticmethod
	def ProtocolAccountLogin():
		"""客户端登录的暗号信息"""
		return 5

	@staticmethod
	def ProtocolAccountRejectLogin():
		"""客户端登录的暗号信息"""
		return 6

	@staticmethod
	def ProtocolUserString():
		"""说明发送的只是文本信息"""
		return 1001

	@staticmethod
	def ProtocolUserBytes():
		"""发送的数据就是普通的字节数组"""
		return 1002

	@staticmethod
	def ProtocolUserBitmap():
		"""发送的数据就是普通的图片数据"""
		return 1003

	@staticmethod
	def ProtocolUserException():
		"""发送的数据是一条异常的数据，字符串为异常消息"""
		return 1004

	@staticmethod
	def ProtocolUserStringArray():
		"""说明发送的数据是字符串的数组"""
		return 1005

	@staticmethod
	def ProtocolFileDownload():
		"""请求文件下载的暗号"""
		return 2001

	@staticmethod
	def ProtocolFileUpload():
		"""请求文件上传的暗号"""
		return 2002

	@staticmethod
	def ProtocolFileDelete():
		"""请求删除文件的暗号"""
		return 2003

	@staticmethod
	def ProtocolFileCheckRight():
		"""文件校验成功"""
		return 2004

	@staticmethod
	def ProtocolFileCheckError():
		"""文件校验失败"""
		return 2005

	@staticmethod
	def ProtocolFileSaveError():
		"""文件保存失败"""
		return 2006

	@staticmethod
	def ProtocolFileDirectoryFiles():
		"""请求文件列表的暗号"""
		return 2007

	@staticmethod
	def ProtocolFileDirectories():
		"""请求子文件的列表暗号"""
		return 2008

	@staticmethod
	def ProtocolProgressReport():
		"""进度返回暗号"""
		return 2009

	@staticmethod
	def ProtocolNoZipped():
		"""不压缩数据字节"""
		return 3001

	@staticmethod
	def ProtocolZipped():
		"""压缩数据字节"""
		return 3002

	@staticmethod
	def CommandBytesBase(command, customer, token, data):
		"""生成终极传送指令的方法，所有的数据均通过该方法出来"""
		_zipped = HslProtocol.ProtocolNoZipped()
		_sendLength = 0
		if data is None:
			buffer = bytearray(HslProtocol.HeadByteLength())
		else:
			data = HslSecurity.ByteEncrypt(data)
			if len(data) > 102400:
				data = SoftZipped.CompressBytes(data)
				_zipped = HslProtocol.ProtocolZipped()
			buffer = bytearray(HslProtocol.HeadByteLength() + len(data))
			_sendLength = len(data)

		buffer[0:4] = struct.pack('<i', command)
		buffer[4:8] = struct.pack('<i', customer)
		buffer[8:12] = struct.pack('<i', _zipped)
		buffer[12:28] = SoftBasic.TokenToBytes(token)
		buffer[28:32] = struct.pack('<i', _sendLength)
		if _sendLength > 0:
			buffer[32:_sendLength + 32] = data
		return buffer

	@staticmethod
	def CommandAnalysis(head, content):
		"""解析接收到数据，先解压缩后进行解密"""
		if content is not None:
			_zipped = struct.unpack('<i', head[8:12])[0]
			if _zipped == HslProtocol.ProtocolZipped():
				content = SoftZipped.Decompress(content)
			return HslSecurity.ByteEncrypt(content)
		return bytearray(0)

	@staticmethod
	def CommandBytes(customer, token, data):
		"""获取发送字节数据的实际数据，带指令头"""
		return HslProtocol.CommandBytesBase(HslProtocol.ProtocolUserBytes(), customer, token, data)

	@staticmethod
	def PackStringArrayToByte(data):
		"""将字符串打包成字节数组内容"""
		if data is None:
			return bytearray(0)

		buffer = bytearray(0)
		buffer.extend(struct.pack('<i', len(data)))

		for i in range(len(data)):
			if data[i] is None or data[i] == "":
				buffer.extend(struct.pack('<i', 0))
			else:
				tmp = SoftBasic.StringToUnicodeBytes(data[i])
				buffer.extend(struct.pack('<i', len(tmp)))
				buffer.extend(tmp)
		return buffer

	@staticmethod
	def UnPackStringArrayFromByte(content):
		"""将字节数组还原成真实的字符串数组"""
		if content is None or len(content) < 4:
			return None
		index = 0
		count = struct.unpack('<i', content[index: index + 4])[0]
		result = []
		index = index + 4
		for i in range(count):
			length = struct.unpack('<i', content[index: index + 4])[0]
			index = index + 4
			if length > 0:
				result.append(content[index: index + length].decode('utf-16'))
			else:
				result.append("")
			index = index + length
		return result


class NetworkBase:
	"""网络基础类的核心"""

	def __init__(self):
		"""初始化方法"""
		super().__init__()
		self.Token = _uuid.UUID('{00000000-0000-0000-0000-000000000000}')
		self.CoreSocket = None

	def Receive(self, socket: _socket, length: int, timeout: int = None):
		"""接收固定长度的字节数组"""
		total = 0
		data = bytearray()
		receiveTimeout = HslTimeOut.HandleTimeOutCheck(socket, timeout / 1000)
		try:
			while total < length:
				data.extend(socket.recv(length - total))
				total = len(data)
			receiveTimeout.IsSuccessful = True
			return OperateResult.CreateSuccessResult(data)
		except Exception as e:
			receiveTimeout.IsSuccessful = True
			if receiveTimeout.IsTimeout:
				return OperateResult(msg='Receive Time out:' + str(timeout))
			result = OperateResult()
			result.Message = str(e)
			return result

	def Send(self, socket: _socket, data: _Union[bytearray, bytes]):
		"""发送消息给套接字，直到完成的时候返回"""
		try:
			socket.sendall(data)
			return OperateResult.CreateSuccessResult()
		except Exception as e:
			return OperateResult(msg=str(e))

	def CreateSocketAndConnect(self, ipAddress: str, port: int, timeout=10000):
		"""创建一个新的socket对象并连接到远程的地址，默认超时时间为10秒钟"""
		socketTmp = _socket.socket()
		receiveTimeout = HslTimeOut.HandleTimeOutCheck(socketTmp, timeout / 1000)
		try:
			socketTmp.connect((ipAddress, port))
			receiveTimeout.IsSuccessful = True
			return OperateResult.CreateSuccessResult(socketTmp)
		except Exception as e:
			receiveTimeout.IsSuccessful = True
			if receiveTimeout.IsTimeout:
				return OperateResult(msg="Connect Timeout " + str(timeout) + " Reason:" + str(e))
			return OperateResult(msg=str(e))

	def ReceiveMessage(self, socket: _socket, timeout: int, net_msg: INetMessage):
		"""接收一条完整的数据，使用异步接收完成，包含了指令头信息"""
		result = OperateResult()
		headResult = self.Receive(socket, net_msg.ProtocolHeadBytesLength(), timeout)
		if not headResult.IsSuccess:
			result.CopyErrorFromOther(headResult)
			return result
		net_msg.HeadBytes = headResult.Content
		if not net_msg.CheckHeadBytesLegal(SoftBasic.TokenToBytes(self.Token)):
			# 令牌校验失败
			if socket is not None:
				socket.close()
			result.Message = StringResources.Language.TokenCheckFailed
			return result

		contentLength = net_msg.GetContentLengthByHeadBytes()
		if contentLength == 0:
			net_msg.ContentBytes = bytearray(0)
		else:
			contentResult = self.Receive(socket, contentLength, timeout)
			if not contentResult.IsSuccess:
				result.CopyErrorFromOther(contentResult)
				return result
			net_msg.ContentBytes = contentResult.Content

		if net_msg.ContentBytes is None:
			net_msg.ContentBytes = bytearray(0)
		result.Content = net_msg
		result.IsSuccess = True
		return result

	def CloseSocket(self, socket: _socket):
		"""关闭网络"""
		if socket is not None:
			socket.close()

	def CheckRemoteToken(self, head: bytearray):
		"""检查当前的头子节信息的令牌是否是正确的"""
		return SoftBasic.IsTwoBytesEqual(head, 12, SoftBasic.TokenToBytes(self.Token), 0, 16)

	def SendBaseAndCheckReceive(self, socket: _socket, head_code: int, customer: int, send: bytearray):
		"""[自校验] 发送字节数据并确认对方接收完成数据，如果结果异常，则结束通讯"""
		# 数据处理
		send = HslProtocol.CommandBytesBase(head_code, customer, self.Token, send)

		sendResult = self.Send(socket, send)
		if not sendResult.IsSuccess:
			return sendResult

		# 检查对方接收完成
		checkResult = self.ReceiveLong(socket)
		if not checkResult.IsSuccess:
			return checkResult

		# 检查长度接收
		if checkResult.Content != len(send):
			self.CloseSocket(socket)
			return OperateResult(msg="接收的数据数据长度验证失败")

		return checkResult

	def SendBytesAndCheckReceive(self, socket: _socket, customer: int, send: bytearray):
		"""[自校验] 发送字节数据并确认对方接收完成数据，如果结果异常，则结束通讯"""
		return self.SendBaseAndCheckReceive(socket, HslProtocol.ProtocolUserBytes(), customer, send)

	def SendStringAndCheckReceive(self, socket: _socket, customer: int, send: str):
		"""[自校验] 直接发送字符串数据并确认对方接收完成数据，如果结果异常，则结束通讯"""
		data = SoftBasic.StringToUnicodeBytes(send)

		return self.SendBaseAndCheckReceive(socket, HslProtocol.ProtocolUserString(), customer, data)

	def ReceiveAndCheckBytes(self, socket: _socket, timeout: int):
		"""[自校验] 接收一条完整的同步数据，包含头子节和内容字节，基础的数据，如果结果异常，则结束通讯"""
		# 30秒超时接收验证
		# if (timeout > 0) ThreadPool.QueueUserWorkItem( new WaitCallback( ThreadPoolCheckTimeOut ), hslTimeOut );

		# 接收头指令
		headResult = self.Receive(socket, HslProtocol.HeadByteLength())
		if not headResult.IsSuccess:
			return OperateResult.CreateFailedResult(headResult)

		# 检查令牌
		if not self.CheckRemoteToken(headResult.Content):
			self.CloseSocket(socket)
			return OperateResult(msg=StringResources.Language.TokenCheckFailed)

		contentLength = struct.unpack('<i', headResult.Content[(HslProtocol.HeadByteLength() - 4):])[0]
		# 接收内容
		contentResult = self.Receive(socket, contentLength)
		if not contentResult.IsSuccess:
			return OperateResult.CreateFailedResult(contentResult)

		# 返回成功信息
		checkResult = self.SendLong(socket, HslProtocol.HeadByteLength() + contentLength)
		if not checkResult.IsSuccess:
			return OperateResult.CreateFailedResult(checkResult)

		head = headResult.Content
		content = contentResult.Content
		content = HslProtocol.CommandAnalysis(head, content)
		return OperateResult.CreateSuccessResult(head, content)

	def ReceiveStringContentFromSocket(self, socket: _socket):
		"""[自校验] 从网络中接收一个字符串数据，如果结果异常，则结束通讯"""
		receive = self.ReceiveAndCheckBytes(socket, 10000)
		if not receive.IsSuccess:
			return OperateResult.CreateFailedResult(receive)

		# 检查是否是字符串信息
		if struct.unpack('<i', receive.Content1[0:4])[0] != HslProtocol.ProtocolUserString():
			self.CloseSocket(socket)
			return OperateResult(msg="ReceiveStringContentFromSocket异常")

		if receive.Content2 is None:
			receive.Content2 = bytearray(0)
		# 分析数据
		return OperateResult.CreateSuccessResult(
			struct.unpack('<i', receive.Content1[4:8])[0],
			receive.Content2.decode('utf-16')
		)

	def ReceiveBytesContentFromSocket(self, socket: _socket):
		"""[自校验] 从网络中接收一串字节数据，如果结果异常，则结束通讯"""
		receive = self.ReceiveAndCheckBytes(socket, 10000)
		if not receive.IsSuccess:
			return OperateResult.CreateFailedResult(receive)

		# 检查是否是字节信息
		if struct.unpack('<i', receive.Content1[0:4])[0] != HslProtocol.ProtocolUserBytes():
			self.CloseSocket(socket)
			return OperateResult(msg="字节内容检查失败")

		# 分析数据
		return OperateResult.CreateSuccessResult(struct.unpack('<i', receive.Content1[4:8])[0], receive.Content2)

	def ReceiveLong(self, socket: _socket):
		"""从网络中接收Long数据"""
		read = self.Receive(socket, 8)
		if not read.IsSuccess:
			return OperateResult.CreateFailedResult(read)

		return OperateResult.CreateSuccessResult(struct.unpack('<Q', read.Content)[0])

	def SendLong(self, socket: _socket, value: int):
		"""将Long数据发送到套接字"""
		return self.Send(socket, struct.pack('<Q', value))

	def SendAccountAndCheckReceive(self, socket: _socket, customer: int, name: str, pwd: str):
		"""[自校验] 直接发送字符串数组并确认对方接收完成数据，如果结果异常，则结束通讯"""
		return self.SendBaseAndCheckReceive(
			socket, HslProtocol.ProtocolAccountLogin(), customer,
			HslProtocol.PackStringArrayToByte([name, pwd])
		)

	def ReceiveStringArrayContentFromSocket(self, socket: _socket):
		""""""
		receive = self.ReceiveAndCheckBytes(socket, 30000)
		if not receive.IsSuccess:
			return receive

		# 检查是否是字符串信息
		if struct.unpack('<i', receive.Content1[0: 4])[0] != HslProtocol.ProtocolUserStringArray():
			self.CloseSocket(socket)
			return OperateResult(msg=StringResources.Language.CommandHeadCodeCheckFailed)

		if receive.Content2 is None:
			receive.Content2 = bytearray(4)
		return OperateResult.CreateSuccessResult(
			struct.unpack('<i', receive.Content1[4:8])[0],
			HslProtocol.UnPackStringArrayFromByte(receive.Content2)
		)

	def ReceiveMqttRemainingLength(self, socket: _socket):
		"""基于MQTT协议，从网络套接字中接收剩余的数据长度"""
		buffer = bytearray()
		while True:
			read = self.Receive(socket, 1)
			if not read.IsSuccess:
				return read

			buffer.append(read.Content[0])
			if read.Content[0] < 0x80:
				break
			if len(buffer) >= 4:
				break
		if len(buffer) > 4:
			return OperateResult(err=0, msg="Receive Length is too long!")
		if len(buffer) == 1:
			return OperateResult.CreateSuccessResult(buffer[0])
		elif len(buffer) == 2:
			return OperateResult.CreateSuccessResult(buffer[0] - 128 + buffer[1] * 128)
		elif len(buffer) == 3:
			return OperateResult.CreateSuccessResult(buffer[0] - 128 + (buffer[1] - 128) * 128 + buffer[2] * 128 * 128)
		else:
			return OperateResult.CreateSuccessResult(
				(buffer[0] - 128) + (buffer[1] - 128) * 128 + (buffer[2] - 128) * 128 * 128 + buffer[3] * 128 * 128 * 128
			)


class DataFormat(Enum):
	"""应用于多字节数据的解析或是生成格式"""
	ABCD = 0
	BADC = 1
	CDAB = 2
	DCBA = 3


class ByteTransform:
	"""数据转换类的基础，提供了一些基础的方法实现."""
	DataFormat = DataFormat.DCBA

	def TransBool(self, buffer, index):
		"""
		将buffer数组转化成bool对象 -> bool

		Parameter
			buffer: bytes 原始的数据对象
			index: int 等待数据转换的起始索引
		Return -> bool
		"""
		return (buffer[index] & 0x01) == 0x01

	def TransByte(self, buffer, index):
		"""
		将buffer中的字节转化成byte对象，需要传入索引

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			byte: 一个byte类型的数据
		"""
		return buffer[index]

	def TransByteArray(self, buffer, index, length):
		"""
		将buffer中的字节转化成byte数组对象，需要传入索引

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			bytearray: byte[]数组
		"""
		data = bytearray(length)
		for i in range(length):
			data[i] = buffer[i + index]
		return data

	def TransInt16(self, buffer, index):
		"""从缓存中提取short结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: short数据类型"""
		data = self.TransByteArray(buffer, index, 2)
		return struct.unpack('<h', data)[0]

	def TransInt16Array(self, buffer, index, length):
		"""从缓存中提取short数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: short类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransInt16(buffer, index + 2 * i))
		return tmp

	def TransUInt16(self, buffer, index):
		"""从缓存中提取ushort结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: ushort数据类型"""
		data = self.TransByteArray(buffer, index, 2)
		return struct.unpack('<H', data)[0]

	def TransUInt16Array(self, buffer, index, length):
		"""从缓存中提取ushort数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: ushort类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransUInt16(buffer, index + 2 * i))
		return tmp

	def TransInt32(self, buffer, index):
		"""从缓存中提取int结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: int数据类型"""
		data = self.ByteTransDataFormat4(self.TransByteArray(buffer, index, 4))
		return struct.unpack('<i', data)[0]

	def TransInt32Array(self, buffer, index, length):
		"""从缓存中提取int数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: int类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransInt32(buffer, index + 4 * i))
		return tmp

	def TransUInt32(self, buffer, index):
		"""从缓存中提取uint结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: uint数据类型"""
		data = self.ByteTransDataFormat4(self.TransByteArray(buffer, index, 4))
		return struct.unpack('<I', data)[0]

	def TransUInt32Array(self, buffer, index, length):
		"""从缓存中提取uint数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: uint类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransUInt32(buffer, index + 4 * i))
		return tmp

	def TransInt64(self, buffer, index):
		"""从缓存中提取long结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: long数据类型"""
		data = self.ByteTransDataFormat8(self.TransByteArray(buffer, index, 8))
		return struct.unpack('<q', data)[0]

	def TransInt64Array(self, buffer, index, length):
		"""从缓存中提取long数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: long类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransInt64(buffer, index + 8 * i))
		return tmp

	def TransUInt64(self, buffer, index):
		"""从缓存中提取ulong结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: ulong数据类型"""
		data = self.ByteTransDataFormat8(self.TransByteArray(buffer, index, 8))
		return struct.unpack('<Q', data)[0]

	def TransUInt64Array(self, buffer, index, length):
		"""从缓存中提取ulong数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: ulong类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransUInt64(buffer, index + 8 * i))
		return tmp

	def TransSingle(self, buffer, index):
		"""从缓存中提取float结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: float数据类型"""
		data = self.ByteTransDataFormat4(self.TransByteArray(buffer, index, 4))
		return struct.unpack('<f', data)[0]

	def TransSingleArray(self, buffer, index, length):
		"""从缓存中提取float数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: float类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransSingle(buffer, index + 4 * i))
		return tmp

	def TransDouble(self, buffer, index):
		"""从缓存中提取double结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
		Return
			int: double数据类型"""
		data = self.ByteTransDataFormat8(self.TransByteArray(buffer, index, 8))
		return struct.unpack('<d', data)[0]

	def TransDoubleArray(self, buffer, index, length):
		"""从缓存中提取double数组结果

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
		Return
			int[]: double类型的数组信息"""
		tmp = []
		for i in range(length):
			tmp.append(self.TransDouble(buffer, index + 8 * i))
		return tmp

	def TransString(self, buffer, index, length, encoding):
		"""从缓存中提取string结果，使用指定的编码

		Parameter
			buffer: bytes 原始的缓存数据对象
			index: int 等待数据转换的起始索引
			length: int 长度信息
			encoding: 编码
		Return
			string: string类型的数组信息
		"""
		data = self.TransByteArray(buffer, index, length)
		return data.decode(encoding)

	def ByteTransByte(self, value):
		"""byte变量转化缓存数据，需要传入byte值"""
		buffer = bytearray(1)
		buffer[0] = value
		return buffer

	def Int16ArrayTransByte(self, values):
		"""short数组变量转化缓存数据，需要传入short数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 2)
		for i in range(len(values)):
			buffer[(i * 2): (i * 2 + 2)] = struct.pack('<h', values[i])
		return buffer

	def Int16TransByte(self, value):
		"""short数组变量转化缓存数据，需要传入short值"""
		return self.Int16ArrayTransByte([value])

	def UInt16ArrayTransByte(self, values):
		"""ushort数组变量转化缓存数据，需要传入ushort数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 2)
		for i in range(len(values)):
			buffer[(i * 2): (i * 2 + 2)] = struct.pack('<H', values[i])
		return buffer

	def UInt16TransByte(self, value):
		"""ushort变量转化缓存数据，需要传入ushort值"""
		return self.UInt16ArrayTransByte([value])

	def Int32ArrayTransByte(self, values):
		"""int数组变量转化缓存数据，需要传入int数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i * 4): (i * 4 + 4)] = self.ByteTransDataFormat4(struct.pack('<i', values[i]))
		return buffer

	def Int32TransByte(self, value):
		"""int变量转化缓存数据，需要传入int值"""
		return self.Int32ArrayTransByte([value])

	def UInt32ArrayTransByte(self, values):
		"""uint数组变量转化缓存数据，需要传入uint数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i * 4): (i * 4 + 4)] = self.ByteTransDataFormat4(struct.pack('<I', values[i]))
		return buffer

	def UInt32TransByte(self, value):
		"""uint变量转化缓存数据，需要传入uint值"""
		return self.UInt32ArrayTransByte([value])

	def Int64ArrayTransByte(self, values):
		"""long数组变量转化缓存数据，需要传入long数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i * 8): (i * 8 + 8)] = self.ByteTransDataFormat8(struct.pack('<q', values[i]))
		return buffer

	def Int64TransByte(self, value):
		"""long变量转化缓存数据，需要传入long值"""
		return self.Int64ArrayTransByte([value])

	def UInt64ArrayTransByte(self, values):
		"""ulong数组变量转化缓存数据，需要传入ulong数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i * 8): (i * 8 + 8)] = self.ByteTransDataFormat8(struct.pack('<Q', values[i]))
		return buffer

	def UInt64TransByte(self, value):
		"""ulong变量转化缓存数据，需要传入ulong值"""
		return self.UInt64ArrayTransByte([value])

	def FloatArrayTransByte(self, values):
		"""float数组变量转化缓存数据，需要传入float数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i * 4): (i * 4 + 4)] = self.ByteTransDataFormat4(struct.pack('<f', values[i]))
		return buffer

	def FloatTransByte(self, value):
		"""float变量转化缓存数据，需要传入float值"""
		return self.FloatArrayTransByte([value])

	def DoubleArrayTransByte(self, values):
		"""double数组变量转化缓存数据，需要传入double数组"""
		if values is None:
			return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i * 8): (i * 8 + 8)] = self.ByteTransDataFormat8(struct.pack('<d', values[i]))
		return buffer

	def DoubleTransByte(self, value):
		"""double变量转化缓存数据，需要传入double值"""
		return self.DoubleArrayTransByte([value])

	def StringTransByte(self, value: str, encoding: str):
		"""使用指定的编码字符串转化缓存数据，需要传入string值及编码信息"""
		return value.encode(encoding)

	def ByteTransDataFormat4(self, value, index=0):
		"""反转多字节的数据信息"""
		buffer = bytearray(4)
		if self.DataFormat == DataFormat.ABCD:
			buffer[0] = value[index + 3]
			buffer[1] = value[index + 2]
			buffer[2] = value[index + 1]
			buffer[3] = value[index + 0]
		elif self.DataFormat == DataFormat.BADC:
			buffer[0] = value[index + 2]
			buffer[1] = value[index + 3]
			buffer[2] = value[index + 0]
			buffer[3] = value[index + 1]
		elif self.DataFormat == DataFormat.CDAB:
			buffer[0] = value[index + 1]
			buffer[1] = value[index + 0]
			buffer[2] = value[index + 3]
			buffer[3] = value[index + 2]
		elif self.DataFormat == DataFormat.DCBA:
			buffer[0] = value[index + 0]
			buffer[1] = value[index + 1]
			buffer[2] = value[index + 2]
			buffer[3] = value[index + 3]
		return buffer

	def ByteTransDataFormat8(self, value, index=0):
		"""反转多字节的数据信息"""
		buffer = bytearray(8)
		if self.DataFormat == DataFormat.ABCD:
			buffer[0] = value[index + 7]
			buffer[1] = value[index + 6]
			buffer[2] = value[index + 5]
			buffer[3] = value[index + 4]
			buffer[4] = value[index + 3]
			buffer[5] = value[index + 2]
			buffer[6] = value[index + 1]
			buffer[7] = value[index + 0]
		elif self.DataFormat == DataFormat.BADC:
			buffer[0] = value[index + 6]
			buffer[1] = value[index + 7]
			buffer[2] = value[index + 4]
			buffer[3] = value[index + 5]
			buffer[4] = value[index + 2]
			buffer[5] = value[index + 3]
			buffer[6] = value[index + 0]
			buffer[7] = value[index + 1]
		elif self.DataFormat == DataFormat.CDAB:
			buffer[0] = value[index + 1]
			buffer[1] = value[index + 0]
			buffer[2] = value[index + 3]
			buffer[3] = value[index + 2]
			buffer[4] = value[index + 5]
			buffer[5] = value[index + 4]
			buffer[6] = value[index + 7]
			buffer[7] = value[index + 6]
		elif self.DataFormat == DataFormat.DCBA:
			buffer[0] = value[index + 0]
			buffer[1] = value[index + 1]
			buffer[2] = value[index + 2]
			buffer[3] = value[index + 3]
			buffer[4] = value[index + 4]
			buffer[5] = value[index + 5]
			buffer[6] = value[index + 6]
			buffer[7] = value[index + 7]
		return buffer


class NetworkDoubleBase(NetworkBase):
	"""支持长连接，短连接两个模式的通用客户端基类"""

	def __init__(self):
		super().__init__()
		self.byteTransform = ByteTransform()
		self.ipAddress = "127.0.0.1"
		self.port = 10000
		self.isPersistentConn = False
		self.isSocketError = False
		self.receiveTimeOut = 10000
		self.connectTimeOut = 5000
		self.isUseSpecifiedSocket = False
		self.interactiveLock = _Lock()
		self.iNetMessage = INetMessage()

	def SetPersistentConnection(self):
		"""在读取数据之前可以调用本方法将客户端设置为长连接模式，相当于跳过了ConnectServer的结果验证，对异形客户端无效"""
		self.isPersistentConn = True

	def ConnectServer(self):
		"""切换短连接模式到长连接模式，后面的每次请求都共享一个通道"""
		self.isPersistentConn = True
		result = OperateResult()
		# 重新连接之前，先将旧的数据进行清空
		if self.CoreSocket is not None:
			self.CoreSocket.close()

		rSocket = self.CreateSocketAndInitialization()
		if not rSocket.IsSuccess:
			self.isSocketError = True
			rSocket.Content = None
			result.Message = rSocket.Message
		else:
			self.CoreSocket = rSocket.Content
			result.IsSuccess = True
		return result

	def ConnectClose(self):
		"""在长连接模式下，断开服务器的连接，并切换到短连接模式"""
		result = OperateResult()
		self.isPersistentConn = False

		self.interactiveLock.acquire()
		# 额外操作
		result = self.ExtraOnDisconnect(self.CoreSocket)
		# 关闭信息
		if self.CoreSocket is not None: self.CoreSocket.close()
		self.CoreSocket = None
		self.interactiveLock.release()
		return result

	# 初始化的信息方法和连接结束的信息方法，需要在继承类里面进行重新实现
	def InitializationOnConnect(self, socket: _socket):
		"""连接上服务器后需要进行的初始化操作"""
		return OperateResult.CreateSuccessResult()

	def ExtraOnDisconnect(self, socket: _socket):
		"""在将要和服务器进行断开的情况下额外的操作，需要根据对应协议进行重写"""
		return OperateResult.CreateSuccessResult()

	def GetAvailableSocket(self):
		"""获取本次操作的可用的网络套接字"""
		if self.isPersistentConn:
			# 如果是异形模式
			if self.isUseSpecifiedSocket:
				if self.isSocketError:
					return OperateResult(msg=StringResources.Language.ConnectionIsNotAvailable)
				else:
					return OperateResult.CreateSuccessResult(self.CoreSocket)
			else:
				# 长连接模式
				if self.isSocketError or self.CoreSocket is None:
					connect = self.ConnectServer()
					if not connect.IsSuccess:
						self.isSocketError = True
						return OperateResult(msg=connect.Message)
					else:
						self.isSocketError = False
						return OperateResult.CreateSuccessResult(self.CoreSocket)
				else:
					return OperateResult.CreateSuccessResult(self.CoreSocket)
		else:
			# 短连接模式
			return self.CreateSocketAndInitialization()

	def CreateSocketAndInitialization(self):
		"""连接并初始化网络套接字"""
		result = self.CreateSocketAndConnect(self.ipAddress, self.port, self.connectTimeOut)
		if result.IsSuccess:
			# 初始化
			init = self.InitializationOnConnect(result.Content)
			if not init.IsSuccess:
				if result.Content is not None:
					result.Content.close()
				result.IsSuccess = init.IsSuccess
				result.CopyErrorFromOther(init)
		return result

	def ReadFromCoreSocketServer(self, socket: _socket, send: bytearray):
		"""在其他指定的套接字上，使用报文来通讯，传入需要发送的消息，返回一条完整的数据指令"""
		read = self.ReadFromCoreServerBase(socket, send)
		if not read.IsSuccess:
			return OperateResult.CreateFailedResult(read)

		# 拼接结果数据
		Content = bytearray(len(read.Content1) + len(read.Content2))
		if len(read.Content1) > 0:
			Content[0:len(read.Content1)] = read.Content1
		if len(read.Content2) > 0:
			Content[len(read.Content1):len(Content)] = read.Content2
		return OperateResult.CreateSuccessResult(Content)

	def ReadFromCoreServer(self, send: bytearray):
		"""使用底层的数据报文来通讯，传入需要发送的消息，返回一条完整的数据指令"""
		result = OperateResult()
		self.interactiveLock.acquire()
		# 获取有用的网络通道，如果没有，就建立新的连接
		resultSocket = self.GetAvailableSocket()
		if not resultSocket.IsSuccess:
			self.isSocketError = True
			self.interactiveLock.release()
			result.CopyErrorFromOther(resultSocket)
			return result

		read = self.ReadFromCoreSocketServer(resultSocket.Content, send)
		if read.IsSuccess:
			self.isSocketError = False
			result.IsSuccess = read.IsSuccess
			result.Content = read.Content
			result.Message = StringResources.Language.SuccessText
		# string tmp2 = BasicFramework.SoftBasic.ByteToHexString( result.Content, '-' )
		else:
			self.isSocketError = True
			result.CopyErrorFromOther(read)

		self.interactiveLock.release()
		if not self.isPersistentConn:
			if resultSocket.Content is not None:
				resultSocket.Content.close()
		return result

	def ReadFromCoreServerBase(self, socket: _socket, send: bytearray):
		"""使用底层的数据报文来通讯，传入需要发送的消息，返回最终的数据结果，被拆分成了头子节和内容字节信息"""
		self.iNetMessage.SendBytes = send
		sendResult = self.Send(socket, send)
		if not sendResult.IsSuccess:
			if socket is not None:
				socket.close()
			return OperateResult.CreateFailedResult(sendResult)

		# 接收超时时间大于0时才允许接收远程的数据
		if self.receiveTimeOut >= 0:
			# 接收数据信息
			resultReceive = self.ReceiveMessage(socket, self.receiveTimeOut, self.iNetMessage)
			if not resultReceive.IsSuccess:
				socket.close()
				return OperateResult(
					msg="Receive data timeout: " + str(self.receiveTimeOut) + " Msg:" + resultReceive.Message
				)
			return OperateResult.CreateSuccessResult(
				resultReceive.Content.HeadBytes, resultReceive.Content.ContentBytes
			)
		else:
			return OperateResult.CreateSuccessResult(bytearray(0), bytearray(0))


class ByteTransformHelper:
	"""所有数据转换类的静态辅助方法"""

	@staticmethod
	def GetResultFromBytes(result, translator):
		"""结果转换操作的基础方法，需要支持类型，及转换的委托

		Parameter
			result: OperateResult<bytearray> OperateResult类型的结果对象
			translator: lambda 一个lambda方法，将bytearray转换真实的对象
		Return
			OperateResult: 包含真实数据的结果类对象
		"""
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(translator(result.Content))
			else:
				return result
		except Exception as ex:
			return OperateResult(msg=str(ex))

	@staticmethod
	def GetResultFromArray(result: OperateResult):
		"""结果转换操作的基础方法，需要支持类型，及转换的委托

		Parameter
			result: OperateResult 带数组对象类型的结果对象
		Return
			OperateResult: 带单个数据的结果类对象
		"""
		if not result.IsSuccess:
			return result
		return OperateResult.CreateSuccessResult(result.Content[0])


class NetworkDeviceBase(NetworkDoubleBase):
	"""设备类的基类，提供了基础的字节读写方法"""

	def __init__(self):
		super().__init__()
		# 单个数据字节的长度，西门子为2，三菱，欧姆龙，modbusTcp就为1
		self.WordLength = 1

	def Read(self, address: str, length: int):
		"""从设备读取原始数据

		Parameter
			address: str 设备的地址，具体需要看设备自身的支持
			length: int 读取的地址长度，至于每个地址占一个字节还是两个字节，取决于具体的设备
		Return
			OperateResult<bytearray>: 带数据的结果类对象
		"""
		return OperateResult()

	def Write(self, address: str, value: _Union[bytearray, bytes]):
		"""将原始数据写入设备

		Parameter
			address: str 设备的地址，具体需要看设备自身的支持
			value: bytearray 原始数据
		Return
			OperateResult: 带有成功标识的结果对象
		"""
		return OperateResult()

	def ReadBool(self, address: str, length: int = None):
		"""读取设备的bool类型的数据或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadBool(address, 1))
		else:
			OperateResult(msg=StringResources.Language.NotSupportedFunction)

	def ReadInt16(self, address: str, length: int = None):
		"""读取设备的short类型的数据或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadInt16(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength),
				lambda m: self.byteTransform.TransInt16Array(m, 0, length)
			)

	def ReadUInt16(self, address: str, length: int = None):
		"""读取设备的ushort数据类型的数据或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadUInt16(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength),
				lambda m: self.byteTransform.TransUInt16Array(m, 0, length)
			)

	def ReadInt32(self, address: str, length: int = None):
		"""读取设备的int类型的数据或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadInt32(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength * 2),
				lambda m: self.byteTransform.TransInt32Array(m, 0, length)
			)

	def ReadUInt32(self, address: str, length: int = None):
		"""读取设备的uint数据类型的数据或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadUInt32(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength * 2),
				lambda m: self.byteTransform.TransUInt32Array(m, 0, length)
			)

	def ReadFloat(self, address: str, length: int = None):
		"""读取设备的float类型的数据或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadFloat(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength * 2),
				lambda m: self.byteTransform.TransSingleArray(m, 0, length)
			)

	def ReadInt64(self, address: str, length: int = None):
		"""读取设备的long类型的数组或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadInt64(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength * 4),
				lambda m: self.byteTransform.TransInt64Array(m, 0, length)
			)

	def ReadUInt64(self, address: str, length: int = None):
		"""读取设备的ulong类型的数组或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadUInt64(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength * 4),
				lambda m: self.byteTransform.TransUInt64Array(m, 0, length)
			)

	def ReadDouble(self, address: str, length: int = None):
		"""读取设备的double类型的数组或是数组"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadDouble(address, 1))
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length * self.WordLength * 4),
				lambda m: self.byteTransform.TransDoubleArray(m, 0, length)
			)

	def ReadString(self, address: str, length: int, encoding: str = None):
		"""读取设备的字符串数据，编码为指定的编码信息，如果不指定，那么就是ascii编码"""
		if encoding is None:
			return self.ReadString(address, length, 'ascii')
		else:
			return ByteTransformHelper.GetResultFromBytes(
				self.Read(address, length),
				lambda m: self.byteTransform.TransString(m, 0, len(m), encoding)
			)

	def WriteBool(self, address: str, value: _Union[bool, list]) -> OperateResult:
		"""向设备中写入bool数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return OperateResult(msg=StringResources.Language.NotSupportedFunction)
		else:
			return self.WriteBool(address, [value])

	def WriteInt16(self, address: str, value: _Union[int, list]) -> OperateResult:
		"""向设备中写入short数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.Int16ArrayTransByte(value))
		else:
			return self.WriteInt16(address, [value])

	def WriteUInt16(self, address: str, value: _Union[int, list]):
		"""向设备中写入short数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.UInt16ArrayTransByte(value))
		else:
			return self.WriteUInt16(address, [value])

	def WriteInt32(self, address: str, value: _Union[int, list]):
		"""向设备中写入int数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.Int32ArrayTransByte(value))
		else:
			return self.WriteInt32(address, [value])

	def WriteUInt32(self, address: str, value: _Union[int, list]):
		"""向设备中写入uint数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.UInt32ArrayTransByte(value))
		else:
			return self.WriteUInt32(address, [value])

	def WriteFloat(self, address: str, value: _Union[float, list]):
		"""向设备中写入float数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.FloatArrayTransByte(value))
		else:
			return self.WriteFloat(address, [value])

	def WriteInt64(self, address: str, value: _Union[int, list]):
		"""向设备中写入long数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.Int64ArrayTransByte(value))
		else:
			return self.WriteInt64(address, [value])

	def WriteUInt64(self, address: str, value: _Union[int, list]):
		"""向设备中写入ulong数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.UInt64ArrayTransByte(value))
		else:
			return self.WriteUInt64(address, [value])

	def WriteDouble(self, address: str, value: _Union[float, list]):
		"""向设备中写入double数据或是数组，返回是否写入成功"""
		if type(value) == list:
			return self.Write(address, self.byteTransform.DoubleArrayTransByte(value))
		else:
			return self.WriteDouble(address, [value])

	def WriteString(self, address: str, value: str, length=None):
		"""向设备中写入string数据，编码为ascii，返回是否写入成功"""
		if length is None:
			return self.Write(address, self.byteTransform.StringTransByte(value, 'ascii'))
		else:
			return self.Write(
				address,
				SoftBasic.ArrayExpandToLength(self.byteTransform.StringTransByte(value, 'ascii'), length)
			)

	def WriteUnicodeString(self, address: str, value: str, length=None):
		"""向设备中写入string数据，编码为unicode，返回是否写入成功"""
		if length is None:
			temp = SoftBasic.StringToUnicodeBytes(value)
			return self.Write(address, temp)
		else:
			temp = SoftBasic.StringToUnicodeBytes(value)
			temp = SoftBasic.ArrayExpandToLength(temp, length * 2)
			return self.Write(address, temp)


class RegularByteTransform(ByteTransform):
	"""常规的字节转换类"""
	def __init__(self):
		return


class MelsecQnA3EBinaryMessage(INetMessage):
	"""三菱的Qna兼容3E帧协议解析规则"""

	def ProtocolHeadBytesLength(self):
		"""协议头数据长度，也即是第一次接收的数据长度"""
		return 9

	def GetContentLengthByHeadBytes(self):
		"""二次接收的数据长度"""
		if self.HeadBytes is not None:
			return self.HeadBytes[8] * 256 + self.HeadBytes[7]
		else:
			return 0

	def CheckHeadBytesLegal(self,token):
		"""令牌检查是否成功"""
		if self.HeadBytes is not None:
			if self.HeadBytes[0] == 0xD0 and self.HeadBytes[1] == 0x00:
				return True
			else:
				return False
		else:
			return False


class ValueType(Enum):
	word = 0x00
	bit = 0x01


class MelsecElementInfo:
	"""三菱 PLC 软元件相关信息。"""

	def __init__(self, code: int, value_type: ValueType, base: int):
		"""如果您清楚类型代号，可以根据值进行扩展"""
		self.__data_code = code
		self.__base = base
		self.__value_type = value_type

	@property
	def base(self):
		return self.__base

	@property
	def value_type(self):
		return self.__value_type

	@property
	def data_code(self):
		return self.__data_code


class FX5UElementInfoGenerator:
	@staticmethod
	def GetX():
		"""X输入寄存器"""
		return MelsecElementInfo(0x9C, ValueType.bit, 8)

	@staticmethod
	def GetY():
		"""Y输出寄存器"""
		return MelsecElementInfo(0x9D, ValueType.bit, 8)

	@staticmethod
	def GetM():
		"""M中间寄存器"""
		return MelsecElementInfo(0x90, ValueType.bit, 10)

	@staticmethod
	def GetD():
		"""D数据寄存器"""
		return MelsecElementInfo(0xA8, ValueType.word, 10)

	@staticmethod
	def GetW():
		"""W链接寄存器"""
		return MelsecElementInfo(0xB4, ValueType.word, 16)

	@staticmethod
	def GetL():
		"""L锁存继电器"""
		return MelsecElementInfo(0x92, ValueType.bit, 10)

	@staticmethod
	def GetF():
		"""F报警器"""
		return MelsecElementInfo(0x93, ValueType.bit, 10)

	@staticmethod
	def GetV():
		"""V边沿继电器"""
		return MelsecElementInfo(0x93, ValueType.bit, 10)

	@staticmethod
	def GetB():
		"""B链接继电器"""
		return MelsecElementInfo(0xA, ValueType.bit, 16)

	@staticmethod
	def GetR():
		"""R文件寄存器"""
		return MelsecElementInfo(0xAF, ValueType.word, 10)

	@staticmethod
	def GetS():
		"""S步进继电器"""
		return MelsecElementInfo(0x98, ValueType.bit, 10)

	@staticmethod
	def GetZ():
		"""变址寄存器"""
		return MelsecElementInfo(0xCC, ValueType.word, 10)

	@staticmethod
	def GetT():
		"""定时器的值"""
		return MelsecElementInfo(0xC2, ValueType.word, 10)

	@staticmethod
	def GetC():
		"""计数器的值"""
		return MelsecElementInfo(0xC5, ValueType.word, 10)


class QSeriesElementInfoGenerator:
	@staticmethod
	def GetX():
		"""X输入寄存器"""
		return MelsecElementInfo(0x9C, ValueType.bit, 16)

	@staticmethod
	def GetY():
		"""Y输出寄存器"""
		return MelsecElementInfo(0x9D, ValueType.bit, 16)

	@staticmethod
	def GetM():
		"""M中间寄存器"""
		return MelsecElementInfo(0x90, ValueType.bit, 10)

	@staticmethod
	def GetD():
		"""D数据寄存器"""
		return MelsecElementInfo(0xA8, ValueType.word, 10)

	@staticmethod
	def GetW():
		"""W链接寄存器"""
		return MelsecElementInfo(0xB4, ValueType.word, 16)

	@staticmethod
	def GetL():
		"""L锁存继电器"""
		return MelsecElementInfo(0x92, ValueType.bit, 10)

	@staticmethod
	def GetF():
		"""F报警器"""
		return MelsecElementInfo(0x93, ValueType.bit, 10)

	@staticmethod
	def GetV():
		"""V边沿继电器"""
		return MelsecElementInfo(0x93, ValueType.bit, 10)

	@staticmethod
	def GetB():
		"""B链接继电器"""
		return MelsecElementInfo(0xA, ValueType.bit, 16)

	@staticmethod
	def GetR():
		"""R文件寄存器"""
		return MelsecElementInfo(0xAF, ValueType.word, 10)

	@staticmethod
	def GetS():
		"""S步进继电器"""
		return MelsecElementInfo(0x98, ValueType.bit, 10)

	@staticmethod
	def GetZ():
		"""变址寄存器"""
		return MelsecElementInfo(0xCC, ValueType.word, 10)

	@staticmethod
	def GetT():
		"""定时器的值"""
		return MelsecElementInfo(0xC2, ValueType.word, 10)

	@staticmethod
	def GetC():
		"""计数器的值"""
		return MelsecElementInfo(0xC5, ValueType.word, 10)


LSeriesElementInfoGenerator = QSeriesElementInfoGenerator


class CPUType(Enum):
	FX5U = FX5UElementInfoGenerator
	LSeries = LSeriesElementInfoGenerator
	QSeries = QSeriesElementInfoGenerator


class MelsecAddressAnalyzer:
	def __init__(self, cpu_type: CPUType):
		self.__generator = cpu_type.value

	def __call__(self, *args, **kwargs):
		assert len(args) == 1 or 'address' in kwargs
		if len(args) == 1:
			address = args[0]
		else:
			address = kwargs['address']
		assert isinstance(address, str) and len(address) > 1

		result = OperateResult()
		getter = getattr(self.__generator, f'Get{address[0]}')
		info: MelsecElementInfo = getter()

		result.Content1 = info
		result.Content2 = int(address[1:], info.base)
		result.IsSuccess = True
		result.Message = StringResources.Language.SuccessText
		return result


class MelsecMcNet(NetworkDeviceBase):
	"""三菱PLC通讯类，采用Qna兼容3E帧协议实现，需要在PLC侧先的以太网模块先进行配置，必须为二进制通讯"""

	def __init__(self, ip_address: str, port: int, cpu_type: CPUType):
		super().__init__()
		self.__address_analyzer = MelsecAddressAnalyzer(cpu_type)
		"""实例化一个三菱的Qna兼容3E帧协议的通讯对象"""
		self.NetworkNumber = 0
		self.NetworkStationNumber = 0
		self.iNetMessage = MelsecQnA3EBinaryMessage()
		self.byteTransform = RegularByteTransform()
		self.ipAddress = ip_address
		self.port = port
		self.WordLength = 1

	@property
	def address_analyzer(self):
		return self.__address_analyzer

	def BuildReadCommand(self, address, length, is_bit, network_number=0, network_station_number=0):
		"""根据类型地址长度确认需要读取的指令头"""
		analysis = self.address_analyzer(address)
		if not analysis.IsSuccess:
			return OperateResult.CreateFailedResult(analysis)

		_PLCCommand = bytearray(21)
		_PLCCommand[0] = 0x50  # 副标题
		_PLCCommand[1] = 0x00
		_PLCCommand[2] = network_number  # 网络号
		_PLCCommand[3] = 0xFF  # PLC编号
		_PLCCommand[4] = 0xFF  # 目标模块IO编号
		_PLCCommand[5] = 0x03
		_PLCCommand[6] = network_station_number  # 目标模块站号
		_PLCCommand[7] = 0x0C  # 请求数据长度
		_PLCCommand[8] = 0x00
		_PLCCommand[9] = 0x0A  # CPU监视定时器
		_PLCCommand[10] = 0x00
		_PLCCommand[11] = 0x01  # 批量读取数据命令
		_PLCCommand[12] = 0x04
		_PLCCommand[13] = 0x01 if is_bit else 0x00  # 以点为单位还是字为单位成批读取
		_PLCCommand[14] = 0x00
		_PLCCommand[15] = analysis.Content2 % 256  # 起始地址的地位
		_PLCCommand[16] = analysis.Content2 // 256
		_PLCCommand[17] = 0x00
		_PLCCommand[18] = analysis.Content1.data_code  # 指明读取的数据
		_PLCCommand[19] = length % 256  # 软元件长度的地位
		_PLCCommand[20] = length // 256

		return OperateResult.CreateSuccessResult(_PLCCommand)

	def BuildWriteCommand(self, address, value, network_number=0, network_station_number=0):
		"""根据类型地址以及需要写入的数据来生成指令头"""
		analysis = self.address_analyzer(address)
		if not analysis.IsSuccess:
			return OperateResult.CreateFailedResult(analysis)

		length = -1
		if analysis.Content1.value_type == ValueType.bit:
			# 按照位写入的操作，数据需要重新计算
			length2 = len(value) // 2 + 1
			if len(value) % 2 == 0:
				length2 = len(value) // 2
			buffer = bytearray(length2)

			for i in range(length2):
				if value[i * 2 + 0] != 0x00:
					buffer[i] += 0x10
				if (i * 2 + 1) < len(value):
					if value[i * 2 + 1] != 0x00:
						buffer[i] += 0x01
			length = len(value)
			value = buffer

		_PLCCommand = bytearray(21 + len(value))
		_PLCCommand[0] = 0x50  # 副标题
		_PLCCommand[1] = 0x00
		_PLCCommand[2] = network_number  # 网络号
		_PLCCommand[3] = 0xFF  # PLC编号
		_PLCCommand[4] = 0xFF  # 目标模块IO编号
		_PLCCommand[5] = 0x03
		_PLCCommand[6] = network_station_number  # 目标模块站号
		_PLCCommand[7] = (len(_PLCCommand) - 9) % 256  # 请求数据长度
		_PLCCommand[8] = (len(_PLCCommand) - 9) // 256
		_PLCCommand[9] = 0x0A  # CPU监视定时器
		_PLCCommand[10] = 0x00
		_PLCCommand[11] = 0x01  # 批量读取数据命令
		_PLCCommand[12] = 0x14
		_PLCCommand[13] = analysis.Content1.value_type.value  # 以点为单位还是字为单位成批读取
		_PLCCommand[14] = 0x00
		_PLCCommand[15] = analysis.Content2 % 256  # 起始地址的低8位
		_PLCCommand[16] = analysis.Content2 // 256  # 起始地址的高8位
		_PLCCommand[17] = 0x00
		_PLCCommand[18] = analysis.Content1.data_code  # 指明写入的数据

		# 判断是否进行位操作
		if analysis.Content1.value_type == ValueType.bit:
			if length > 0:
				_PLCCommand[19] = length % 256  # 软元件长度的地位
				_PLCCommand[20] = length // 256
			else:
				_PLCCommand[19] = len(value) * 2 % 256  # 软元件长度的地位
				_PLCCommand[20] = len(value) * 2 // 256
		else:
			_PLCCommand[19] = len(value) // 2 % 256  # 软元件长度的地位
			_PLCCommand[20] = len(value) // 2 // 256
		_PLCCommand[21:] = value

		return OperateResult.CreateSuccessResult(_PLCCommand)

	@staticmethod
	def ExtractActualData(response, is_bit: bool):
		""" 从PLC反馈的数据中提取出实际的数据内容，需要传入反馈数据，是否位读取"""
		if is_bit:
			# 如果以 ASCII 模式通信，反馈数据以一个字节表示一个位的值：字节值为 0x30 表示对应位为 True，字节值为 0x31 表示对应位为 False
			# binary 模式，相应地，把 ASCII 模式下的一个字节用 4 个位表示，所以一个字节表示了两个位的值
			Content = bytearray((len(response) - 11) * 2)
			i = 11
			while i < len(response):
				if (response[i] & 0x10) == 0x10:
					Content[(i - 11) * 2 + 0] = 0x01
				if (response[i] & 0x01) == 0x01:
					Content[(i - 11) * 2 + 1] = 0x01
				i += 1

			return OperateResult.CreateSuccessResult(Content)
		else:
			# 字读取
			Content = bytearray(len(response) - 11)
			Content[0:] = response[11:]

			return OperateResult.CreateSuccessResult(Content)

	def Read(self, address, length):
		"""从三菱PLC中读取想要的数据，返回读取结果"""
		# 获取指令
		command = self.BuildReadCommand(address, length, False, self.NetworkNumber, self.NetworkStationNumber)
		if not command.IsSuccess:
			return OperateResult.CreateFailedResult(command)

		# 核心交互
		read = self.ReadFromCoreServer(command.Content)
		if not read.IsSuccess:
			return OperateResult.CreateFailedResult(read)

		# 错误代码验证
		errorCode = read.Content[9] * 256 + read.Content[10]
		if errorCode != 0:
			return OperateResult(
				err=errorCode, msg=StringResources.Language.MelsecPleaseReferToManulDocument
			)

		# 数据解析，需要传入是否使用位的参数
		return MelsecMcNet.ExtractActualData(read.Content, False)

	def ReadBool(self, address: str, length: int = None):
		"""从三菱PLC中批量读取位软元件，返回读取结果"""
		if length is None:
			return ByteTransformHelper.GetResultFromArray(self.ReadBool(address, 1))
		else:
			# 获取指令
			command = self.BuildReadCommand(address, length, True, self.NetworkNumber, self.NetworkStationNumber)
			if not command.IsSuccess:
				return OperateResult.CreateFailedResult(command)

			# 核心交互
			read = self.ReadFromCoreServer(command.Content)
			if not read.IsSuccess:
				return OperateResult.CreateFailedResult(read)

			# 错误代码验证
			errorCode = read.Content[9] * 256 + read.Content[10]
			if errorCode != 0:
				return OperateResult(
					err=errorCode, msg=StringResources.Language.MelsecPleaseReferToManulDocument
				)

			# 数据解析，需要传入是否使用位的参数
			extract = MelsecMcNet.ExtractActualData(read.Content, True)
			if not extract.IsSuccess:
				return OperateResult.CreateFailedResult(extract)

			# 转化bool数组
			content = []
			for i in range(length):
				if extract.Content[i] == 0x01:
					content.append(True)
				else:
					content.append(False)
			return OperateResult.CreateSuccessResult(content)

	def Write(self, address: str, value: bytearray):
		"""向PLC写入数据，数据格式为原始的字节类型"""
		# 解析指令
		command = self.BuildWriteCommand(address, value, self.NetworkNumber, self.NetworkStationNumber)
		if not command.IsSuccess:
			return command

		# 核心交互
		read = self.ReadFromCoreServer(command.Content)
		if not read.IsSuccess:
			return read

		# 错误码校验
		errorCode = read.Content[9] * 256 + read.Content[10]
		if errorCode != 0:
			return OperateResult(
				err=errorCode, msg=StringResources.Language.MelsecPleaseReferToManulDocument
			)

		# 成功
		return OperateResult.CreateSuccessResult()

	def WriteBool(self, address, values):
		"""向PLC中位软元件写入bool数组或是值，返回值说明，比如你写入M100,values[0]对应M100"""
		if type(values) == list:
			buffer = bytearray(len(values))
			for i in range(len(values)):
				if values[i]:
					buffer[i] = 0x01
			return self.Write(address, buffer)
		else:
			return self.WriteBool(address, [values])


class MelsecQnA3EAsciiMessage(INetMessage):
	"""三菱的Qna兼容3E帧的ASCII协议解析规则"""

	def ProtocolHeadBytesLength(self):
		"""协议头数据长度，也即是第一次接收的数据长度"""
		return 18

	def GetContentLengthByHeadBytes(self):
		"""二次接收的数据长度"""
		if self.HeadBytes is not None:
			return int(self.HeadBytes[14:18].decode('ascii'),16)
		else:
			return 0

	def CheckHeadBytesLegal(self,token):
		"""令牌检查是否成功"""
		if self.HeadBytes is not None:
			if self.HeadBytes[0] == ord('D') and self.HeadBytes[1] == ord('0') and self.HeadBytes[2] == ord('0') and self.HeadBytes[3] == ord('0'):
				return True
			else:
				return False
		else:
			return False


class Qna3EException(Exception):
	def __init__(self, result: OperateResult):
		desc = f'Error: Qna3E communication failed: Code {result.ErrorCode}, {result.Message}'
		Exception.__init__(self, desc)


class Qna3E:
	"""
		适用于三菱 FX-5U、L、Q 系列 PLC 以太网通信，使用 QNA 3E 协议，二进制或 ASCII 码格式，TCP 连接方式。
	"""
	def __init__(self, host: str, port: int, cpu_type: CPUType, mode: str = 'binary'):
		"""
		:param host: PLC 的 IP 地址或域名地址（如果有的话）
		:param port: PLC 配置的 TCP 通信端口号。最好是设立一个专门的端口号（信道），不要与触摸屏等其他客户端共用。
		:param mode: 如果传入 'ASCII'（不区分大小写），表示帧格式为 ASCII 码，否则，帧格式为二进制。这必须要与 PLC 设置一致。默认二进制。
		注意：本程序库目前只实现了二进制模式。
		"""
		if mode.lower().startswith('ascii'):
			raise NotImplementedError('ASCII 通信模式没有实现。请改为使用 binary 模式。')
		else:
			self.connection = MelsecMcNet(ip_address=host, port=port, cpu_type=cpu_type)
		self.connection.SetPersistentConnection()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.connection.ConnectClose()

	def get_coil(self, name: str) -> bool:
		result = self.connection.ReadBool(address=name, length=1)
		# 如果读取结果成功，result.IsSuccess是True,反之result.IsSuccess是False,
		# result内有3个属性
		# 1.result.IsSuccess显示读取结果
		# 2.result.ErrorCode错误代码
		# 3.result.Message错误信息
		# 4.result.Content返回结果
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_coil(self, name: str, count: int) -> _List[bool]:
		result = self.connection.ReadBool(address=name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_coil_uint16(self, address) -> int:
		result = self.connection.ReadBool(address, length=16)
		if not result.IsSuccess:
			raise Qna3EException(result)
		bool_list = result.Content
		value = bool_list_2_int(bool_list)
		return value

	def get_int32(self, name: str):
		result = self.connection.ReadInt32(address=name, length=1)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_int32(self, name: str, count: int):
		result = self.connection.ReadInt32(address=name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_int16(self, name: str) -> int:
		result = self.connection.ReadInt16(address=name, length=1)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_int16(self, name: str, count: int) -> _List[int]:
		result = self.connection.ReadInt16(address=name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_uint16(self, name: str):
		result = self.connection.ReadUInt16(address=name, length=1)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_uint16(self, name: str, count: int):
		result = self.connection.ReadUInt16(address=name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_uint32(self, name: str) -> int:
		result = self.connection.ReadUInt32(name, length=1)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_uint32(self, name: str, count: int):
		result = self.connection.ReadUInt32(name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_uint64(self, name: str) -> int:
		result = self.connection.ReadUInt64(address=name, length=1)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_uint64(self, name: str, count: int) -> _List[int]:
		result = self.connection.ReadUInt64(address=name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_int64(self, name: str) -> int:
		result = self.connection.ReadInt64(address=name, length=1)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content[0]

	def get_multi_int64(self, name: str, count: int):
		result = self.connection.ReadInt64(address=name, length=count)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_float(self, address, length):
		result = self.connection.ReadFloat(address, length=length)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_double(self, address, length):
		result = self.connection.ReadDouble(address, length=length)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def get_string(self, address, length):
		result = self.connection.ReadString(address, length=length)
		if not result.IsSuccess:
			raise Qna3EException(result)
		return result.Content

	def set_coil(self, name: str, value: bool):
		result = self.connection.WriteBool(name, value)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_coil(self, name: str, values: _List[bool]):
		result = self.connection.WriteBool(name, values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_int16(self, name: str, value: int):
		result = self.connection.WriteInt16(address=name, value=[value])
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_int16(self, name: str, values: _List[int]):
		result = self.connection.WriteInt16(address=name, value=values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_int32(self, name: str, value: int):
		result = self.connection.WriteInt32(address=name, value=[value])
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_int32(self, name: str, values: _List[int]):
		result = self.connection.WriteInt32(name, values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_int64(self, name: str, value: int):
		result = self.connection.WriteInt64(address=name, value=[value])
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_int64(self, name: str, values: _List[int]):
		result = self.connection.WriteInt64(address=name, value=values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_uint16(self, name: str, value: int):
		result = self.connection.WriteUInt16(address=name, value=[value])
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_uint16(self, name: str, values: _List[int]):
		result = self.connection.WriteUInt16(address=name, value=values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_uint32(self, name: str, value: int):
		result = self.connection.WriteUInt32(address=name, value=[value])
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_uint32(self, name: str, values: _List[int]):
		result = self.connection.WriteUInt32(address=name, value=values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_uint64(self, name: str, value: int):
		result = self.connection.WriteUInt64(address=name, value=[value])
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_multi_uint64(self, name: str, values: _List[int]):
		result = self.connection.WriteUInt64(address=name, value=values)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_float(self, address, value):
		result = self.connection.WriteFloat(address, value)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_double(self, address, value):
		result = self.connection.WriteDouble(address, value)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def set_string(self, address, value, length=None):
		result = self.connection.WriteString(address, value, length=length)
		if not result.IsSuccess:
			raise Qna3EException(result)

	def write_UnicodeString(self, address, value, length=None):
		result = self.connection.WriteUnicodeString(address, value, length=length)
		if not result.IsSuccess:
			raise Qna3EException(result)


class Qna1E:
	CoilTypeMap = {
		'X': 0x5820,
		'Y': 0x5920,
		'M': 0x4D20
	}

	def __init__(self, host: str, port: int, timeout: float = 1):
		self.timeout = timeout
		self._connection = _create_connection((host, port), timeout=timeout)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	@staticmethod
	def construct_read_coils_command(name: str, count: int):
		assert name[0] in 'XYM', f'当前仅支持读取 X、Y、M 类型的继电器'
		base = 10 if name[0] == 'M' else 16
		address = int(name[1:], base)
		coil_type = Qna1E.CoilTypeMap[name[0]]
		buffer = [0, 0xFF, 0xA0, 0, address % 256, address // 256, 0, 0, coil_type % 256, coil_type // 256, count % 256, count // 256]
		data = bytearray(buffer)
		return data

	@staticmethod
	def construct_write_coils_command(name: str, values: _List[bool]):
		coil_head = name[0]
		base = 10 if name[0] == 'M' else 16
		address = int(name[1:], base)
		coil_type = Qna1E.CoilTypeMap[coil_head]
		count = len(values)
		buffer = [
			2, 0xFF, 0xA0, 0, address % 256, address // 256, 0, 0, coil_type % 256, coil_type // 256, count % 256, count // 256
		]
		pair_count = count // 2
		for i in range(pair_count):
			bit_4 = 1 if values[i * 2] else 0
			bit_0 = 1 if values[i * 2 + 1] else 0
			byte_value = (bit_4 << 4) | bit_0
			buffer.append(byte_value)
		if count % 2:
			byte_value = 0x10 if values[-1] else 0
			buffer.append(byte_value)
		data = bytearray(buffer)
		return data

	def _do_query(self, cmd: bytearray, needed_length: int):
		assert needed_length >= 2, '设备响应数据帧至少有2个字节的长度'
		self._connection.send(cmd)
		feedback = bytearray()
		head = self._connection.recv(2)
		assert len(head) == 2, f'响应报文头部长度有误：{len(head)}，内容为：[{head}]'
		assert (head[0] & 0x80) == 0x80, f'QnA1E device unknown response head: {head}'
		assert head[1] == 0x00, f'QnA1E device response error code: {head[1]}'

		left_len = needed_length - 2
		feedback.extend(head)
		if left_len > 0:
			body = self._connection.recv(left_len)
			assert len(body) == left_len, f'响应报文数据段长度有误：{len(body)}，内容为：[{body}]'
			feedback.extend(body)

		return feedback

	def read_coils(self, name: str, count: int):
		cmd = Qna1E.construct_read_coils_command(name, count)
		needed_length = 2 + count // 2 + count % 2
		feedback = self._do_query(cmd, needed_length)

		result = list()
		for i in range(count):
			shift_bit_count = 4 if (i % 2) == 0 else 0
			value = (feedback[2+i//2] >> shift_bit_count) & 0xF
			result.append(value != 0)
		return result

	def write_coils(self, name: str, values: _List[bool]):
		cmd = Qna1E.construct_write_coils_command(name, values)
		self._do_query(cmd, needed_length=2)

	def set_coil(self, name: str, value: bool = True):
		self.write_coils(name, [value])

	def reset_coil(self, name: str):
		self.write_coils(name, [False])

	@staticmethod
	def construct_read_registers_command(name: str, count: int):
		assert name.startswith('D'), f'当前仅支持普通数据寄存器类型，名称须以[D]开头。'
		address = int(name[1:])
		buffer = [0x1, 0xFF, 0x0A, 0x00, address % 256, address // 256, 0x00, 0x00, 0x20, 0x44, count % 256, count // 256]
		data = bytearray(buffer)
		return data

	def read_registers(self, name: str, count: int):
		cmd = Qna1E.construct_read_registers_command(name, count)
		needed_length = 2 + 2 * count
		feedback = self._do_query(cmd, needed_length)

		result = list()
		for i in range(count):
			low = feedback[2+i*2]
			high = feedback[2+i*2+1]
			value = (high << 8) + low
			result.append(value)
		return result

	def close(self):
		self._connection.close()

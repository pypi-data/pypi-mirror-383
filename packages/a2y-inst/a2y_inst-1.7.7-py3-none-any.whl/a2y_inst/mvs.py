from ctypes import byref as _byref, cast as _cast, memset as _memset
from ctypes import sizeof as _sizeof, POINTER as _POINTER, c_ubyte as _c_ubyte, c_float as _c_float
from enum import Enum as _Enum
from .mvs_native import MV_CC_DEVICE_INFO_LIST as _MV_CC_DEVICE_INFO_LIST
from .mvs_native import MV_CC_DEVICE_INFO as _MV_CC_DEVICE_INFO
from .mvs_native import MV_FRAME_OUT_INFO_EX as _MV_FRAME_OUT_INFO_EX
from .mvs_native import MV_GIGE_DEVICE as _MV_GIGE_DEVICE, MV_USB_DEVICE as _MV_USB_DEVICE
from .mvs_native import MvCamera as _MvCamera, MVCC_INTVALUE as _MVCC_INTVALUE
from .mvs_native import MV_ACCESS_Exclusive as _MV_ACCESS_Exclusive
from .mvs_native import MV_TRIGGER_MODE_OFF as _MV_TRIGGER_MODE_OFF
from .mvs_native import PixelType_header as _PixelTypeHeader
import numpy as _np
from threading import Lock as _Lock, Thread as _Thread
from typing import Callable as _Callable, Optional as _Optional, Union as _Union


class Transform(_Enum):
	Nothing = 0
	ROTATE_90_CLOCKWISE = 1
	ROTATE_180 = 2
	ROTATE_90_COUNTERCLOCKWISE = 3
	FLIP_HORIZONTAL = 4
	FLIP_VERTICAL = 5
	# Flip both is the same with rotate 180


def _is_mono(pixel_type) -> bool:
	return pixel_type in (
		_PixelTypeHeader.PixelType_Gvsp_Mono8,
		_PixelTypeHeader.PixelType_Gvsp_Mono10,
		_PixelTypeHeader.PixelType_Gvsp_Mono10_Packed,
		_PixelTypeHeader.PixelType_Gvsp_Mono12,
		_PixelTypeHeader.PixelType_Gvsp_Mono12_Packed,
		_PixelTypeHeader.PixelType_Gvsp_Mono14,
		_PixelTypeHeader.PixelType_Gvsp_Mono16
	)


class MVSException(Exception):
	pass


class MVSInterface(_Enum):
	GIGE = _MV_GIGE_DEVICE
	USB = _MV_USB_DEVICE


class Camera:
	def __init__(self, camera_info: '_CameraInfo'):
		native_handle = camera_info.native_handle
		camera = _MvCamera()
		ret = camera.MV_CC_CreateHandle(native_handle)
		if ret != 0:
			raise MVSException(f'Create camera from camera info failed. ret[0x{ret:0x}].')
		ret = camera.MV_CC_OpenDevice(_MV_ACCESS_Exclusive, 0)
		if ret != 0:
			camera.MV_CC_DestroyHandle()
			raise MVSException(f'Open camera failed. ret[0x{ret:0x}].')

		self.__camera = camera
		self.__camera_info = camera_info
		self.__frame_buffer = None

		try:
			payload = self.__initialize_camera(camera_info)
			self.__frame_buffer = (_c_ubyte * payload)()
		except Exception as _e:
			self.close()
			raise

		self.__frame_info = _MV_FRAME_OUT_INFO_EX()
		_memset(_byref(self.__frame_info), 0, _sizeof(self.__frame_info))

	def __initialize_camera(self, camera_info: '_CameraInfo'):
		self.__camera.MV_CC_SetEnumValue('TriggerMode', _MV_TRIGGER_MODE_OFF)

		if camera_info.interface == MVSInterface.GIGE:
			package_size = self.__camera.MV_CC_GetOptimalPacketSize()
			if int(package_size) > 0:
				self.__camera.MV_CC_SetIntValue('GevSCPSPacketSize', package_size)

		para = _MVCC_INTVALUE()
		_memset(_byref(para), 0, _sizeof(_MVCC_INTVALUE))
		ret = self.__camera.MV_CC_GetIntValue('PayloadSize', para)
		if ret != 0:
			raise MVSException(f'Initialize camera failed: could not get PayloadSize. ret[0x{ret:0x}]')
		ret = self.__camera.MV_CC_StartGrabbing()
		if ret != 0:
			raise MVSException(f'Initialize camera failed: could not start grabbing. ret[0x{ret:0x}]')

		return para.nCurValue

	@property
	def camera_info(self):
		return self.__camera_info

	@property
	def exposure_time(self) -> float:
		value = _c_float()
		ret = self.__camera.MV_CC_GetFloatValue('ExposureTime', value)
		if ret != 0:
			raise MVSException(f'Get camera exposure time failed. ret[0x{ret}]')
		return value.value

	@exposure_time.setter
	def exposure_time(self, value: float):
		ret = self.__camera.MV_CC_SetFloatValue('ExposureTime', value)
		if ret != 0:
			raise MVSException(f'Set camera exposure time failed. Target value: {value}. ret[0x{ret}]')

	@property
	def gain(self) -> float:
		value = _c_float()
		ret = self.__camera.MV_CC_GetFloatValue('Gain', value)
		if ret != 0:
			raise MVSException(f'Get camera gain failed. ret[0x{ret}]')
		return value.value

	@gain.setter
	def gain(self, value: float):
		ret = self.__camera.MV_CC_SetFloatValue('Gain', value)
		if ret != 0:
			raise MVSException(f'Set camera gain failed. Target value: {value}. ret[0x{ret}]')

	def snap(self, timeout: float = 1, copy: bool = False, transform: Transform = Transform.Nothing) -> _np.ndarray:
		ms = int(timeout * 1000)
		ret = self.__camera.MV_CC_GetOneFrameTimeout(
			_byref(self.__frame_buffer), _sizeof(self.__frame_buffer), self.__frame_info, nMsec=ms
		)
		if ret != 0:
			raise MVSException(f'Grab frame failed. ret[0x{ret}]')

		width = self.__frame_info.nWidth
		height = self.__frame_info.nHeight
		channel = 1 if _is_mono(self.__frame_info.enPixelType) else 3
		image = _np.frombuffer(self.__frame_buffer, dtype=_np.ubyte, count=width*height*channel)
		image = image.reshape(height, width, channel)

		# 看起来以下的 transform 操作都是在原帧缓冲区上进行
		if transform == Transform.ROTATE_180:
			image[::, ::, ::] = image[::-1, ::-1, ::]
		elif transform == Transform.ROTATE_90_CLOCKWISE:
			image = image.transpose((1, 0, 2))
			image[::, ::, ::] = image[::, ::-1, ::]
		elif transform == Transform.ROTATE_90_COUNTERCLOCKWISE:
			image = image.transpose((1, 0, 2))
			image[::, ::, ::] = image[::-1, ::, ::]
		elif transform == Transform.FLIP_VERTICAL:
			image[::, ::, ::] = image[::-1, ::, ::]
		elif transform == Transform.FLIP_HORIZONTAL:
			image[::, ::, ::] = image[::, ::-1, ::]

		if copy:
			image = image.copy()

		if channel == 1:
			image = image.reshape((height, width))

		return image

	def close(self):
		if self.__camera is not None:
			self.__camera.MV_CC_StopGrabbing()
			self.__camera.MV_CC_CloseDevice()
			self.__camera.MV_CC_DestroyHandle()
			self.__camera = None

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()


class _CameraInfo:
	InfoAttrNameMap = {
		_MV_GIGE_DEVICE: 'stGigEInfo',
		_MV_USB_DEVICE: 'stUsb3VInfo'
	}

	def __init__(self, dev_list: _MV_CC_DEVICE_INFO_LIST, index: int):
		self.__dev_list = dev_list
		self.__index = index

	@property
	def native_handle(self) -> _MV_CC_DEVICE_INFO:
		info = _cast(self.__dev_list.pDeviceInfo[self.__index], _POINTER(_MV_CC_DEVICE_INFO)).contents
		return info

	@property
	def interface(self) -> MVSInterface:
		return MVSInterface(self.native_handle.nTLayerType)

	@property
	def serial_number(self) -> str:
		info = getattr(self.native_handle.SpecialInfo, _CameraInfo.InfoAttrNameMap[self.native_handle.nTLayerType])
		sn = bytes(info.chSerialNumber).strip(b'\x00')
		return sn.decode(encoding='latin')

	@property
	def model(self) -> str:
		info = getattr(self.native_handle.SpecialInfo, _CameraInfo.InfoAttrNameMap[self.native_handle.nTLayerType])
		sn = bytes(info.chModelName).strip(b'\x00')
		return sn.decode(encoding='latin')

	@property
	def ipv4(self) -> str:
		if self.interface != MVSInterface.GIGE:
			return ''
		else:
			ip = self.native_handle.SpecialInfo.stGigEInfo.nCurrentIp
			return f'{(ip & 0xff000000) >> 24}.{(ip & 0xff0000) >> 16}.{(ip & 0xff00) >> 8}.{ip & 0xff}'

	def open_camera(self):
		return Camera(self)

	def __str__(self):
		return f'MVS Camera\nS/N: {self.serial_number}\nModel: {self.model}\nI/F: {self.interface}\nIPv4: {self.ipv4}'


class _CameraEnumeratorIterator:
	def __init__(self, enumerator: 'CameraEnumerator', info_name: str = ''):
		self.__enumerator = enumerator
		self.__index = 0
		self.__info_name = info_name

	def __iter__(self):
		return self

	def __next__(self):
		if self.__index < self.__enumerator.count:
			item = self.__enumerator[self.__index]
			self.__index += 1
			if self.__info_name and hasattr(item, self.__info_name):
				return getattr(item, self.__info_name)
			return item
		raise StopIteration


class CameraEnumerator:
	def __init__(self):
		dev_list = _MV_CC_DEVICE_INFO_LIST()
		ret = _MvCamera.MV_CC_EnumDevices(_MV_GIGE_DEVICE | _MV_USB_DEVICE, dev_list)
		if ret != 0:
			raise MVSException(f'Enum devices fail. ret[0x{ret:0x}]')

		self.__dev_list = dev_list

	@property
	def count(self) -> int:
		"""
		找到的所有相机的数量
		"""
		return self.__dev_list.nDeviceNum

	def __getitem__(self, item):
		if item < 0 or item >= self.count:
			raise MVSException(f'Index out of range: {item}')

		return _CameraInfo(self.__dev_list, item)

	def serial_numbers(self):
		"""
		返回一个迭代器，可迭代找到的所有相机的序列号。注意：根据实际运行结果，可能会有重复的条目。
		"""
		return _CameraEnumeratorIterator(self, 'serial_number')

	def items(self):
		"""
		返回一个迭代器，可迭代找到的所有相机信息。注意：根据实际运行结果，可能会有重复的条目。
		"""
		return _CameraEnumeratorIterator(self)

	def open_first_camera(self):
		"""
		打开第一个找到的相机，如果有的话，否则，抛出一个 ValueError
		"""
		if self.count > 0:
			return self[0].open_camera()
		raise ValueError('No camera found.')

	def get_camera_info_by_serial_number(self, serial_number: str):
		"""
		根据序列号找到对应相机的 CameraInfo 对象。如果相机不存在，抛出一个 ValueError
		"""
		for i in range(self.count):
			info = self[i]
			if info.serial_number == serial_number:
				return info
		raise MVSException(f'Camera with serial number [{serial_number}] not found.')

	def open_camera_by_serial_number(self, serial_number: str):
		"""
		打开指定序列号的那个相机，如果存在的话，否则，抛出一个 ValueError
		"""
		return self.get_camera_info_by_serial_number(serial_number).open_camera()


class MVSCamera:
	# TODO: 实现这个类的时候，锁的使用有些随意。另外，有朝一日，或许要把这个类重新实现，完全替代 Camera 类，而不是作为它的一个 Wrapper

	def __init__(self, identify: _Union[str, _CameraInfo]):
		if isinstance(identify, str):
			self.__identify = CameraEnumerator().get_camera_info_by_serial_number(identify)
		elif isinstance(identify, _CameraInfo):
			self.__identify = identify
		else:
			raise MVSException('Invalid MVS Camera Identity.')

		self.__transform = Transform.Nothing
		self.__timeout = 1.0
		self.__camera_lock = _Lock()
		self.__camera: _Optional[Camera] = None
		self.__play_thread: _Optional[_Thread] = None
		self.__stop_flag = False
		self.__buf_lock = _Lock()
		self.__buffer: _Optional[_np.ndarray] = None
		self.open()
		self.__callback: _Optional[_Callable[[_np.ndarray], None]] = None

	@property
	def callback(self):
		return self.__callback

	@callback.setter
	def callback(self, value: _Callable[[_np.ndarray], None]):
		with self.__buf_lock:
			self.__callback = value

	@property
	def timeout(self):
		return self.__timeout

	@timeout.setter
	def timeout(self, value: float):
		self.__timeout = value

	@property
	def transform(self):
		return self.__transform

	@transform.setter
	def transform(self, value: Transform):
		self.__transform = value

	@property
	def serial_number(self) -> str:
		return self.__identify.serial_number

	@property
	def ipv4(self) -> str:
		return self.__identify.ipv4

	@property
	def exposure_time(self) -> float:
		if self.closed:
			raise MVSException('Camera is closed')
		return self.__camera.exposure_time

	@exposure_time.setter
	def exposure_time(self, value: float):
		if self.closed:
			raise MVSException('Camera is closed')
		self.__camera.exposure_time = value

	@property
	def gain(self) -> float:
		if self.closed:
			raise MVSException('Camera is closed')
		return self.__camera.gain

	@gain.setter
	def gain(self, value: float):
		if self.closed:
			raise MVSException('Camera is closed')
		self.__camera.gain = value

	@property
	def closed(self) -> bool:
		return self.__camera is None

	@property
	def is_open(self) -> bool:
		return not self.closed

	def close(self):
		self.stop()
		if self.__camera is not None:
			self.__camera.close()
			self.__camera = None

	def open(self):
		if not self.closed:
			raise MVSException('Camera is already opened.')
		self.__camera = self.__identify.open_camera()

	def __play_function(self):
		while True:
			if self.__stop_flag:
				break

			image = self.snap(self.timeout, copy=True, transform=self.transform)

			with self.__buf_lock:
				callback = self.callback
				if callback is not None:
					callback(image)

	def snap(self, timeout: float = 1, copy: bool = False, transform: Transform = Transform.Nothing):
		"""
		这个方法参数的设计主要是为了兼容 Camera.snap
		"""
		with self.__camera_lock:
			return self.__camera.snap(timeout, copy, transform)

	def start(self):
		if self.closed:
			raise MVSException('Camera is closed')
		elif self.__play_thread is not None:
			raise MVSException('Camera is already playing')

		with self.__buf_lock:
			self.__play_thread = _Thread(target=self.__play_function)
			self.__play_thread.start()
			self.__stop_flag = False

	def stop(self):
		with self.__buf_lock:
			if self.__play_thread is not None:
				self.__stop_flag = True
				self.__play_thread.join()
				self.__play_thread = None

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

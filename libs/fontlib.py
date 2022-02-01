"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
import gc
import struct
from micropython import const
from framebuf import MONO_HLSB, MONO_HMSB, MONO_VLSB


class FontLibHeaderException(Exception):
	pass

class FontLibException(Exception):
	pass

class FontLibHeader(object):
	LENGTH = const(25)
	SCAN_MODE_HORIZONTAL = BYTE_ORDER_LSB = const(0)
	SCAN_MODE_VERTICAL = BYTE_ORDER_MSB = const(1)
	SCAN_MODE = {SCAN_MODE_HORIZONTAL: 'Horizontal', SCAN_MODE_VERTICAL: 'Vertical'}
	BYTE_ORDER = {BYTE_ORDER_LSB: 'LSB', BYTE_ORDER_MSB: 'MSB'}

	def __init__(self, header_data):
		if len(header_data) != FontLibHeader.LENGTH:
			raise FontLibHeaderException('Invalid header length')

		self.identify,\
		self.file_size,\
		self.font_width,\
		self.font_height,\
		self.characters,\
		self.has_index_table,\
		self.scan_mode,\
		self.byte_order,\
		self.ascii_start,\
		self.gb2312_start,\
		_ = struct.unpack('<4sIBBHBBBII2s', header_data)

		if self.identify not in (b'FMUX', b'FMUY'):
			raise FontLibHeaderException('Invalid font file')

		self.data_size = ((self.font_width - 1) // 8 + 1) * self.font_height

		if self.has_index_table:
			self.index_table_address = FontLibHeader.LENGTH
		else:
			self.index_table_address = 0
		
		self.format = MONO_VLSB
		if self.scan_mode == FontLibHeader.SCAN_MODE_HORIZONTAL:
			self.format = MONO_HMSB if self.byte_order == FontLibHeader.BYTE_ORDER_MSB else MONO_HLSB


class FontLib(object):
	FORMAT = {MONO_VLSB: 'MONO_VLSB', MONO_HMSB: 'MONO_HMSB', MONO_HLSB: 'MONO_HLSB'}
	ASCII_START = const(0x20)
	ASCII_END = const(0x7f)
	GB2312_START = const(0x80)
	GB2312_END = const(0xffef)

	def __init__(self, font_filename):
		self.__font_filename = font_filename
		self.__header = None

		with open(self.__font_filename, 'rb') as font_file:
			self.__header = FontLibHeader(memoryview(font_file.read(FontLibHeader.LENGTH)))
			self.__placeholder_buffer = self.__get_character_unicode_buffer(font_file, {ord('?')}, True)[0][1] # [ord('?')]

	def __is_ascii(self, char_code):
		return FontLib.ASCII_START <= char_code <= FontLib.ASCII_END

	def __is_gb2312(self, char_code):
		return FontLib.GB2312_START <= char_code <= FontLib.GB2312_END

	def __get_character_unicode_buffer(self, font_file, unicode_set, is_placeholder=False):
		buffer_list = []
		ascii_list = []
		gb2312_list = []
		chunk_size = const(1000)

		def __seek(offset, data, targets):
			# target:
			# 	0: unicode
			#	1: little endian bytes
			#	2: charest index offset
			seeked_count = 0
			for target in targets:
				if target[2] is not None:
					seeked_count += 1
					continue

				seek_offset = -1
				while True:
					seek_offset = data.find(target[1], seek_offset + 1)

					if seek_offset >= 0:
						if seek_offset % 2 == 0:
							target[2] = seek_offset + offset
							break
						else:
							continue
					else:
						break

			return seeked_count == len(targets)

		gc.disable()
		for unicode in unicode_set:
			if unicode in (9, 10, 13): continue
			if self.__is_ascii(unicode):
				char_offset = self.__header.ascii_start + (unicode - FontLib.ASCII_START) * self.__header.data_size
				ascii_list.append([unicode, char_offset])
			elif self.__is_gb2312(unicode):
				gb2312_list.append([unicode, struct.pack('<H', unicode), None])
			else:
				buffer_list.append([unicode, memoryview(self.__placeholder_buffer)])

		del unicode_set

		for ascii in ascii_list:
			font_file.seek(ascii[1])
			buffer_list.append([ascii[0], memoryview(font_file.read(self.__header.data_size))])
		gc.enable()

		if is_placeholder:
			return buffer_list

		del ascii_list

		if len(gb2312_list):
			font_file.seek(self.__header.index_table_address)

			for offset in range(self.__header.index_table_address, self.__header.ascii_start, chunk_size):
				if __seek(offset, font_file.read(chunk_size), gb2312_list):
					break
			else:
				__seek(self.__header.ascii_start - offset, font_file.read(chunk_size), gb2312_list)

		gc.disable()
		for gb2312 in gb2312_list:
			if gb2312[2] is None:
				buffer_list.append([gb2312[0], memoryview(self.__placeholder_buffer)])
			else:
				char_offset = int(self.__header.gb2312_start + (gb2312[2] - self.__header.index_table_address) / 2 * self.__header.data_size)

				font_file.seek(char_offset)
				buffer_list.append([gb2312[0], memoryview(font_file.read(self.__header.data_size))])
		gc.enable()
		gc.collect()

		del gb2312_list
		return buffer_list

	def get_characters(self, characters: str):
		result = {}
		with open(self.__font_filename, 'rb') as font_file:
			unicode_list = list(set(ord(char) for char in characters))

			chunk = 30
			for count in range(0, len(unicode_list) // chunk + 1):
				for char in self.__get_character_unicode_buffer(font_file, unicode_list[count * chunk:count * chunk + chunk]):
					result[char[0]] = char[1]

		return result

	@property
	def scan_mode(self):
		return self.__header.scan_mode

	@property
	def byte_order(self):
		return self.__header.byte_order

	@property
	def format(self):
		return self.__header.format

	@property
	def data_size(self):
		return self.__header.data_size

	@property
	def file_size(self):
		return self.__header.file_size
	
	@property
	def font_width(self):
		return self.__header.font_width

	@property
	def font_height(self):
		return self.__header.font_height

	@property
	def characters(self):
		return self.__header.characters

	def info(self):
		print('\
HZK Info: {}\n\
    file size : {}\n\
   font width : {}\n\
  font height : {}\n\
    data size : {}\n\
    scan mode : {} ({})\n\
   byte order : {} ({})\n\
       format : {} ({})\n\
   characters : {}\n'.format(
			  self.__font_filename,
			  self.file_size,
			  self.font_width,
			  self.font_height,
			  self.data_size,
			  self.scan_mode,
			  FontLibHeader.SCAN_MODE[self.scan_mode],
			  self.byte_order,
			  FontLibHeader.BYTE_ORDER[self.byte_order],
			  self.format,
			  FontLib.FORMAT[self.format],
			  self.characters
			))

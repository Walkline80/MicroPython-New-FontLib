"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
import gc
import struct


class FontLibHeaderException(Exception):
	pass

class FontLibException(Exception):
	pass

class FontLibHeader(object):
	LENGTH = 24

	def __init__(self, header_data):
		if len(header_data) != FontLibHeader.LENGTH:
			raise FontLibHeaderException('Invalid header length')

		self.identify,\
		self.file_size,\
		self.font_height,\
		self.characters,\
		self.has_index_table,\
		self.scan_mode,\
		self.byte_order,\
		self.ascii_start,\
		self.gb2312_start,\
		_ = struct.unpack('<4sIBHBBBII2s', header_data)

		if self.identify not in (b'FMUX', b'FMUY'):
			raise FontLibHeaderException('Invalid font file')

		self.data_size = ((self.font_height - 1) // 8 + 1) * self.font_height

		if self.has_index_table:
			self.index_table_address = FontLibHeader.LENGTH
		else:
			self.index_table_address = 0


class FontLib(object):
	SCAN_MODE_HORIZONTAL = BYTE_ORDER_LSB = 0
	SCAN_MODE_VERTICAL = BYTE_ORDER_MSB = 1
	SCAN_MODE = {SCAN_MODE_HORIZONTAL: 'Horizontal', SCAN_MODE_VERTICAL: 'Vertical'}
	BYTE_ORDER = {BYTE_ORDER_LSB: 'LSB', BYTE_ORDER_MSB: 'MSB'}

	def __init__(self, font_filename):
		self.__font_filename = font_filename
		self.__header = None

		with open(self.__font_filename, 'rb') as font_file:
			self.__header = FontLibHeader(memoryview(font_file.read(FontLibHeader.LENGTH)))
			self.__placeholder_buffer = self.__get_character_unicode_buffer(font_file, {ord('?')})[ord('?')]

		gc.collect()

	def __is_ascii(self, char_code):
		return 0x20 <= char_code <= 0x7f

	def __is_gb2312(self, char_code):
		return 0x80 <= char_code <= 0xffef

	def __get_character_unicode_buffer(self, font_file, unicode_set):
		buffer_list = {}

		for unicode in unicode_set:
			if self.__is_ascii(unicode):
				char_offset = self.__header.ascii_start + (unicode - 0x20) * self.__header.data_size
			elif self.__is_gb2312(unicode):
				gb2312_index = struct.pack('<H', unicode)

				def __seek(data, target):
					seek_offset = 0
					while True:
						seek_offset = data.find(target, seek_offset + 1)

						if seek_offset >= 0:
							if seek_offset % 2 == 0:
								return seek_offset
							else:
								continue
						else:
							return False

				for offset in range(self.__header.index_table_address, self.__header.ascii_start, 1000):
					font_file.seek(offset)

					char_index_offset = __seek(font_file.read(1000), gb2312_index)
					if char_index_offset:
						char_index_offset += offset
						break
				else:
					buffer_list[unicode] = self.__placeholder_buffer
					continue

				char_offset = self.__header.gb2312_start + (char_index_offset - self.__header.index_table_address) / 2 * self.__header.data_size
			else:
				buffer_list[unicode] = self.__placeholder_buffer
				continue

			font_file.seek(int(char_offset))
			info_data = font_file.read(self.__header.data_size)

			buffer_list[unicode] = info_data

		gc.collect()
		return buffer_list

	def get_characters(self, characters: str):
		with open(self.__font_filename, 'rb') as font_file:
			unicode_set = set()
			for char in characters:
				unicode_set.add(ord(char))

			return self.__get_character_unicode_buffer(font_file, unicode_set)

	@property
	def scan_mode(self):
		return self.__header.scan_mode

	@property
	def byte_order(self):
		return self.__header.byte_order

	@property
	def data_size(self):
		return self.__header.data_size

	@property
	def file_size(self):
		return self.__header.file_size
	
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
  font height : {}\n\
    data size : {}\n\
    scan mode : {}\n\
   byte order : {}\n\
   characters : {}\n'.format(
			  self.__font_filename,
			  self.file_size,
			  self.font_height,
			  self.data_size,
			  FontLib.SCAN_MODE[self.scan_mode],
			  FontLib.BYTE_ORDER[self.byte_order],
			  self.characters
			))

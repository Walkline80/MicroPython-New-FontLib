"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
import os
import gc
import struct


try:
	import framebuf
	MICROPYTHON = True
except ImportError:
	MICROPYTHON = False

CURRENT_DIR = os.getcwd() if MICROPYTHON else os.path.dirname(__file__) + '/'
FONT_DIR = '/client/'
HZK_FILE = 'combined.bin'


class FontLibHeaderException(Exception):
	pass

class FontLibException(Exception):
	pass


'''
Header Data Sample:
	b'FMUX\xa4\xa1\x04\x00\x10\xe4"\x01$E\x00\x00$Q\x00\x00\\\x00A\x00' # little-endian

	[4] b'FMUX'				- identify
	[4] b'\xa4\xa1\x04\x00'	- file length
	[1] b'\x10'				- font height
	[2] b'\xe4"'			- character counts
	[1] b'\x01'				- has index table
	[4] b'$E\x00\x00'		- ascii start address
	[4] b'$Q\x00\x00'		- gb2312 start address
	[4] b'\\\x00A\x00'		- reserved
'''
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
		self.ascii_start,\
		self.gb2312_start,\
		_ = struct.unpack('<4sIBHBII4s', header_data)

		if self.identify not in (b'FMUX',):
			raise FontLibHeaderException('Invalid font file')

		self.data_size = ((self.font_height - 1) // 8 + 1) * self.font_height

		if self.has_index_table:
			self.index_table_address = FontLibHeader.LENGTH
		else:
			self.index_table_address = 0


class FontLib(object):
	def __init__(self, font_filename):
		self.__font_filename = font_filename
		self.__header = None

		with open(self.__font_filename, 'rb') as font_file:
			self.__header = FontLibHeader(font_file.read(FontLibHeader.LENGTH))
			self.__placeholder_buffer = self.__get_character_unicode_buffer(font_file, {ord('?')})[0][1]

		gc.collect()

	def __is_ascii(self, char_code):
		return 0x20 <= char_code <= 0x7f

	def __is_gb2312(self, char_code):
		return 0x80 <= char_code <= 0xffef

	def __get_character_unicode_buffer(self, font_file, unicode_set):
		buffer_list = []

		for unicode in unicode_set:
			if self.__is_ascii(unicode):
				char_offset = self.__header.ascii_start + (unicode - 0x20) * self.__header.data_size
			elif self.__is_gb2312(unicode):
				gb2312_index = struct.pack('<H', unicode)

				for offset in range(self.__header.index_table_address, self.__header.ascii_start, 2):
					font_file.seek(offset)

					if font_file.read(2) == gb2312_index:
						char_index_offset = font_file.tell() - 2
						break
				else:
					buffer_list.append([unicode, self.__placeholder_buffer])
					continue

				char_offset = self.__header.gb2312_start + (char_index_offset - self.__header.index_table_address) / 2 * self.__header.data_size
			else:
				buffer_list.append([unicode, self.__placeholder_buffer])
				continue

			font_file.seek(int(char_offset))
			info_data = font_file.read(self.__header.data_size)

			buffer_list.append([unicode, info_data])

		return buffer_list

	def get_characters(self, characters: str):
		with open(self.__font_filename, 'rb') as font_file:
			unicode_set = set()
			for char in characters:
				unicode_set.add(ord(char))

			return self.__get_character_unicode_buffer(font_file, unicode_set)

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
   characters : {}\n'.format(
			  self.__font_filename,
			  self.file_size,
			  self.font_height,
			  self.data_size,
			  self.characters
			))


def is_font_file_exist(font_file):
	try:
		os.stat(font_file)
		return True
	except:
		return False

def run_test():
	font_file = CURRENT_DIR + FONT_DIR + HZK_FILE

	if is_font_file_exist(font_file):
		fontlib = FontLib(font_file)
		fontlib.info()
		buffer_list = fontlib.get_characters('爱我，中华！Hello⒉あβǚㄘＢ⑴■☆')

		if MICROPYTHON:
			from machine import I2C, Pin
			from drivers.ssd1306 import SSD1306_I2C
			import framebuf

			i2c = I2C(0, scl=Pin(18), sda=Pin(19))
			slave_list = i2c.scan()

			if slave_list:
				print('slave id: {}'.format(slave_list[0]))
				oled = SSD1306_I2C(128, 64, i2c)

				buffer = framebuf.FrameBuffer(bytearray(buffer_list[-1][1]), fontlib.font_height, fontlib.font_height, framebuf.MONO_HLSB)
				oled.fill(0)
				oled.blit(buffer, 20, 20)
				oled.show()
		else:
			for buffer in buffer_list:
				character = chr(buffer[0])
				print("'{}' {}\n".format(character, buffer))

			data_size = fontlib.data_size
			font_height = fontlib.font_height
			bytes_per_row = int(data_size / font_height)
			chars_per_row = 8

			for char in range(len(buffer_list) // chars_per_row + 1):
				for row in range(font_height):
					for buffer in buffer_list[char * chars_per_row:char * chars_per_row + chars_per_row]:
						for index in range(bytes_per_row):
							data = buffer[1][row * bytes_per_row + index]
							print('{:08b}'.format(data).replace('0', '.').replace('1', '@'), end='')
						print(' ', end='')
					print('')
				print('')


if __name__ == '__main__':
	run_test()
"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
import os
import gc
import struct
import math


try:
	import framebuf
	MICROPYTHON = True
except ImportError:
	MICROPYTHON = False

CURRENT_DIR = os.getcwd() if MICROPYTHON else os.path.dirname(__file__) + '/'
FONT_DIR = '/client/'


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
	[1] b'\x00'				- scan mode
	[1] b'\x00'				- byte order
	[4] b'$E\x00\x00'		- ascii start address
	[4] b'$Q\x00\x00'		- gb2312 start address
	[2] b'\x00\x00'		- reserved
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
		ascii_list = []
		gb2312_list = []
		chunk_size = 1000

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

		for unicode in unicode_set:
			if self.__is_ascii(unicode):
				char_offset = self.__header.ascii_start + (unicode - 0x20) * self.__header.data_size
				ascii_list.append([unicode, char_offset])
			elif self.__is_gb2312(unicode):
				gb2312_list.append([unicode, struct.pack('<H', unicode), None])
			else:
				buffer_list[unicode] = memoryview(self.__placeholder_buffer)

		for ascii in ascii_list:
			font_file.seek(0)

			for _ in range(0, ascii[1] - font_file.tell() - chunk_size, chunk_size):
				font_file.read(chunk_size)
			font_file.read(ascii[1] - font_file.tell())

			buffer_list[ascii[0]] = memoryview(font_file.read(self.__header.data_size))

		if len(gb2312_list):
			font_file.seek(0)
			font_file.read(self.__header.index_table_address)

			for offset in range(self.__header.index_table_address, self.__header.ascii_start, chunk_size):
				if __seek(offset, font_file.read(chunk_size), gb2312_list):
					break
			else:
				__seek(self.__header.ascii_start - offset, font_file.read(chunk_size), gb2312_list)

		for gb2312 in gb2312_list:
			font_file.seek(0)

			if gb2312[2] is None:
				buffer_list[gb2312[0]] = memoryview(self.__placeholder_buffer)
			else:
				char_offset = int(self.__header.gb2312_start + (gb2312[2] - self.__header.index_table_address) / 2 * self.__header.data_size)

				for _ in range(0, char_offset - font_file.tell() - chunk_size, chunk_size):
					font_file.read(chunk_size)
				font_file.read(char_offset - font_file.tell())

				buffer_list[gb2312[0]] = memoryview(font_file.read(self.__header.data_size))

			gc.collect()

		return buffer_list

	def get_characters(self, characters: str):
		with open(self.__font_filename, 'rb') as font_file:
			unicode_set = set()
			for char in characters:
				unicode_set.add(ord(char))

			gc.collect()
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


def reverseBits(n):
	bits = "{:0>8b}".format(n)
	return int(bits[::-1], 2)

def list_bin_files(root):
	import os

	def list_files(root):
		files=[]
		for dir in os.listdir(root):
			fullpath = ('' if root=='/' else root)+'/'+dir
			if os.stat(fullpath)[0] & 0x4000 != 0:
				files.extend(list_files(fullpath))
			else:
				if dir.endswith('.bin'):
					files.append(fullpath)
		return files

	return list_files(root)

def run_test():
	font_files = list_bin_files(CURRENT_DIR + FONT_DIR)

	if len(font_files) == 0:
		print('No font file founded')
		return
	elif len(font_files) == 1:
		if MICROPYTHON:
			from utime import ticks_diff, ticks_us
			start_time = ticks_us()
		fontlib = FontLib(font_files[0])
		if MICROPYTHON:
			print('### load font file: {} ms'.format(ticks_diff(ticks_us(), start_time) / 1000))
		fontlib.info()
	else:
		print('\nFont file list')
		for index,file in enumerate(font_files, start=1):
			print('    [{}] {}'.format(index, file))
		
		selected=None
		while True:
			try:
				selected=int(input('Choose a file: '))
				print('')
				assert type(selected) is int and 0 < selected <= len(font_files)
				break
			except KeyboardInterrupt:
				break
			except:
				pass

		if selected:
			if MICROPYTHON:
				from utime import ticks_diff, ticks_us
				start_time = ticks_us()
			fontlib = FontLib(font_files[selected - 1])
			if MICROPYTHON:
				print('### load font file: {} ms'.format(ticks_diff(ticks_us(), start_time) / 1000))
			fontlib.info()
		else:
			return

	if MICROPYTHON:
		from machine import I2C, Pin
		from drivers.ssd1306 import SSD1306_I2C
		import framebuf
		from utime import ticks_us, ticks_diff

		i2c = I2C(0, scl=Pin(18), sda=Pin(19))
		slave_list = i2c.scan()

		if slave_list:
			print('slave id: {}'.format(slave_list[0]))
			oled = SSD1306_I2C(128, 64, i2c)

			chars = '使用MicroPython开发板读取自定义字库并显示'
			start_time = ticks_us()
			buffer_list = fontlib.get_characters(chars)
			diff_time = ticks_diff(ticks_us(), start_time) / 1000
			print('###  get {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

			format = framebuf.MONO_VLSB
			if fontlib.scan_mode == FontLib.SCAN_MODE_HORIZONTAL:
				format = framebuf.MONO_HMSB if fontlib.byte_order == FontLib.BYTE_ORDER_MSB else framebuf.MONO_HLSB
			
			def __fill_buffer(buffer, width, height, x, y):
				fb = framebuf.FrameBuffer(bytearray(buffer), width, height, format)
				oled.blit(fb, x, y)

			x = y = 0
			width = height = fontlib.font_height

			start_time = ticks_us()
			for char in chars:
				buffer = memoryview(buffer_list[ord(char)])

				if x > ((128 // width - 1) * width):
					x = 0
					y += height

				__fill_buffer(buffer, width, height, x, y)
				x += width
			oled.show()
			diff_time = ticks_diff(ticks_us(), start_time) / 1000
			print('### show {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))
	else:
		buffer_dict = fontlib.get_characters('\ue900鼽爱我，中华！Hello⒉あβǚㄘＢ⑴■☆')
		buffer_list = []

		for unicode, buffer in buffer_dict.items():
			buffer_list.append([unicode, buffer])
			print("{}: {}\n".format(chr(unicode), bytes(buffer)))

		data_size = fontlib.data_size
		font_height = fontlib.font_height
		bytes_per_row = int(data_size / font_height)
		chars_per_row = 150 // font_height

		if fontlib.scan_mode == FontLib.SCAN_MODE_VERTICAL:
			for char in range(math.ceil(len(buffer_list) / chars_per_row)):
				for count in range(bytes_per_row):
					for col in range(8):
						if count * 8 + col >= font_height: continue
						for buffer in buffer_list[char * chars_per_row:char * chars_per_row + chars_per_row]:
							if len(buffer[1]) < data_size: buffer[1] = bytes(data_size)

							for index in range(count * font_height, count * font_height + font_height):
								data = ''.join(reversed('{:08b}'.format(buffer[1][index])))
								print('{}'.format(data[col].replace('0', '.').replace('1', '@')), end='')
							print(' ', end='')
						print('')
				print('')
		else:
			for char in range(math.ceil(len(buffer_list) / chars_per_row)):
				for row in range(font_height):
					for buffer in buffer_list[char * chars_per_row:char * chars_per_row + chars_per_row]:
						for index in range(bytes_per_row):
							if len(buffer[1]) < data_size: buffer[1] = bytes(data_size)
							data = buffer[1][row * bytes_per_row + index]
							if fontlib.byte_order == FontLib.BYTE_ORDER_MSB:
								data = reverseBits(buffer[1][row * bytes_per_row + index])

							offset = 8 if (index + 1) * 8 < font_height else 8 - ((index + 1) * 8 - font_height)
							print('{:08b}'.format(data)[:offset].replace('0', '.').replace('1', '@'), end='')
						print(' ', end='')
					print('')
				print('')


if __name__ == '__main__':
	run_test()

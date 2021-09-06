"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
from utime import ticks_us, ticks_diff, sleep
import framebuf
from libs.fontlib import FontLib


class FontLibTest1(object):
	'''FontLib 测试单元，用于测试读取字符数据和显示'''
	def __init__(self, oled=None):
		self.__fontlib = None
		self.__buffer_format = None
		self.__oled = oled
		self.__oled_width = None
		self.__oled_height = None

		if self.__oled:
			self.__oled_width = self.__oled.width
			self.__oled_height = self.__oled.height

	def load_font(self, font_file):
		start_time = ticks_us()
		self.__fontlib = FontLib(font_file)
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### load font file: {} ms'.format(diff_time))
		self.__fontlib.info()

		self.__font_width = self.__fontlib.font_height
		self.__font_height = self.__fontlib.font_height
		self.__buffer_format = self.__fontlib.format

	def run_test1(self, chars:str=None):
		'''一次性读取所有字符数据然后逐个显示'''
		if self.__oled is None or chars is None:
			return

		start_time = ticks_us()
		buffer_dict = self.__fontlib.get_characters(chars)
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### get {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

		x = y = 0
		width = height = self.__fontlib.font_height

		start_time = ticks_us()
		for char in chars:
			if ord(char) == 10:
				x = 0
				y += height
				continue

			buffer = memoryview(buffer_dict[ord(char)])

			if x > ((self.__oled_width // width - 1) * width):
				x = 0
				y += height
			
			if y > ((self.__oled_height // height - 1) * height):
				x = 0
				y = 0
				sleep(1.5)
				self.__oled.fill(0)

			self.__fill_buffer(buffer, x, y, self.__buffer_format)
			self.__oled.show()
			x += width
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### show {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

	def run_test2(self, chars:str=None):
		'''一次性读取所有字符数据，每次显示一屏'''
		if self.__oled is None or chars is None:
			return

		start_time = ticks_us()
		buffer_dict = self.__fontlib.get_characters(chars)
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('###  get {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

		x = y = 0
		width = height = self.__fontlib.font_height

		start_time = ticks_us()
		for char in chars:
			if ord(char) == 10:
				x = 0
				y += height
				continue

			buffer = memoryview(buffer_dict[ord(char)])

			if x > ((self.__oled_width // width - 1) * width):
				x = 0
				y += height
			
			if y > ((self.__oled_height // height - 1) * height):
				self.__oled.show()
				self.__oled.fill(0)
				sleep(3)
				x = y = 0

			self.__fill_buffer(buffer, x, y, self.__buffer_format)
			x += width

		self.__oled.show()

		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### show {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

	def run_test3(self, chars:str=None):
		'''每次读取一个字符数据并显示'''
		if self.__oled is None or chars is None:
			return

		x = y = 0
		width = height = self.__fontlib.font_height

		start_time = ticks_us()
		for char in chars:
			buffer_dict = self.__fontlib.get_characters(char)

			if ord(char) == 10:
				x = 0
				y += height
				continue

			buffer = memoryview(buffer_dict[ord(char)])

			if x > ((self.__oled_width // width - 1) * width):
				x = 0
				y += height

			if y > ((self.__oled_height // height - 1) * height):
				x = 0
				y = 0
				sleep(1.5)
				self.__oled.fill(0)
 
			self.__fill_buffer(buffer, x, y, self.__buffer_format)
			self.__oled.show()
			x += width
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### show {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

	def __fill_buffer(self, buffer, x, y, format):
		if isinstance(buffer, (bytes, memoryview)):
			buffer = framebuf.FrameBuffer(bytearray(buffer), self.__font_width, self.__font_height, format)
		self.__oled.blit(buffer, x, y)

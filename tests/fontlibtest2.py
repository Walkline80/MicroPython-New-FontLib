"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
import framebuf
from libs.fontlib import FontLib


class FontLibTest2(object):
	'''FontLib 测试单元，用于测试读取图标字库数据和显示'''
	def __init__(self, oled=None):
		self.__oled = oled
		self.__oled_width = None
		self.__oled_height = None

		if self.__oled:
			self.__oled_width = self.__oled.width
			self.__oled_height = self.__oled.height

	def run_test(self):
		if self.__oled is None:
			return

		welcome = FontLib('/client/welcome.bin')
		iconic = FontLib('/client/fonts/open-iconic.bin')
		welcome.info()
		iconic.info()

		welcome_buffer_dict = welcome.get_characters('欢迎')
		iconic_buffer_dict = iconic.get_characters('\ue056\ue057')

		width = height = welcome.font_height
		x = int((self.__oled_width - width * 4) / 2)
		y = int((self.__oled_height - height) / 2)

		buffer_list = [
			memoryview(iconic_buffer_dict[ord('\ue056')]),
			memoryview(welcome_buffer_dict[ord('欢')]),
			memoryview(welcome_buffer_dict[ord('迎')]),
			memoryview(iconic_buffer_dict[ord('\ue057')])
		]

		for buffer in buffer_list:
			self.__fill_buffer(buffer, width, height, x, y, welcome.format)
			x += width

		self.__oled.show()

	def __fill_buffer(self, buffer, width, height, x, y, format):
		if isinstance(buffer, (bytes, memoryview)):
			buffer = framebuf.FrameBuffer(bytearray(buffer), width, height, format)
		self.__oled.blit(buffer, x, y)

"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
from utime import ticks_us, ticks_diff, sleep
from machine import I2C, Pin
from drivers.ssd1306 import SSD1306_I2C
import framebuf
from libs.fontlib import FontLib


class FontLibTest(object):
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
		print('### load font file: {} ms'.format(ticks_diff(ticks_us(), start_time) / 1000))
		self.__fontlib.info()
		self.__buffer_format = self.__get_format()

	def run_test1(self, chars=None):
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

			buffer = buffer_dict[ord(char)]

			if x > ((self.__oled_width // width - 1) * width):
				x = 0
				y += height
			
			if y > ((self.__oled_height // height - 1) * height):
				x = 0
				y = 0
				sleep(1.5)
				self.__oled.fill(0)
				self.__oled.show()

			self.__show(buffer, width, height, x, y, self.__buffer_format)
			x += width
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### show {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

	def run_test2(self, chars=None):
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

			buffer = buffer_dict[ord(char)]

			if x > ((self.__oled_width // width - 1) * width):
				x = 0
				y += height

			if y > ((self.__oled_height // height - 1) * height):
				x = 0
				y = 0
				sleep(1.5)
				self.__oled.fill(0)
				self.__oled.show()
 
			self.__show(buffer, width, height, x, y, self.__buffer_format)
			x += width
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### show {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

	def run_test3(self, chars=None):
		if self.__oled is None or chars is None:
			return

		start_time = ticks_us()
		buffer_dict = self.__fontlib.get_characters(chars)
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### get {} chars: {} ms, avg: {} ms'.format(len(chars), diff_time, diff_time / len(chars)))

		x = y = 0
		width = height = self.__fontlib.font_height

		for char in chars:
			if ord(char) == 10:
				x = 0
				y += height
				continue

			buffer = buffer_dict[ord(char)]

			if x > ((self.__oled_width // width - 1) * width):
				x = 0
				y += height
			
			if y > ((self.__oled_height // height - 1) * height):
				self.__oled.show()
				sleep(3)
				self.__oled.fill(0)
				self.__oled.show()
				x = y = 0

			self.__show(buffer, width, height, x, y, self.__buffer_format, False)
			x += width

		self.__oled.show()

	def __get_format(self):
		format = framebuf.MONO_VLSB

		if self.__fontlib.scan_mode == FontLib.SCAN_MODE_HORIZONTAL:
			format = framebuf.MONO_HMSB if self.__fontlib.byte_order == FontLib.BYTE_ORDER_MSB else framebuf.MONO_HLSB

		return format

	def __show(self, buffer, width, height, x, y, format, show=True):
		fb = framebuf.FrameBuffer(bytearray(buffer), width, height, format)
		oled.blit(fb, x, y)
		if show: oled.show()


chars =\
'''　　问题，到底应该如何实现。
　　既然如此，我们都知道，只要有意义，那么就必须慎重考虑。
　　现在，解决问题的问题，是非常非常重要的。
　　所以，在这种困难的抉择下，本人思来想去，寝食难安。
　　要想清楚，问题，到底是一种怎么样的存在。
　　一般来说，生活中，若问题出现了，我们就不得不考虑它出现了的事实。
　　维龙曾经说过，要成功不需要什么特别的才能，只要把你能做的小事做得好就行了。
　　这似乎解答了我的疑惑。
　　这种事实对本人来说意义重大，相信对这个世界也是有一定意义的。
'''
chars2 = '几凡也习丰井无勿正轧占田它地因网乔乒仿次军她巡寿找批走抗扭估体伯饮即妙到贤忠咏使周兔泡陕'


if __name__ == '__main__':
	i2c = I2C(0, scl=Pin(18), sda=Pin(19))
	slave_list = i2c.scan()

	if slave_list:
		oled = SSD1306_I2C(128, 64, i2c)

		runner = FontLibTest(oled)
		runner.load_font('client/combined.bin')

		runner.run_test1(chars) # 一次性读取所有字符数据然后逐个显示
		# runner.run_test2(chars) # 一次读取并显示一个字符数据
		# runner.run_test3(chars) # 一次读取一屏并显示

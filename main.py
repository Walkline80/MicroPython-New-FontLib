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

		self.__font_width = self.__fontlib.font_height
		self.__font_height = self.__fontlib.font_height
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

	def run_test3(self, chars=None):
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

	def run_test4(self, chars=None):
		if self.__oled is None or chars is None:
			return

		from math import ceil
		chars = chars.replace('\t', '')
		newline_count = chars.count('\n')
		chars_count = len(chars)
		chars_per_row = int(self.__oled_width / self.__fontlib.font_height)
		chars_per_col = int(self.__oled_height / self.__fontlib.font_height)
		total_rows = ceil(chars_count / chars_per_row) + newline_count
		total_pages = ceil(total_rows / chars_per_col)
		x = y = 0
		width = height = self.__fontlib.font_height
		buffer_size = self.__oled_width // 8 * self.__oled_height
		fb_foreground = framebuf.FrameBuffer(bytearray(buffer_size))
		fb_background = framebuf.FrameBuffer(bytearray(buffer_size))

		def __fill_page(fb):
			pass
		return

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

	def __get_format(self):
		format = framebuf.MONO_VLSB

		if self.__fontlib.scan_mode == FontLib.SCAN_MODE_HORIZONTAL:
			format = framebuf.MONO_HMSB if self.__fontlib.byte_order == FontLib.BYTE_ORDER_MSB else framebuf.MONO_HLSB

		return format

	def __fill_buffer(self, buffer, x, y, format):
		if isinstance(buffer, (bytes, memoryview)):
			buffer = framebuf.FrameBuffer(bytearray(buffer), self.__font_width, self.__font_height, format)
		oled.blit(buffer, x, y)


class FontLibTest2(object):
	def __init__(self, oled=None):
		self.__oled = oled
		self.__oled_width = None
		self.__oled_height = None

		if self.__oled:
			self.__oled_width = self.__oled.width
			self.__oled_height = self.__oled.height

	def run_test(self):
		if self.__oled is None or chars is None:
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
			self.__fill_buffer(buffer, width, height, x, y, framebuf.MONO_VLSB)
			x += width

		self.__oled.show()

	def __fill_buffer(self, buffer, width, height, x, y, format):
		if isinstance(buffer, (bytes, memoryview)):
			buffer = framebuf.FrameBuffer(bytearray(buffer), width, height, format)
		oled.blit(buffer, x, y)


chars =\
'''　　清晨4:50，老刀穿过熙熙攘攘的步行街，去找彭蠡。
　　从垃圾站下班之后，老刀回家洗了个澡，换了衣服。白色衬衫和褐色裤子，这是他唯一一套体面衣服，衬衫袖口磨了边，他把袖子卷到胳膊肘。老刀四十八岁，没结婚，已经过了注意外表的年龄，又没人照顾起居，这一套衣服留着穿了很多年，每次穿一天，回家就脱了叠上。他在垃圾站上班，没必要穿得体面，偶尔参加谁家小孩的婚礼，才拿出来穿在身上。这一次他不想脏兮兮地见陌生人。他在垃圾站连续工作了五小时，很担心身上会有味道。'''

chars2 =\
'''　　问题，到底应该如何实现。
　　既然如此，我们都知道，只要有意义，那么就必须慎重考虑。
　　现在，解决问题的问题，是非常非常重要的。
　　所以，在这种困难的抉择下，本人思来想去，寝食难安。
　　要想清楚，问题，到底是一种怎么样的存在。
　　一般来说，生活中，若问题出现了，我们就不得不考虑它出现了的事实。
　　维龙曾经说过，要成功不需要什么特别的才能，只要把你能做的小事做得好就行了。
　　这似乎解答了我的疑惑。
　　这种事实对本人来说意义重大，相信对这个世界也是有一定意义的。'''


if __name__ == '__main__':
	i2c = I2C(0, scl=Pin(18), sda=Pin(19))
	slave_list = i2c.scan()

	if slave_list:
		oled = SSD1306_I2C(128, 64, i2c)

		runner = FontLibTest(oled)
		runner.load_font('client/combined.bin')
		# runner.load_font('client/customize.bin')
		# runner.load_font('client/combined_hmsb.bin')
		# runner.load_font('client/customize_hmsb.bin')
		# runner.load_font('client/combined_vlsb.bin')

		# runner.run_test1(chars) # 一次性读取所有字符数据然后逐个显示
		# runner.run_test2(chars) # 一次读取并显示一个字符数据
		# runner.run_test3(chars) # 一次读取一屏并显示
		runner.run_test4(chars2)


		# 要测试 FontLibTest2 的代码，需要生成一个新字库
		#
		# $ cd client
		# $ echo 欢迎>> input.txt
		# $ FontMaker_Cli.exe -f 幼圆 --input input.txt -o welcome.bin
		#
		# 将生成的字库和 fonts/open-iconic.bin 一起上传到开发板
		# runner = FontLibTest2(oled)
		# runner.run_test()

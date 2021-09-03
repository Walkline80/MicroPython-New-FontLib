"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
from utime import ticks_us, ticks_diff, sleep
from machine import I2C, Pin, Timer
from drivers.ssd1306 import SSD1306_I2C
import framebuf
from libs.fontlib import FontLib
import gc
import _thread


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
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		print('### load font file: {} ms'.format(diff_time))
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

	def __get_format(self):
		format = framebuf.MONO_VLSB

		if self.__fontlib.scan_mode == FontLib.SCAN_MODE_HORIZONTAL:
			format = framebuf.MONO_HMSB if self.__fontlib.byte_order == FontLib.BYTE_ORDER_MSB else framebuf.MONO_HLSB

		return format

	def __fill_buffer(self, buffer, x, y, format):
		if isinstance(buffer, (bytes, memoryview)):
			buffer = framebuf.FrameBuffer(bytearray(buffer), self.__font_width, self.__font_height, format)
		self.__oled.blit(buffer, x, y)


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


class FontLibTest3(object):
	def __init__(self, oled=None):
		self.__oled = oled
		self.__oled_width = None
		self.__oled_height = None

		if self.__oled:
			self.__oled_width = self.__oled.width
			self.__oled_height = self.__oled.height

	def load_font(self, font_file):
		self.__fontlib = FontLib(font_file)
		self.__fontlib.info()

		self.__font_width = self.__fontlib.font_height
		self.__font_height = self.__fontlib.font_height

	def run_test(self, scroll_height=1, interval=20, chars=None, load_all=False, thread=False):
		if self.__oled is None or chars is None:
			return

		self.__scroll_speed = scroll_height
		self.__scroll_interval = interval
		self.__chars = chars.replace('\t', '').replace('\r\n', '\n')
		self.__load_all = load_all
		self.__thread = thread

		self.__setup()
		self.__fill_page(2, True)

		self.__oled.blit(self.__fb_foreground, 0, 0)
		self.__oled.show()

		self.__page_prepared = True
		if self.__thread:
			self.__need_next_page = True
			_thread.start_new_thread(self.__fill_page_thread, ())
		else:
			self.__fill_page()

		sleep(1)

		if self.__thread:
			_thread.start_new_thread(self.__scroll_thread, ())
		else:
			self.__scroll_timer.init(
				mode=Timer.PERIODIC,
				period=self.__scroll_interval,
				callback=self.__scroll_cb
			)

	def __setup(self):
		self.__chars_per_row = int(self.__oled_width / self.__fontlib.font_height)
		self.__chars_per_col = int(self.__oled_height / self.__fontlib.font_height)
		self.__chars_per_page = self.__chars_per_row * self.__chars_per_col

		self.__total_rows = int(len(self.__chars) / self.__chars_per_row) + self.__chars.count('\n')
		self.__total_pages = int(self.__total_rows / self.__chars_per_col)

		self.__buffer_size = self.__oled_width // 8 * self.__oled_height
		self.__fb_foreground = framebuf.FrameBuffer(bytearray(self.__buffer_size * 2), self.__oled_width, self.__oled_height * 2, framebuf.MONO_VLSB)
		self.__fb_background = framebuf.FrameBuffer(bytearray(self.__buffer_size), self.__oled_width, self.__oled_height, framebuf.MONO_VLSB)
		# self.__fb_temp = framebuf.FrameBuffer(bytearray(self.__buffer_size), self.__oled_width, self.__oled_height, framebuf.MONO_VLSB)

		self.__scroll_timer = Timer(1)
		self.__buffer_dict = self.__fontlib.get_characters(self.__chars) if self.__load_all else {}

		self.__need_next_page = False
		self.__page_prepared = False
		self.__current_page = 0
		self.__x = self.__y = 0
		self.__current_char_index = 0

	def __fill_buffer(self, buffer):
		return framebuf.FrameBuffer(bytearray(buffer), self.__font_width, self.__font_height, framebuf.MONO_VLSB)

	def __fill_page(self, num=1, first=False):
		x = y = 0
		while num:
			col = 0
			current_page_chars = self.__chars[self.__current_char_index:self.__current_char_index + self.__chars_per_page]

			if not self.__load_all:
				self.__buffer_dict = self.__fontlib.get_characters(current_page_chars)

			self.__fb_background.fill(0)

			for char in current_page_chars:
				if ord(char) == 10:
					x = 0
					y += self.__font_height
					col += 1
					self.__current_char_index += 1
					continue

				if x > ((self.__oled_width // self.__font_width - 1) * self.__font_width):
					x = 0
					y += self.__font_height
					col += 1

				if col >= self.__chars_per_col:
					break

				# print(char, end='')

				buffer = self.__fill_buffer(memoryview(self.__buffer_dict[ord(char)]))
				self.__fb_foreground.blit(buffer, x, y) if first else self.__fb_background.blit(buffer, x, y)
				x += self.__font_width
				self.__current_char_index += 1

			num -= 1
			self.__current_page += 1
		self.__page_prepared = True

	def __scroll_cb(self, timer):
		if self.__current_page > self.__total_pages:
			self.__scroll_timer.deinit()
			return

		if self.__y >= self.__oled_height:
			if not self.__page_prepared:
				return

			self.__fb_foreground.blit(self.__fb_background, 0, self.__oled_height)
			# print('page ', self.__current_page, ' used')

			self.__page_prepared = False
			self.__fill_page()
			self.__x = self.__y = 0

		self.__fb_foreground.scroll(0, self.__scroll_speed * -1)
		self.__oled.blit(self.__fb_foreground, 0, 0)
		self.__oled.show()
		self.__y += self.__scroll_speed

	def __scroll_thread(self):
		while self.__current_page <= self.__total_pages:
			if self.__y >= self.__oled_height:
				if not self.__page_prepared:
					return

				self.__fb_foreground.blit(self.__fb_background, 0, self.__oled_height)
				# print('page ', self.__current_page, ' used')

				self.__page_prepared = False
				self.__need_next_page = True
				self.__x = self.__y = 0
				self.__current_page += 1

			self.__fb_foreground.scroll(0, self.__scroll_speed * -1)
			self.__oled.blit(self.__fb_foreground, 0, 0)
			self.__oled.show()
			self.__y += self.__scroll_speed

			sleep(self.__scroll_interval / 1000)

	def __fill_page_thread(self):
		while self.__current_page < self.__total_pages:
			if self.__need_next_page:
				# print('filling page ', self.__current_page)
				col = x = y = 0
				current_page_chars = self.__chars[self.__current_char_index:self.__current_char_index + self.__chars_per_page]

				if not self.__load_all:
					self.__buffer_dict = self.__fontlib.get_characters(current_page_chars)

				self.__fb_background.fill(0)

				for char in current_page_chars:
					if ord(char) == 10:
						x = 0
						y += self.__font_height
						col += 1
						self.__current_char_index += 1
						continue

					if x > ((self.__oled_width // self.__font_width - 1) * self.__font_width):
						x = 0
						y += self.__font_height
						col += 1

					if col >= self.__chars_per_col:
						break

					# print(char, end='')

					buffer = self.__fill_buffer(memoryview(self.__buffer_dict[ord(char)]))
					self.__fb_background.blit(buffer, x, y)
					x += self.__font_width
					self.__current_char_index += 1

				# print('\npage: ', self.__current_page, ' filled')
				self.__page_prepared = True
				self.__need_next_page = False

		print('thread exit')


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

chars3 =\
'''出师表
　　先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。然侍卫之臣不懈于内，忠志之士忘身于外者，盖追先帝之殊遇，欲报之于陛下也。诚宜开张圣听，以光先帝遗德，恢弘志士之气，不宜妄自菲薄，引喻失义，以塞忠谏之路也。
　　宫中府中，俱为一体；陟罚臧否，不宜异同：若有作奸犯科及为忠善者，宜付有司论其刑赏，以昭陛下平明之理；不宜偏私，使内外异法也。
　　侍中、侍郎郭攸之、费祎、董允等，此皆良实，志虑忠纯，是以先帝简拔以遗陛下：愚以为宫中之事，事无大小，悉以咨之，然后施行，必能裨补阙漏，有所广益。
　　将军向宠，性行淑均，晓畅军事，试用于昔日，先帝称之曰“能”，是以众议举宠为督：愚以为营中之事，悉以咨之，必能使行阵和睦，优劣得所。
　　亲贤臣，远小人，此先汉所以兴隆也；亲小人，远贤臣，此后汉所以倾颓也。先帝在时，每与臣论此事，未尝不叹息痛恨于桓、灵也。侍中、尚书、长史、参军，此悉贞良死节之臣，愿陛下亲之信之，则汉室之隆，可计日而待也。
　　臣本布衣，躬耕于南阳，苟全性命于乱世，不求闻达于诸侯。先帝不以臣卑鄙，猥自枉屈，三顾臣于草庐之中，咨臣以当世之事，由是感激，遂许先帝以驱驰。后值倾覆，受任于败军之际，奉命于危难之间：尔来二十有一年矣。先帝知臣谨慎，故临崩寄臣以大事也。受命以来，夙夜忧叹，恐托付不效，以伤先帝之明；故五月渡泸，深入不毛。今南方已定，兵甲已足，当奖率三军，北定中原，庶竭驽钝，攘除奸凶，兴复汉室，还于旧都。此臣所以报先帝而忠陛下之职分也。至于斟酌损益，进尽忠言，则攸之、祎、允之任也。
　　愿陛下托臣以讨贼兴复之效，不效，则治臣之罪，以告先帝之灵。若无兴德之言，则责攸之、祎、允等之慢，以彰其咎；陛下亦宜自谋，以咨诹善道，察纳雅言，深追先帝遗诏。臣不胜受恩感激。今当远离，临表涕零，不知所言。'''


if __name__ == '__main__':
	i2c = I2C(0, scl=Pin(18), sda=Pin(19))
	slave_list = i2c.scan()

	if slave_list:
		oled = SSD1306_I2C(128, 64, i2c)

		# runner = FontLibTest(oled)
		# runner.load_font('client/combined.bin')
		# runner.load_font('client/customize.bin')
		# runner.load_font('client/combined_hmsb.bin')
		# runner.load_font('client/customize_hmsb.bin')
		# runner.load_font('client/combined_vlsb.bin')

		# runner.run_test1(chars) # 一次性读取所有字符数据然后逐个显示
		# runner.run_test2(chars) # 一次读取并显示一个字符数据
		# runner.run_test3(chars) # 一次读取一屏并显示


		# 要测试 FontLibTest2 的代码，需要生成一个新字库
		#
		# $ cd client
		# $ echo 欢迎>> input.txt
		# $ FontMaker_Cli.exe -f 幼圆 --input input.txt -o welcome.bin
		#
		# 将生成的字库和 fonts/open-iconic.bin 一起上传到开发板
		# runner = FontLibTest2(oled)
		# runner.run_test()


		runner = FontLibTest3(oled)
		runner.load_font('client/wenqy_chushibiao.bin')
		runner.run_test(scroll_height=1, interval=40, chars=chars3, thread=True) # 每次滚动 1 像素

		# 读取所有字符数据，每次滚动 1 像素
		# runner = FontLibTest3(oled)
		# runner.load_font('client/combined_vlsb.bin')
		# runner.run_test(1, 20, chars2, True)

	gc.collect()

"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
from utime import sleep
import framebuf
from libs.fontlib import FontLib
import uasyncio as asyncio


class FontLibTest4(object):
	'''FontLib 测试单元，用 协程 方式测试滚动显示长文'''
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
		self.__buffer_format = self.__fontlib.format

	def run_test(self, scroll_height:int=1, interval:int=20, chars:str=None):
		if self.__oled is None or chars is None:
			return

		self.__scroll_speed = scroll_height
		self.__scroll_interval = interval
		self.__chars = chars.replace('\t', '').replace('\r\n', '\n')

		self.__loop = asyncio.get_event_loop()
		self.__setup()
		self.__fill_page()

		self.__oled.blit(self.__fb_foreground, 0, 0)
		self.__oled.show()

		sleep(1)

		self.__page_prepared = True
		self.__need_next_page = True

		self.__loop.create_task(self.__scroll_thread())
		self.__loop.create_task(self.__fill_page_thread())
		self.__loop.run_forever()

	def __setup(self):
		self.__chars_per_row = int(self.__oled_width / self.__fontlib.font_height)
		self.__chars_per_col = int(self.__oled_height / self.__fontlib.font_height)
		self.__chars_per_page = self.__chars_per_row * self.__chars_per_col

		self.__total_rows = int(len(self.__chars) / self.__chars_per_row) + self.__chars.count('\n')
		self.__total_pages = int(self.__total_rows / self.__chars_per_col)

		self.__buffer_size = self.__oled_width // 8 * self.__oled_height
		self.__fb_foreground = framebuf.FrameBuffer(bytearray(self.__buffer_size * 2), self.__oled_width, self.__oled_height * 2, self.__buffer_format)
		self.__fb_background = framebuf.FrameBuffer(bytearray(self.__buffer_size), self.__oled_width, self.__oled_height, self.__buffer_format)

		self.__buffer_dict = {}
		self.__need_next_page = False
		self.__page_prepared = False
		self.__current_page = 0
		self.__x = self.__y = 0
		self.__current_char_index = 0

	def __fill_buffer(self, buffer):
		return framebuf.FrameBuffer(bytearray(buffer), self.__font_width, self.__font_height, self.__buffer_format)

	def __fill_page(self, num:int=2):
		x = y = 0
		while num:
			col = 0
			current_page_chars = self.__chars[self.__current_char_index:self.__current_char_index + self.__chars_per_page]

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
				self.__fb_foreground.blit(buffer, x, y)
				x += self.__font_width
				self.__current_char_index += 1

			num -= 1
			self.__current_page += 1
		self.__page_prepared = True

	async def __scroll_thread(self):
		while self.__current_page <= self.__total_pages:
			if self.__y >= self.__oled_height:
				if not self.__page_prepared:
					continue

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
			await asyncio.sleep_ms(20)

		self.__loop.stop()
		print('loop scroll exit')

	async def __fill_page_thread(self):
		while self.__current_page < self.__total_pages:
			if self.__need_next_page:
				# print('filling page ', self.__current_page)
				col = x = y = 0
				current_page_chars = self.__chars[self.__current_char_index:self.__current_char_index + self.__chars_per_page]

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
				await asyncio.sleep_ms(10)

			await asyncio.sleep_ms(10)
		self.__page_prepared = True
		print('loop fill page exit')

'''
\x00\x00 ................
\x00\x00 ................
\x00\x00 ................
\x10\x00 ...#............
\x10\x00 ...#............
\x10\x00 ...#............
\x10\x00 ...#............
\x10\x00 ...#............

\x10\x00 ...#............
\x10\x00 ...#............
\x00\x00 ................
\x00\x00 ................
\x18\x00 ...##...........
\x18\x00 ...##...........
\x00\x00 ................
\x00\x00 ................
'''

'''
\x00
\x00
\x00
\xf8
\x00
\x00
\x00
\x00
\x00
\x00
\x00
\x00
\x00
\x00
\x00
\x00

\x00\x00\x0030\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
'''

'''
vlsb
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0xF8,0x33, 00110011 11111000
0x00,0x30, 00110000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
0x00,0x00, 00000000 00000000
'''

from struct import unpack

# buffer_list = [[33, b'\x32\x44\x13\xFc\x10\x48\x13\xB8\x19\x10\x10\xA0\x10\xE0\x03\x1E\x0C\x00\x00\x00\x00\x00\x0c\x40\x7B\xFC\x4A\x48\x52\x48\x55\xF0']]
# buffer_list = [[33, b'\x00\x00\x00\x00\x00\x00\xF8\x33\x00\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']]
buffer_list = [[33, b'\x00\x00\x00\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0030\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']]
data_size = 32
font_height = 16
bytes_per_row = int(data_size / font_height)
chars_per_row = 6

for char in range(len(buffer_list) // chars_per_row + 1):
	for row in range(font_height):
		for buffer in buffer_list[char * chars_per_row:char * chars_per_row + chars_per_row]:
			for index in range(bytes_per_row):
				data = buffer[1][row * bytes_per_row + index]
				print('{:08b}'.format(data).replace('0', '.').replace('1', '@'), end='')
			print(' ', end='')
		print('')
	print('')

# for row in range(font_height):
# 	for buffer in buffer_list:
# 		for index in range(bytes_per_row):
# 			data = buffer[1][row * bytes_per_row + index]
# 			print('{:08b}'.format(data).replace('0', '.').replace('1', '@'), end='')
# 		print(' ', end='')
# 	print('')





def main():
	from machine import I2C, Pin
	from drivers.ssd1306 import SSD1306_I2C
	import framebuf

	global oled

	i2c = I2C(0, scl=Pin(18), sda=Pin(19))
	slave_list = i2c.scan()

	if slave_list:
		print('slave id: {}'.format(slave_list[0]))
		oled = SSD1306_I2C(128, 64, i2c)

		char = bytearray( b'\x00\x00\x00\x00?\xf8\x11\x10\t\x10?\xfcD\x02B\x02\x1f\xf8\x04\x00\x07\xf8\x0e\x08\x13\x10 \xe0\x01\xe0\x1e\x1e')
		buffer = framebuf.FrameBuffer(char, 16, 16, framebuf.MONO_HLSB)
		oled.fill(0)
		oled.blit(buffer, 20, 20)
		oled.show()

if __name__ == "__main__":
	pass
	# main()

from fontlib import FontLib

fontlib = FontLib('combined.bin')
data_size = fontlib.data_size
font_height = fontlib.font_height
bytes_per_row = int(data_size / font_height)
#buffer = b'\x00\x80\x40\x48\x50\x40\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x11\x11\x11\x11\x0f\x10\x00\x00\x00\x00\x00\x00\x00\x00'
#buffer = b'\x00\x00\x00\x00\x00\x00\x10\x00\x08\x00\x00\x00\x3c\x00\x42\x00\x3e\x00\x42\x00\x42\x00\x42\x00\x3d\x00\x00\x00\x00\x00\x00\x00'
#print(len(buffer))

def reverseBits(n):
	bits = "{:0>8b}".format(n)
	return int(bits[::-1], 2)
import math
buffer_dict = fontlib.get_characters('\ue000\ue001\ue002\ue003\ue004\ue005\ue006\ue007')
buffer_list = []

for unicode, buffer in buffer_dict.items():
	buffer_list.append([unicode, buffer])
	print("{}: {}\n".format(chr(unicode), buffer))

for char in range(math.ceil(len(buffer_list) / chars_per_row)):
	for row in range(font_height):
		#for buffer in buffer_list[char * chars_per_row:char * chars_per_row + chars_per_row]:
		for index in range(bytes_per_row):
			#if len(buffer[1]) < data_size: buffer[1] = bytes(data_size)
			data = buffer[row * bytes_per_row + index]
			#data = reverseBits(buffer[1][row * bytes_per_row + index])

			offset = 8 if (index + 1) * 8 < font_height else 8 - ((index + 1) * 8 - font_height)
			print('{:08b}'.format(data)[:offset].replace('0', '.').replace('1', '@'), end='')
		print('')
print('')
"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
import uasyncio as asyncio
from utime import sleep_ms


loop = None
# filename = 'client/combined_vlsb.bin'
filename = '北京折叠.txt'
fontfile = None
data = None
output_done = True

async def read():
	global loop, fontfile, data, output_done

	while True:
		while output_done:
			data = fontfile.readline()

			if not data:
				fontfile.close()
				loop.stop()
				return

			output_done = False

		await asyncio.sleep_ms(1)

async def output():
	global loop, data, output_done

	while True:
		if data and not output_done:
# 			for char in data:
# 				print(char, end='')
				# sleep_ms(200)
# 			print('')
			print(data)
			asyncio.sleep_ms(1000)

			output_done = True

		await asyncio.sleep_ms(10)


fontfile = open(filename, 'r', encoding='utf-8')
loop = asyncio.get_event_loop()
loop.create_task(read())
loop.create_task(output())
loop.run_forever()

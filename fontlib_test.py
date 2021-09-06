"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
from libs.fontlib import FontLib
from utime import ticks_diff, ticks_us


fontlib = None

chars =\
'''　　问题，到底应该如何实现。
　　既然如此，我们都知道，只要有意义，那么就必须慎重考虑。
　　现在，解决问题的问题，是非常非常重要的。
　　所以，在这种困难的抉择下，本人思来想去，寝食难安。
　　要想清楚，问题，到底是一种怎么样的存在。
　　一般来说，生活中，若问题出现了，我们就不得不考虑它出现了的事实。
　　维龙曾经说过，要成功不需要什么特别的才能，只要把你能做的小事做得好就行了。
　　这似乎解答了我的疑惑。
　　这种事实对本人来说意义重大，相信对这个世界也是有一定意义的。'''

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

def choose_a_file(file_list):
	print('\nFile list')
	for index,file in enumerate(file_list, start=1):
		print('    [{}] {}'.format(index, file))
	
	selected=None
	while True:
		try:
			selected=int(input('Choose a file: '))
			print('')
			assert type(selected) is int and 0 < selected <= len(file_list)
			break
		except KeyboardInterrupt:
			break
		except:
			pass

	if selected:
		return selected
	else:
		return


if __name__ == '__main__':
	font_files = list_bin_files('/')
	if not len(font_files): print('no font file found')

	selected = choose_a_file(font_files)
	if not selected: exit(1)

	start_time = ticks_us()
	fontlib = FontLib(font_files[selected - 1])
	print('### load font file: {} ms'.format(ticks_diff(ticks_us(), start_time) / 1000))
	fontlib.info()

	start_time = ticks_us()
	buffer_list = fontlib.get_characters(chars)
	diff_time = ticks_diff(ticks_us(), start_time) / 1000
	print('\n### method: load all')
	print('### {} chars, get {} chars: {} ms, avg: {} ms'.format(len(chars), len(buffer_list), diff_time, diff_time / len(buffer_list)))

	print('\n### method separated')
	chunk = 24
	char_count = time_count = avg_count = 0
	for count in range(0, len(chars) // chunk + 1):
		sep_chars = chars[count * chunk:count * chunk + chunk]

		start_time = ticks_us()
		buffer_list = fontlib.get_characters(sep_chars)
		diff_time = ticks_diff(ticks_us(), start_time) / 1000
		if not buffer_list: continue
		
		avg_time = diff_time / len(buffer_list)

		char_count += len(buffer_list)
		avg_count += avg_time
		time_count += diff_time
		print('### {} get {} chars: {} ms, avg: {} ms'.format(count, len(buffer_list), diff_time, avg_time))

	print('### {} chars, get {} chars: {} ms, avg: {} ms'.format(len(chars), char_count, time_count, avg_count / (count-1)))

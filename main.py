"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
Gitee: https://gitee.com/walkline/micropython-new-fontlib
"""
from machine import I2C, Pin
from drivers.ssd1306 import SSD1306_I2C
import gc


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

def choose_a_font(file_list):
	print('\nFont File List')
	for index,file in enumerate(file_list, start=1):
		print('  [{}] {}'.format(index, file))
	
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
	i2c = I2C(0, scl=Pin(18), sda=Pin(19))
	slave_list = i2c.scan()

	if not slave_list:
		oled = SSD1306_I2C(128, 64, i2c)

		font_files = list_bin_files('/')
		if len(font_files) == 0:
			print('no font file found')
			exit(1)

		selected = choose_a_font(font_files)
		if not selected: exit(1)
		fontfile = font_files[selected - 1]

		tests = [
			'Test1_test1: 一次性读取所有字符数据然后逐个显示',
			'Test1_test2: 一次性读取所有字符数据然后逐屏显示',
			'Test1_test3: 每次读取并显示一个字符数据',
			'Test2: 读取图标字库数据并显示',
			'Test3_test1: 多线程方式，每次读取一屏字符数据，每次滚动 1 像素',
			'Test3_test2: 定时器方式，读取所有字符数据，每次滚动 1 像素'
		]

		print('Test List')
		for index, test in enumerate(tests, start=1):
			print('  [{}] {}'.format(index, test))

		selected=None
		while True:
			try:
				selected=int(input('Choose a test: '))
				assert type(selected) is int and 0 < selected <= len(tests)
				break
			except KeyboardInterrupt:
				break
			except:
				pass

		runner = None
		if selected:
			if selected in [1, 2, 3]:
				from tests.fontlibtest1 import FontLibTest1
				runner = FontLibTest1(oled)
			elif selected in [5, 6]:
				from tests.fontlibtest3 import FontLibTest3
				runner = FontLibTest3(oled)

			if selected == 1:
				# 一次性读取所有字符数据然后逐个显示
				runner.load_font(fontfile)
				runner.run_test1(chars)
			elif selected == 2:
				# 一次读取一屏并显示
				runner.load_font(fontfile)
				runner.run_test2(chars)
			elif selected == 3:
				# 一次读取并显示一个字符数据
				runner.load_font(fontfile)
				runner.run_test2(chars)
			elif selected == 4:
				# 要测试 FontLibTest2 的代码，需要生成一个新字库
				#
				# $ cd client
				# $ echo 欢迎>> input.txt
				# $ FontMaker_Cli.exe -f 幼圆 --input input.txt -o welcome.bin
				#
				# 将生成的字库和 fonts/open-iconic.bin 一起上传到开发板
				from tests.fontlibtest2 import FontLibTest2
				runner = FontLibTest2(oled)
				runner.run_test()
			elif selected == 5:
				# 多线程方式，每次读取一屏字符数据，每次滚动 1 像素
				runner.load_font(fontfile)
				runner.run_test(scroll_height=1, interval=40, chars=chars3, thread=True)
			elif selected == 6:
				# 定时器方式，读取所有字符数据，每次滚动 1 像素
				runner.load_font(fontfile)
				runner.run_test(1, 20, chars2, True)

		del runner
		gc.collect()

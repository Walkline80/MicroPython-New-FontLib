<h1 align="center">使用图标字体生成字库</h1>

> 本文以 [IcoMoon](https://icomoon.io/#icons-icomoon) 提供的免费图标字体为例，讲解如何生成图标字库

* 首先下载`Free Version`的[压缩包](https://github.com/Keyamoon/IcoMoon-Free/archive/master.zip)

* 从压缩包中提取如下文件：

	* `Font/IcoMoon-Free.ttf`：图标字体文件
	* `Font/demo-files/demo.css`：样式表文件，包含图标的`Unicode`值

* 打开`.ttf`文件，点击`安装`按钮，同时记录下字体名称`IcoMoon-Free`

* 打开`.css`文件，找到第一个和最后一个与如下格式类似的内容

	```css
	// 第一个
	.icon-home:before {
	    content: "\e900";
	}

	// 最后一个
	.icon-IcoMoon:before {
	    content: "\eaea";
	}
	```

* 记录`content`后边的`Unicode`值，这里分别是`e900`和`eaea`

* 打开`client/fonts/cst_generator.py`，根据`font_list`的格式添加一个`icomoon-free`列表

	```python
	font_list = [
	    # [
	    # 	output_file_prefix,
	    # 	charset_range,
	    # 	fontface,
	    # 	fontfile
	    # ]
	    ['open-iconic', range(0xe000, 0xe0de + 1), 'Icons', 'open-iconic.ttf'],
	    ['emoticons21', range(0x20, 0x3f + 1), 'Emoticons21', 'emoticons21.fon'],
	    ['icomoon-free', range(0xe900, 0xeaea + 1), 'IcoMoon-Free', 'icomoon-free.ttf']
	]
	```

* 运行`cst_generator.py`文件，并根据提示内容进行操作，最终生成`icomoon-free.cst`文件（字符映射表）

	```bash
	$ cd client
	$ python fonts/cst_generator.py
	```

* 运行命令行工具生成字库文件，其中`IcoMoon-Free`为安装`.ttf`文件时记录的`字体名称`

	```bash
	$ FontMaker_Cli.exe -f IcoMoon-Free -s 16 --charset fonts/icomoon-free.cst -o icomoon-free.bin
	```

* 以二进制方式打开刚刚生成的`icomoon-free.bin`文件，滚动条拉到文件中部，如果文件内容全部为`00`表示以上操作步骤中的某一步出现了问题，字库文件生成失败

* 使用`FontLib`获取字符点阵数据

	```python
	from libs.fontlib import FontLib

	fontlib = FontLib('client/icomoon-free.bin')
	fontlib.info()
	
	chars = '\ue977\ue9e9\ue978'
	buffer_dict = fontlib.get_characters(chars)

	for unicode, data in buffer_dict.items():
	    print('{}: {}'.format(unicode, bytes(data)))

	for char in chars:
	    print('{}: {}'.format(char, bytearray(buffer_dict[ord(char)])))
	```

* 运行`cst_generator.py`文件同时会生成图标预览页面，可以使用预览方式选择图标

	> 注：`.fon`文件无效

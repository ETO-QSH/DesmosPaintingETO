# DesmosPaintingETO

### 前言

欢迎来到我的项目！本项目名为**DesmosPaintingETO**，顾名思义就是利用Desmos进行简单绘画的项目。你可以使用它将图片或者视频“画”进Desmos，就像下面那样！（原图来源 --> [https://www.pixiv.net/users/6657532/artworks](https://www.pixiv.net/users/6657532/artworks)）

![image](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707123931.gif)

如果你想知道如何简单的完成这样一个作品，希望你能耐心的看后续的内容，它不会太长也不会太难的说。

***

### 下载

我在 [Releases](https://github.com/ETO-QSH/DesmosPaintingETO/releases) 里面提供了已经打包好的项目，我使用pyinstaller打包，并且我执意使用onefile模式生成单文件exe使得相较于自己运行.py文件占用了更大的体积，所以看起来有些庞大不是。

总之，你可以直接下载最新的releases，解压后会得到四个exe文件，一个md文件（就是本文），以及一个pdf文件（本文pdf版）。四个exe中，DesmosPaintingETO.exe是主程序负责GUI，netwoke.exe和showdata.exe是对主程序的支持，分别负责web服务器和展示data，potrace.exe是真正的核心，是一个很有名的算法（大概）。

这里是potrace的链接：[github](https://github.com/lgcc/potrace)、[官网](https://potrace.sourceforge.net/)，感兴趣的可以去瞅瞅。

***

### 使用

为了避免任何意外，请将文件放在全英文路径下。

双击运行DesmosPaintingETO.exe，你会打开这样一个界面（已点击展开）。用 tk 画的（最后一次用了太难受了），字体文件在项目里面，叫 Lolita.ttf ，画的还可以吧 ~

（我没有测试不同DPI的情况，我的屏幕是2160×1440，缩放是150%，在我的这里是正常的说）

![image](https://github.com/user-attachments/assets/d9da71a8-9553-4b0e-9de1-98302642ad4d)

我们将鼠标悬停在 **?** 上面后，会显示一些解释性文本，它会提示你基本的操作。

（这里不好写画的不好看应付一下拜托了。。。）

对于类按钮控件，我支持了左键和右键。

| |左键|右键
|-|-|-
|蓝色图片|打开本地pdf文件|[跳转本项目地址](https://github.com/ETO-QSH/DesmosPaintingETO)
|open按钮|打开文本选择器|将剪切板的内容粘贴至文本框
|开始绘制|运行同时反馈运行状态|运行但不打开showdata.exe

ps：滑块可以点击左右空白的地方微调

你可能会注意到展开后一排排乱七八糟的什么参数，其实可能用到的并不多，旁边的 **?** 有所解释，控制变量起来也不是很麻烦，对于不太复杂（什么乱七八糟的阴影手绘高光虚化渐变）的图片处理起来非常轻松，默认的参数大概就能解决问题。（比如上面的，我真没调的说，一打开就这样）

对于一些大型的图片和视频，我只能说我的程序能跑出结果（edged文件夹），但是把大量数据发送到你的浏览器里面你的内存可能会吃不消（错误代码: Out of Memory）。对于一些超大的图片你可以适当的缩小先，边缘检测的时候会丢失很少的细节（L2可以救但是没必要），一个视频（包括gif）会被分解成帧先，或者你可以尝试进行分段？调参也可以减少线条的数量。总之请减少线条的数量！

成果的颜色可以看得出来会比原来选择的颜色要淡，因为是线条跟白色背景混合了。

我的窗口都没有进行置顶（结束的弹窗有提示音），要是桌面比较凌乱可能需要你找找。。。

如果使用时出现弹窗** • cv2解析出现错误**，可能是类似这个错误：
`[ WARN:0@12.939] global loadsave.cpp:241 cv::findDecoder imread_('D:\Work Files\DesmosETO\src\艾雅法拉.png'): can't open/read file: check file path/integrity`。
请检查一下文件格式，或者改中文路径为英文，还有事欢迎找我麻烦 ~

还有一个bug就是当你勾选矢量保存的时候应该会出现（除非你安装了reportlab），这个我用来把svg转png（这不是一个必要的功能，毕竟你都希望矢量保存了，我转是为了合成gif）。

```
Traceback (most recent call last):
  File "reportlab\graphics\renderPM.py", line 44, in _getPMBackend
ModuleNotFoundError: No module named 'rlPyCairo'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "reportlab\graphics\renderPM.py", line 47, in _getPMBackend
ModuleNotFoundError: No module named '_rl_renderPM'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "multiprocessing\process.py", line 314, in _bootstrap
  File "multiprocessing\process.py", line 108, in run
  File "netwoke.py", line 68, in create_gif
    renderPM.drawToFile(drawing, png_data, fmt="PNG")
  File "reportlab\graphics\renderPM.py", line 734, in drawToFile
  File "reportlab\graphics\renderPM.py", line 719, in drawToPMCanvas
  File "reportlab\graphics\renderPM.py", line 313, in __init__
  File "reportlab\graphics\renderPM.py", line 327, in _getGState
  File "reportlab\graphics\renderPM.py", line 49, in _getPMBackend
reportlab.graphics.utils.RenderPMError: cannot import desired renderPM backend rlPyCairo
Seek advice at the users list see
https://pairlist2.pair.net/mailman/listinfo/reportlab-users

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "netwoke.py", line 444, in <module>
    multiprocessing.freeze_support()
  File "PyInstaller\hooks\rthooks\pyi_rth_multiprocessing.py", line 50, in _freeze_support
  File "multiprocessing\spawn.py", line 122, in spawn_main
  File "multiprocessing\spawn.py", line 135, in _main
  File "multiprocessing\process.py", line 329, in _bootstrap
AttributeError: 'NoneType' object has no attribute 'write'
```

你可以忽略它，这不影响你正确运行程序，就是 output 里面只会有zip（里面是svg图像）而没有合成gif了，我会在后续更新中修复它。

分解帧的时候你要是太多了可能会假装无响应，搁一边放着就行。

***

### 测试

下面给出部分测试过的样本，在 [src](https://github.com/ETO-QSH/DesmosPaintingETO/tree/main/src) 里面有原图，成果在 [output](https://github.com/ETO-QSH/DesmosPaintingETO/tree/main/output) 里面。（一些比例问题是开发早期的老图）

你大可以跳过这一段表格，因为其实并不重要，图是好久之前到处捡的，只是你真的不想看看效果的吗 ~

当然这不代表最高画质，我的破电脑30000多线就歇菜了所以我是压过线条数量的（直接一半一半砍的随意）

（后面摆烂了全部用预设参数了，这不更说明不用调也行不是，预设参数的效果还不赖耶，其实调了效果更好）

|图片名|src|output|测试用参数
|-|-|-|-
|预设参数|     {~划掉划掉划掉~}|     {~划掉划掉划掉~}|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|可莉.png|![%E5%8F%AF%E8%8E%89.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E5%8F%AF%E8%8E%89.png)|![output-png-20240707124130.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707124130.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|ETO.png|![ETO.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/ETO.png)|![output-png-20240707154151.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707154151.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 25, 'upper': 150, 'modified': 5}`
|铃兰.gif|![铃兰.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E9%93%83%E5%85%B0.gif)|![output-png-20240707133005.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707133005.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 10, 'opticurve': 'True', 'diameter': 10, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 75, 'modified': 5}`
|初音未来.png|![%E5%88%9D%E9%9F%B3%E6%9C%AA%E6%9D%A5.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E5%88%9D%E9%9F%B3%E6%9C%AA%E6%9D%A5.png)|![output-png-20240709103734.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240709103734.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 10, 'opticurve': 'True', 'diameter': 10, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 75, 'modified': 5}`
|克拉拉.jpg|![%E5%85%8B%E6%8B%89%E6%8B%89.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E5%85%8B%E6%8B%89%E6%8B%89.jpg)|![output-png-20240709112053.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240709112053.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 0, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 75, 'upper': 210, 'modified': 5}`
|Yoolalouse.jpg|![Yoolalouse.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/Yoolalouse.jpg)|![output-png-20240709113018.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240709113018.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|略nd.jpg|![略nd.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/略nd.jpg)|![output-png-20240721012801.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240721012801.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|ai.jpg|![ai.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/ai.jpg)|![output-png-20240710005336.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240710005336.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|warma.jpg|![warma.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/warma.jpg)|![output-png-20240720112948.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720112948.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|艾雅法拉.png|![艾雅法拉.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/艾雅法拉.png)|![output-png-20240720220201.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720220201.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|铃兰.png|![铃兰.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/铃兰.png)|![output-png-20240720143216.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720143216.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|星尘.jpg|![星尘.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/星尘.jpg)|![output-png-20240720154250.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720154250.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|ai.png|![ai.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/ai.png)|![output-png-20240720155857.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720155857.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|岁.jpg|![岁.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/岁.jpg)|![output-png-20240720181318.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720181318.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 20, 'opticurve': 'True', 'diameter': 20, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 60, 'modified': 5}`
|和泉雾纱.jpg|![和泉雾纱.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/和泉雾纱.jpg)|![output-png-20240720182843.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720182843.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|塞西莉亚.jpg|![塞西莉亚.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/塞西莉亚.jpg)|![output-png-20240720184255.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720184255.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|Nahaki.png|![Nahaki.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/Nahaki.png)|![output-png-20240720190942.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720190942.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|康娜.jpg|![康娜.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/康娜.jpg)|![output-png-20240720191928.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720191928.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|女孩子.jpg|![女孩子.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/女孩子.jpg)|![output-png-20240720194207.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720194207.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 90, 'modified': 5}`
|真找不到谁.jpg|![真找不到谁.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/真找不到谁.jpg)|![output-png-20240720195129.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720195129.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|甘雨.jpg|![甘雨.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/甘雨.jpg)|![output-png-20240720200827.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720200827.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|aii.jpg|![aii.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/aii.jpg)|![output-png-20240720203807.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720203807.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|小刻.jpg|![小刻.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/小刻.jpg)|![output-png-20240720204727.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720204727.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|雨.png|![雨.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/雨.png)|![output-png-20240720210438.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720210438.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|西条.jpg|![西条.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/西条.jpg)|![output-png-20240720211235.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720211235.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|萌新.jpg|![萌新.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/萌新.jpg)|![output-png-20240720214800.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720214800.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|aai.jpg|![aai.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/aai.jpg)|![output-png-20240720221010.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720221010.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|skeb.jpg|![skeb.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/skeb.jpg)|![output-png-20240720221654.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720221654.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|霍霍.jpg|![霍霍.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/霍霍.jpg)|![output-png-20240720222847.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720222847.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|Alice.jpg|![Alice.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/Alice.jpg)|![output-png-20240720223755.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240720223755.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|网页截图.png|![网页截图.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/网页截图.png)|![edged_0_8660.svg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/edged_0_8660.svg)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|明日方舟.jpg|![明日方舟.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/明日方舟.jpg)|![edged_0_25099.bmp](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/edged_0_25099.bmp)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`

如果你决定要亲手调参，有一个技巧就是我们先勾选**不自动打开web**，他会在 edged 目录下面生成成对的文件，一个png一个svg，分别是提到的cv2和potrace的结果。这样在不进行web渲染之前就能看到效果会方便些。不足就是可能要求任务管理器查杀netwoke.exe（调好之后杀就行），或者说可以试试运行这个（psutil是要pip的），它会帮你做到！

```
import psutil

def find_and_terminate_process(window_title):
    for proc in psutil.process_iter(['pid', 'name']):
        if window_title in proc.info['name']:
            proc.terminate()
            proc.wait(timeout=1)

find_and_terminate_process("netwoke.exe")
```

还有就是视频太长了的话（其实长不是事，就是不要有太复杂的帧直接给网页搞崩溃了就行，尽量不要给你电脑上强度不是），并且你可以接受删除很多帧，可以先运行程序，勾选不自动打开web，他会拆解帧在tempETO文件夹里面，你可以挑选一些帧保留，文件夹带走。下次运行你拿第一张图片给它跑，预先放之前的tempETO文件夹回来，他就会读取所有图片（年轻人来骗），下面是删除奇数编号文件和重新编号的代码：

```
import os, re

folder_path = 'D:\\Desktop\\Desktop\\tempETO'

pattern = re.compile(r'frame(\d+)\.png')

files = os.listdir(folder_path)

sorted_files = sorted(
    (f for f in files if pattern.match(f)),
    key=lambda x: int(pattern.match(x).group(1))
)

# 遍历文件列表，删除奇数顺序的文件
for i in range(0, len(sorted_files), 2):
    file_path = os.path.join(folder_path, sorted_files[i])
    os.remove(file_path)
    print(f"Deleted: {file_path}")

# 从1开始重新编号剩余的图片
for i, file_name in enumerate(sorted_files, start=1):
    original_number = int(pattern.match(file_name).group(1))
    new_file_name = f'frame{i}.png'
    os.rename(os.path.join(folder_path, file_name), os.path.join(folder_path, new_file_name))
    print(f'Renamed: {file_name} to {new_file_name}')

print("Renaming operation completed.")
```

目前还没有支持命令行，下次更新会加入命令行操作。

***

### 尾音

早期测试时的一个小插曲 ~

![390f824238f44acb1c5ef625e192a983](https://github.com/user-attachments/assets/7cf6df93-e2f6-482c-85a6-9250716b1299)

笑着笑着就哭出来了呢（调参不规范，亲人两行泪）

好了回到正题，我们设置好点击开始绘制，会打开一个窗口（左键开始绘制）和网页（勾选自动打开网页），根据指示点击 **f->1** 它就会自动完成了，如下：

![image}{Z5$ B2EEIIY24HU( 6](https://github.com/user-attachments/assets/d62dc58f-cda3-4351-b6ee-7c2c073abc85)

如果你像我一样勾选了自动下载，你会在 output 文件夹里面看到一对新的gif和zip文件（文件名随时间），这就完成了所有工作了！（我这破电脑不到半分钟）

***

### 开发

<img align="right" src="https://github.com/user-attachments/assets/b0b7a522-afd9-448a-a2bc-499a39ab2475"/>

本项目一开始是在Linux下面开发的，因为potrace的python库只在Linux有效，故我保留了Linux时期的代码（有点老旧了，一些tk的api还用不了），但暂时没有继续完善的打算（画gui累死个人）。

里面还有一个**为Windows多进程版本开发的DesmosETO**，这是一开始的设想，我希望在一个文件里面完成所有事（听起来就舒服），但是tk和multiprocessing的兼容性搞得我十分头大，新引入的tkintertools又把我的gui毁了（字面意思，本来依靠一个tk的dpi缩放bug运行，tkintertools说它顺手给修了，啊？）。

所以我搞了个三家分晋给他裂了三个exe，但是这样搞得好大的库包了三次，本来用pyinstaller包80M就能解决的现在搞那么大。有大佬会的可以教教不是 ~


***

### 说明

现在发布的版本未经过除了项目作者以外任何人的测试，如存在问题请联系我。

如果你要提交**Issues**请麻烦使用**English**，这样可以方便所有人阅读。

如果你想靠这个项目混一个Desmos艺术大赛的作品，大可放心这个混不到的。

如果被杀毒软件关小黑屋了可以救一下，世界上没那么多病毒。

如果图片有侵权请联系我，我会尽快进行删除。

如果你得到了一些不错的作品可以在Issues里面分享鸭。

如果这个你喜欢这个项目，我能不能混一个免费的**Star**呢，谢谢喵 ~

早期有借鉴这个项目[DesmosBezierRenderer](https://github.com/kevinjycui/DesmosBezierRenderer)，一开始只是想要搞一下在Windows里面用，想不到就重写了。

待更新：命令行操作，单文件打包，修复reportlab问题，支持中文路径

###### 本项目采用 GNU Affero General Public License v3.0 协议

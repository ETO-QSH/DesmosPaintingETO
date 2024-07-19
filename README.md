# DesmosPaintingETO

欢迎来到我的项目！本项目名为**DesmosPaintingETO**，顾名思义就是利用Desmos进行简单绘画的项目。你可以使用它将图片或者视频“画”进Desmos，就像下面那样！（原图来源 --> [https://www.pixiv.net/users/6657532/artworks](https://www.pixiv.net/users/6657532/artworks)）

![image](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707123931.gif)

如果你想知道如何简单的完成这样一个作品，希望你能耐心的看后续的内容，它不会太长也不会太难的说。

## 使用说明

我在 [Releases](https://github.com/ETO-QSH/DesmosPaintingETO/releases) 里面提供了已经打包好的项目，我使用pyinstaller打包，并且我执意使用onefile模式生成单文件exe使得相较于自己运行.py文件占用了更大的体积，所以看起来有些庞大不是。

总之，你可以直接下载最新的releases，解压后会得到三个exe文件，一个md文件（就是本文），以及一个pdf文件（本文pdf版）。三个exe中，DesmosPaintingETO.exe是主程序负责GUI，netwoke.exe和showdata.exe是对主程序的支持，分别负责web服务器和展示data。

双击运行DesmosPaintingETO.exe，你会打开这样一个界面（已点击展开）。用tk画的，画的还可以吧~

![image](https://github.com/user-attachments/assets/d9da71a8-9553-4b0e-9de1-98302642ad4d)

我们将鼠标悬停在 **?** 上面后，会显示一些解释性文本，它会提示你基本的操作。

对于类按钮控件，我支持了左键和右键。
| |左键|右键
|-|-|-
|蓝色图片|打开本地pdf文件|[跳转本项目地址](https://github.com/ETO-QSH/DesmosPaintingETO)
|open按钮|打开文本选择器|将剪切板的内容粘贴至文本框
|开始绘制|运行同时反馈运行状态|运行但不打开showdata.exe

你可能会注意到展开后一排排乱七八糟的什么参数，其实可能用到的并不多，旁边的 **?** 有所解释，控制变量起来也不是很麻烦，对于不太复杂（什么乱七八糟的阴影手绘高光）的图片处理起来非常轻松，默认的参数大概就能解决问题。（比如上面的，我真没调的说，一打开就这样）

下面给出部分测试过的样本，在 [src](https://github.com/ETO-QSH/DesmosPaintingETO/tree/main/src) 里面有原图，成果在 [output](https://github.com/ETO-QSH/DesmosPaintingETO/tree/main/output) 里面。（一些比列问题和渲染问题是开发早期的结果）

|图片名|src|output|测试用参数
|-|-|-|-
|预设参数|     {划掉划掉}|     {划掉划掉}|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|可莉.png|![%E5%8F%AF%E8%8E%89.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E5%8F%AF%E8%8E%89.png)|![output-png-20240707124130.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707124130.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`
|ETO.png|![ETO.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/ETO.png)|![output-png-20240707154151.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707154151.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 25, 'upper': 150, 'modified': 5}}`
|铃兰.gif|![铃兰.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E9%93%83%E5%85%B0.gif)|![output-png-20240707133005.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240707133005.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 10, 'opticurve': 'True', 'diameter': 10, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 75, 'modified': 5}}`
|初音未来.png|![%E5%88%9D%E9%9F%B3%E6%9C%AA%E6%9D%A5.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E5%88%9D%E9%9F%B3%E6%9C%AA%E6%9D%A5.png)|![output-png-20240709103734.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240709103734.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 10, 'opticurve': 'True', 'diameter': 10, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 75, 'modified': 5}}`
|克拉拉.jpg|![%E5%85%8B%E6%8B%89%E6%8B%89.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/%E5%85%8B%E6%8B%89%E6%8B%89.jpg)|![output-png-20240709112053.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240709112053.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 0, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 75, 'upper': 210, 'modified': 5}}`
|Yoolalouse.jpg|![Yoolalouse.jpg](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/Yoolalouse.jpg)|![output-png-20240709113018.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240709113018.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}}`
|略nd.mp4|![]()|![]()|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 5, 'opticurve': 'True', 'diameter': 15, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 95, 'upper': 100, 'modified': 5}}`
|ai.jpg|![ai.png](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/src/ai.png)|![output-png-20240710005336.gif](https://github.com/ETO-QSH/DesmosPaintingETO/blob/main/output/output-png-20240710005336.gif)|`{'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}`


import tkinter as tk
from PIL import Image
from threading import Timer
from flask_cors import CORS
from tkinter import messagebox
from svglib.svglib import svg2rlg
import xml.etree.ElementTree as ET
from reportlab.graphics import renderPM
from flask import Flask, jsonify, request, redirect, render_template, send_from_directory
import io, os, re, cv2, ast, sys, copy, json, time, base64, psutil, shutil, signal, zipfile, pyperclip, subprocess, webbrowser, multiprocessing

# os.path.dirname(os.path.abspath(__file__)), os.path.dirname(os.path.realpath(sys.executable))
app = Flask(__name__, template_folder=os.path.dirname(os.path.realpath(sys.executable)))
app.static_folder = os.path.dirname(os.path.realpath(sys.executable))
CORS(app)

height = multiprocessing.Value('i', 10, lock=False)
width = multiprocessing.Value('i', 10, lock=False)
frame = multiprocessing.Value('i', 0)
FRAME_DIR = 'tempETO'
frame_latexETO = []
names = locals()
x_y_side = []

with open('InformationDictionary.txt', 'r', encoding='utf-8') as file:
    STR = file.read()
    str_c = ast.literal_eval(STR)
    for str_key in str_c.keys():
        names['%s' % str_key] = str_c[str_key]

def find_and_terminate_process(window_title):
    for proc in psutil.process_iter(['pid', 'name']):
        if window_title in proc.info['name']:
            proc.terminate()
            proc.wait(timeout=1)

def create_zip(folder_path):
    if not os.path.exists('output'):
        os.makedirs('output')
    files = [f for f in os.listdir(folder_path)]
    if all(f.endswith('.svg') for f in files):
        zip_path = os.path.join(os.path.dirname(folder_path), 'output', 'output-svg-{}.zip'.format(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for svg_file in files:
                svg_path = os.path.join(folder_path, svg_file)
                zip_file.write(svg_path, os.path.basename(svg_path))
    elif all(f.endswith('.png') for f in files):
        zip_path = os.path.join(os.path.dirname(folder_path), 'output', 'output-png-{}.zip'.format(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))))
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for png_file in files:
                png_path = os.path.join(folder_path, png_file)
                zip_file.write(png_path, os.path.basename(png_path))

def create_gif(folder_path, dur, num):
    if not os.path.exists('output'):
        os.makedirs('output')
    files = sorted([f for f in os.listdir(folder_path)])
    durations_list = copy.deepcopy([int(1000/dur)]*num)
    for i in range(1, int((num/dur)*1000)-int(1000/dur)*num+1):
        durations_list[int((i-0.5)*(int((num/(int((num/dur)*1000)-int(1000/dur)*num))+0.5))+0.5)] = int(1000/dur)+1
    if all(f.endswith('.svg') for f in files):
        frames = []
        for svg_file in files:
            svg_path = os.path.join(folder_path, svg_file)
            drawing = svg2rlg(svg_path)
            png_data = io.BytesIO()
            renderPM.drawToFile(drawing, png_data, fmt="PNG")
            png_data.seek(0)
            frames.append(Image.open(png_data))
        gif_path = os.path.join(os.path.dirname(folder_path), 'output', 'output-svg-{}.gif'.format(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))))
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=durations_list, loop=0)
        for frame in frames:
            frame.close()
    elif all(f.endswith('.png') for f in files):
        frames = [Image.open(os.path.join(folder_path, f)) for f in files]
        gif_path = os.path.join(os.path.dirname(folder_path), 'output', 'output-png-{}.gif'.format(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))))
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=durations_list, loop=0)

def SVGtransformation(path, X, Y, aX, aY, sx, sy):
    with open(path, 'r') as file:
        content = file.read()
    pattern = r'<g transform=.*?>'
    matches = re.findall(pattern, content)
    pattern = r'".*?"'
    matches = re.findall(pattern, matches[0])
    content = content.replace(matches[0],'" translate({},{}) scale({},{})"'.format(round(-X*aX, 6), round(-Y*aY, 6), round(aX, 6), round(aY, 6)))
    pattern = r'width="\d+" height="\d+"'
    matches = re.findall(pattern, content)
    content = content.replace(matches[0], 'width="{}" height="{}"'.format(sx, sy))
    with open(path, 'w') as file:
        file.write(content)

def PNGtransformation(path, original_sizes, display_sizes, mode):
    original_width, original_height = original_sizes
    display_width, display_height = display_sizes[0], display_sizes[1]
    scale_width = original_width / display_width
    scale_height = original_height / display_height
    scale = min(scale_width, scale_height)
    new_width = int(display_width * scale)
    new_height = int(display_height * scale)
    if scale_width > scale_height:
        left, top = int((original_width - new_width) / 2), 0
        right, bottom = left + new_width, top + new_height
    else:
        left, top = 0, int((original_height - new_height) / 2)
        right, bottom = left + new_width, top + new_height
    if mode == 'png':
        image = Image.open(path)
        original_image = image.crop((left, top, right, bottom))
        resized_image = original_image.resize((original_width, int(original_height/hidden_window_data['modified'])), Image.Resampling.LANCZOS)
        resized_image.save(path)
    else:
        SVGtransformation(path, left, top, original_width/(display_width*scale), original_height/(display_height*scale*hidden_window_data['modified']), original_width, int(original_height/hidden_window_data['modified']))

def save_image_data(base64_image_data, name, e):
    if not os.path.exists('datatemp'):
        os.makedirs('datatemp')
    image_data = base64.b64decode(base64_image_data)
    with open('datatemp//{}.{}'.format(name, e), 'wb') as file:
        file.write(image_data)
    if SCREENSHOT_SIZE[0] > list(x_y_side)[0] or SCREENSHOT_SIZE[1] > list(x_y_side)[1]:
        PNGtransformation('datatemp//{}.{}'.format(name, e), SCREENSHOT_SIZE, list(x_y_side), e)
    print('{}.{}'.format(name, e), 'Saved', time.ctime())
    with open('data.txt', 'a', encoding='utf-8') as file:
        print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '图片{}.{}已保存至datatemp文件夹'.format(name, e), file=file)
    if len(os.listdir(FRAME_DIR)) == len(os.listdir('datatemp')):
        with open('data.txt', 'a', encoding='utf-8') as file:
            print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '所有帧已收录完全，开始合成gif和zip', file=file)
        gif_process = multiprocessing.Process(target=create_gif, args=('datatemp', int(form_data['get'][1]), len(os.listdir('datatemp')),))
        zip_process = multiprocessing.Process(target=create_zip, args=('datatemp',))
        gif_process.start()
        zip_process.start()
        gif_process.join()
        zip_process.join()
        with open('data.txt', 'a', encoding='utf-8') as file:
            print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '合成gif和zip结束，已保存至output文件夹', file=file)
        stop_app()

def Svg2Curves(svg_path):
    root = ET.parse(svg_path).getroot()
    path = root.find('.//{http://www.w3.org/2000/svg}path')
    g = root.find('.//{http://www.w3.org/2000/svg}g')
    transform_attribute = g.get('transform')
    input_txt = path.get('d')
    scale_x, scale_y = transform_attribute.split('scale(')[1].split(')')[0].split(',')
    List = []

    for x in input_txt.split(' '):
        i = []
        for y in x:
            i.append(y)
        if len(set(i).intersection(set(['M', 'L', 'H', 'V', 'C', 'S', 'Q', 'T', 'A', 'm', 'l', 'h', 'v', 'c', 's', 'q', 't', 'a']))) > 0:
            List.append(x[0])
            List.append(int(x[1:]))
        elif len(set(i).intersection(set(['Z', 'z']))) > 0:
            List.append(int(x[:-1]))
            List.append(x[-1])
        else:
            List.append(int(x))

# with open('output.txt', 'w') as file:
    i = 0
    mode = None
    x0, y0 = 0, 0
    svgoutput = []
    for x, y in enumerate(List):
        if x < i:
            pass
        else:
            if (not y in ['M', 'L', 'H', 'V', 'C', 'S', 'Q', 'T', 'A', 'Z', 'm', 'l', 'h', 'v', 'c', 's', 'q', 't', 'a', 'z']) and mode != None:
                y = mode
                t = True
            else:
                t = False
            if str(y) == 'Z' or str(y) == 'z' or str(y) == 'Zz':
                mode = 'Zz'
                # print('Zz：闭合曲线由({}, {})至({}, {})'.format(x0, y0, _x, _y), file=file)
                svgoutput.append({mode: None})
            elif str(y) == 'M':
                mode = str(y)
                x0, y0 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('M：设置起点为({}, {})'.format(x0, y0), file=file)
                svgoutput.append({mode: [(x0, y0)]})
                _x, _y = x0, y0
                i = x + 3 - t
            elif str(y) == 'm':
                mode = str(y)
                x0, y0 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('m：设置起点为({}, {})'.format(x0, y0), file=file)
                svgoutput.append({mode: [(x0, y0)]})
                _x, _y = x0, y0
                i = x + 3 - t
            elif str(y) == 'L':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('L：绘制直线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 'l':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('l：绘制直线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 'H':
                mode = str(y)
                x1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit'])
                # print('H：绘制水平线由({}, {})至({}, {})'.format(x0, y0, x1, y0), file=file)
                svgoutput.append({mode: [(x0, y0), (x1, y0)]})
                x0 = x1
                i = x + 2 - t
            elif str(y) == 'h':
                mode = str(y)
                x1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit'])
                # print('h：绘制水平线由({}, {})至({}, {})'.format(x0, y0, x1, y0), file=file)
                svgoutput.append({mode: [(x0, y0), (x1, y0)]})
                x0 = x1
                i = x + 2 - t
            elif str(y) == 'V':
                mode = str(y)
                y1 = round(List[x + 1 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('V：绘制竖直线由({}, {})至({}, {})'.format(x0, y0, x0, y1), file=file)
                y0 = y1
                i = x + 2 - t
                svgoutput.append({mode: [(x0, y0), (x0, y1)]})
            elif str(y) == 'v':
                mode = str(y)
                y1 = round(y0 + List[x + 1 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('v：绘制竖直线由({}, {})至({}, {})'.format(x0, y0, x0, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x0, y1)]})
                y0 = y1
                i = x + 2 - t
            elif str(y) == 'C':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x3, y3 = round(List[x + 5 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 6 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('C：绘制三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {})和c2({}, {})'.format(x0, y0, x3, y3, x1, y1, x2, y2), file=file)
                svgoutput.append({mode: [(x0, y0), (x3, y3), (x1, y1), (x2, y2)]})
                x0, y0 = x3, y3
                i = x + 7 - t
            elif str(y) == 'c':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(x0 + List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x3, y3 = round(x0 + List[x + 5 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 6 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('c：绘制三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {})和c2({}, {})'.format(x0, y0, x3, y3, x1, y1, x2, y2), file=file)
                svgoutput.append({mode: [(x0, y0), (x3, y3), (x1, y1), (x2, y2)]})
                x0, y0 = x3, y3
                i = x + 7 - t
            elif str(y) == 'S':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('S：绘制平滑三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 's':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(x0 + List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('s：绘制平滑三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 'Q':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('Q：绘制二次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 'q':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(x0 + List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('q：绘制二次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 'T':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('T：绘制平滑的二次贝塞尔曲线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 't':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('t：绘制平滑的二次贝塞尔曲线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgoutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 'A':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                r1, r2, r3 = List[x + 3 - t], int(List[x + 4 - t]), int(List[x + 5 - t])
                # print('A：绘制椭圆弧由({}, {})至({}, {})，双轴半径为({}, {})且角度为{}°的{}时针{}弧'.format(x0, y0, x2, y2, x1, y1, r1, ['顺' if r3 else '逆'], ['大' if r2 else '小']), file=file)
                svgoutput.append({mode: [(x0, y0), (x2, y2), (x1, y1), (r1, r2, r3)]})
                x0, y0 = x2, y2
                i = x + 8 - t
            elif str(y) == 'a':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = x0 + round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), y0 + round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                r1, r2, r3 = List[x + 3 - t], int(List[x + 4 - t]), int(List[x + 5 - t])
                # print('a：绘制椭圆弧由({}, {})至({}, {})，双轴半径为({}, {})且角度为{}°的{}时针{}弧'.format(x0, y0, x2, y2, x1, y1, r1, ['顺' if r3 else '逆'], ['大' if r2 else '小']), file=file)
                svgoutput.append({mode: [(x0, y0), (x2, y2), (x1, y1), (r1, r2, r3)]})
                x0, y0 = x2, y2
                i = x + 8 - t
    return svgoutput

def get_contours(filename, framevalue):
    lower = hidden_window_data['lower']
    upper = hidden_window_data['upper']
    USE_L2_GRADIENT = {'True': True, 'False': False}
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if BILATERAL_FILTER:
        filtered = cv2.bilateralFilter(gray, int(hidden_window_data['diameter']), int(hidden_window_data['sigmaColor']), int(hidden_window_data['sigmaSpace']))
        edged = cv2.Canny(filtered, lower, upper, L2gradient=USE_L2_GRADIENT[hidden_window_data['L2gradient']])
    else:
        edged = cv2.Canny(gray, lower, upper, L2gradient=USE_L2_GRADIENT[hidden_window_data['L2gradient']])
    with frame.get_lock():
        height.value = image.shape[0]
        width.value = image.shape[1]
    print('\r|| Processing frame %d/%d ' % (framevalue, len(os.listdir(FRAME_DIR))), end='')
    with open('data.txt', 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        file.seek(0)
        file.writelines(lines[:-1])
        file.truncate()
        print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '正在处理帧 {}/{}'.format(framevalue, len(os.listdir(FRAME_DIR))), file=file)
    img = Image.fromarray(edged, mode='L')
    img_name = 'edged//edged_{}_{}.'.format(int(framevalue) - 1, PORT)
    while not os.path.exists(img_name + 'bmp'):
        img.save(img_name + 'bmp')
    command = 'potrace {} -z {} -t {} -a {} {} -O {} -s -i -u {} --flat --output {}'.format(img_name + 'bmp', hidden_window_data['turnpolicy'], hidden_window_data['turdsize'], round(hidden_window_data['alphamax']*1.3333, 4), ['' if hidden_window_data['opticurve'] == 'True' else '-n'][0], hidden_window_data['opttolerance'], 10**hidden_window_data['unit'], img_name + 'svg')
    while not os.path.exists(img_name + 'svg'):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return Svg2Curves(img_name + 'svg')

def get_latex(filename, framevalue):
    latex = []
    svgoutput = get_contours(filename, framevalue)
    for path in svgoutput:
        if list(path.keys())[0] in ['L', 'l']:
            vars = path[list(path.keys())[0]]
            latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (vars[0][0], vars[1][0], vars[0][1], vars[1][1]))
        elif list(path.keys())[0] in ['C', 'c']:
            vars = path[list(path.keys())[0]]
            latex.append('((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)),\
            (1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))' % \
            (vars[0][0], vars[2][0], vars[2][0], vars[3][0], vars[2][0], vars[3][0], vars[3][0], vars[1][0], vars[0][1], vars[2][1], vars[2][1], vars[3][1], vars[2][1], vars[3][1], vars[3][1], vars[1][1]))
    return latex

def get_expressions(frame):
    exprid = 0
    exprs = []
    for expr in get_latex(FRAME_DIR + '/frame%d.%s' % (frame+1, 'png'), frame+1):
        exprid += 1
        exprs.append({'id': 'expr-' + str(exprid), 'latex': expr, 'color': COLOUR, 'secret': True})
    return exprs, width.value, height.value

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if request.args.get('frame') is not None:
            frame = int(request.args.get('frame'))
            if frame >= len(os.listdir(FRAME_DIR)):
                if DOWNLOAD_IMAGES == False:
                    stop_app()
                return {'result': None}
            with open('data.txt', 'a', encoding='utf-8') as file:
                print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '向本地服务器发送第{}帧数据'.format(frame+1), file=file)
            return json.dumps({'result': list(frame_latexETO)[frame]})
        else:
            return redirect('/calculator')
    elif request.method == 'POST':
        data = request.get_json()
        message = str(data.get('message'))
        if message[0:10] != 'screenshot':
            if DOWNLOAD_IMAGES == True:
                if message[11:14] == 'png':
                   save_image_data(message[22:-11], message[-11:], message[11:14])
                elif message[11:14] == 'svg':
                   save_image_data(message[26:-11], message[-11:], message[11:14])
        else:
            _, X, Y = message.split('-')
            x_y_side.append(float(X))
            x_y_side.append(float(Y))
        return jsonify({"message": "POST request received"})

@app.route("/calculator")
def client():
    return render_template('index.html', api_key='dcb31709b452b1cf9dc26972add0fda6', # Development-only API_key. See https://www.desmos.com/api/v1.8/docs/index.html#document-api-keys
            height=height.value, width=width.value, total_frames=len(os.listdir(FRAME_DIR)), download_images=DOWNLOAD_IMAGES, show_grid=SHOW_GRID, screenshot_size=SCREENSHOT_SIZE, screenshot_format=SCREENSHOT_FORMAT)

@app.route('/sendLogs.js')
def send_logs():
    return send_from_directory(app.static_folder, 'sendLogs.js')

@app.route('/stop')
def stop_app():
    hidden = tk.Tk()
    hidden.title('Hidden')
    hidden.geometry('1x1+-1+-1')
    hidden.withdraw()
    messagebox.showinfo(parent=hidden, title="Tips！", message='程序运行结束\n关闭弹窗将清理临时文件\n会关闭端口但不会关闭已打开的网页')
    hidden.destroy()
    hidden.mainloop()
    delete_temp_folder(FRAME_DIR)
    delete_temp_folder('datatemp')
    [shutil.rmtree('edged') if (len(os.listdir('edged')) == 0 or PUT_EDAGE_IMAGE == False) else False]
    [os.remove('InformationDictionary.txt') if os.path.exists('InformationDictionary.txt') else False]
    [os.remove('output.txt') if os.path.exists('output.txt') else False]
    [os.remove(js_path) if os.path.exists(js_path) else False]
    [os.remove(index_path) if os.path.exists(index_path) else False]
    [os.remove(calculator_path) if os.path.exists(calculator_path) else False]
    with open('data.txt', 'a', encoding='utf-8') as file:
        print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '临时文件清理完成', file=file)
    with open('data.txt', 'a', encoding='utf-8') as file:
        print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '本地服务器已断开连接，程序运行结束', file=file)
        print('', file=file)
        print('-'*100, file=file)
        print('', file=file)
    find_and_terminate_process("showdata.exe")
    os.kill(os.getpid(), signal.SIGINT)
    return 'Application stopped'

def delete_temp_folder(path):
    temp_dir = os.path.join(os.getcwd(), path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    multiprocessing.freeze_support()

    def backend(PORT, OPEN_BROWSER):
        if not os.path.exists('edged'):
            os.makedirs('edged')
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            print('|| Separated need to process frame %d, please wait... ||' % len(os.listdir(FRAME_DIR)), flush=True)
            with open('data.txt', 'a', encoding='utf-8') as file:
                print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '读取到tempETO文件夹内共{}帧'.format(len(os.listdir(FRAME_DIR))), file=file)
                print('', file=file)
            for frame_index in list(range(len(os.listdir(FRAME_DIR)))):
                try:
                    result = pool.apply_async(get_expressions, args=(frame_index,))
                    result.wait()
                    frame_latexETO.append(result.get()[0])
                    width.value = result.get()[1]
                    height.value = result.get()[2]
                except Exception as e:
                    for attempt in range(3):
                        time.sleep(1)
                        try:
                            result = pool.apply_async(get_expressions, args=(frame_index,))
                            result.wait()
                            frame_latexETO.append(result.get()[0])
                            width.value = result.get()[1]
                            height.value = result.get()[2]
                            break
                        except Exception as e:
                            if attempt == 2:
                                with open('data.txt', 'a', encoding='utf-8') as file:
                                    print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', 'Task failed for frame {}: {}'.format(frame_index, e), file=file)
                                print("Task failed for frame {}: {}".format(frame_index, e))
            pool.close()
            pool.join()

        print('|| http://127.0.0.1:%d/calculator ||' % PORT)
        with open('data.txt', 'a', encoding='utf-8') as file:
            print('['+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+']', '本地服务器将在http://127.0.0.1:{}运行'.format(PORT), file=file)
        if OPEN_BROWSER == False:
            pyperclip.copy('http://127.0.0.1:{}'.format(PORT))
            hidden = tk.Tk()
            hidden.title('Hidden')
            hidden.geometry('1x1+-1+-1')
            hidden.withdraw()
            messagebox.showinfo("Tips！", 'Running on http://127.0.0.1:{}\n链接已复制至剪切板'.format(PORT))
            hidden.destroy()
            hidden.mainloop()
        if OPEN_BROWSER:
            def open_browser():
                webbrowser.open('http://127.0.0.1:%d/calculator' % PORT)
            Timer(1, open_browser).start()
        app.run(host='127.0.0.1', port=PORT)

    backend(PORT, OPEN_BROWSER)

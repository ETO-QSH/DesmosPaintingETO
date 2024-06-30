#!/usr/bin/python
# -*- coding: utf-8 -*-

import potrace
import tkinter as tk
from PIL import Image, ImageTk
from threading import Timer
from flask_cors import CORS
import tkinter.font as tkfont
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from werkzeug.utils import secure_filename
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk, Canvas, filedialog, messagebox
from flask import Flask, jsonify, request, redirect, render_template, send_from_directory
import io, os, re, cv2, sys, copy, json, time, base64, numpy, shutil, signal, pyglet, random, zipfile, tempfile, colorsys, webbrowser, multiprocessing

def creat_index(PORT, path):
    global index_path
    if path != None:
        os.remove(path)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'), 'w') as f:
        index_text = '''
<script src='https://www.desmos.com/api/v1.8/calculator.js?apiKey={{ api_key }}'></script>
<html lang='en'>
   <head>
      <title>Desmos | Graphing Calculator</title>
      <link rel='icon' href='https://www.desmos.com/assets/img/apps/graphing/favicon.ico'>
      <script src="sendLogs.js"></script>
   </head>
   <div id='calculator' style='width: 100%; height: 100%;'></div>
   <script>
        var elt = document.getElementById('calculator');
        var calculator = Desmos.GraphingCalculator(elt);

        var inner = elt.getElementsByClassName('dcg-graph-outer')[0]; // The part of the screen with a visible grid
        var defaultState;
        var hiddenGraph;
        var latex;

        function sleep(milliseconds) {
            return new Promise(r => setTimeout(r, milliseconds));
        }

        async function changeGraph(latex) {
            //console.log(latex);

            var default_expressions = hiddenGraph.expressions.list.slice();

            for (var expr of latex) {
                hiddenGraph.expressions.list.push({
                    color: expr.color,
                    id: expr.id,
                    latex: expr.latex,
                    type: "expression"
                })
            }

            calculator.setState( hiddenGraph, {'allowUndo': false} );
            hiddenGraph.expressions.list = default_expressions;

            if (latex.length < 3000) {
                await sleep(5000);
            }
        }

        calculator.updateSettings({
            showGrid: {{ show_grid|tojson }},
            showXAxis: {{ show_grid|tojson }},
            showYAxis: {{ show_grid|tojson }}
        });

        calculator.setMathBounds({
            left: 0,
            right: {{ width }},
            bottom: 0,
            top: {{ height }}
        });

        calculator.setExpression({ id: 'frame', latex: 'f=0', sliderBounds: { step: 1, max: {{ total_frames }}, min: 0 } });
        calculator.setExpression({ id: 'lines', latex: 'L=0', sliderBounds: { step: 1, min: 0 } });
        calculator.setExpression({ id: 'start', latex: 'f\\->1' });

        // This is used to set expressions off screen
        hiddenGraph = calculator.getState();

        const interval = setInterval(() => {
            const f = calculator.HelperExpression({ latex: 'f' });
            f.observe('numericValue', () => {
                f.unobserve('numericValue');
                if (Number.isNaN(f.numericValue) || f.numericValue <= 0) return;
                clearInterval(interval);
                setTimeout(() => renderFrame(--f.numericValue), 3000); // Wait for additional keystrokes
            });
        }, 500);
        
        defaultState = calculator.getState(); // setBlank resets graph settings, this doesn't
        defaultState.graph.showGrid = defaultState.graph.showXAxis = defaultState.graph.showYAxis = {{ show_grid|tojson }};

        var tmpState = calculator.getState();
        tmpState.expressions.list.push({type: 'text', id: 'info', text: 'To begin rendering from start, please click the arrow button on the third line (In f->1 left) to set f=1 and wait. '});
        calculator.setState(tmpState);

        async function renderFrame(frame) {
            
            const requestData = (frame) => {
            
                return new Promise((resolve, reject) => {

                    xhr = new XMLHttpRequest();
                    xhr.open('GET', `http://127.0.0.1:5000/?frame=${frame}`);
                    xhr.send();
                    xhr.onload = () => {
                        latex = JSON.parse(xhr.response);

                        if (latex.result === null) {
                            reject(`frame: ${frame} could not be rendered.`);
                        } else {
                            resolve(latex.result);
                        }
                    }
                });
            }

            try { // Render each frame
                var response = await requestData(frame);
                while (frame < {{ total_frames }} && response) {
                    hiddenGraph.expressions.list[0].latex = 'f=' + (frame + 1);
                    hiddenGraph.expressions.list[1].latex = 'L=' + response.length;

                    // console.log('Lines for frame ' + (frame + 1) + ': ' + response.length);

                    await changeGraph(response);

                    const params = {
                        mode: 'contain',
                        mathBounds: { left: 0, bottom: 0, right: {{ width }}, top: {{ height }} },
                        width: {{ screenshot_size|tojson }}[0] || window.screen.width,
                        height: {{ screenshot_size|tojson }}[1] || window.screen.height,
                        targetPixelRatio: 1,
                        format: {{ screenshot_format|tojson }}
                    }
                    
                    function finishRender() {
                        return new Promise(resolve => {
                             // Waits for frame to render, takes a screenshot and runs handleScreenshot
                            calculator.asyncScreenshot(params, screenshot => {
                                handleScreenshot(screenshot, frame +1);
                                resolve('render has finished');
                            });
                        });
                    }

                    await finishRender();

                    // this delay happens after the frame is rendered
                    if (response.length >= 3000) { // a cooldown because this is a big file
                        await sleep(5000);
                    }

                    frame++;
                    response = await requestData(frame);
                }
            }
            catch (err) {
                console.log(err);
            }
        }

        const imgcont = document.createElement('a');
        document.body.appendChild(imgcont);
        async function handleScreenshot(screenshot, frame) {

            if (!{{ download_images|tojson }}) {
                return;
            }

            if ( {{ screenshot_format|tojson }} === 'png' ) {
                screenshot_uri = screenshot;
            }
            else if ( {{ screenshot_format|tojson }} === 'svg' ) {
                var svg_b64 = window.btoa(screenshot); // encode to base64
                screenshot_uri = "data:image/svg+xml;base64," + svg_b64;
            }

            consoleETO.log(screenshot_uri + String('frame-' + String(frame).padStart(5, '0')));
            imgcont.href = screenshot_uri;
            imgcont.download = 'frame-' + String(frame).padStart(5, '0');
            imgcont.innerHTML = `<img src= ${screenshot_uri}>`;
             // imgcont.click();
            
        }
   </script>
</html>
'''
        index_text = re.sub(r'http://127.0.0.1:\d+', 'http://127.0.0.1:{}'.format(PORT), index_text)
        f.write(index_text)
        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

def creat_sendLogs(PORT, path):
    global js_path
    if path != None:
        os.remove(path)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sendLogs.js'), 'w') as f:
        f.write('''function sendToServer(message) {{
  const data = JSON.stringify({{ message: message }});
  const xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://127.0.0.1:{}', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(data);
}}
consoleETO = {{
  log: function(message) {{
    console.log(message);
    sendToServer(message);
  }}
}};'''.format(PORT))
    js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sendLogs.js')

def creat_calculator(PORT, path):
    global calculator_path
    if path != None:
        os.remove(path)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calculator.html'), 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
<script>
    window.location.replace('http://127.0.0.1:{}/calculator');
</script>
</head>
</html>'''.format(PORT))
    calculator_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calculator.html')

def find_lolita_font_path(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ttf') and file.startswith('Lolita'):
                return os.path.join(root, file)
    return None

def find_index_html_path(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') and file.startswith('index'):
                return os.path.join(root, file)
    return None

def find_calculator_html_path(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') and file.startswith('calculator'):
                return os.path.join(root, file)
    return None

def find_sendLogs_js_path(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.js') and file.startswith('sendLogs'):
                return os.path.join(root, file)
    return None

def save_image_data(base64_image_data, name, e):
    if not os.path.exists('datatemp'):
        os.makedirs('datatemp')
    image_data = base64.b64decode(base64_image_data)
    with open('datatemp//{}.{}'.format(name, e), 'wb') as file:
        file.write(image_data)
        print('{}.{}'.format(name, e), 'Saved')
    if len(os.listdir('tempETO')) == len(os.listdir('datatemp')):
        gif_process = multiprocessing.Process(target=create_gif, args=('datatemp', int(form_data['get'][1]), len(os.listdir('datatemp')),))
        zip_process = multiprocessing.Process(target=create_zip, args=('datatemp',))
        gif_process.start()
        zip_process.start()
        gif_process.join()
        zip_process.join()
        hidden = tk.Tk()
        hidden.title('Hidden')
        hidden.geometry('1x1+-1+-1')
        hidden.protocol("WM_DELETE_WINDOW", on_close)
        hidden.withdraw()
        messagebox.showinfo(parent=hidden, title="Tips！", message='程序运行结束\n关闭弹窗将清理临时文件\n会关闭端口但不会关闭已打开的网页')
        hidden.destroy()
        stop_app()

PORT = random.randint(1, 65536)
temp_dir = tempfile.gettempdir()
index_path = find_index_html_path(temp_dir)
js_path = find_sendLogs_js_path(temp_dir)
calculator_path = find_calculator_html_path(temp_dir)
fontpath = [find_lolita_font_path(temp_dir) if find_lolita_font_path(temp_dir) != None else 'Lolita.ttf'][0]
creat_sendLogs(PORT, js_path)
creat_index(PORT, index_path)
creat_calculator(PORT, calculator_path)
pyglet.options['win32_gdi_font'] = True
pyglet.font.add_file(fontpath)
pyglet.font.load('Lolita')
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.static_folder = os.path.dirname(os.path.abspath(__file__))
CORS(app)
FRAME_DIR = 'tempETO'
FILE_EXT = 'png'
COLOUR = '#ffffff'
SCREENSHOT_SIZE = [ None, None ]
SCREENSHOT_FORMAT = 'png'
OPEN_BROWSER = True
BILATERAL_FILTER = False
DOWNLOAD_IMAGES = False
USE_L2_GRADIENT = False
SHOW_GRID = True
frame = multiprocessing.Value('i', 0)
height = multiprocessing.Value('i', 0, lock = False)
width = multiprocessing.Value('i', 0, lock = False)
frame_latex = 0

def start_backend_process(arguments):
    multiprocessing.freeze_support()
    p = multiprocessing.Process(target=backend, args=arguments)
    p.start()

def get_contours(filename, nudge = 0.33):
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if BILATERAL_FILTER:
        median = max(10, min(245, numpy.median(gray)))
        lower = int(max(0, (1 - nudge) * median))
        upper = int(min(255, (1 + nudge) * median))
        filtered = cv2.bilateralFilter(gray, 5, 50, 50)
        edged = cv2.Canny(filtered, lower, upper, L2gradient = USE_L2_GRADIENT)
    else:
        edged = cv2.Canny(gray, 30, 200)
    with frame.get_lock():
        frame.value += 1
        height.value = max(height.value, image.shape[0])
        width.value = max(width.value, image.shape[1])
    print('\r--> Frame %d/%d' % (frame.value, len(os.listdir(FRAME_DIR))), end='  ')
    return edged[::-1]

def get_trace(data):
    global hidden_window_data
    for i in range(len(data)):
        data[i][data[i] > 1] = 1
    bmp = potrace.Bitmap(data)
    turnpolicy = {'MINORITY': potrace.TURNPOLICY_MINORITY, 'MAJORITY': potrace.TURNPOLICY_MAJORITY, 'RANDOM': potrace.TURNPOLICY_MAJORITY, 'BLACK': potrace.TURNPOLICY_BLACK, 'WHITE': potrace.TURNPOLICY_WHITE, 'LEFT': potrace.TURNPOLICY_LEFT, 'RIGHT': potrace.TURNPOLICY_RIGHT}
    opticurve = {'True': 1, 'Flase': 0}
    path = bmp.trace(turdsize=int(hidden_window_data['turdsize']), turnpolicy=turnpolicy[hidden_window_data['turnpolicy']], alphamax=round(hidden_window_data['alphamax']*1.3333, 4), opticurve=opticurve[hidden_window_data['opticurve']], opttolerance=hidden_window_data['opttolerance'])
    return path

def get_latex(filename):
    latex = []
    path = get_trace(get_contours(filename))
    for curve in path.curves:
        segments = curve.segments
        start = curve.start_point
        for segment in segments:
            x0, y0 = start
            if segment.is_corner:
                x1, y1 = segment.c
                x2, y2 = segment.end_point
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x0, x1, y0, y1))
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x1, x2, y1, y2))
            else:
                x1, y1 = segment.c1
                x2, y2 = segment.c2
                x3, y3 = segment.end_point
                latex.append('((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)),\
                (1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))' % \
                (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = segment.end_point
    return latex

def get_expressions(frame):
    exprid = 0
    exprs = []
    for expr in get_latex(FRAME_DIR + '/frame%d.%s' % (frame+1, FILE_EXT)):
        exprid += 1
        exprs.append({'id': 'expr-' + str(exprid), 'latex': expr, 'color': COLOUR, 'secret': True})
    return exprs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if request.args.get('frame') is not None:
            frame = int(request.args.get('frame'))
            if frame >= len(os.listdir(FRAME_DIR)):
                return {'result': None}
            return json.dumps({'result': frame_latexETO[frame]})
        else:
            return redirect('/calculator')
    elif request.method == 'POST':
        data = request.get_json()
        message = str(data.get('message'))
        if DOWNLOAD_IMAGES == True:
            if message[11:14] == 'png':
               save_image_data(message[22:-11], message[-11:], message[11:14])
            elif message[11:14] == 'svg':
               save_image_data(message[26:-11], message[-11:], message[11:14])
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
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)
    return 'Application stopped'

class Tooltip:
    def __init__(self, widget, text, color='black', width=90):
        self.widget = widget
        self.text = text
        self.color = color
        self.width = width
        self.tooltip = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip is None:
            x, y, _, _ = self.widget.bbox('insert')
            x += self.widget.winfo_rootx() + 15
            y += self.widget.winfo_rooty() + 15
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f'+{x}+{y}')
            text = tk.Text(self.tooltip, wrap='none', width=self.width, background='#f0f0f0')
            text.pack()
            heightETO = self.text.count('\n') + 1
            text.configure(height=heightETO)
            bold_font = tkfont.Font(family=my_font_llt_8[0], size=my_font_llt_8[1])
            bold_font.configure(weight='bold')
            pattern = r'‘(.*?)’'
            matches = re.findall(pattern, self.text)
            start = 0
            for match in matches:
                index = self.text.find(match, start)
                text.insert('end', self.text[start:index])
                text.insert('end', match, ('bold',))
                start = index + len(match)
            text.insert('end', self.text[start:].replace('‘', '').replace('’', ''))
            text.configure(state='disabled')
            text.configure(font=my_font_llt_8)
            text.configure(foreground=self.color)
            text.tag_configure('bold', font=bold_font)

    def hide_tooltip(self, event):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None

class newEntry(tk.Entry):
    def __init__(self, master=None, placeholder='PLACEHOLDER', color='grey', name=None, textvariable=None, state=None):
        super().__init__(master, takefocus=False)
        self.name = name
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.bind('<FocusIn>', self.foc_in)
        self.bind('<FocusOut>', self.foc_out)
        self.bind('<Button-1>', self.on_click)
        if textvariable is None:
            self.textvariable = None
        else:
            self.textvariable = textvariable
        self.put_placeholder()
        self.custom_font = tkfont.Font(family=my_font_llt_8[0], size=my_font_llt_8[1])
        self.configure(font=self.custom_font, justify='center')
        if state:
            self.configure(state=state)

    def put_placeholder(self):
        self.config(state='normal')
        if self.textvariable is None or not self.textvariable.get():
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color
        if not self.winfo_name() in ['entryT', 'load_entry_1', 'load_entry_2']:
            self.config(state='disabled')

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if self.textvariable is None or not self.textvariable.get():
            self.put_placeholder()

    def on_click(self, *args):
        self.focus_set()

    def set_placeholder(self, placeholder):
        self.placeholder = placeholder
        self.after(0, self.put_placeholder)

class Separat:
    def __init__(self, master, width, height, bg='white', color='#ffffff', line='common', x=0, y=0):
        self.canvas = Canvas(master, width=width, height=height, background=bg, highlightthickness=0, relief='flat', bd=0)
        if line == '-common-':
            self.canvas.create_line(0, 4, width, 4, fill=color, width=2)
        elif line == '-dash-':
            self.canvas.create_line(0, 4, width, 4, fill=color, dash=(10, 3), width=2)
        elif line == '-dash_point-':
            self.canvas.create_line(0, 4, width, 4, fill=color, dash=(5, 2, 3), width=2)
        elif line == '-point-':
            self.canvas.create_line(0, 4, width, 4, fill=color, dash=(2, 2), width=2)
        elif line == '-double_line-':
            self.canvas.create_line(0, 2, width, 2, fill=color, width=1)
            self.canvas.create_line(0, 4, width, 4, fill=color, width=1)
        elif line == '-double_dash-':
            self.canvas.create_line(0, 2, width, 2, fill=color, dash=(5, 2), width=1)
            self.canvas.create_line(0, 4, width, 4, fill=color, dash=(5, 2), width=1)
        if line == '+common+':
            self.canvas.create_line(4, 0, 4, height, fill=color, width=2)  # 竖线
        elif line == '+dash+':
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(10, 3), width=2)  # 竖线
        elif line == '+dash_point+':
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(5, 2, 3), width=2)  # 竖线
        elif line == '+point+':
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(2, 2), width=2)  # 竖线
        elif line == '+double_line+':
            self.canvas.create_line(2, 0, 2, height, fill=color, width=1)  # 竖线
            self.canvas.create_line(4, 0, 4, height, fill=color, width=1)  # 竖线
        elif line == '+double_dash+':
            self.canvas.create_line(2, 0, 2, width, fill=color, dash=(5, 2), width=1)  # 竖线
            self.canvas.create_line(4, 0, 4, width, fill=color, dash=(5, 2), width=1)  # 竖线
        self.canvas.place(x=x, y=y)

    def hide(self):
        self.canvas.place_forget()

def img2base64(path):
    img = Image.open(path)
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format='PNG')
    img_byte_array = img_byte_array.getvalue()
    encoded_string = base64.b64encode(img_byte_array).decode('utf-8')
    return encoded_string

def extract_gif_frames(input_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with Image.open(input_path) as im:
        try:
            while True:
                im.seek(im.tell() + 1)
                frame = im.copy()
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                width, height = frame.size
                white_image = Image.new('RGB', (width, height), (255, 255, 255))
                white_image.paste(frame, (0, 0), mask=frame)
                output_file = os.path.join(output_dir, f"frame{im.tell()}.png")
                white_image.save(output_file)
        except EOFError:
            pass

def extract_frames(input_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cap = cv2.VideoCapture(input_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame_idx in range(total_frames):
        ret, frame = cap.read()
        if ret:
            frame[numpy.where(frame[:, :, 3] == 0)] = [255, 255, 255, 255]
            output_file = os.path.join(output_dir, f"frame{frame_idx+1}.png")
            cv2.imwrite(output_file, frame)
    cap.release()

def copy_file_to_temp(form_data):
    file_dir, file_name = os.path.split(form_data)
    temp_dir = os.path.join(os.getcwd(), 'tempETO')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    dst_file = os.path.join(temp_dir, 'frame1.png')
    shutil.copy2(form_data, dst_file)

def delete_temp_folder(path):
    temp_dir = os.path.join(os.getcwd(), path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def toggle_selection_1():
    global counter1
    counter1 += 1
    if counter1 % 2 == 0:
        var1.set(0)
    if var1.get() == 0:
        rgb_entry_0.config(state='disabled')
        rgb_entry_1.config(state='disabled')
        rgb_entry_2.config(state='disabled')
        hsv_entry_0.config(state='disabled')
        hsv_entry_1.config(state='disabled')
        hsv_entry_2.config(state='disabled')
    elif var1.get() == 1:
        rgb_entry_0.config(state='normal')
        rgb_entry_1.config(state='normal')
        rgb_entry_2.config(state='normal')
        hsv_entry_0.config(state='disabled')
        hsv_entry_1.config(state='disabled')
        hsv_entry_2.config(state='disabled')
    elif var1.get() == 2:
        rgb_entry_0.config(state='disabled')
        rgb_entry_1.config(state='disabled')
        rgb_entry_2.config(state='disabled')
        hsv_entry_0.config(state='normal')
        hsv_entry_1.config(state='normal')
        hsv_entry_2.config(state='normal')

def open_file(entry):
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_path = filedialog.askopenfilename(initialdir=desktop_path, filetypes=[('Image Or Video Files', '*.mp4;*.jpg;*.png;*.gif;')])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, os.path.normpath(file_path))
        entry.config(fg='black')

def on_drop(event, entries):
    global window_modle
    if window_modle == 0:
        file_paths = []
        temp = drop_label.tk.splitlist(event.data)
        for i in range(len(temp)):
            file_path = os.path.normpath(temp[i])
            if os.path.isfile(file_path):
                file_paths.append(file_path)
                break
            else:
                continue
        if file_paths:
            file_name, file_extension = os.path.splitext(file_paths[0])
            if file_extension.lower() in ['.jpg', '.png', '.gif', '.mp4']:
                entries[0].delete(0, tk.END)
                entries[0].insert(0, file_paths[0])
                entries[0].config(fg='black')

def on_root_click(event, entries):
    if event.widget == root:
        for i, entry in enumerate(entries):
            if i == 0:
                if not entry.get() or not os.path.exists(entry.get()):
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.placeholder)
            elif i == 7:
                if not entry.get():
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.placeholder)
                try:
                    num = float(entry.get())
                    numList = str(num).split('.')
                    if not ((9 >= int(numList[0]) >= 0 and 9 >= int(numList[1]) >= 0 and num != 0.0) or (int(numList[0]) == 10 and int(numList[1]) == 0)):
                        entry.config(state='normal')
                        entry.delete(0, tk.END)
                        entry.insert(0, entry.placeholder)
                except Exception as e:
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.placeholder)
            elif i == 8:
                if not entry.get() or entry.get().isdecimal() == False:
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.placeholder)
                elif not 1 <= int(entry.get()) <= 60:
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.placeholder)
            else:
                if not entry.get() or not entry.get().isdigit() or not -1 < int(entry.get()) < 256:
                    entry.delete(0, tk.END)
                    entry.insert(0, entry.placeholder)
            entry.config(fg='gray')
        if var1.get() == 1:
            entries[1].config(fg='black')
            entries[2].config(fg='black')
            entries[3].config(fg='black')
            entries[1].config(fg='gray')
            entries[2].config(fg='gray')
            entries[3].config(fg='gray')
            if (entries[1].get() and entries[1].get().isdigit() and -1 < int(entries[1].get()) < 256) and (entries[2].get() and entries[2].get().isdigit() and -1 < int(entries[2].get()) < 256) and (entries[3].get() and entries[3].get().isdigit() and -1 < int(entries[3].get()) < 256):
                v_rbg = (int(entries[1].get()) / 255, int(entries[2].get()) / 255, int(entries[3].get()) / 255)
                entries[4].set_placeholder(str(int(colorsys.rgb_to_hsv(v_rbg[0], v_rbg[1], v_rbg[2])[0] * 255 + 0.5)))
                entries[5].set_placeholder(str(int(colorsys.rgb_to_hsv(v_rbg[0], v_rbg[1], v_rbg[2])[1] * 255 + 0.5)))
                entries[6].set_placeholder(str(int(colorsys.rgb_to_hsv(v_rbg[0], v_rbg[1], v_rbg[2])[2] * 255 + 0.5)))
            else:
                entries[4].set_placeholder('H')
                entries[5].set_placeholder('S')
                entries[6].set_placeholder('V')
        if var1.get() == 2:
            entries[1].config(fg='gray')
            entries[2].config(fg='gray')
            entries[3].config(fg='gray')
            entries[1].config(fg='black')
            entries[2].config(fg='black')
            entries[3].config(fg='black')
            if (entries[4].get() and entries[4].get().isdigit() and -1 < int(entries[4].get()) < 256) and (entries[5].get() and entries[5].get().isdigit() and -1 < int(entries[5].get()) < 256) and (entries[6].get() and entries[6].get().isdigit() and -1 < int(entries[6].get()) < 256):
                v_hsv = (int(entries[4].get()) / 255, int(entries[5].get()) / 255, int(entries[6].get()) / 255)
                entries[1].set_placeholder(str(int(colorsys.hsv_to_rgb(v_hsv[0], v_hsv[1], v_hsv[2])[0] * 255 + 0.5)))
                entries[2].set_placeholder(str(int(colorsys.hsv_to_rgb(v_hsv[0], v_hsv[1], v_hsv[2])[1] * 255 + 0.5)))
                entries[3].set_placeholder(str(int(colorsys.hsv_to_rgb(v_hsv[0], v_hsv[1], v_hsv[2])[2] * 255 + 0.5)))
            else:
                entries[1].set_placeholder('R')
                entries[2].set_placeholder('B')
                entries[3].set_placeholder('G')
        canvas = tk.Canvas(root, width=170, height=10, bg=['#{}{}{}'.format(format(int(rgb_entry_0.get()), '02X'), format(int(rgb_entry_1.get()), '02X'), format(int(rgb_entry_2.get()), '02X')) if (rgb_entry_0.get().isdigit() and rgb_entry_1.get().isdigit() and rgb_entry_2.get().isdigit()) else 'white'][0])
        canvas.place(x=8, y=175)
        root.focus()

def create_checkbuttons(root):
    global variables
    checkbuttons = []
    variables = []

    var01 = tk.IntVar()
    cb1 = tk.Checkbutton(root, text='禁用双边过滤器', font=my_font_llt_8, variable=var01, takefocus=False)
    cb1.place(x=5, y=210)
    checkbuttons.append(cb1)
    variables.append(var01)

    var02 = tk.IntVar()
    cb2 = tk.Checkbutton(root, text='减少L2梯度行数', font=my_font_llt_8, variable=var02, takefocus=False)
    cb2.place(x=5, y=230)
    checkbuttons.append(cb2)
    variables.append(var02)

    var03 = tk.IntVar()
    cb3 = tk.Checkbutton(root, text='自动下载', font=my_font_llt_8, variable=var03, takefocus=False)
    cb3.place(x=115, y=210)
    checkbuttons.append(cb3)
    variables.append(var03)

    var04 = tk.IntVar()
    cb4 = tk.Checkbutton(root, text='去除网格', font=my_font_llt_8, variable=var04, takefocus=False)
    cb4.place(x=115, y=230)
    checkbuttons.append(cb4)
    variables.append(var04)

    var05 = tk.IntVar()
    cb4 = tk.Checkbutton(root, text='不自动打开web', font=my_font_llt_8, variable=var05, takefocus=False)
    cb4.place(x=5, y=250)
    checkbuttons.append(cb4)
    variables.append(var05)

    var06 = tk.IntVar()
    cb4 = tk.Checkbutton(root, text='矢量保存', font=my_font_llt_8, variable=var06, takefocus=False)
    cb4.place(x=115, y=250)
    checkbuttons.append(cb4)
    variables.append(var06)

def get_selected_options(variables):
    selected_options = []
    for var in variables:
        if var.get():
            selected_options.append(var.get())
    return selected_options

def on_close():
    sys.exit()

root = TkinterDnD.Tk()
root.title('ETO')
root.protocol("WM_DELETE_WINDOW", on_close)
#root.wm_attributes("-topmost", 1)
root.resizable(False, False)
window_modle = 0

my_font_llt_10_b = ('Lolita', 10, 'bold')
my_font_llt_12 = ('Lolita', 12)
my_font_llt_10 = ('Lolita', 10)
my_font_llt_9 = ('Lolita', 9)
my_font_llt_8 = ('Lolita', 8)
my_font_llt_6 = ('Lolita', 6)

counter0 = 0
counter1 = 0
var1 = tk.IntVar()
rgb = tk.StringVar()
hsv = tk.StringVar()
int_var = tk.IntVar()
float_var = tk.DoubleVar()

label = tk.Label(root, text='倍率', font=my_font_llt_9)
label.place(x=27, y=306, width=30, height=25, anchor='w')

label = tk.Label(root, text='帧率', font=my_font_llt_9)
label.place(x=107, y=306, width=30, height=25, anchor='w')

rgb_entry_0 = newEntry(root, textvariable=rgb, state='disabled', placeholder='R')
rgb_entry_0.place(x=90, y=125, width=30, height=20)

rgb_entry_1 = newEntry(root, textvariable=rgb, state='disabled', placeholder='G')
rgb_entry_1.place(x=120, y=125, width=30, height=20)

rgb_entry_2 = newEntry(root, textvariable=rgb, state='disabled', placeholder='B')
rgb_entry_2.place(x=150, y=125, width=30, height=20)

hsv_entry_0 = newEntry(root, textvariable=hsv, state='disabled', placeholder='H')
hsv_entry_0.place(x=90, y=150, width=30, height=20)

hsv_entry_1 = newEntry(root, textvariable=hsv, state='disabled', placeholder='S')
hsv_entry_1.place(x=120, y=150, width=30, height=20)

hsv_entry_2 = newEntry(root, textvariable=hsv, state='disabled', placeholder='V')
hsv_entry_2.place(x=150, y=150, width=30, height=20)

rgb_radio = tk.Radiobutton(root, text='RBG色彩', variable=var1, value=1, command=toggle_selection_1, font=my_font_llt_9, takefocus=False)
rgb_radio.place(x=0, y=135, width=90, height=20, anchor='w')

hsv_radio = tk.Radiobutton(root, text='HSV色彩', variable=var1, value=2, command=toggle_selection_1, font=my_font_llt_9, takefocus=False)
hsv_radio.place(x=0, y=160, width=90, height=20, anchor='w')

load_entry_1 = newEntry(root, textvariable=float_var, state='normal', name=f'load_entry_1', placeholder='1.00')
load_entry_1.place(x=55, y=298, width=45, height=16)

load_entry_2 = newEntry(root, textvariable=int_var, state='normal', name=f'load_entry_2', placeholder='10')
load_entry_2.place(x=135, y=298, width=45, height=16)

label = tk.Label(root, text='1.  文件上传', font=my_font_llt_9)
label.place(x=0, y=20, width=90, height=25, anchor='w')

label = tk.Label(root, text='2.  线条颜色', font=my_font_llt_9)
label.place(x=0, y=110, width=90, height=25, anchor='w')

label = tk.Label(root, text='3.  简化选项', font=my_font_llt_9)
label.place(x=0, y=200, width=90, height=25, anchor='w')

label = tk.Label(root, text='4.  素材导出', font=my_font_llt_9)
label.place(x=0, y=285, width=90, height=25, anchor='w')

label = tk.Label(root, text='5.  算法参数', font=my_font_llt_9)
label.place(x=0, y=330, width=90, height=25, anchor='w')

canvas = tk.Canvas(root, width=170, height=10, bg='white')
canvas.place(x=8, y=175)

checkbuttons = create_checkbuttons(root)

entries = []
buttons = []

entryT = newEntry(root, placeholder='Image Or Video Files', name=f'entryT', state='normal')
entryT.place(x=16, y=5+2*20, width=125, height=20, anchor='w')
button = tk.Button(root, text='open', command=lambda entry=entryT, func=open_file:func(entryT), relief=tk.RIDGE, font=my_font_llt_8, takefocus=False)
button.place(x=16+125, y=45, width=39, height=23, anchor='w')
buttons.append(button)
entries.append(entryT)
entries.append(rgb_entry_0)
entries.append(rgb_entry_1)
entries.append(rgb_entry_2)
entries.append(hsv_entry_0)
entries.append(hsv_entry_1)
entries.append(hsv_entry_2)
entries.append(load_entry_1)
entries.append(load_entry_2)

drop_label = tk.Label(root, text='拖拽上传区域', bg='white', relief='ridge', width=20, height=5, font=my_font_llt_10, fg='gray')
drop_label.place(x=15, y=55, width=165, height=40)
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', lambda event:on_drop(event, entries))

for entry in entries:
    entry.bind('<FocusIn>', lambda event:event.widget.config(fg='black'))
    entry.bind('<FocusOut>', lambda event:event.widget.config(fg='grey'))
    entry.bind('<Button-1>', lambda event:event.widget.focus_set())

root.bind('<Button-1>', lambda event:on_root_click(event, entries))

button_texts = [[' • 支持‘选择、填写、拖入’文件 \n      如果文件不满足条件就会被拒绝 \n      理论支持所有常见图片视频格式 \n      这里选择这几种是为了测试方便 \n      其他格式可以自行用ffmpeg处理 ‘ ’',
                 ' • 你可以通过‘RGB’或者‘HSV’的形式来填写颜色 \n      然后‘点击空白处’会进行同步并显示至下面的条带中 ‘ ’',
                 ' • 禁用双边过滤器：减少行数与双边过滤器更简单的渲染 \n • 减少L2梯度行数：减少L2梯度的行数，以便更快地渲染 \n • 自动下载：自动下载渲染帧（会保存在默认浏览器的下载位置） \n • 去除网格：在图形的背景中隐藏网格 \n • 不自动打开web：运行渲染服务器而不打开web浏览器 \n • 矢量保存：以矢量图的形式保存（SVG）而不是点阵图（PNG） ‘ ’',
                 ' • 倍率：指输出图片相对于原图的长宽百分百大小 \n                 支持‘0.1~10的不连续一位小数输入’ \n                 具体缩放运算时会进行四舍五入 \n                 也就是缩小有可能丢失精度提高质感 \n                 放大则会保留更多的曲线细节 \n • 帧率：指合成的gif每秒期望播放帧的数量 \n                 支持‘1~60的整数输入’ \n                 计算时会转为毫秒计帧间隔时长 \n                 会通过插值尽可能保证长时间帧率稳定 \n                 具体来说比较整的数可能会有好的效果 ‘ ’',
                 ' • 该项目主要基于‘potrace’ \n      这里是一些可以调节的算法参数 \n      如果不了解可以使用默认的数值 \n      以下是命令行中基本的解释 \n • turnpolicy <p>：解决路径选择分歧的策略 \n • turdsize <i>：抑制大小最多为n的斑点 \n • alphamax <f>：角阈值参数 \n • opticurve <b>：关闭曲线优化 \n • opttolerance <f>：曲线优化容差 ‘ ’'],
                [12, 102, 192, 277, 322], [27, 42, 48, 36, 33]]
buttons = []

for i, text in enumerate(button_texts[0]):
    square = tk.Label(root, bg='#f0f0f0', width=3, height=1)
    square.place(x=82, y=button_texts[1][i], width=14, height=14)
    label = tk.Label(square, text='?', bg='#f0f0f0', fg='black', font=my_font_llt_10_b)
    label.pack(expand=True)
    tooltip = Tooltip(square, f'{button_texts[0][i]}',  color='blue', width=button_texts[2][i])
    buttons.append(square)

def open_web(url):
    webbrowser.open(url)

def putbase64img(x, y, width, height, size, Str, url):
    global tk_img
    canvas_px = tk.Canvas(root, width=width, height=height)
    canvas_px.place(x=x, y=y, width=width, height=height)
    binary_string = Str
    img_data = io.BytesIO(base64.b64decode(binary_string))
    img = Image.open(img_data)
    resized_img = img.resize(size, Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(resized_img)
    canvas_px.create_image(0, 0, anchor=tk.NW, image=tk_img)
    canvas_px.bind("<Button-1>", lambda event, url=url: open_web(url))

def get_form_data():
    global BILATERAL_FILTER, COLOUR, SCREENSHOT_FORMAT, SHOW_GRID, OPEN_BROWSER, DOWNLOAD_IMAGES, USE_L2_GRADIENT, SCREENSHOT_SIZE, FRAME_DIR, frame_latex, form_data
    form_data = {'radio': 0, 'path': '', 'color': '#ffffff', 'mode': [0, 0, 0, 0, 0, 0], 'size': '0x0', 'get': [load_entry_1.get(), load_entry_2.get()]}
    error_messages = []
    if entryT.get() == 'Image Or Video Files':
        error_messages.append(' · 请填写需处理文件地址')
    else:
        form_data['path'] = entryT.get()
        e = '{}'.format(os.path.splitext(form_data['path'])[1][1:])
        if e in ['png', 'jpg']:
            form_data['radio'] = 1
        elif e in ['gif', 'mp4']:
            form_data['radio'] = 2
    if rgb_entry_0.get() == 'R' or rgb_entry_1.get() == 'G' or rgb_entry_2.get() == 'B':
        error_messages.append(' · 未填写线条颜色')
    else:
        form_data['color'] = '#{}{}{}'.format(format(int(rgb_entry_0.get()), '02X'), format(int(rgb_entry_1.get()), '02X'), format(int(rgb_entry_2.get()), '02X'))
    form_data['mode'] = [var.get() for var in variables]
    if form_data['mode'][0] == 1:
        BILATERAL_FILTER = True
    if form_data['mode'][1] == 1:
        USE_L2_GRADIENT = True
    if form_data['mode'][2] == 1:
        DOWNLOAD_IMAGES = True
        try:
            if str(form_data['radio']) == '1':
                file = cv2.imread(form_data['path'])
                form_data['size'] = '{}x{}'.format(int(file.shape[1]*float(load_entry_1.get()) + 0.5), int(file.shape[0]*float(load_entry_1.get()) + 0.5))
            elif str(form_data['radio']) == '2':
                file = cv2.VideoCapture(form_data['path'])
                form_data['size'] = '{}x{}'.format(int(int(file.get(cv2.CAP_PROP_FRAME_WIDTH))*float(load_entry_1.get()) + 0.5), int(int(file.get(cv2.CAP_PROP_FRAME_HEIGHT))*float(load_entry_1.get()) + 0.5))
                file.release()
        except Exception as e:
            print(e)
            error_messages.append(' · cv2解析出现错误')
        if form_data['mode'][5] == 0:
            SCREENSHOT_FORMAT = 'png'
        elif form_data['mode'][5] == 1:
            SCREENSHOT_FORMAT = 'svg'
    if form_data['mode'][3] == 1:
        SHOW_GRID = False
    if form_data['mode'][4] == 1:
        OPEN_BROWSER = False
    if len(error_messages) == 0:
        if form_data['radio'] == 1:
            try:
                copy_file_to_temp(form_data['path'])
            except shutil.SameFileError:
                pass
        elif form_data['radio'] == 2:
            if '{}'.format(os.path.splitext(form_data['path'])[1][1:]) == 'gif':
                extract_gif_frames(form_data['path'], 'tempETO')
            else:
                extract_frames(form_data['path'], 'tempETO')
        frame_latex = range(len(os.listdir(FRAME_DIR)))
        COLOUR = '{}'.format(form_data['color'])
        SCREENSHOT_SIZE = [int(i) for i in form_data['size'].split('x')]
        if OPEN_BROWSER == False:
            message = messagebox.showinfo("Tips！", 'Running on http://127.0.0.1:{}'.format(PORT))
        root.destroy()
        start_backend_process((js_path, index_path, calculator_path, PORT))
    else:
        messagebox.showerror('ERROR！', '\n'.join(error_messages))
    print('-'*100)

variableInt = tk.IntVar()
variableStr = tk.StringVar()

hidden_window_data = {'turnpolicy': 'MINORITY', 'level-B2W': 0.5, 'alphamax': 1.0, 'opttolerance': 0.5, 'turdsize': '2', 'opticurve': 'True'}

def callback():
    global hidden_window_data, b, c, d, e, f, g, variableStr, variableInt
    hidden_window_data['turnpolicy'] = variableStr.get()
    # hidden_window_data['level-B2W'] = c.get()
    hidden_window_data['alphamax'] = d.get()
    hidden_window_data['opttolerance'] = e.get()
    hidden_window_data['turdsize'] = f.get()
    hidden_window_data['opticurve'] = g.get()

hidden_window = 0

putbase64img(x=150, y=8, width=30, height=24, size=(30, 24), url='https://github.com/ETO-QSH', Str=b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACRklEQVR4nO1aPW7CMBR+rsLaEzDTAyB17DU6IoR6AE5QcQ0qVLHRa8BWiQN0YmFm6Eokd3qpCbH9nuPghJdvCo7tvO97n38SDFprDUJRcJcogmjyCNEiiCaPEC2CaPII0SKIJo8QLQJyVkXB+QxqMJAihCpfSCFehlJQQf7l/TNBLM1ju5helV0IUCaODcxyalmbYQrxgBeV5Dc5wCYvGmwXUzjtlnDaLS/KDvMRHOajSoXbCJPrg6OeCBRDoMq+9zoEAP5jdgpwz7gSQCrEzwEZXkz2x5Rx3Bzr8RAAegf0AogXIPNXSQ8cry6EzmGNOGA9HpKCpvYVs14ZnXAAAMDsw75dWb0p6z0fojsgVuZvBbYDkKBvzOF9an0f6mTZBZYD6mQ3tC1VuFCByQ4wCdgeVkVysj8W5evxMCjQJnepJAdQyJso1zF/t22O8DqASt5HrI4TYohme57TAdzMc4Joen2n9mN1QCh5yuoQ4oTz7zM5hjIGj9/We/27gO0GJ1Mcm4Y6y5XFOnA6IPbsHUI+1hJo68e7CnCcQHUJl1TyfYDLCRRnxF5NYoK8E/Q5gbI7DCUfMvyoz2KtAnWyd0vynHbst0HuxBjL8j+vM3Ldp68VuW6UfUDbxjUHnfkixMkqB7UcMNkfG89+aP/Udp1wQPJ9wD2jFyB1AKlRCNC2T1VNwuRaeUCiy+u6C1VJVnmeQ5ZlUk+JKFwGpZ0YvfyXBQ8OSzozLfqkOEK0CKLJI0SLIJo8QrQIoskjRIsgmjxCa63/AE9sk6rkBl4RAAAAAElFTkSuQmCC')

separator_0 = Separat(root, width=500, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=0)
separator_3 = Separat(root, width=8, height=500, bg='#f0f0f0', color='#c0c0c0', line='+dash+', x=-1, y=9)
separator_4 = Separat(root, width=8, height=500, bg='#f0f0f0', color='#c0c0c0', line='+dash+', x=185, y=9)
separator_1 = Separat(root, width=500, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=374)
separator_2 = Separat(root, width=500, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=504)

def hidden_window_def():
    global hidden_window, separator_1, separator_2
    x, y = root.winfo_rootx() - 8, root.winfo_rooty() - 31
    if hidden_window % 2 == 0:
        label_h0.place_forget()
        # label_h1.place_forget()
        label_h2.place_forget()
        label_h3.place_forget()
        label_h4.place_forget()
        b.place_forget()
        # c.place_forget()
        d.place_forget()
        e.place_forget()
        f.place_forget()
        g.place_forget()
        unfold_button_0.place(x=135, y=320, width=40, height=20)
        unfold_button_1.place_forget()
        get_data_button.place(x=12, y=345, width=170, height=25)
        separator_1.canvas.destroy()
        separator_2.canvas.destroy()
        separator_1 = Separat(root, width=500, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=374)
        [root.geometry('192x380+{}+{}'.format(int(root.winfo_screenwidth() / 2 - 96), int(root.winfo_screenheight() / 2 - 240))) if hidden_window == 0 else root.geometry('192x380+{}+{}'.format(x, y))]
        hidden_window += 1
    elif hidden_window % 2 == 1:
        label_h0.place(x=10, y=355, width=90, height=10, anchor='w')
        # label_h1.place(x=10, y=58, width=90, height=10, anchor='w')
        label_h2.place(x=10, y=385, width=90, height=10, anchor='w')
        label_h3.place(x=10, y=415, width=90, height=10, anchor='w')
        label_h4.place(x=10, y=450, width=90, height=25, anchor='w')
        b.place(x=142, y=355, width=80, height=20, anchor='center')
        # c.place(x=100, y=30)
        d.place(x=100, y=365)
        e.place(x=100, y=395)
        f.place(x=103, y=443)
        g.place(x=143, y=443)
        unfold_button_0.place_forget()
        unfold_button_1.place(x=135, y=320, width=40, height=20)
        get_data_button.place(x=12, y=475, width=170, height=25)
        separator_1.canvas.destroy()
        separator_2.canvas.destroy()
        separator_2 = Separat(root, width=500, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=504)
        root.geometry('192x510+{}+{}'.format(x, y))
        hidden_window += 1

label_h0 = tk.Label(root, font=my_font_llt_8, text='turnpolicy')
#label_h1 = tk.Label(root, font=my_font_llt_8, text='level-B2W')
label_h2 = tk.Label(root, font=my_font_llt_8, text='alphamax')
label_h3 = tk.Label(root, font=my_font_llt_8, text='opttolerance')
label_h4 = tk.Label(root, font=my_font_llt_8, text='turdsize\nopticurve')


b = ttk.Combobox(root, textvariable=variableStr, values=['MINORITY', 'MAJORITY', 'RANDOM', 'BLACK', 'WHITE', 'LEFT', 'RIGHT'])
b.config(font=my_font_llt_6)
b['state'] = 'readonly'
root.option_add('*TCombobox*Listbox.font', my_font_llt_6)
#style = ttk.Style()
#style.configure('my.TMenubutton', font=my_font_llt_6)
#b = ttk.OptionMenu(root, variableStr, 'MINORITY', 'MAJORITY', 'RANDOM', 'BLACK', 'WHITE', 'LEFT', 'RIGHT')
#b['style'] = 'my.TMenubutton'
#menu = b['menu']
#[menu.insert_separator(i) for i in range(1, 11, 2)]
#menu.configure(font=my_font_llt_6)
variableStr.set(hidden_window_data['turnpolicy'])

# c = tk.Scale(root, from_=0, to=1.00, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=0.01, width=8, takefocus=False, sliderlength=15)
# c.configure(font=my_font_llt_6)
# c.set(hidden_window_data['level-B2W'])

d = tk.Scale(root, from_=0, to=1.00, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=0.01, width=8, takefocus=False, sliderlength=15)
d.configure(font=my_font_llt_6)
d.set(hidden_window_data['alphamax'])

e = tk.Scale(root, from_=0, to=1.00, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=0.01, width=8, takefocus=False, sliderlength=15)
e.configure(font=my_font_llt_6)
e.set(hidden_window_data['opttolerance'])

f = tk.Spinbox(root, from_=0, to=25, width=5, wrap=True, takefocus=False, justify='center')
f.configure(font=my_font_llt_6)
f.delete(0, 'end')
f.insert(0, hidden_window_data['turdsize'])

g = tk.Spinbox(root, values=('True', 'False'), width=5, wrap=True, takefocus=False, justify='center')
g.configure(font=my_font_llt_6)
g.delete(0, 'end')
g.insert(0, hidden_window_data['opticurve'])

unfold_button_0 = tk.Button(root, text='展开▽', command=hidden_window_def, font=my_font_llt_8, compound='center', relief='ridge', bd=0, anchor='center', takefocus=False)

unfold_button_1 = tk.Button(root, text='收起△', command=hidden_window_def, font=my_font_llt_8, compound='center', relief='ridge', bd=0, anchor='center', takefocus=False)

get_data_button = tk.Button(root, text='开始绘制', command=get_form_data, font=my_font_llt_9, compound='center', relief='ridge', bd=2, takefocus=False)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    hidden_window_def()

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

    def create_zip(folder_path):
        if not os.path.exists('output'):
            os.makedirs('output')
        files = [f for f in os.listdir(folder_path)]
        if all(f.endswith('.svg') for f in files):
            zip_path = os.path.join(os.path.dirname(folder_path), 'output', 'output-svg-{}.zip'.format(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))))
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for svg_file in files:
                    svg_path = os.path.join(folder_path, svg_file)
                    zip_file.write(svg_path, os.path.basename(svg_path))
        elif all(f.endswith('.png') for f in files):
            zip_path = os.path.join(os.path.dirname(folder_path), 'output', 'output-png-{}.zip'.format(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))))
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for png_file in files:
                    png_path = os.path.join(folder_path, png_file)
                    zip_file.write(png_path, os.path.basename(png_path))

    def backend(js_path, index_path, calculator_path, PORT):
        global frame_latexETO
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            print('Processing %d frames... Please wait for processing to finish before running on frontend' % len(os.listdir(FRAME_DIR)))
            frame_latexETO = pool.map(get_expressions, frame_latex)
            print('|| http://127.0.0.1:%d/calculator ||' % PORT)
            if OPEN_BROWSER:
                def open_browser():
                    webbrowser.open('http://127.0.0.1:%d/calculator' % PORT)
                Timer(1, open_browser).start()
            app.run(host='127.0.0.1', port=PORT)
            delete_temp_folder('tempETO')
            delete_temp_folder('datatemp')
            [os.remove(js_path) if os.path.exists(js_path) else False]
            [os.remove(index_path) if os.path.exists(index_path) else False]
            [os.remove(calculator_path) if os.path.exists(calculator_path) else False]
            sys.exit()

    root.mainloop()

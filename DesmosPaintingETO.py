#!/usr/bin/python
# -*- coding: utf-8 -*-
import tkinter as tk
from threading import Timer
from flask_cors import CORS
from collections import deque
import tkinter.font as tkfont
from PIL import Image, ImageTk
from svglib.svglib import svg2rlg
import xml.etree.ElementTree as ET
from reportlab.graphics import renderPM
from tkinterdnd2 import DND_FILES, TkinterDnD
from flask import Flask, jsonify, request, redirect, render_template
from tkinter import ttk, Canvas, filedialog, messagebox, DISABLED, END, NORMAL
import io, os, re, cv2, sys, copy, json, time, numpy, base64, pyglet, random, shutil, zipfile, \
       datetime, tempfile, colorsys, pyperclip, threading, subprocess, webbrowser, multiprocessing

# os.path.dirname(os.path.abspath(__file__)), os.path.dirname(os.path.realpath(sys.executable))

def creat_index(PORT, path):
    global index_path
    if path != None: os.remove(path)
    with open(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'index.html'), 'w') as file:
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
        consoleETO.log("screenshot-" + inner.offsetWidth + "-" + inner.offsetHeight);

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
                                handleScreenshot(screenshot, frame + 1);
                                resolve('render has fileinished');
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
        file.write(re.sub(r'http://127.0.0.1:\d+', 'http://127.0.0.1:{}'.format(PORT), index_text))
        index_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'index.html')

def creat_sendLogs(PORT, path):
    global js_path
    if path != None: os.remove(path)
    with open(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'sendLogs.js'), 'w') as file:
        file.write('''function sendToServer(message) {{
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
    js_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'sendLogs.js')

def creat_calculator(PORT, path):
    global calculator_path
    if path != None: os.remove(path)
    with open(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'calculator.html'), 'w') as file:
        file.write('''<!DOCTYPE html>
<html>
<head>
<script>
    window.location.replace('http://127.0.0.1:{}/calculator');
</script>
</head>
</html>'''.format(PORT))
    calculator_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'calculator.html')

def find_path(directory, filename):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(os.path.splitext(filename)[1]) and file.startswith(os.path.splitext(filename)[0]):
                return os.path.join(root, file)
    return None

def getTime():
    return datetime.datetime.now().strftime("[%H:%M:%S] ")


temp_dir = tempfile.gettempdir()
js_path = find_path(temp_dir, 'sendLogs.js')
index_path = find_path(temp_dir, 'index.html')
calculator_path = find_path(temp_dir, 'calculator.html')

pdf_path = find_path(temp_dir, '教程.pdf')
pdf_path = pdf_path if pdf_path else '教程.pdf'
font_path = find_path(temp_dir, 'Lolita.ttf')
font_path = font_path if font_path else 'Lolita.ttf'
potrace_path = find_path(temp_dir, 'potrace.exe')
potrace_path = potrace_path if potrace_path else 'potrace.exe'

pyglet.options['win32_gdi_font'] = True
pyglet.font.add_file(font_path)
pyglet.font.load('Lolita')

COLOUR = '#ffffff'
FRAME_DIR = 'temp'
SCREENSHOT_SIZE = [None, None]
SCREENSHOT_FORMAT = 'png'
BILATERAL_FILTER = False
DOWNLOAD_IMAGES = False
PUT_EDAGE_IMAGE = False
OPEN_BROWSER = True
SHOW_GRID = True

hidden_window = 0

class Tooltip:
    def __init__(self, widget, text, color='black', width=90):
        self.widget, self.text, self.color, self.width, self.tooltip = widget, text, color, width, None
        self.widget.bind('<Enter>', self.show_tooltip); self.widget.bind('<Leave>', self.hide_tooltip)

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
            matches = re.findall(r'‘(.*?)’', self.text)
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
        self.name, self.placeholder, self.placeholder_color, self.default_fg_color = name, placeholder, color, self['fg']
        self.bind('<FocusIn>', self.foc_in); self.bind('<FocusOut>', self.foc_out); self.bind('<Button-1>', self.on_click)
        if textvariable is None: self.textvariable = None
        else: self.textvariable = textvariable
        self.put_placeholder()
        self.custom_font = tkfont.Font(family=my_font_llt_8[0], size=my_font_llt_8[1])
        self.configure(font=self.custom_font, justify='center')
        if state: self.configure(state=state)

    def put_placeholder(self):
        self.config(state='normal')
        if self.textvariable is None or not self.textvariable.get():
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color
        if not self.winfo_name() in ['entryT', 'load_entry_1', 'load_entry_2']: self.config(state='disabled')

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
            self.canvas.create_line(4, 0, 4, height, fill=color, width=2)
        elif line == '+dash+':
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(10, 3), width=2)
        elif line == '+dash_point+':
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(5, 2, 3), width=2)
        elif line == '+point+':
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(2, 2), width=2)
        elif line == '+double_line+':
            self.canvas.create_line(2, 0, 2, height, fill=color, width=1)
            self.canvas.create_line(4, 0, 4, height, fill=color, width=1)
        elif line == '+double_dash+':
            self.canvas.create_line(2, 0, 2, height, fill=color, dash=(4, 2), width=1)
            self.canvas.create_line(4, 0, 4, height, fill=color, dash=(4, 2), width=1)
        self.canvas.place(x=x, y=y)


class re_Text():
    def __init__(self, queue):
        self.queue = queue

    def write(self, content):
        self.queue.append(content)

    def flush(self):
        pass


class GUI():
    def __init__(self, root):
        self.msg_queue = deque()
        self.initGUI(root)

    def show_msg(self):
        save_queue = self.msg_queue
        while self.msg_queue:
            content = self.msg_queue.popleft()
            if not isinstance(content, bytes):
                self.text.config(state=NORMAL)
                self.text.insert(tk.END, content, 'w')
                c_t = re.findall(r'^\[\d{2}:\d{2}:\d{2}]', content)
                if c_t: self.apply_tag('c', c_t[0])
                self.text.config(state=DISABLED)
        self.msg_queue = save_queue
        self.text.see(END)
        self.root.after(50, self.show_msg)

    def initGUI(self, root):
        self.root = root

        self.scrollBar = tk.Scrollbar(self.root)

        self.text = tk.Text(self.root, yscrollcommand=self.scrollBar.set, state=DISABLED, relief='flat', font=my_font_llt_8, fg='black', bg='#fcfcfc')
        self.text.place(x=390, y=10, width=175, height=365)
        self.scrollBar.config(command=self.text.yview)

        self.text.bind('<1>', lambda e: 'break')
        self.text.bind('<Shift-1>', lambda e: 'break')
        self.text.bind('<B1-Motion>', lambda e: 'break')

        self.text.tag_configure('c', foreground='#ff7f7f')
        self.text.tag_config('w', lmargin2=50)

        self.root.after(50, self.show_msg)

    def delLastText(self):
        self.msg_queue.pop()
        self.msg_queue.pop()

    def apply_tag(self, tag_name, search_string, replacement_string=None):
        start_pos = '1.0'
        while True:
            start_pos = self.text.search(search_string, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = self.text.index(start_pos + '+%dc' % len(search_string))
            if replacement_string:
                self.text.delete(start_pos, end_pos)
                self.text.insert(start_pos, replacement_string)
            self.text.tag_add(tag_name, start_pos, end_pos)
            start_pos = end_pos

def extract_gif_frames(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with Image.open(input_path) as im:
        try:
            print(' ')
            while True:
                im.seek(im.tell() + 1)
                _frame = im.copy()
                if _frame.mode != 'RGBA': _frame = _frame.convert('RGBA')
                width, height = _frame.size
                white_image = Image.new('RGB', (width, height), (255, 255, 255))
                white_image.paste(_frame, (0, 0), mask=_frame)
                output_file = os.path.join(output_dir, f"frame{im.tell()}.png")
                white_image.save(output_file)
                myGUI.delLastText()
                print(getTime() + '已经分离出需处理的帧{}帧'.format(im.tell()))
        except EOFError: pass

def extract_frames(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(input_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(' ')
    for frame_idx in range(total_frames):
        myGUI.delLastText()
        print(getTime() + '已经分离出需处理的帧{}帧'.format(frame_idx+1))
        ret, _frame = cap.read()
        if ret:
            try: _frame[numpy.where(_frame[:, :, 3] == 0)] = [255, 255, 255, 255]
            except: pass
            output_file = os.path.join(output_dir, f"frame{frame_idx+1}.png")
            cv2.imwrite(output_file, _frame)
    cap.release()

def copy_file_to_temp(form_data):
    temp_dir = os.path.join(os.getcwd(), FRAME_DIR)
    os.makedirs(temp_dir, exist_ok=True)
    dst_file = os.path.join(temp_dir, 'frame1.png')
    shutil.copy2(form_data, dst_file)

def toggle_selection_1():
    global counter
    counter += 1
    if counter % 2 == 0:
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

def open_file_l(entry):
    global buttons
    file_path = filedialog.askopenfilename(initialdir='./', filetypes=[('Image Or Video Files', '*.mp4;*.jpg;*.png;*.gif;')])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, os.path.normpath(file_path))
        entry.config(fg='black')
    button = tk.Button(root, text='open', relief=tk.RIDGE, font=my_font_llt_8, takefocus=False)
    button.bind('<Button-1>', lambda event, entry=entryT, func=open_file_l: func(entry))
    button.bind('<Button-3>', lambda event, entry=entryT, func=open_file_r: func(entry))
    button.place(x=16 + 125, y=45, width=39, height=23, anchor='w')
    del buttons[0]
    buttons.insert(0, button)

def open_file_r(entry):
    global buttons
    file_path = pyperclip.paste()
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, os.path.normpath(file_path))
        entry.config(fg='black')
    button = tk.Button(root, text='open', relief=tk.RIDGE, font=my_font_llt_8, takefocus=False)
    button.bind('<Button-1>', lambda event, entry=entryT, func=open_file_l: func(entry))
    button.bind('<Button-3>', lambda event, entry=entryT, func=open_file_r: func(entry))
    button.place(x=16+125, y=45, width=39, height=23, anchor='w')
    del buttons[0]
    buttons.insert(0, button)

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
            else: continue
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
                except:
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
        canvas = tk.Canvas(root, width=170, height=10, bg='#{}{}{}'.format(format(int(rgb_entry_0.get()), '02X'), format(int(rgb_entry_1.get()), '02X'), format(int(rgb_entry_2.get()), '02X')) if (rgb_entry_0.get().isdigit() and rgb_entry_1.get().isdigit() and rgb_entry_2.get().isdigit()) else 'white')
        canvas.place(x=8, y=175)
        root.focus()

def create_checkbuttons(root):
    global variables
    checkbuttons = []
    variables = []

    var01 = tk.IntVar()
    cb1 = tk.Checkbutton(root, text='启用双边过滤器', font=my_font_llt_8, variable=var01, takefocus=False)
    cb1.place(x=5, y=210)
    checkbuttons.append(cb1)
    variables.append(var01)

    var02 = tk.IntVar()
    cb2 = tk.Checkbutton(root, text='输出检测轮廓图', font=my_font_llt_8, variable=var02, takefocus=False)
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
    return [var.get() for var in variables if var.get()]

def delete_temp_folder(path):
    temp_dir = os.path.join(os.getcwd(), path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def cv_imread(filePath):
    cv_img = cv2.imdecode(np.fromfile(filePath, dtype=np.uint8), -1)
    return cv_img

def on_close():
    delete_temp_folder(FRAME_DIR)
    if os.path.exists(js_path): os.remove(js_path)
    if os.path.exists(index_path): os.remove(index_path)
    if os.path.exists(calculator_path): os.remove(calculator_path)
    sys.exit(0)

my_font_llt_10_b = ('Lolita', 10, 'bold')
my_font_llt_12 = ('Lolita', 12)
my_font_llt_10 = ('Lolita', 10)
my_font_llt_9 = ('Lolita', 9)
my_font_llt_8 = ('Lolita', 8)
my_font_llt_7 = ('Lolita', 7)
my_font_llt_6 = ('Lolita', 6)

root = TkinterDnD.Tk()
root.title('ETO')
root.protocol("WM_DELETE_WINDOW", on_close)
root.resizable(False, False)
myGUI = GUI(root)
sys.stdout = re_Text(myGUI.msg_queue)
window_modle = 0
names = locals()

counter = 0
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
button = tk.Button(root, text='open', relief=tk.RIDGE, font=my_font_llt_8, takefocus=False)
button.bind('<Button-1>', lambda event, entry=entryT, func=open_file_l: func(entry))
button.bind('<Button-3>', lambda event, entry=entryT, func=open_file_r: func(entry))
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
drop_label.dnd_bind('<<Drop>>', lambda event: on_drop(event, entries))

for entry in entries:
    entry.bind('<FocusIn>', lambda event: event.widget.config(fg='black'))
    entry.bind('<FocusOut>', lambda event: event.widget.config(fg='grey'))
    entry.bind('<Button-1>', lambda event: event.widget.focus_set())

root.bind('<Button-1>', lambda event: on_root_click(event, entries))

button_texts = [[' • 支持‘选择 填写 拖入 粘贴’文件 \n      如果文件不满足条件就会被拒绝 \n      理论支持所有常见图片视频格式 \n      这里选择这几种是为了测试方便 \n      其他格式可以自行用ffmpeg处理 ‘ ’',
                 ' • 你可以通过‘RGB’或者‘HSV’的形式来填写颜色 \n      然后‘点击空白处’会进行同步并显示至下面的条带中 \n      若其中的值‘无效’则默认为黑色‘#000000’ ‘ ’',
                 ' • 启用双边过滤器：实现双边过滤器更简单粗略的渲染 \n • 输出检测轮廓图：输出边缘检测结果，是cv2调参的主要依据 \n • 自动下载：自动下载渲染帧（会以 .gif 和 .zip 形式保存） \n • 去除网格：在图形的背景中隐藏网格 \n • 不自动打开web：运行渲染服务器而不打开web浏览器 \n • 矢量保存：以矢量图的形式保存（SVG）而不是点阵图（PNG） ‘ ’',
                 ' • 倍率：指输出图片相对于原图的长宽百分百大小 \n                 支持‘0.1~10的不连续一位小数输入’ \n                 具体缩放运算时会进行四舍五入 \n                 也就是缩小有可能丢失精度提高质感 \n                 放大则会保留更多的曲线细节 \n • 帧率：指合成的gif每秒期望播放帧的数量 \n                 支持‘1~60的整数输入’ \n                 计算时会转为毫秒计帧间隔时长 \n                 会通过插值尽可能保证长时间帧率稳定 \n                 具体来说比较整的数可能会有好的效果 ‘ ’',
                 ' • 该项目主要基于‘cv2’和‘potrace’ \n      这里是一些可以调节的算法参数 \n      如果不了解可以使用默认的数值 \n • 以下是‘potrace’所使用的参数 \n      turnpolicy <p>：解决路径选择分歧的策略 \n      turdsize <i>：抑制大小最多为n的斑点 \n      alphamax <f>：角阈值参数 \n      opticurve <b>：开启曲线优化 \n      opttolerance <f>：曲线优化容差 \n      unit <i>：将输出量化为1/unit像素 \n • 以下是‘cv2’所使用的参数 \n      sigmaColor <i>：颜色域滤波器标准差 \n      sigmaSpace <i>：空间域滤波器标准差 \n      diameter <i>：滤波器的直径 \n      L2gradient <b>：采用欧几里得范数 \n      lower <i>：计算Canny边缘检测器的下阈值 \n      upper <i>：计算Canny边缘检测器的上阈值 \n • 实践中先进行cv2处理而后进行potrace处理 \n      选择输出检测轮廓图可以获得第一阶段结果 \n      若没有启用双边过滤器则可调节lower和upper \n      默认情况下调节这两个参数对图像影响最大 \n      清晰度高线条少的图像基本不用调参 \n      如果最后计算出的数据太多会导致网页过卡 \n      modified <i>：如果图片显示不完全就调大 ‘ ’'],
                [12, 102, 192, 277, 322], [28, 42, 48, 37, 36]]
buttons = []

for i, text in enumerate(button_texts[0]):
    square = tk.Label(root, bg='#f0f0f0', width=3, height=1)
    square.place(x=82, y=button_texts[1][i], width=14, height=14)
    label = tk.Label(square, text='?', bg='#f0f0f0', fg='black', font=my_font_llt_10_b)
    label.pack(expand=True)
    tooltip = Tooltip(square, f'{button_texts[0][i]}',  color='blue', width=button_texts[2][i])
    buttons.append(square)

def putbase64img(x, y, width, height, size, b64s, url, pdf_path):
    global tk_img
    canvas_px = tk.Canvas(root, width=width, height=height)
    canvas_px.place(x=x, y=y, width=width, height=height)
    img = Image.open(io.BytesIO(base64.b64decode(b64s)))
    resized_img = img.resize(size, Image.Resampling.LANCZOS)
    tk_img = ImageTk.PhotoImage(resized_img)
    canvas_px.create_image(0, 0, anchor=tk.NW, image=tk_img)
    canvas_px.bind("<Button-3>", lambda event, uri=url: webbrowser.open(url))
    canvas_px.bind("<Button-1>", lambda event, uri=url: webbrowser.open(pdf_path))
putbase64img(x=150, y=8, width=30, height=24, size=(30, 24), url='https://github.com/ETO-QSH/DesmosPaintingETO', pdf_path=pdf_path,
             b64s=b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACRklEQVR4nO1aPW7CMBR+rsLaEzDTAyB17DU6IoR6AE5QcQ0qVLHRa8BWiQN0YmF \
                    m6Eokd3qpCbH9nuPghJdvCo7tvO97n38SDFprDUJRcJcogmjyCNEiiCaPEC2CaPII0SKIJo8QLQJyVkXB+QxqMJAihCpfSCFehlJQQf7l/TNBLM \
                    1ju5helV0IUCaODcxyalmbYQrxgBeV5Dc5wCYvGmwXUzjtlnDaLS/KDvMRHOajSoXbCJPrg6OeCBRDoMq+9zoEAP5jdgpwz7gSQCrEzwEZXkz2x \
                    5Rx3Bzr8RAAegf0AogXIPNXSQ8cry6EzmGNOGA9HpKCpvYVs14ZnXAAAMDsw75dWb0p6z0fojsgVuZvBbYDkKBvzOF9an0f6mTZBZYD6mQ3tC1V \
                    uFCByQ4wCdgeVkVysj8W5evxMCjQJnepJAdQyJso1zF/t22O8DqASt5HrI4TYohme57TAdzMc4Joen2n9mN1QCh5yuoQ4oTz7zM5hjIGj9/We/2 \
                    7gO0GJ1Mcm4Y6y5XFOnA6IPbsHUI+1hJo68e7CnCcQHUJl1TyfYDLCRRnxF5NYoK8E/Q5gbI7DCUfMvyoz2KtAnWyd0vynHbst0HuxBjL8j+vM3 \
                    Ldp68VuW6UfUDbxjUHnfkixMkqB7UcMNkfG89+aP/Udp1wQPJ9wD2jFyB1AKlRCNC2T1VNwuRaeUCiy+u6C1VJVnmeQ5ZlUk+JKFwGpZ0YvfyXB \
                    Q8OSzozLfqkOEK0CKLJI0SLIJo8QrQIoskjRIsgmjxCa63/AE9sk6rkBl4RAAAAAElFTkSuQmCC')


app = Flask(__name__, template_folder=os.path.dirname(os.path.realpath(sys.executable)))
app.static_folder = os.path.dirname(os.path.realpath(sys.executable))
CORS(app)

mpHeight = multiprocessing.Value('i', 10, lock=False)
mpWidth = multiprocessing.Value('i', 10, lock=False)
x_y_side = multiprocessing.Array('f', [0.0, 0.0])
frame = multiprocessing.Value('i', 0)

def create_zip(folder_path):
    os.makedirs('output', exist_ok=True)
    files = [f for f in os.listdir(folder_path)]
    if all(f.endswith('.svg') for f in files):
        zip_path = os.path.join(os.path.dirname(folder_path), 'output', f'output-svg-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.zip')
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for svg_file in files:
                svg_path = os.path.join(folder_path, svg_file)
                zip_file.write(svg_path, os.path.basename(svg_path))
    elif all(f.endswith('.png') for f in files):
        zip_path = os.path.join(os.path.dirname(folder_path), 'output', f'output-png-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.zip')
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for png_file in files:
                png_path = os.path.join(folder_path, png_file)
                zip_file.write(png_path, os.path.basename(png_path))

def create_gif(folder_path, dur, num):
    os.makedirs('output', exist_ok=True)
    files = sorted([f for f in os.listdir(folder_path)])
    durations_list = copy.deepcopy([int(1000/dur)]*num)
    for i in range(1, int((num/dur)*1000)-int(1000/dur)*num+1):
        durations_list[int((i-0.5)*(int((num/(int((num/dur)*1000)-int(1000/dur)*num))+0.5))+0.5)] = int(1000/dur)+1
    if all(f.endswith('.svg') for f in files):
        frames = []
        try:
            for svg_file in files:
                svg_path = os.path.join(folder_path, svg_file)
                drawing = svg2rlg(svg_path)
                png_data = io.BytesIO()
                renderPM.drawToFile(drawing, png_data, fmt="PNG")
                png_data.seek(0)
                frames.append(Image.open(png_data))
            gif_path = os.path.join(os.path.dirname(folder_path), 'output', f'output-svg-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.gif')
            frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=durations_list, loop=0)
        except:
            print(getTime() + '未安装reportlab，无法拼接svg为gif（非必要功能）')
        finally:
            for frame in frames: frame.close()
    elif all(f.endswith('.png') for f in files):
        frames = [Image.open(os.path.join(folder_path, f)) for f in files]
        gif_path = os.path.join(os.path.dirname(folder_path), 'output', f'output-png-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.gif')
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=durations_list, loop=0)

def SVGtransformation(path, X, Y, aX, aY, sx, sy):
    with open(path, 'r') as file: content = file.read()
    matches = re.findall(r'<g transform=.*?>', content)
    matches = re.findall(r'".*?"', matches[0])
    content = content.replace(matches[0],'" translate({},{}) scale({},{})"'.format(round(-X*aX, 6), round(-Y*aY, 6), round(aX, 6), round(aY, 6)))
    matches = re.findall(r'width="\d+" height="\d+"', content)
    content = content.replace(matches[0], 'width="{}" height="{}"'.format(sx, sy))
    with open(path, 'w') as file: file.write(content)

def PNGtransformation(path, original_sizes, display_sizes, mode):
    original_width, original_height = original_sizes
    display_width, display_height = display_sizes
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
    os.makedirs('datatemp', exist_ok=True)
    image_data = base64.b64decode(base64_image_data)
    with open('datatemp//{}.{}'.format(name, e), 'wb') as file: file.write(image_data)
    if SCREENSHOT_SIZE[0] > x_y_side[0] or SCREENSHOT_SIZE[1] > x_y_side[1]:
        PNGtransformation('datatemp//{}.{}'.format(name, e), SCREENSHOT_SIZE, x_y_side, e)
    print(getTime() + '图片{}.{}已保存至datatemp'.format(name, e))
    if len(os.listdir(FRAME_DIR)) == len(os.listdir('datatemp')):
        print(getTime() + '所有帧已收录完全，开始合成gif和zip')
        gif_process = multiprocessing.Process(target=create_gif, args=('datatemp', int(form_data['get'][1]), len(os.listdir('datatemp')),))
        zip_process = multiprocessing.Process(target=create_zip, args=('datatemp',))
        gif_process.start(); zip_process.start()
        gif_process.join(); zip_process.join()
        print(getTime() + '打包gif和zip结束，已保存至output文件夹')
        stop_app()

def Svg2Curves(svg_path):
    List, root = [], ET.parse(svg_path).getroot()
    transform_attribute = root.find('.//{http://www.w3.org/2000/svg}g').get('transform')
    input_txt = root.find('.//{http://www.w3.org/2000/svg}path').get('d')
    scale_x, scale_y = transform_attribute.split('scale(')[1].split(')')[0].split(',')
    for x in input_txt.split(' '):
        i = [y for y in x]
        if len(set(i).intersection({'M', 'L', 'H', 'V', 'C', 'S', 'Q', 'T', 'A', 'm', 'l', 'h', 'v', 'c', 's', 'q', 't', 'a'})) > 0:
            List.append(x[0])
            List.append(int(x[1:]))
        elif len(set(i).intersection({'Z', 'z'})) > 0:
            List.append(int(x[:-1]))
            List.append(x[-1])
        else: List.append(int(x))
    i, x0, y0, mode, svgOutput = 0, 0, 0, None, []
    for x, y in enumerate(List):
        if x >= i:
            if (not y in ['M', 'L', 'H', 'V', 'C', 'S', 'Q', 'T', 'A', 'Z', 'm', 'l', 'h', 'v', 'c', 's', 'q', 't', 'a', 'z']) and mode != None:
                y = mode
                t = True
            else:
                t = False
            if str(y) in ['Z', 'z', 'Zz']:
                mode = 'Zz'
                # print('Zz：闭合曲线由({}, {})至({}, {})'.format(x0, y0, _x, _y), file=file)
                svgOutput.append({mode: None})
            elif str(y) == 'M':
                mode = str(y)
                x0, y0 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('M：设置起点为({}, {})'.format(x0, y0), file=file)
                svgOutput.append({mode: [(x0, y0)]})
                _x, _y = x0, y0
                i = x + 3 - t
            elif str(y) == 'm':
                mode = str(y)
                x0, y0 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('m：设置起点为({}, {})'.format(x0, y0), file=file)
                svgOutput.append({mode: [(x0, y0)]})
                _x, _y = x0, y0
                i = x + 3 - t
            elif str(y) == 'L':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('L：绘制直线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 'l':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('l：绘制直线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 'H':
                mode = str(y)
                x1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit'])
                # print('H：绘制水平线由({}, {})至({}, {})'.format(x0, y0, x1, y0), file=file)
                svgOutput.append({mode: [(x0, y0), (x1, y0)]})
                x0 = x1
                i = x + 2 - t
            elif str(y) == 'h':
                mode = str(y)
                x1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit'])
                # print('h：绘制水平线由({}, {})至({}, {})'.format(x0, y0, x1, y0), file=file)
                svgOutput.append({mode: [(x0, y0), (x1, y0)]})
                x0 = x1
                i = x + 2 - t
            elif str(y) == 'V':
                mode = str(y)
                y1 = round(List[x + 1 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('V：绘制竖直线由({}, {})至({}, {})'.format(x0, y0, x0, y1), file=file)
                y0 = y1
                i = x + 2 - t
                svgOutput.append({mode: [(x0, y0), (x0, y1)]})
            elif str(y) == 'v':
                mode = str(y)
                y1 = round(y0 + List[x + 1 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('v：绘制竖直线由({}, {})至({}, {})'.format(x0, y0, x0, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x0, y1)]})
                y0 = y1
                i = x + 2 - t
            elif str(y) == 'C':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x3, y3 = round(List[x + 5 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 6 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('C：绘制三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {})和c2({}, {})'.format(x0, y0, x3, y3, x1, y1, x2, y2), file=file)
                svgOutput.append({mode: [(x0, y0), (x3, y3), (x1, y1), (x2, y2)]})
                x0, y0 = x3, y3
                i = x + 7 - t
            elif str(y) == 'c':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(x0 + List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x3, y3 = round(x0 + List[x + 5 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 6 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('c：绘制三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {})和c2({}, {})'.format(x0, y0, x3, y3, x1, y1, x2, y2), file=file)
                svgOutput.append({mode: [(x0, y0), (x3, y3), (x1, y1), (x2, y2)]})
                x0, y0 = x3, y3
                i = x + 7 - t
            elif str(y) == 'S':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('S：绘制平滑三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 's':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(x0 + List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('s：绘制平滑三次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 'Q':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('Q：绘制二次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 'q':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(x0 + List[x + 3 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 4 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('q：绘制二次贝塞尔曲线由({}, {})至({}, {})，控制点为c1({}, {}))'.format(x0, y0, x2, y2, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x2, y2), (x1, y1)]})
                x0, y0 = x2, y2
                i = x + 5 - t
            elif str(y) == 'T':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('T：绘制平滑的二次贝塞尔曲线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 't':
                mode = str(y)
                x1, y1 = round(x0 + List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(y0 + List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                # print('t：绘制平滑的二次贝塞尔曲线由({}, {})至({}, {})'.format(x0, y0, x1, y1), file=file)
                svgOutput.append({mode: [(x0, y0), (x1, y1)]})
                x0, y0 = x1, y1
                i = x + 3 - t
            elif str(y) == 'A':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                r1, r2, r3 = List[x + 3 - t], int(List[x + 4 - t]), int(List[x + 5 - t])
                # print('A：绘制椭圆弧由({}, {})至({}, {})，双轴半径为({}, {})且角度为{}°的{}时针{}弧'.format(x0, y0, x2, y2, x1, y1, r1, ['顺' if r3 else '逆'], ['大' if r2 else '小']), file=file)
                svgOutput.append({mode: [(x0, y0), (x2, y2), (x1, y1), (r1, r2, r3)]})
                x0, y0 = x2, y2
                i = x + 8 - t
            elif str(y) == 'a':
                mode = str(y)
                x1, y1 = round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                x2, y2 = x0 + round(List[x + 1 - t] * float(scale_x), hidden_window_data['unit']), y0 + round(List[x + 2 - t] * float(scale_y) * -1, hidden_window_data['unit'])
                r1, r2, r3 = List[x + 3 - t], int(List[x + 4 - t]), int(List[x + 5 - t])
                # print('a：绘制椭圆弧由({}, {})至({}, {})，双轴半径为({}, {})且角度为{}°的{}时针{}弧'.format(x0, y0, x2, y2, x1, y1, r1, ['顺' if r3 else '逆'], ['大' if r2 else '小']), file=file)
                svgOutput.append({mode: [(x0, y0), (x2, y2), (x1, y1), (r1, r2, r3)]})
                x0, y0 = x2, y2
                i = x + 8 - t
    return svgOutput

def get_contours(filename, framevalue, PORT, BILATERAL_FILTER):
    lower, upper = hidden_window_data['lower'], hidden_window_data['upper']
    USE_L2_GRADIENT = {'True': True, 'False': False}
    image = cv_imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if BILATERAL_FILTER:
        filtered = cv2.bilateralFilter(gray, int(hidden_window_data['diameter']), int(hidden_window_data['sigmaColor']), int(hidden_window_data['sigmaSpace']))
        edged = cv2.Canny(filtered, lower, upper, L2gradient=USE_L2_GRADIENT[hidden_window_data['L2gradient']])
    else: edged = cv2.Canny(gray, lower, upper, L2gradient=USE_L2_GRADIENT[hidden_window_data['L2gradient']])
    with frame.get_lock(): mpHeight.value, mpWidth.value = image.shape[0], image.shape[1]
    print(getTime() + '正在处理帧 {}/{}'.format(framevalue, len(os.listdir(FRAME_DIR))))
    img = Image.fromarray(edged, mode='L')
    img_name = 'edged//edged_{}_{}.'.format(int(framevalue) - 1, PORT)
    while not os.path.exists(img_name + 'bmp'): img.save(img_name + 'bmp')
    command = 'potrace {} -z {} -t {} -a {} {} -O {} -s -i -u {} --flat --output {}'.format(
        img_name + 'bmp', hidden_window_data['turnpolicy'], hidden_window_data['turdsize'], round(hidden_window_data['alphamax']*1.3333, 4),
        '' if hidden_window_data['opticurve'] == 'True' else '-n', hidden_window_data['opttolerance'], 10**hidden_window_data['unit'], img_name + 'svg')
    while not os.path.exists(img_name + 'svg'): subprocess.run(command, shell=True, capture_output=True, text=True)
    return Svg2Curves(img_name + 'svg')

def get_latex(filename, framevalue, latex, PORT, BILATERAL_FILTER):
    svgOutput = get_contours(filename, framevalue, PORT, BILATERAL_FILTER)
    for path in svgOutput:
        if list(path.keys())[0] in ['L', 'l']:
            vars = path[list(path.keys())[0]]
            latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (vars[0][0], vars[1][0], vars[0][1], vars[1][1]))
        elif list(path.keys())[0] in ['C', 'c']:
            vars = path[list(path.keys())[0]]
            latex.append('((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)), \
                          (1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))' %
            (vars[0][0], vars[2][0], vars[2][0], vars[3][0], vars[2][0], vars[3][0], vars[3][0], vars[1][0],
             vars[0][1], vars[2][1], vars[2][1], vars[3][1], vars[2][1], vars[3][1], vars[3][1], vars[1][1]))
    return latex

def get_expressions(frame, PORT, COLOUR, BILATERAL_FILTER):
    exps = [{'id': 'expr-' + str(eid), 'latex': expr, 'color': COLOUR, 'secret': True} for eid, expr in enumerate(
             get_latex(FRAME_DIR + '/frame%d.%s' % (frame+1, 'png'), frame+1, [], PORT, BILATERAL_FILTER), 1)]
    return exps, mpWidth.value, mpHeight.value

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if request.args.get('frame') is not None:
            frame = int(request.args.get('frame'))
            if frame >= len(os.listdir(FRAME_DIR)):
                if DOWNLOAD_IMAGES == False: stop_app()
                return {'result': None}
            print(getTime() + '发送第{}帧数据'.format(frame+1))
            return json.dumps({'result': list(frame_latexETO)[frame]})
        else: return redirect('/calculator')
    elif request.method == 'POST':
        data = request.get_json()
        message = str(data.get('message'))
        if message[0:10] != 'screenshot':
            if DOWNLOAD_IMAGES == True:
                if message[11:14] == 'png': save_image_data(message[22:-11], message[-11:], message[11:14])
                elif message[11:14] == 'svg': save_image_data(message[26:-11], message[-11:], message[11:14])
        else:
            _, X, Y = message.split('-')
            x_y_side[0] = float(X)
            x_y_side[1] = float(Y)
        return jsonify({"message": "POST request received"})

@app.route("/calculator")
def client():
    return render_template('index.html', api_key='dcb31709b452b1cf9dc26972add0fda6', # Development-only API_key. See https://www.desmos.com/api/v1.8/docs/index.html#document-api-keys
            height=mpHeight.value, width=mpWidth.value, total_frames=len(os.listdir(FRAME_DIR)), download_images=DOWNLOAD_IMAGES, show_grid=SHOW_GRID, screenshot_size=SCREENSHOT_SIZE, screenshot_format=SCREENSHOT_FORMAT)

@app.route('/sendLogs.js')
def send_logs():
    return render_template('sendLogs.js')

@app.route('/stop')
def stop_app():
    print(getTime() + '程序运行结束弹窗')
    messagebox.showinfo("Tips！", '程序运行结束\n关闭弹窗将清理临时文件\n会关闭端口但不会关闭已打开的网页')
    delete_temp_folder(FRAME_DIR)
    delete_temp_folder('datatemp')
    if (len(os.listdir('edged')) == 0 or PUT_EDAGE_IMAGE == False): shutil.rmtree('edged')
    if os.path.exists('data.json'):  os.remove('data.json')
    if os.path.exists('output.txt'): os.remove('output.txt')
    if os.path.exists(js_path): os.remove(js_path)
    if os.path.exists(index_path): os.remove(index_path)
    if os.path.exists(calculator_path): os.remove(calculator_path)
    print(getTime() + '临时文件清理完成')
    print(getTime() + '服务器已断开连接')
    return 'Application stopped'

def delete_temp_folder(path):
    temp_dir = os.path.join(os.getcwd(), path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def backend():
    os.makedirs('edged', exist_ok=True)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        print(getTime() + f'读取到{FRAME_DIR}文件夹内共{len(os.listdir(FRAME_DIR))}帧')
        for frame_index in list(range(len(os.listdir(FRAME_DIR)))):
            try:
                result = pool.apply_async(get_expressions, args=(frame_index, PORT, COLOUR, BILATERAL_FILTER,))
                result.wait()
                frame_latexETO.append(result.get()[0])
                _, mpWidth.value, mpHeight.value = result.get()
            except Exception as e:
                for attempt in range(3):
                    time.sleep(1)
                    try:
                        result = pool.apply_async(get_expressions, args=(frame_index, PORT, COLOUR, BILATERAL_FILTER,))
                        result.wait()
                        frame_latexETO.append(result.get()[0])
                        _, mpWidth.value, mpHeight.value = result.get()
                        break
                    except Exception as e:
                        if attempt == 2:
                            print(getTime() + 'Task failed for frame {}: {}'.format(frame_index, e))
        pool.close()
        pool.join()

    print(getTime() + '本地服务器将在http://127.0.0.1:{}运行'.format(PORT))
    if OPEN_BROWSER == False:
        pyperclip.copy('http://127.0.0.1:{}'.format(PORT))
        messagebox.showinfo("Tips！", 'Running on http://127.0.0.1:{}\n链接已复制至剪切板'.format(PORT))
    if OPEN_BROWSER:
        def open_browser(): webbrowser.open('http://127.0.0.1:%d/calculator' % PORT)
        Timer(1, open_browser).start()
    app.run(host='127.0.0.1', port=PORT)

def get_form_data():
    global BILATERAL_FILTER, COLOUR, SCREENSHOT_FORMAT, SHOW_GRID, OPEN_BROWSER, DOWNLOAD_IMAGES, PUT_EDAGE_IMAGE, SCREENSHOT_SIZE, form_data
    form_data = {'radio': 0, 'path': '', 'color': '#ffffff', 'mode': [0, 0, 0, 0, 0, 0], 'size': '0x0', 'get': [load_entry_1.get(), load_entry_2.get()]}
    error_messages = []
    if entryT.get() == 'Image Or Video Files': error_messages.append(' • 请填写需处理文件地址')
    else:
        form_data['path'] = entryT.get()
        e = '{}'.format(os.path.splitext(form_data['path'])[1][1:])
        if e in ['png', 'jpg']: form_data['radio'] = 1
        elif e in ['gif', 'mp4']: form_data['radio'] = 2
    if rgb_entry_0.get() == 'R' and rgb_entry_1.get() == 'G' and rgb_entry_2.get() == 'B': form_data['color'] = '#000000'
    elif rgb_entry_0.get() == 'R' or rgb_entry_1.get() == 'G' or rgb_entry_2.get() == 'B': error_messages.append(' • 颜色信息不完整')
    else: form_data['color'] = '#{}{}{}'.format(format(int(rgb_entry_0.get()), '02X'), format(int(rgb_entry_1.get()), '02X'), format(int(rgb_entry_2.get()), '02X'))
    form_data['mode'] = [var.get() for var in variables]
    if form_data['mode'][0] == 1: BILATERAL_FILTER = True
    if form_data['mode'][1] == 1: PUT_EDAGE_IMAGE = True
    if form_data['mode'][2] == 1:
        DOWNLOAD_IMAGES = True
        try:
            if str(form_data['radio']) == '1':
                file = cv2.imread(form_data['path'])
                form_data['size'] = '{}x{}'.format(int(file.shape[1]*float(load_entry_1.get()) + 0.5), int(file.shape[0]*float(load_entry_1.get()) + 0.5) * hidden_window_data['modified'])
            elif str(form_data['radio']) == '2':
                file = cv2.VideoCapture(form_data['path'])
                form_data['size'] = '{}x{}'.format(int(int(file.get(cv2.CAP_PROP_FRAME_WIDTH))*float(load_entry_1.get()) + 0.5), int(int(file.get(cv2.CAP_PROP_FRAME_HEIGHT))*float(load_entry_1.get()) + 0.5))
                file.release()
        except: error_messages.append(' • cv2解析出现错误')
        if form_data['mode'][5] == 0: SCREENSHOT_FORMAT = 'png'
        elif form_data['mode'][5] == 1: SCREENSHOT_FORMAT = 'svg'
    if form_data['mode'][3] == 1: SHOW_GRID = False
    if form_data['mode'][4] == 1: OPEN_BROWSER = False
    if not (hidden_window_data['lower'] < hidden_window_data['upper']): error_messages.append(' • lower应小于upper')
    if len(error_messages) == 0:
        print(getTime() + f'信息已录入data.json')
        get_data_button = tk.Button(root, text='已 锁 定', font=my_font_llt_9, compound='center', relief='ridge', bd=2, takefocus=False)
        get_data_button.place(x=12, y=345, width=170, height=27)
        print(getTime() + f'文件路径: {form_data["path"]}')
        if form_data['radio'] == 1:
            try: copy_file_to_temp(form_data['path'])
            except shutil.SameFileError: pass
            print(getTime() + '图片无需帧分解')
        elif form_data['radio'] == 2:
            if '{}'.format(os.path.splitext(form_data['path'])[1][1:]) == 'gif': extract_gif_frames(form_data['path'], FRAME_DIR)
            else: extract_frames(form_data['path'], FRAME_DIR)
        COLOUR = f'{form_data[("color")]}'
        SCREENSHOT_SIZE = list(map(int, form_data['size'].split('x')))
        InformationDictionary = {'PORT': PORT, 'potrace_path': potrace_path, 'index_path': index_path, 'js_path': js_path, 'calculator_path': calculator_path, 'COLOUR': COLOUR, 'SCREENSHOT_SIZE': SCREENSHOT_SIZE, 'SCREENSHOT_FORMAT': SCREENSHOT_FORMAT, 'OPEN_BROWSER': OPEN_BROWSER, 'BILATERAL_FILTER': BILATERAL_FILTER, 'DOWNLOAD_IMAGES': DOWNLOAD_IMAGES, 'PUT_EDAGE_IMAGE': PUT_EDAGE_IMAGE, 'SHOW_GRID': SHOW_GRID, 'form_data': form_data, 'hidden_window_data': hidden_window_data}
        with open('data.json', 'w', encoding='utf-8') as file: json.dump(InformationDictionary, file, indent=4)
        T = threading.Thread(target=lambda :backend())
        T.daemon = True
        T.start()
    else: messagebox.showerror('ERROR！', '\n'.join(error_messages))

variableInt = tk.IntVar()
variableStr = tk.StringVar()

hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5} # 预设

#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 25, 'upper': 150, 'modified': 5}} # ETO.png
#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 10, 'opticurve': 'True', 'diameter': 10, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 75, 'modified': 5}} # 铃兰.gif
#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 10, 'opticurve': 'True', 'diameter': 10, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 30, 'upper': 75, 'modified': 5}} # 初音未来.png
#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 0, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 75, 'upper': 210, 'modified': 5}} # 克拉拉.jpg
#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5}} # Yoolalouse.jpg
#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 5, 'opticurve': 'True', 'diameter': 15, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 95, 'upper': 100, 'modified': 5}} # 略nd.mp4
#hidden_window_data = {'turnpolicy': 'MINORITY', 'unit': 3, 'alphamax': 0.75, 'opttolerance': 0.5, 'turdsize': 2, 'opticurve': 'True', 'diameter': 5, 'L2gradient': 'False', 'sigmaColor': 50, 'sigmaSpace': 50, 'lower': 60, 'upper': 150, 'modified': 5} # ai.jpg

def callback():
    global hidden_window_data, b, c, d, e, f, g, h, j, k, l, m, n, o, variableStr, variableInt
    hidden_window_data['turnpolicy'] = variableStr.get()
    hidden_window_data['unit'] = c.get()
    hidden_window_data['alphamax'] = d.get()
    hidden_window_data['opttolerance'] = e.get()
    hidden_window_data['turdsize'] = f.get()
    hidden_window_data['diameter'] = g.get()
    hidden_window_data['sigmaColor'] = h.get()
    hidden_window_data['sigmaSpace'] = j.get()
    hidden_window_data['lower'] = k.get()
    hidden_window_data['upper'] = l.get()
    hidden_window_data['opticurve'] = m.get()
    hidden_window_data['L2gradient'] = n.get()
    hidden_window_data['modified'] = o.get()

label_h0 = tk.Label(root, font=my_font_llt_8, text='turnpolicy')
label_h1 = tk.Label(root, font=my_font_llt_8, text='unit')
label_h2 = tk.Label(root, font=my_font_llt_8, text='alphamax')
label_h3 = tk.Label(root, font=my_font_llt_8, text='opttolerance')
label_h4 = tk.Label(root, font=my_font_llt_8, text='turdsize')
label_h5 = tk.Label(root, font=my_font_llt_8, text='diameter')
label_h6 = tk.Label(root, font=my_font_llt_8, text='sigmaColor')
label_h7 = tk.Label(root, font=my_font_llt_8, text='sigmaSpace')
label_h8 = tk.Label(root, font=my_font_llt_8, text='lower')
label_h9 = tk.Label(root, font=my_font_llt_8, text='upper')
label_h10 = tk.Label(root, font=my_font_llt_8, text='modified')
label_h11 = tk.Label(root, font=my_font_llt_8, text='opticurve\nL2gradient')

b = ttk.Combobox(root, textvariable=variableStr, values=['MINORITY', 'MAJORITY', 'RANDOM', 'BLACK', 'WHITE', 'LEFT', 'RIGHT'])
b.config(font=my_font_llt_7)
b['state'] = 'readonly'
root.option_add('*TCombobox*Listbox.font', my_font_llt_7)
variableStr.set(hidden_window_data['turnpolicy'])

c = tk.Scale(root, from_=0, to=6, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
c.configure(font=my_font_llt_7)
c.set(hidden_window_data['unit'])

d = tk.Scale(root, from_=0, to=1.00, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=0.01, width=8, takefocus=False, sliderlength=15)
d.configure(font=my_font_llt_7)
d.set(hidden_window_data['alphamax'])

e = tk.Scale(root, from_=0, to=1.00, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=0.01, width=8, takefocus=False, sliderlength=15)
e.configure(font=my_font_llt_7)
e.set(hidden_window_data['opttolerance'])

f = tk.Scale(root, from_=0, to=25, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
f.configure(font=my_font_llt_7)
f.set(hidden_window_data['turdsize'])

g = tk.Scale(root, from_=0, to=25, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
g.configure(font=my_font_llt_7)
g.set(hidden_window_data['diameter'])

h = tk.Scale(root, from_=0, to=255, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
h.configure(font=my_font_llt_7)
h.set(hidden_window_data['sigmaColor'])

j = tk.Scale(root, from_=0, to=255, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
j.configure(font=my_font_llt_7)
j.set(hidden_window_data['sigmaSpace'])

k = tk.Scale(root, from_=0, to=255, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
k.configure(font=my_font_llt_7)
k.set(hidden_window_data['lower'])

l = tk.Scale(root, from_=0, to=255, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
l.configure(font=my_font_llt_7)
l.set(hidden_window_data['upper'])

m = tk.Spinbox(root, values=('True', 'False'), width=5, wrap=True, takefocus=False, justify='center')
m.configure(font=my_font_llt_7)
m.delete(0, 'end')
m.insert(0, hidden_window_data['opticurve'])

n = tk.Spinbox(root, values=('True', 'False'), width=5, wrap=True, takefocus=False, justify='center')
n.configure(font=my_font_llt_7)
n.delete(0, 'end')
n.insert(0, hidden_window_data['L2gradient'])

o = tk.Scale(root, from_=0, to=100, tickinterval=0, sliderrelief='ridge', length=80, orient='horizontal', resolution=1, width=8, takefocus=False, sliderlength=15)
o.configure(font=my_font_llt_7)
o.set(hidden_window_data['modified'])

# def on_left_click(event):
#     get_form_data(True)
#     get_data_button = tk.Button(root, text='开始绘制', font=my_font_llt_9, compound='center', relief='ridge', bd=2, takefocus=False)
#     get_data_button.place(x=12, y=345, width=170, height=27)
#     get_data_button.bind('<Button-1>', on_left_click)
#     get_data_button.bind('<Button-3>', on_right_click)
#
# def on_right_click(event):
#     get_form_data(False)

get_data_button = tk.Button(root, text='开始绘制', font=my_font_llt_9, compound='center', relief='ridge', bd=2, takefocus=False, command=lambda: get_form_data())

# get_data_button.bind('<Button-1>', on_left_click)
# get_data_button.bind('<Button-3>', on_right_click)

def hidden_window_def():
    global hidden_window
    x, y = root.winfo_rootx() - 8, root.winfo_rooty() - 31
    if hidden_window % 2 == 0:
        for i in range(0, 12): names['label_h%s' % (i)].place_forget()
        for i in ['b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'o']: names['%s' % (i)].place_forget()
        unfold_button_0.place(x=125, y=320, width=60, height=20)
        unfold_button_1.place_forget()
        get_data_button.place(x=12, y=345, width=170, height=27)
        root.geometry('192x384+{}+{}'.format(int(root.winfo_screenwidth() / 2 - 288), int(root.winfo_screenheight() / 2 - 252))) if hidden_window == 0 else root.geometry('192x384+{}+{}'.format(x, y))
        hidden_window += 1
    else:
        label_h0.place(x=192, y=25, width=90, height=10, anchor='w')
        label_h1.place(x=192, y=55, width=90, height=10, anchor='w')
        label_h2.place(x=192, y=85, width=90, height=10, anchor='w')
        label_h3.place(x=192, y=115, width=90, height=10, anchor='w')
        label_h4.place(x=192, y=147, width=90, height=25, anchor='w')
        label_h5.place(x=192, y=177, width=90, height=25, anchor='w')
        label_h6.place(x=192, y=207, width=90, height=25, anchor='w')
        label_h7.place(x=192, y=235, width=90, height=25, anchor='w')
        label_h8.place(x=192, y=265, width=90, height=25, anchor='w')
        label_h9.place(x=192, y=295, width=90, height=25, anchor='w')
        label_h10.place(x=192, y=325, width=90, height=25, anchor='w')
        label_h11.place(x=192, y=358, width=90, height=25, anchor='w')
        b.place(x=334, y=25, width=80, height=20, anchor='center')
        c.place(x=292, y=35); d.place(x=292, y=65)
        e.place(x=292, y=95); f.place(x=292, y=125)
        g.place(x=292, y=155); h.place(x=292, y=185)
        j.place(x=292, y=215); k.place(x=292, y=245)
        l.place(x=292, y=275); m.place(x=295, y=351)
        n.place(x=335, y=351); o.place(x=292, y=305)
        unfold_button_0.place_forget()
        unfold_button_1.place(x=125, y=320, width=60, height=20)
        get_data_button.place(x=12, y=345, width=170, height=27)
        root.geometry('576x384+{}+{}'.format(x, y))
        hidden_window += 1
    Separat(root, width=600, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=0)
    Separat(root, width=8, height=640, bg='#f0f0f0', color='#c0c0c0', line='+dash+', x=-1, y=9)
    Separat(root, width=8, height=640, bg='#f0f0f0', color='#c0c0c0', line='+double_dash+', x=188, y=9)
    Separat(root, width=8, height=640, bg='#f0f0f0', color='#c0c0c0', line='+double_dash+', x=380, y=9)
    Separat(root, width=8, height=640, bg='#f0f0f0', color='#c0c0c0', line='+dash+', x=569, y=9)
    Separat(root, width=600, height=8, bg='#f0f0f0', color='#c0c0c0', line='-dash-', x=0, y=377)


unfold_button_0 = tk.Button(root, text='◁ 展 | 开 ▷', command=hidden_window_def, font=my_font_llt_8, compound='center', relief='ridge', bd=0, anchor='center', takefocus=False)
unfold_button_1 = tk.Button(root, text='▷ 收 | 起 ◁', command=hidden_window_def, font=my_font_llt_8, compound='center', relief='ridge', bd=0, anchor='center', takefocus=False)

hidden_window_def()

def track_root_position():
    callback()
    root.after(50, track_root_position)
root.after(50, track_root_position)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    frame_latexETO = multiprocessing.Manager().list()

    PORT = multiprocessing.Value('i', 0)
    PORT.value = random.randint(1, 65536)
    PORT = copy.deepcopy(PORT.value)

    creat_sendLogs(PORT, js_path)
    creat_index(PORT, index_path)
    creat_calculator(PORT, calculator_path)

    print(getTime() + '程序初始化完成')
    root.mainloop()

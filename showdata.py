
import tkintertools as tkt
import os, sys, pyglet, tempfile

def find_lolita_font_path(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ttf') and file.startswith('Lolita'):
                return os.path.join(root, file)
    return None

def find_miku_path(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.png') and file.startswith('miku'):
                return os.path.join(root, file)
    return None

def data_update(filename):
    global old_text
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    lines = lines[int(len(lines) - lines[::-1].index('-' * 100 + '\n') + 1):]
    text = ''.join([lines if len(lines) <= 45 else lines[-45:]][0])
    if text != old_text:
        tkt.Text(tkt.Canvas(data_root, 540, 960, 0, 0), 0, 1, 540, 960, text=(text, text), radius=5, borderwidth=1, font=myfort, image=tkt.PhotoImage(mikupath), color_fill=tkt.COLOR_NONE, justify='left', color_text=('#ffffff', '#ffffff', '#ffffff', '#ffffff'), read=True)
        old_text = text
    data_root.after(50, data_update, sys.argv[1])

if __name__ == "__main__":
    sys.exit(1) if len(sys.argv) != 2 else 0
    data_root = tkt.Tk(sys.argv[1])
    data_root.geometry('540x960+{}+{}'.format(int(data_root.winfo_screenwidth() / 2 - 270), int(data_root.winfo_screenheight() / 2 - 540)))
    data_root.resizable(False, False)
    old_text = ''
    temp_dir = tempfile.gettempdir()
    fontpath = [find_lolita_font_path(temp_dir) if find_lolita_font_path(temp_dir) != None else 'Lolita.ttf'][0]
    mikupath = [find_miku_path(temp_dir) if find_miku_path(temp_dir) != None else 'miku.png'][0]
    pyglet.options['win32_gdi_font'] = True
    pyglet.font.add_file(fontpath)
    pyglet.font.load('Lolita')
    myfort = ('Lolita', 8)
    data_root.after(50, data_update, sys.argv[1])
    data_root.mainloop()

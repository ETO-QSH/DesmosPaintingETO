# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['DesmosETO.py'],
    pathex=[],
    binaries=[],
    datas=[('Lolita.ttf', '.')],
    hiddenimports=['tkinter','PIL','PIL._tkinter_finder','potrace','potrace.bezier','potrace.agg','potrace.agg.curves'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DesmosETO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

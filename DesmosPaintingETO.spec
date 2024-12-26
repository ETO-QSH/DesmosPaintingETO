# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Work Files\\DesmosPaintingETO\\DesmosPaintingETO.py'],
    pathex=['D:\\Work Files\\DesmosPaintingETO\\.venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('D:\\Work Files\\DesmosPaintingETO\\.venv\\Lib\\site-packages\\tkinterdnd2', 'tkinterdnd2')],
    hiddenimports=['tkinterdnd2'],
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
    name='DesmosPaintingETO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\Work Files\\DesmosPaintingETO\\DesmosPaintingETO.ico'],
)

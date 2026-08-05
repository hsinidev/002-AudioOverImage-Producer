# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Datas & Binaries
datas = [
    ('assets', 'assets')
]

if os.path.exists('bin/ffmpeg.exe'):
    datas.append(('bin/ffmpeg.exe', '.'))
if os.path.exists('bin/ffprobe.exe'):
    datas.append(('bin/ffprobe.exe', '.'))

binaries = []
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL.Image',
    'PIL.ImageFilter',
    'PIL.ImageDraw',
    'PIL.ImageOps',
    'PIL.ImageTk',
    'numpy',
    'queue',
    'json',
    're',
    'subprocess',
    'threading'
]

# Collect dynamic dependencies for CustomTkinter, Pillow, and NumPy
for pkg in ['customtkinter', 'PIL', 'numpy']:
    tmp = collect_all(pkg)
    datas += tmp[0]
    binaries += tmp[1]
    hiddenimports += tmp[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AudioOverImageProducer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'
)

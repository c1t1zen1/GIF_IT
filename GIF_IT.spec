# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for GIF IT v0.6.0
# Build with: pyinstaller GIF_IT.spec

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect CustomTkinter data files (themes, etc.)
ctk_datas = collect_data_files("customtkinter")

# Collect tkinterdnd2 data files (tkdnd shared libraries)
tkdnd_datas = collect_data_files("tkinterdnd2")

# App assets
app_datas = [
    ("GIF_IT.png", "."),
    ("GIF_IT_UP.png", "."),
    ("GIF_IT_ICON2.ico", "."),
    ("icon_16.png", "."),
    ("icon_32.png", "."),
]

a = Analysis(
    ["GIF_IT_v_beta_060.py"],
    pathex=[],
    binaries=[],
    datas=app_datas + ctk_datas + tkdnd_datas,
    hiddenimports=[
        "customtkinter",
        "tkinterdnd2",
        "PIL",
<<<<<<< HEAD
=======
        "imageio",
        "imageio_ffmpeg",
>>>>>>> 5604c83d56ab0d53eaf5002c383867275b8176d5
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
<<<<<<< HEAD
    excludes=["imageio_ffmpeg", "imageio_ffmpeg._utils", "imageio"],
=======
    excludes=[],
>>>>>>> 5604c83d56ab0d53eaf5002c383867275b8176d5
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
    name="GIF_IT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="GIF_IT_ICON2.ico" if sys.platform == "win32" else None,
)

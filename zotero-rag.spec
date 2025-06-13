# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect data files for sentence transformers and other ML packages
datas = []
datas += collect_data_files('sentence_transformers')
datas += collect_data_files('transformers') 
datas += collect_data_files('tokenizers')
datas += collect_data_files('huggingface_hub')

# Add license and readme
datas += [('LICENSE', '.')]
datas += [('README.md', '.')]

# Collect hidden imports for ML packages
hiddenimports = []
hiddenimports += collect_submodules('sentence_transformers')
hiddenimports += collect_submodules('transformers')
hiddenimports += collect_submodules('tokenizers')
hiddenimports += collect_submodules('huggingface_hub')
hiddenimports += collect_submodules('torch')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('sklearn')

# Additional hidden imports that might be needed
hiddenimports += [
    'sqlite3',
    'json',
    'pathlib',
    'webbrowser',
    'argparse',
    'PyPDF2',
    'faiss',
    'sklearn.utils._cython_blas',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree',
    'sklearn.tree._utils',
    'PIL._tkinter_finder',
]

block_cipher = None

a = Analysis(
    ['fast_pdf_opener.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
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
    name='zotero-rag',
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
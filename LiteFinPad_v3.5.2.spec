# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
import glob
import os

# Collect all Python files from widgets directory
widgets_files = []
if os.path.exists('widgets'):
    for py_file in glob.glob('widgets/*.py'):
        # Add tuple: (source_file, destination_directory)
        widgets_files.append((py_file, 'widgets'))

datas = [('icon.ico', '.'), ('gui.py', '.'), ('expense_table.py', '.'), ('export_data.py', '.'), ('error_logger.py', '.'), ('analytics.py', '.'), ('data_manager.py', '.'), ('validation.py', '.')]
datas += widgets_files
binaries = []
hiddenimports = ['xlsxwriter', 'xlsxwriter.workbook', 'xlsxwriter.worksheet', 'xlsxwriter.format', 'fpdf', 'fpdf.fpdf', 'encodings', 'encodings.utf_8', 'encodings.ascii', 'encodings.latin_1', 'encodings.cp1252', 'html', 'html.parser', 'html.entities', 'urllib', 'urllib.parse', 'urllib.request', 'base64', 'zlib', 're', 'math', 'datetime', 'json']
hiddenimports += collect_submodules('xlsxwriter')
hiddenimports += collect_submodules('fpdf')
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'test', 'setuptools', 'setuptools._vendor', 'pkg_resources', 'PIL', 'Pillow', 'ssl', '_ssl'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LiteFinPad_v3.5.2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LiteFinPad_v3.5.2',
)

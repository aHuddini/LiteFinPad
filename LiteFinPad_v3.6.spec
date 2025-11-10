# -*- mode: python ; coding: utf-8 -*-
"""
LiteFinPad v3.6.1 PyInstaller Spec File
Includes all modules, dependencies, dark mode theme support, and recent refactoring changes.
"""
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

# Data files to include
datas = [('icon.ico', '.')]
binaries = []

# Hidden imports - modules that PyInstaller might not auto-detect
hiddenimports = [
    # Standard library modules
    'functools',  # For @win32_safe decorator in tray_icon.py
    'ctypes',  # For Win32 API calls
    'ctypes.wintypes',  # For Win32 types
    'threading',  # For tray icon message loop
    'queue',  # For GUI queue system
    'calendar',  # For date calculations
    
    # Win32 API modules (pywin32)
    'win32gui',  # For system tray and window management
    'win32con',  # For Win32 constants
    'win32api',  # For Win32 API calls
    'pywintypes',  # For Win32 types
    
    # Export libraries
    'xlsxwriter',
    'xlsxwriter.workbook',
    'xlsxwriter.worksheet',
    'xlsxwriter.format',
    'fpdf',
    'fpdf.fpdf',
    
    # Encoding support
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
    'encodings.cp1252',
    
    # HTML/PDF support
    'html',
    'html.parser',
    'html.entities',
    'urllib',
    'urllib.parse',
    'urllib.request',
    
    # Standard library utilities
    'base64',
    'zlib',
    're',
    'math',
    'datetime',
    'json',
]

# Collect all submodules for export libraries
hiddenimports += collect_submodules('xlsxwriter')
hiddenimports += collect_submodules('fpdf')

# Collect all Tkinter modules and data
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'test',
        'setuptools',
        'setuptools._vendor',
        'pkg_resources',
        'PIL',
        'Pillow',
        'ssl',
        '_ssl',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LiteFinPad_v3.6.1',
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
    name='LiteFinPad_v3.6.1',
)

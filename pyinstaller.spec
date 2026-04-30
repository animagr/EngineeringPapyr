# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Bundle pandoc binary if build.py found it
pandoc_path = os.environ.get('PANDOC_BINARY_PATH', '')
extra_binaries = []
if pandoc_path and os.path.isfile(pandoc_path):
    extra_binaries.append((pandoc_path, '.'))

# Bundle installed packages metadata
extra_datas = [
    ('frontend/public', 'public'),
]
packages_json = os.path.join('python', 'installed_packages.json')
if os.path.isfile(packages_json):
    extra_datas.append((packages_json, '.'))

a = Analysis(
    ['python/main.py'],
    pathex=['python'],
    binaries=extra_binaries,
    datas=extra_datas,
    hiddenimports=[
        'sympy',
        'sympy.core',
        'sympy.parsing',
        'sympy.parsing.latex',
        'sympy.printing',
        'sympy.solvers',
        'sympy.matrices',
        'sympy.physics',
        'numpy',
        'scipy',
        'scipy.optimize',
        'scipy.interpolate',
        'sklearn',
        'sklearn.preprocessing',
        'sklearn.linear_model',
        'CoolProp',
        'jedi',
        'parso',
        'webview',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PIL',
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
    a.datas,
    [],
    name='EngineeringPapyr',
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
    icon='frontend/public/favicon.ico',
)

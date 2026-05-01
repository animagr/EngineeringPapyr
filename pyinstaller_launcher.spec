# -*- mode: python ; coding: utf-8 -*-
# Minimal spec: compiles only the launcher script (~6MB), not the full app.

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'sympy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EngineeringPapyr',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='frontend/public/favicon.ico',
)

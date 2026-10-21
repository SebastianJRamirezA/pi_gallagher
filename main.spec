# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    console=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PIGallagher',
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='main',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='MiJuego.app',
        icon='assets/graphics/icon.icns',
        bundle_identifier='com.miusuario.mijuego',
    )
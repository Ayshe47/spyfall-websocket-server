# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ui2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('firstScreen.png', '.'),
        ('joinbk.png', '.'),
        ('joinbk2.png', '.'),
        ('gamebg.png', '.'),
        ('rolebg.png', '.'),
        ('settingsbk.png', '.'),
        ('bk.png', '.'),
        ('RussoOne.ttf', '.')
    ],
    hiddenimports=[],
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
    name='Spyfall',
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
)

# Важно для MacOS: BUNDLE создает структуру .app
app = BUNDLE(
    exe,
    name='Spyfall.app',
    icon=None,
    bundle_identifier=None,
)
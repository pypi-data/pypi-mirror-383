# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
datas = [
    ('editor/theme_editor/samples', 'editor/theme_editor/samples'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'ttkbootstrap',
    'markdown',
    'mistune',
    'tinycss2',
    'cssselect2',
    'webencodings',
]

a = Analysis(
    ['theme_editor.py'],
    pathex=[],
    binaries=[],
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
    name='TyporaThemeEditor',
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
    icon=None,  # Add icon path here if you have one
)

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Images', 'Images'),
        ('Протокол_шаблон.xlsx', '.'),
        ('Шаблон протокола для ПР.xlsx', '.'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'aspose.words',
        'requests',
        'bs4',
        'lxml',
        'PyQt6',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF_Maker',
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
    icon=['Images\\icons\\icon_pdf_maker_255_size.ico'],
)

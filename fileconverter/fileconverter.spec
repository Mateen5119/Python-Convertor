# fileconverter.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Bundle the 'static' folder containing your index.html and web assets
# Bundle the 'static' folder AND LibreOffice Portable
added_files = [
    ('static', 'static'),
#   ('templates', 'templates'), # (Kept it for future reference )
    ('libreoffice_portable', 'libreoffice_portable') # This line was added for the libre office Library.
]

# Explicitly define hidden imports that PyInstaller might miss dynamically
hidden_imports = [
    'flask',
    'fitz',          # PyMuPDF
    'pymupdf',
    'pymupdfb',
    'pdf2docx',
    'pptx',
    'pandas',
    'openpyxl',
    'PIL',
    'werkzeug.datastructures'
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['extra_archive'], # Prevent the archive from being bundled
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FileConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Set to False later if you want to hide the backend terminal window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FileConverter',
)

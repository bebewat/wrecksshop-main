# -*- mode: python -*-

import os
import PyInstaller
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

block_cipher = None


pyi_loader_dir = os.path.join(os.path.dirname(PyInstaller.file), 'loader')

a = Analysis(
['wrecksshop_launcher_gui.py'],
pathex=[Path(file).parent.resolve().as_posix()],
binaries=[],
datas=[
# Include entire PyInstaller loader directory
(pyi_loader_dir, 'PyInstaller/loader'),
('data/CleanArkData.csv', 'data'),
('assets/logo.ico', 'assets')
],
hiddenimports=['ipaddress'],
hookspath=[],
runtime_hooks=[],
excludes=[],
win_no_prefer_redirects=False,
win_private_assemblies=False,
cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
pyz,
a.scripts,
[],
exclude_binaries=True,
name='WrecksShopLauncher',
debug=False,
bootloader_ignore_signals=False,
strip=False,
upx=True,
console=False,
icon='assets/icon.ico'
)

coll = COLLECT(
exe,
a.binaries,
a.zipfiles,
a.datas,
strip=False,
upx=True,
name='WrecksShopLauncher'
)

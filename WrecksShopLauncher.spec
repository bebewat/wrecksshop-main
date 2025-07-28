# -*- mode: python -*-

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path
import PyInstaller

block_cipher = None

i_loader_pkg_path = os.path.dirname(PyInstaller.__file__)
pyi_loader_dir    = os.path.join(i_loader_pkg_path, 'loader')

pyinstaller_submodules = collect_submodules('PyInstaller')

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
hiddenimports=['ipaddress'] + pyinstaller_submodules,
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
debug=True,
bootloader_ignore_signals=False,
strip=False,
upx=True,
console=True,
icon='assets/logo.ico'
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

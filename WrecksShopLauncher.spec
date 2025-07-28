# -*- mode: python -*-

import os
from pathlib import Path
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_submodules
import PyInstaller

block_cipher = None

pyi_pkg_path = os.path.dirname(PyInstaller.__file__)
pyi_loader_dir = os.path.join(pyi_pkg_path, 'loader')

pyinstaller_submodules = collect_submodules('PyInstaller')

from PyInstaller.utils.hooks import Tree, collect_submodules

loader_tree = Tree(pyi_loader_dire, prefix='PyInstaller/loader')

a = Analysis(
['wrecksshop_launcher_gui_full.py'],
pathex=[os.getcwd()],
binaries=[],
datas=[
loader_tree,
('data/CleanArkData.csv', 'data'),
('assets/icon.ico', 'assets'),
],
hiddenimports=['ipaddress'] + pyinstaller_submodules,
hookspath=[],
runtime_hooks=[],
excludes=[],
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

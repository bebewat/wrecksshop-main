import json
from pathlib import Path
from arklib_loader import load_ark_lib, ArkItem

# Path to base CSV data (should match GUI lookup logic)
BASE_CSV_PATH = Path(__file__).parent / 'data' / 'CleanArkData.csv'
if not BASE_CSV_PATH.is_file():
    BASE_CSV_PATH = Path(__file__).parent / 'CleanArkData.csv'

# Load the base library from CSV
def update_base_library():
    """Reloads and returns the base Ark data library from CSV."""
    return load_ark_lib(BASE_CSV_PATH)

# Load mod JSON files and merge with base
def update_full_library(mods_path: Path):
    """
    Scans JSON files in mods_path for mods and merges their entries with the base library.
    Expects JSON files containing lists of entries with 'name' or 'internalName'.
    """
    base = update_base_library()
    mod_lib = {"dinos": {}, "items": {}}
    mods_dir = Path(mods_path)
    if not mods_dir.is_dir():
        return base
    for json_file in mods_dir.glob('*.json'):
        data = json.load(json_file.open('r', encoding='utf-8'))
        key = 'dinos' if 'Dino' in json_file.name else 'items'
        for entry in data:
            identifier = entry.get('name') or entry.get('internalName')
            mod_lib[key][identifier] = entry
    # Merge mod entries onto base
    base.get('dinos', {}).update(mod_lib['dinos'])
    base.get('items', {}).update(mod_lib['items'])
    return base

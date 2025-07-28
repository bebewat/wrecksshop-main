import json
from pathlib import Path
from arklib_loader import load_ark_lib, ArkItem

# Paths to CSV data library
BASE_CSV_PATH = Path(__file__).parent / 'data' / 'CleanArkData.csv'
if not BASE_CSV_PATH.is_file():
    BASE_CSV_PATH = Path(__file__).parent / 'CleanArkData.csv'

# Load the base Ark data library as a dict of sections -> [ArkItem]
def update_base_library():
    raw = load_ark_lib(BASE_CSV_PATH)  # likely a dict of section -> [ArkItem]
    grouped = {}
    for section, items in raw.items():
        grouped[section] = {item.name: item for item in items}
    return grouped

# Load mod JSON files and merge their entries onto the base library
def update_full_library(mods_path: Path):
    """
    Scans JSON files in mods_path and merges their entries with the base library.
    JSON mods should be lists of entries with 'name' or 'internalName'.
    """
    base_lib = update_base_library()
    # Prepare mod libraries structure matching base
    mod_lib = {"dinos": {}, "items": {}}
    mods_dir = Path(mods_path)
    if not mods_dir.is_dir():
        return base_lib
    for json_file in mods_dir.glob('*.json'):
        try:
            entries = json.load(json_file.open('r', encoding='utf-8'))
        except json.JSONDecodeError:
            continue
        key = 'dinos' if 'Dino' in json_file.name else 'items'
        for entry in entries:
            identifier = entry.get('name') or entry.get('internalName')
            if identifier:
                mod_lib[key][identifier] = entry
    # Merge mod entries onto base
    # Ensure base has correct keys
    if isinstance(base_lib, dict):
        base_lib.get('dinos', {}).update(mod_lib['dinos'])
        base_lib.get('items', {}).update(mod_lib['items'])
    return base_lib

# arkdata_updater.py

import os
import subprocess
import json
from pathlib import Path

ARKDATA_REPO = Path(__file__).parent / "arkdata"
REMOTE_URL = "https://github.com/jonxmitchell/arkdata.git"

def ensure_repo():
    """Clone once or pull latest if already present."""
    if not ARKDATA_REPO.exists():
        subprocess.run(
            ["git", "clone", REMOTE_URL, str(ARKDATA_REPO)],
            check=True
        )
    else:
        subprocess.run(
            ["git", "-C", str(ARKDATA_REPO), "pull"],
            check=True
        )

def load_json(filename: str):
    path = ARKDATA_REPO / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_base_library():
    """
    Pull latest ArkData and return a dict with 'dinos' and 'items'.
    """
    ensure_repo()
    dinos = load_json("DinoNames.json")      # adjust filename if different
    items = load_json("ItemList.json")       # adjust filename if different

    # Normalize into your own structure:
    base_lib = {
        "dinos": { entry["name"]: entry for entry in dinos },
        "items": { entry["internalName"]: entry for entry in items },
    }
    return base_lib

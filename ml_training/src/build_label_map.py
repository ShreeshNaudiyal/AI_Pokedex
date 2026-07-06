"""
Maps Pokedex number (filename) -> Pokemon name, using PokeAPI.
Since the Kaggle dataset names files "1.png", "2.png", etc., we need
this mapping to build data/processed/<name>/ folders.

Run: python -m src.build_label_map
"""

import json
import os
import time
import requests
from src import config

CACHE_PATH = os.path.join(config.BASE_DIR, "data", "number_to_name.json")
POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon"


def build_map(max_id: int = 819):
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            mapping = json.load(f)
        print(f"[build_label_map] Loaded existing cache with {len(mapping)} entries.")
    else:
        mapping = {}

    for dex_id in range(1, max_id + 1):
        if str(dex_id) in mapping:
            continue
        try:
            resp = requests.get(f"{POKEAPI_BASE}/{dex_id}", timeout=10)
            resp.raise_for_status()
            name = resp.json()["name"]
            mapping[str(dex_id)] = name
            print(f"[build_label_map] {dex_id} -> {name}")
        except requests.RequestException as e:
            print(f"[build_label_map] WARNING: failed for id {dex_id}: {e}")
        time.sleep(0.05)  # be polite to the public API

        if dex_id % 50 == 0:
            _save(mapping)

    _save(mapping)
    print(f"[build_label_map] Done. {len(mapping)} entries saved to {CACHE_PATH}")


def _save(mapping):
    with open(CACHE_PATH, "w") as f:
        json.dump(mapping, f, indent=2)


if __name__ == "__main__":
    build_map()
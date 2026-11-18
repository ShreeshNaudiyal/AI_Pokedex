"""
Maps Pokedex number / filename -> Pokemon name, using PokeAPI.
Handles both numeric IDs (1.png -> bulbasaur) and form suffixes (115-mega.png -> kangaskhan).
"""

import json
import os
import re
import requests
from src import config

CACHE_PATH = os.path.join(config.BASE_DIR, "data", "number_to_name.json")
POKEAPI_LIST = "https://pokeapi.co/api/v2/pokemon?limit=721"


def build_map():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            mapping = json.load(f)
        print(f"[build_label_map] Loaded existing cache with {len(mapping)} entries.")
        return mapping

    print("[build_label_map] Fetching Pokemon names from PokeAPI...")
    try:
        resp = requests.get(POKEAPI_LIST, timeout=20)
        resp.raise_for_status()
        results = resp.json()["results"]
        base_map = {str(i + 1): item["name"] for i, item in enumerate(results)}
    except requests.RequestException as e:
        print(f"[build_label_map] Error fetching PokeAPI list: {e}")
        base_map = {}

    raw_dir = config.RAW_DATA_DIR
    mapping = {}
    if os.path.exists(raw_dir):
        for fname in os.listdir(raw_dir):
            if not fname.endswith(".png"):
                continue
            key = os.path.splitext(fname)[0]
            m = re.match(r"^(\d+)", key)
            if m:
                base_id = m.group(1)
                name = base_map.get(base_id, f"pokemon-{base_id}")
                mapping[key] = name
            else:
                mapping[key] = key

    _save(mapping)
    print(f"[build_label_map] Done. {len(mapping)} entries saved to {CACHE_PATH}")
    return mapping


def _save(mapping):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(mapping, f, indent=2)


if __name__ == "__main__":
    build_map()

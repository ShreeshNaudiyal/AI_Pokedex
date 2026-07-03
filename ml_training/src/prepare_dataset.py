"""
Normalizes a raw Kaggle Pokémon image dataset into the folder structure
expected by data_loader.py:

    data/processed/<pokemon_name>/<image>.jpg

Handles two common raw layouts:
  A) data/raw/<pokemon_name>/<image>.jpg          (already per-class folders)
  B) data/raw/*.jpg with labels inferred from filename prefix, e.g.
     "pikachu_001.jpg" -> class "pikachu"

Also:
  - Skips/deletes corrupt or unreadable images (common in scraped Kaggle sets)
  - Resizes to config.IMG_SIZE and writes out as clean .jpg
  - Normalizes class folder names (lowercase, strip whitespace/punctuation)

Run: python -m src.prepare_dataset
"""

import os
import re
import shutil
import cv2
from tqdm import tqdm
from src import config

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def normalize_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


def is_readable_image(path: str) -> bool:
    img = cv2.imread(path)
    return img is not None and img.size > 0


def process_and_save(src_path: str, dest_path: str) -> bool:
    """Reads, resizes, and writes an image. Returns False if unreadable."""
    img = cv2.imread(src_path)
    if img is None:
        return False
    img = cv2.resize(img, config.IMG_SIZE, interpolation=cv2.INTER_AREA)
    cv2.imwrite(dest_path, img)
    return True


def prepare_from_class_folders():
    """Case A: data/raw/<class_name>/<image>"""
    class_dirs = [
        d for d in os.listdir(config.RAW_DATA_DIR)
        if os.path.isdir(os.path.join(config.RAW_DATA_DIR, d))
    ]

    skipped = 0
    for class_dir in tqdm(class_dirs, desc="Classes"):
        clean_name = normalize_name(class_dir)
        src_class_path = os.path.join(config.RAW_DATA_DIR, class_dir)
        dest_class_path = os.path.join(config.PROCESSED_DATA_DIR, clean_name)
        os.makedirs(dest_class_path, exist_ok=True)

        images = [f for f in os.listdir(src_class_path) if f.lower().endswith(VALID_EXTENSIONS)]
        for i, fname in enumerate(images):
            src_file = os.path.join(src_class_path, fname)
            dest_file = os.path.join(dest_class_path, f"{clean_name}_{i:04d}.jpg")
            if not process_and_save(src_file, dest_file):
                skipped += 1

    print(f"[prepare_dataset] Done. Skipped {skipped} unreadable images.")


def prepare_from_flat_filenames():
    """Case B: data/raw/*.jpg where label is the filename prefix before '_' or digits."""
    files = [f for f in os.listdir(config.RAW_DATA_DIR) if f.lower().endswith(VALID_EXTENSIONS)]
    skipped = 0
    counters = {}

    for fname in tqdm(files, desc="Images"):
        # Strip extension, strip trailing digits/index, e.g. "pikachu_001" -> "pikachu"
        stem = os.path.splitext(fname)[0]
        label_raw = re.split(r"[_\-]?\d+$", stem)[0]
        clean_name = normalize_name(label_raw)

        dest_class_path = os.path.join(config.PROCESSED_DATA_DIR, clean_name)
        os.makedirs(dest_class_path, exist_ok=True)

        counters[clean_name] = counters.get(clean_name, 0) + 1
        dest_file = os.path.join(dest_class_path, f"{clean_name}_{counters[clean_name]:04d}.jpg")

        src_file = os.path.join(config.RAW_DATA_DIR, fname)
        if not process_and_save(src_file, dest_file):
            skipped += 1

    print(f"[prepare_dataset] Done. Skipped {skipped} unreadable images.")


def detect_layout_and_run():
    entries = os.listdir(config.RAW_DATA_DIR)
    has_subdirs = any(os.path.isdir(os.path.join(config.RAW_DATA_DIR, e)) for e in entries)

    if os.path.exists(config.PROCESSED_DATA_DIR):
        print(f"[prepare_dataset] Clearing existing {config.PROCESSED_DATA_DIR} ...")
        shutil.rmtree(config.PROCESSED_DATA_DIR)
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

    if has_subdirs:
        print("[prepare_dataset] Detected per-class folder layout.")
        prepare_from_class_folders()
    else:
        print("[prepare_dataset] Detected flat file layout, inferring labels from filenames.")
        prepare_from_flat_filenames()

    # Report class counts + flag classes with too few images (risk of overfitting)
    class_counts = {
        d: len(os.listdir(os.path.join(config.PROCESSED_DATA_DIR, d)))
        for d in os.listdir(config.PROCESSED_DATA_DIR)
    }
    low_count = {k: v for k, v in class_counts.items() if v < 20}
    print(f"\n[prepare_dataset] Total classes: {len(class_counts)}")
    if low_count:
        print(f"[prepare_dataset] WARNING: {len(low_count)} classes have <20 images "
              f"(may hurt accuracy for those Pokémon): {list(low_count.keys())[:10]}...")


if __name__ == "__main__":
    detect_layout_and_run()
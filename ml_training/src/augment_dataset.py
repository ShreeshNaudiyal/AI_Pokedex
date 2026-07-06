"""
Expands a 1-image-per-class sprite dataset into a full augmented dataset
suitable for transfer-learning classification.

Input:  data/raw/<dex_number>.png   (RGBA, transparent background)
Output: data/processed/<pokemon_name>/<name>_0000.jpg ... _00NN.jpg

Run: python -m src.augment_dataset
"""

import json
import os
import random
import numpy as np
import cv2
from PIL import Image
from tqdm import tqdm
from src import config

VALID_EXTENSIONS = (".png",)


def load_name_map():
    with open(config.NUMBER_TO_NAME_PATH) as f:
        return json.load(f)


def random_background(size):
    """Generates a synthetic background: solid color, gradient, or soft noise."""
    w, h = size
    mode = random.choice(["solid", "gradient", "noise"])

    if mode == "solid":
        color = tuple(random.randint(0, 255) for _ in range(3))
        bg = Image.new("RGB", (w, h), color)

    elif mode == "gradient":
        top = np.array([random.randint(0, 255) for _ in range(3)])
        bottom = np.array([random.randint(0, 255) for _ in range(3)])
        gradient = np.linspace(top, bottom, h).astype(np.uint8)
        gradient = np.tile(gradient[:, np.newaxis, :], (1, w, 1))
        bg = Image.fromarray(gradient, mode="RGB")

    else:  # noise
        noise = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
        noise = cv2.GaussianBlur(noise, (25, 25), 0)  # soften harsh noise
        bg = Image.fromarray(noise, mode="RGB")

    return bg


def augment_single(sprite: Image.Image, canvas_size=(300, 300)) -> Image.Image:
    """Applies one random augmentation pass and composites onto a random background."""
    # Random rotation (expand canvas so nothing gets clipped, transparent fill)
    angle = random.uniform(config.MIN_ROTATION_DEG, config.MAX_ROTATION_DEG)
    rotated = sprite.rotate(angle, expand=True, resample=Image.BICUBIC)

    # Random scale
    scale = random.uniform(config.MIN_SCALE, config.MAX_SCALE)
    new_size = (max(1, int(rotated.width * scale)), max(1, int(rotated.height * scale)))
    rotated = rotated.resize(new_size, Image.BICUBIC)

    # Random horizontal flip
    if random.random() < 0.5:
        rotated = rotated.transpose(Image.FLIP_LEFT_RIGHT)

    # Composite onto random background, sprite placed at random offset
    bg = random_background(canvas_size).convert("RGBA")
    max_x = max(1, canvas_size[0] - rotated.width)
    max_y = max(1, canvas_size[1] - rotated.height)
    offset = (random.randint(0, max_x), random.randint(0, max_y))
    bg.paste(rotated, offset, rotated)  # rotated's alpha channel used as mask

    result = bg.convert("RGB")

    # Photometric jitter via OpenCV (brightness/contrast)
    arr = np.array(result).astype(np.float32)
    brightness = random.uniform(-20, 20)
    contrast = random.uniform(0.85, 1.15)
    arr = arr * contrast + brightness
    arr = np.clip(arr, 0, 255).astype(np.uint8)

    # Occasional slight blur (simulates camera focus variance)
    if random.random() < 0.3:
        arr = cv2.GaussianBlur(arr, (3, 3), 0)

    return Image.fromarray(arr)


def process_all():
    name_map = load_name_map()
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

    raw_files = [f for f in os.listdir(config.RAW_DATA_DIR) if f.lower().endswith(VALID_EXTENSIONS)]
    print(f"[augment_dataset] Found {len(raw_files)} source sprites.")

    for fname in tqdm(raw_files, desc="Pokemon"):
        dex_number = os.path.splitext(fname)[0]
        name = name_map.get(dex_number)
        if name is None:
            print(f"[augment_dataset] WARNING: no name mapping for {fname}, skipping.")
            continue

        class_dir = os.path.join(config.PROCESSED_DATA_DIR, name)
        os.makedirs(class_dir, exist_ok=True)

        existing = len([f for f in os.listdir(class_dir) if f.endswith(".jpg")])
        if existing >= config.AUGMENTED_COPIES_PER_CLASS:
            continue  # resume support: already fully generated

        sprite_path = os.path.join(config.RAW_DATA_DIR, fname)
        sprite = Image.open(sprite_path).convert("RGBA")

        for i in range(existing, config.AUGMENTED_COPIES_PER_CLASS):
            augmented = augment_single(sprite)
            augmented = augmented.resize(config.IMG_SIZE)
            out_path = os.path.join(class_dir, f"{name}_{i:04d}.jpg")
            augmented.save(out_path, quality=90)

    print("[augment_dataset] Done.")


if __name__ == "__main__":
    process_all()
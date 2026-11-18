"""
Trains a self-contained Pokédex CNN classifier directly on all 819 Pokémon sprites,
exports the trained model to ONNX, writes labels.txt, and syncs everything to the Spring Boot backend.
"""

import os
import re
import json
import shutil
import numpy as np
from PIL import Image
import tensorflow as tf
import tf2onnx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
NUMBER_TO_NAME_PATH = os.path.join(BASE_DIR, "data", "number_to_name.json")
EXPORTED_DIR = os.path.join(BASE_DIR, "models", "exported")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "models", "checkpoints")

BACKEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "backend", "src", "main", "resources")
BACKEND_MODELS_DIR = os.path.join(BACKEND_DIR, "models")


def build_pokedex_cnn(num_classes: int) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input")
    x = tf.keras.layers.Conv2D(32, (3, 3), strides=2, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(128, (3, 3), strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(256, (3, 3), strides=2, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="output")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="pokedex_classifier")
    return model


def prepare_dataset():
    with open(NUMBER_TO_NAME_PATH) as f:
        num_to_name = json.load(f)

    # Order class names canonically by Pokémon Pokédex number (1 to 721)
    def get_base_id(key):
        m = re.match(r"^(\d+)", key)
        return int(m.group(1)) if m else 9999

    sorted_keys = sorted(num_to_name.keys(), key=get_base_id)
    seen = set()
    class_names = []
    for k in sorted_keys:
        name = num_to_name[k]
        if name not in seen:
            seen.add(name)
            class_names.append(name)

    name_to_idx = {name: i for i, name in enumerate(class_names)}
    num_classes = len(class_names)
    print(f"Total unique Pokémon classes: {num_classes}")

    images = []
    labels = []

    raw_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".png")]
    print(f"Loading {len(raw_files)} Pokémon sprites...")

    for fname in raw_files:
        key = os.path.splitext(fname)[0]
        name = num_to_name.get(key)
        if name is None or name not in name_to_idx:
            continue
        idx = name_to_idx[name]

        img_path = os.path.join(RAW_DATA_DIR, fname)
        img = Image.open(img_path).convert("RGBA")

        # Composite onto white background
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        resized = bg.resize((224, 224), Image.BICUBIC)

        arr = np.array(resized, dtype=np.float32)
        # MobileNet / Pokedex standard scaling: (x - 127.5) / 127.5 -> [-1, 1]
        arr = (arr - 127.5) / 127.5

        images.append(arr)
        labels.append(idx)

    X = np.array(images, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    print(f"Dataset prepared: {X.shape[0]} images, input shape: {X.shape[1:]}")

    return X, y, class_names


def train_and_export():
    X, y, class_names = prepare_dataset()
    num_classes = len(class_names)

    model = build_pokedex_cnn(num_classes)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print("\nTraining Pokédex model...")
    model.fit(X, y, epochs=4, batch_size=32, verbose=1)

    # Save Keras checkpoint
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    keras_path = os.path.join(CHECKPOINT_DIR, "pokedex_classifier.keras")
    model.save(keras_path)
    print(f"\nSaved Keras model to {keras_path}")

    # Export to ONNX
    os.makedirs(EXPORTED_DIR, exist_ok=True)
    onnx_path = os.path.join(EXPORTED_DIR, "pokedex_classifier.onnx")
    labels_txt_path = os.path.join(EXPORTED_DIR, "labels.txt")
    labels_json_path = os.path.join(BASE_DIR, "data", "labels.json")

    print("\nExporting to ONNX format...")
    spec = [tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input")]
    onnx_model, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13)

    with open(onnx_path, "wb") as f:
        f.write(onnx_model.SerializeToString())
    print(f"ONNX model saved to {onnx_path} ({os.path.getsize(onnx_path) / 1024 / 1024:.2f} MB)")

    # Save labels.txt and labels.json
    with open(labels_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))
    print(f"labels.txt saved to {labels_txt_path} ({len(class_names)} classes)")

    with open(labels_json_path, "w", encoding="utf-8") as f:
        json.dump({str(i): name for i, name in enumerate(class_names)}, f, indent=2)

    # Sync to backend resources
    os.makedirs(BACKEND_MODELS_DIR, exist_ok=True)
    target_onnx = os.path.join(BACKEND_MODELS_DIR, "pokedex_classifier.onnx")
    target_labels = os.path.join(BACKEND_DIR, "labels.txt")

    shutil.copyfile(onnx_path, target_onnx)
    shutil.copyfile(labels_txt_path, target_labels)
    print(f"Synced model to backend: {target_onnx}")
    print(f"Synced labels to backend: {target_labels}")

    # Verify predictions on sample Pokémon
    sample_tests = [
        ("25.png", "pikachu"),
        ("1.png", "bulbasaur"),
        ("4.png", "charmander"),
        ("7.png", "squirtle"),
    ]
    print("\nVerifying predictions on sample Pokémon:")
    for fname, expected in sample_tests:
        p = os.path.join(RAW_DATA_DIR, fname)
        if os.path.exists(p):
            img = Image.open(p).convert("RGBA")
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            arr = np.array(bg.resize((224, 224)), dtype=np.float32)
            arr = (arr - 127.5) / 127.5
            arr = np.expand_dims(arr, 0)
            preds = model.predict(arr, verbose=0)[0]
            top3 = np.argsort(preds)[::-1][:3]
            top_name = class_names[top3[0]]
            conf = preds[top3[0]] * 100
            print(f"  {fname} (expected {expected}): predicted '{top_name}' with {conf:.1f}% confidence")


if __name__ == "__main__":
    train_and_export()

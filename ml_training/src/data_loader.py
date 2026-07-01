"""
Builds tf.data.Dataset pipelines from the processed image directory.
Directory layout expected:
    data/processed/<pokemon_name>/<image>.jpg
Keras' image_dataset_from_directory infers class labels from folder names.
"""

import json
import tensorflow as tf
from src import config


def build_datasets():
    """Returns (train_ds, val_ds, class_names)."""
    train_ds = tf.keras.utils.image_dataset_from_directory(
        config.PROCESSED_DATA_DIR,
        validation_split=config.VALIDATION_SPLIT,
        subset="training",
        seed=config.SEED,
        image_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        label_mode="categorical",
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        config.PROCESSED_DATA_DIR,
        validation_split=config.VALIDATION_SPLIT,
        subset="validation",
        seed=config.SEED,
        image_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        label_mode="categorical",
    )

    class_names = train_ds.class_names
    _persist_labels(class_names)

    # Data augmentation applied only at train time
    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomContrast(0.1),
    ])

    def preprocess(images, labels, training):
        images = tf.cast(images, tf.float32)
        if training:
            images = augmentation(images)
        # MobileNetV2-style scaling: [-1, 1] — must match backend Translator
        images = (images - config.RESCALE_MEAN) / config.RESCALE_STD
        return images, labels

    train_ds = train_ds.map(lambda x, y: preprocess(x, y, training=True),
                             num_parallel_calls=tf.data.AUTOTUNE)
    val_ds = val_ds.map(lambda x, y: preprocess(x, y, training=False),
                         num_parallel_calls=tf.data.AUTOTUNE)

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, class_names


def _persist_labels(class_names):
    """Writes index->name mapping so export.py and the backend can share it."""
    labels_map = {str(i): name for i, name in enumerate(class_names)}
    with open(config.LABELS_JSON_PATH, "w") as f:
        json.dump(labels_map, f, indent=2)
    print(f"[data_loader] Wrote {len(labels_map)} labels to {config.LABELS_JSON_PATH}")
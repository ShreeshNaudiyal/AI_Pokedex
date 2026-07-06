"""
Central config for the Pokédex classifier training pipeline.
Keep every path/hyperparameter here so train.py, evaluate.py,
and export.py never hardcode values independently.
"""

import os

# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ml-training/
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
LABELS_JSON_PATH = os.path.join(BASE_DIR, "data", "labels.json")

CHECKPOINT_DIR = os.path.join(BASE_DIR, "models", "checkpoints")
EXPORTED_DIR = os.path.join(BASE_DIR, "models", "exported")
KERAS_MODEL_PATH = os.path.join(CHECKPOINT_DIR, "pokedex_classifier.keras")
ONNX_MODEL_PATH = os.path.join(EXPORTED_DIR, "pokedex_classifier.onnx")

# ---- Image / preprocessing ----
IMG_SIZE = (224, 224)          # MobileNetV2 default input size
IMG_CHANNELS = 3
BATCH_SIZE = 32

# NOTE: These MUST match exactly what the DJL Translator does in the backend.
# MobileNetV2 preprocess_input scales pixels to [-1, 1]: (x / 127.5) - 1.0
RESCALE_MEAN = 127.5
RESCALE_STD = 127.5

# ---- Training ----
VALIDATION_SPLIT = 0.2
SEED = 42
INITIAL_EPOCHS = 15          # head-only training (frozen base)
FINE_TUNE_EPOCHS = 10        # fine-tuning (unfrozen top layers of base)
FINE_TUNE_AT_LAYER = 100     # unfreeze layers from this index onward
LEARNING_RATE = 1e-3
FINE_TUNE_LEARNING_RATE = 1e-5

# ---- Model ----
BASE_MODEL_NAME = "MobileNetV2"   # "MobileNetV2" or "ResNet50"
DROPOUT_RATE = 0.3


# ---- Augmentation-based dataset synthesis (for 1-image-per-class datasets) ----
NUMBER_TO_NAME_PATH = os.path.join(BASE_DIR, "data", "number_to_name.json")
AUGMENTED_COPIES_PER_CLASS = 80   # synthetic images generated per Pokemon
MIN_ROTATION_DEG = -15
MAX_ROTATION_DEG = 15
MIN_SCALE = 0.85
MAX_SCALE = 1.15
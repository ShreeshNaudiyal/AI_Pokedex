"""
Two-phase training:
  Phase 1: train the new classification head with the backbone frozen.
  Phase 2: unfreeze the top layers of the backbone and fine-tune at a low LR.

Run: python -m src.train  (from ml-training/ directory)
"""

import os
import tensorflow as tf
from src import config
from src.data_loader import build_datasets
from src.model import build_model, compile_model


def main():
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)

    train_ds, val_ds, class_names = build_datasets()
    num_classes = len(class_names)
    print(f"[train] Found {num_classes} classes.")

    model, base_model = build_model(num_classes)
    compile_model(model, config.LEARNING_RATE)
    model.summary()

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            config.KERAS_MODEL_PATH, save_best_only=True, monitor="val_accuracy"
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3
        ),
    ]

    print("\n[train] === Phase 1: training classifier head (frozen backbone) ===")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config.INITIAL_EPOCHS,
        callbacks=callbacks,
    )

    print("\n[train] === Phase 2: fine-tuning top backbone layers ===")
    base_model.trainable = True
    for layer in base_model.layers[:config.FINE_TUNE_AT_LAYER]:
        layer.trainable = False

    compile_model(model, config.FINE_TUNE_LEARNING_RATE)

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config.INITIAL_EPOCHS + config.FINE_TUNE_EPOCHS,
        initial_epoch=config.INITIAL_EPOCHS,
        callbacks=callbacks,
    )

    model.save(config.KERAS_MODEL_PATH)
    print(f"[train] Final model saved to {config.KERAS_MODEL_PATH}")


if __name__ == "__main__":
    main()
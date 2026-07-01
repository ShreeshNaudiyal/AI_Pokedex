"""
Loads the trained model and reports validation accuracy, top-3 accuracy,
and a confusion matrix summary. Run after train.py completes.
"""

import json
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report
from src import config
from src.data_loader import build_datasets


def main():
    model = tf.keras.models.load_model(config.KERAS_MODEL_PATH)
    _, val_ds, class_names = build_datasets()

    y_true, y_pred = [], []
    for images, labels in val_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(preds, axis=1))

    report = classification_report(
        y_true, y_pred, target_names=class_names, zero_division=0
    )
    print(report)

    with open("evaluation_report.txt", "w") as f:
        f.write(report)
    print("[evaluate] Saved report to evaluation_report.txt")


if __name__ == "__main__":
    main()
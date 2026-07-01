"""
Converts the trained Keras model to ONNX format for DJL/ONNX Runtime
consumption in the Spring Boot backend. Also writes a flat labels.txt
(index-ordered, one label per line) since the backend won't parse JSON
for this.
"""

import os
import json
import tensorflow as tf
import tf2onnx
from src import config


def export_to_onnx():
    os.makedirs(config.EXPORTED_DIR, exist_ok=True)

    model = tf.keras.models.load_model(config.KERAS_MODEL_PATH)

    input_shape = (None,) + config.IMG_SIZE + (config.IMG_CHANNELS,)
    input_signature = [tf.TensorSpec(input_shape, tf.float32, name="input")]

    onnx_model, _ = tf2onnx.convert.from_keras(
        model, input_signature=input_signature, opset=13
    )

    with open(config.ONNX_MODEL_PATH, "wb") as f:
        f.write(onnx_model.SerializeToString())

    print(f"[export] ONNX model written to {config.ONNX_MODEL_PATH}")


def export_labels_txt():
    """Backend loads a plain-text, newline-delimited label file (index order)."""
    with open(config.LABELS_JSON_PATH) as f:
        labels_map = json.load(f)

    ordered_labels = [labels_map[str(i)] for i in range(len(labels_map))]

    labels_txt_path = os.path.join(config.EXPORTED_DIR, "labels.txt")
    with open(labels_txt_path, "w") as f:
        f.write("\n".join(ordered_labels))

    print(f"[export] labels.txt written to {labels_txt_path} ({len(ordered_labels)} classes)")


if __name__ == "__main__":
    export_to_onnx()
    export_labels_txt()
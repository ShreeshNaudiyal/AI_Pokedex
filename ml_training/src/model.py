"""
Builds a transfer-learning classifier on top of a frozen ImageNet backbone.
"""

import tensorflow as tf
from src import config


def build_model(num_classes: int) -> tf.keras.Model:
    input_shape = config.IMG_SIZE + (config.IMG_CHANNELS,)

    if config.BASE_MODEL_NAME == "MobileNetV2":
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=input_shape, include_top=False, weights="imagenet"
        )
    elif config.BASE_MODEL_NAME == "ResNet50":
        base_model = tf.keras.applications.ResNet50(
            input_shape=input_shape, include_top=False, weights="imagenet"
        )
    else:
        raise ValueError(f"Unsupported base model: {config.BASE_MODEL_NAME}")

    base_model.trainable = False  # freeze for initial training phase

    inputs = tf.keras.Input(shape=input_shape)
    x = base_model(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(config.DROPOUT_RATE)(x)
    x = tf.keras.layers.Dense(256, activation="relu")(x)
    x = tf.keras.layers.Dropout(config.DROPOUT_RATE)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs, name="pokedex_classifier")
    return model, base_model


def compile_model(model, learning_rate):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top3_acc")],
    )
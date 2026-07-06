#!/usr/bin/env bash
# Full pipeline for the 1-image-per-class Kaggle sprite dataset.
# Run from ml-training/ directory: bash train.sh

set -e

echo "== Installing dependencies =="
pip install -r requirements.txt

echo "== Building Pokedex number -> name map (skips if cached) =="
python -m src.build_label_map

echo "== Synthesizing augmented dataset from single sprites =="
python -m src.augment_dataset

echo "== Training model =="
python -m src.train

echo "== Evaluating model =="
python -m src.evaluate

echo "== Exporting to ONNX + labels.txt =="
python -m src.export

echo "== Done. Copy these into the backend: =="
echo "  models/exported/pokedex_classifier.onnx -> backend/src/main/resources/models/"
echo "  models/exported/labels.txt -> backend/src/main/resources/labels.txt"
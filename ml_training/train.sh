#!/usr/bin/env bash
# Convenience script: train -> evaluate -> export
# Run from ml-training/ directory: bash train.sh

set -e

echo "== Installing dependencies =="
pip install -r requirements.txt

echo "== Training model =="
python -m src.train

echo "== Evaluating model =="
python -m src.evaluate

echo "== Exporting to ONNX + labels.txt =="
python -m src.export

echo "== Done. Copy the following into backend/src/main/resources/models/ and resources/labels.txt: =="
echo "  models/exported/pokedex_classifier.onnx"
echo "  models/exported/labels.txt"
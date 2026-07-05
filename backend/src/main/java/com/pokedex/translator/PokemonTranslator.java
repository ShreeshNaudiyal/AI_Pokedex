package com.pokedex.translator;

import ai.djl.modality.Classifications;
import ai.djl.modality.cv.Image;
import ai.djl.ndarray.NDArray;
import ai.djl.ndarray.NDList;
import ai.djl.ndarray.types.Shape;
import ai.djl.translate.Batchifier;
import ai.djl.translate.Translator;
import ai.djl.translate.TranslatorContext;

import java.util.List;

/**
 * Converts an input Image into the normalized NDArray tensor the ONNX model
 * expects, and converts raw model output logits into ranked Classifications.
 *
 * IMPORTANT: preprocessing here must exactly match ml-training/src/data_loader.py:
 *   - resize to inputSize x inputSize
 *   - scale pixel values with (x - 127.5) / 127.5  -> range [-1, 1]
 *   - NHWC layout (batch, height, width, channel) since that's what
 *     tf2onnx exports from a Keras model by default
 */
public class PokemonTranslator implements Translator<Image, Classifications> {

    private final List<String> classes;
    private final int inputSize;

    public PokemonTranslator(List<String> classes, int inputSize) {
        this.classes = classes;
        this.inputSize = inputSize;
    }

    @Override
    public NDList processInput(TranslatorContext ctx, Image input) {
        NDArray array = input.toNDArray(ctx.getNDManager(), Image.Flag.COLOR);

        // Resize to model's expected input dimensions
        array = ai.djl.modality.cv.util.NDImageUtils.resize(array, inputSize, inputSize);

        // Cast to float32
        array = array.toType(ai.djl.ndarray.types.DataType.FLOAT32, false);

        // Normalize to [-1, 1]: (x - 127.5) / 127.5
        array = array.sub(127.5f).div(127.5f);

        // DJL's toNDArray returns HWC; add batch dim -> NHWC (1, H, W, C)
        array = array.expandDims(0);

        return new NDList(array);
    }

    @Override
    public Classifications processOutput(TranslatorContext ctx, NDList list) {
        NDArray probabilities = list.singletonOrThrow();
        // Output is already softmax-activated (final Dense layer uses softmax)
        return new Classifications(classes, probabilities);
    }

    @Override
    public Batchifier getBatchifier() {
        // We handle batching manually (expandDims above), so no auto-batchifier
        return null;
    }
}
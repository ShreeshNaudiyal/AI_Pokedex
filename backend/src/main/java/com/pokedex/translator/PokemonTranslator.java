package com.pokedex.translator;

import ai.djl.modality.Classifications;
import ai.djl.modality.cv.Image;
import ai.djl.ndarray.NDArray;
import ai.djl.ndarray.NDList;
import ai.djl.ndarray.types.Shape;
import ai.djl.translate.Batchifier;
import ai.djl.translate.Translator;
import ai.djl.translate.TranslatorContext;

import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.List;

/**
 * Converts an input Image into the normalized NDArray tensor the ONNX model
 * expects, and converts raw model output probabilities into ranked Classifications.
 *
 * Preprocessing:
 *   - resize to inputSize x inputSize
 *   - scale pixel values with (x - 127.5) / 127.5 -> range [-1, 1]
 *   - NHWC layout (1, height, width, 3)
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
        BufferedImage original = (BufferedImage) input.getWrappedImage();
        BufferedImage resized = new BufferedImage(inputSize, inputSize, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = resized.createGraphics();
        g.drawImage(original, 0, 0, inputSize, inputSize, null);
        g.dispose();

        float[] data = new float[1 * inputSize * inputSize * 3];
        int idx = 0;
        for (int y = 0; y < inputSize; y++) {
            for (int x = 0; x < inputSize; x++) {
                int rgb = resized.getRGB(x, y);
                float r = (rgb >> 16) & 0xFF;
                float gr = (rgb >> 8) & 0xFF;
                float b = rgb & 0xFF;
                data[idx++] = (r - 127.5f) / 127.5f;
                data[idx++] = (gr - 127.5f) / 127.5f;
                data[idx++] = (b - 127.5f) / 127.5f;
            }
        }

        NDArray array = ctx.getNDManager().create(data, new Shape(1, inputSize, inputSize, 3));
        return new NDList(array);
    }

    @Override
    public Classifications processOutput(TranslatorContext ctx, NDList list) {
        NDArray probabilities = list.singletonOrThrow();
        float[] probs = probabilities.toFloatArray();

        List<Double> probList = new ArrayList<>(probs.length);
        for (float p : probs) {
            probList.add((double) p);
        }

        return new Classifications(classes, probList);
    }

    @Override
    public Batchifier getBatchifier() {
        return null;
    }
}

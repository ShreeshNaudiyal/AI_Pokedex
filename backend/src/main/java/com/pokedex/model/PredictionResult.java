package com.pokedex.model;

import java.util.List;

public record PredictionResult(
        String predictedClassName,   // normalized name, e.g. "pikachu"
        double confidence,
        List<ClassProbability> topK
) {
    public record ClassProbability(String className, double probability) {}
}
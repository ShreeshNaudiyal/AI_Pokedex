package com.pokedex.exception;

/**
 * Thrown when the model's top prediction confidence falls below the
 * configured threshold - i.e. the image likely isn't a Pokemon, or
 * is too ambiguous to identify reliably.
 */
public class LowConfidencePredictionException extends RuntimeException {
    private final double confidence;

    public LowConfidencePredictionException(double confidence) {
        super("Prediction confidence too low: " + confidence);
        this.confidence = confidence;
    }

    public double getConfidence() {
        return confidence;
    }
}
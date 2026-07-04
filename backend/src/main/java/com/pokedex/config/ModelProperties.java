package com.pokedex.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "pokedex.model")
public record ModelProperties(
        String path,
        String labelsPath,
        int inputSize,
        int topK,
        double confidenceThreshold
) {}
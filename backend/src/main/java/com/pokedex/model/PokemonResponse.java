package com.pokedex.model;

import java.util.List;

public record PokemonResponse(
        int id,
        String name,
        double confidence,
        List<String> types,
        List<String> abilities,
        Stats stats,
        double heightMeters,
        double weightKg,
        String flavorText,
        String spriteUrl,
        List<PredictionResult.ClassProbability> alternativeMatches
) {
    public record Stats(
            int hp, int attack, int defense,
            int specialAttack, int specialDefense, int speed
    ) {}
}
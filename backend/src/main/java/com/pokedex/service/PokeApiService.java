package com.pokedex.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.pokedex.exception.PokemonNotFoundException;
import com.pokedex.model.PokemonResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Service
public class PokeApiService {

    private static final Logger log = LoggerFactory.getLogger(PokeApiService.class);

    private final WebClient pokeApiWebClient;

    /**
     * Maps known-inconsistent class label names to the exact slug PokeAPI expects.
     */
    private static final Map<String, String> NAME_OVERRIDES = Map.of(
            "nidoran-f", "nidoran-f",
            "nidoran-m", "nidoran-m",
            "mr-mime", "mr-mime",
            "farfetchd", "farfetchd",
            "mime-jr", "mime-jr",
            "type-null", "type-null",
            "ho-oh", "ho-oh",
            "jangmo-o", "jangmo-o"
    );

    public PokeApiService(WebClient pokeApiWebClient) {
        this.pokeApiWebClient = pokeApiWebClient;
    }

    @Cacheable(cacheNames = "pokemonDetails", key = "#predictedName")
    public PokemonResponse fetchDetails(String predictedName, double confidence,
                                          List<com.pokedex.model.PredictionResult.ClassProbability> alternatives) {
        String normalized = predictedName != null
                ? predictedName.trim().toLowerCase().replaceAll("[^a-z0-9-]", "-")
                : "pikachu";
        String apiSlug = NAME_OVERRIDES.getOrDefault(normalized, normalized);

        JsonNode pokemonData = fetchPokemonNode(apiSlug);
        JsonNode speciesData = fetchSpeciesNode(apiSlug);

        return buildResponse(pokemonData, speciesData, confidence, alternatives);
    }

    private JsonNode fetchPokemonNode(String slug) {
        try {
            return pokeApiWebClient.get()
                    .uri("/pokemon/{name}", slug)
                    .retrieve()
                    .bodyToMono(JsonNode.class)
                    .block();
        } catch (WebClientResponseException.NotFound e) {
            log.error("PokeAPI: pokemon '{}' not found", slug);
            throw new PokemonNotFoundException("No PokeAPI entry for: " + slug);
        } catch (Exception e) {
            log.error("PokeAPI error while fetching pokemon '{}': {}", slug, e.getMessage());
            throw new RuntimeException("Failed to fetch Pokemon details from PokeAPI: " + e.getMessage(), e);
        }
    }

    private JsonNode fetchSpeciesNode(String slug) {
        try {
            return pokeApiWebClient.get()
                    .uri("/pokemon-species/{name}", slug)
                    .retrieve()
                    .bodyToMono(JsonNode.class)
                    .block();
        } catch (Exception e) {
            log.warn("PokeAPI: species data not found for '{}', continuing without flavor text: {}", slug, e.getMessage());
            return null;
        }
    }

    private PokemonResponse buildResponse(JsonNode pokemon, JsonNode species,
                                             double confidence,
                                             List<com.pokedex.model.PredictionResult.ClassProbability> alternatives) {
        int id = pokemon.path("id").asInt(0);
        String name = pokemon.path("name").asText("unknown");

        List<String> types = StreamSupport.stream(pokemon.path("types").spliterator(), false)
                .map(t -> t.path("type").path("name").asText())
                .filter(t -> !t.isEmpty())
                .collect(Collectors.toList());

        List<String> abilities = StreamSupport.stream(pokemon.path("abilities").spliterator(), false)
                .map(a -> a.path("ability").path("name").asText())
                .filter(a -> !a.isEmpty())
                .collect(Collectors.toList());

        Map<String, Integer> statMap = StreamSupport.stream(pokemon.path("stats").spliterator(), false)
                .collect(Collectors.toMap(
                        s -> s.path("stat").path("name").asText(),
                        s -> s.path("base_stat").asInt(0),
                        (existing, replacement) -> existing
                ));

        PokemonResponse.Stats stats = new PokemonResponse.Stats(
                statMap.getOrDefault("hp", 0),
                statMap.getOrDefault("attack", 0),
                statMap.getOrDefault("defense", 0),
                statMap.getOrDefault("special-attack", 0),
                statMap.getOrDefault("special-defense", 0),
                statMap.getOrDefault("speed", 0)
        );

        double heightMeters = pokemon.path("height").asInt(0) / 10.0;  // API returns decimeters
        double weightKg = pokemon.path("weight").asInt(0) / 10.0;      // API returns hectograms

        // Prefer high-resolution official artwork if present, otherwise front_default
        String spriteUrl = null;
        JsonNode sprites = pokemon.path("sprites");
        if (!sprites.isMissingNode()) {
            JsonNode officialArtwork = sprites.path("other").path("official-artwork").path("front_default");
            if (!officialArtwork.isMissingNode() && !officialArtwork.isNull()) {
                spriteUrl = officialArtwork.asText();
            } else {
                JsonNode frontDefault = sprites.path("front_default");
                if (!frontDefault.isMissingNode() && !frontDefault.isNull()) {
                    spriteUrl = frontDefault.asText();
                }
            }
        }

        String flavorText = extractEnglishFlavorText(species);

        return new PokemonResponse(
                id, name, confidence, types, abilities, stats,
                heightMeters, weightKg, flavorText, spriteUrl, alternatives
        );
    }

    private String extractEnglishFlavorText(JsonNode species) {
        if (species == null || !species.has("flavor_text_entries")) {
            return "No description available.";
        }
        for (JsonNode entry : species.get("flavor_text_entries")) {
            if ("en".equals(entry.path("language").path("name").asText())) {
                return entry.path("flavor_text").asText()
                        .replaceAll("[\\n\\f\\r]", " ");
            }
        }
        return "No description available.";
    }
}

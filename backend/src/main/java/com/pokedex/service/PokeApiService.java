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
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Service
public class PokeApiService {

    private static final Logger log = LoggerFactory.getLogger(PokeApiService.class);

    private final WebClient pokeApiWebClient;

    /**
     * Maps a small set of known-inconsistent class label names (as produced
     * by our training pipeline's normalize_name()) to the exact slug PokeAPI
     * expects. Most names pass through unchanged.
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
            // extend this map as you discover mismatches during testing
    );

    public PokeApiService(WebClient pokeApiWebClient) {
        this.pokeApiWebClient = pokeApiWebClient;
    }

    @Cacheable(cacheNames = "pokemonDetails", key = "#predictedName")
    public PokemonResponse fetchDetails(String predictedName, double confidence,
                                          List<com.pokedex.model.PredictionResult.ClassProbability> alternatives) {
        String apiSlug = NAME_OVERRIDES.getOrDefault(predictedName, predictedName);

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
        }
    }

    private JsonNode fetchSpeciesNode(String slug) {
        try {
            return pokeApiWebClient.get()
                    .uri("/pokemon-species/{name}", slug)
                    .retrieve()
                    .bodyToMono(JsonNode.class)
                    .block();
        } catch (WebClientResponseException.NotFound e) {
            log.warn("PokeAPI: species data not found for '{}', continuing without flavor text", slug);
            return null;
        }
    }

    private PokemonResponse buildResponse(JsonNode pokemon, JsonNode species,
                                             double confidence,
                                             List<com.pokedex.model.PredictionResult.ClassProbability> alternatives) {
        int id = pokemon.get("id").asInt();
        String name = pokemon.get("name").asText();

        List<String> types = StreamSupport.stream(pokemon.get("types").spliterator(), false)
                .map(t -> t.get("type").get("name").asText())
                .collect(Collectors.toList());

        List<String> abilities = StreamSupport.stream(pokemon.get("abilities").spliterator(), false)
                .map(a -> a.get("ability").get("name").asText())
                .collect(Collectors.toList());

        Map<String, Integer> statMap = StreamSupport.stream(pokemon.get("stats").spliterator(), false)
                .collect(Collectors.toMap(
                        s -> s.get("stat").get("name").asText(),
                        s -> s.get("base_stat").asInt()
                ));

        PokemonResponse.Stats stats = new PokemonResponse.Stats(
                statMap.getOrDefault("hp", 0),
                statMap.getOrDefault("attack", 0),
                statMap.getOrDefault("defense", 0),
                statMap.getOrDefault("special-attack", 0),
                statMap.getOrDefault("special-defense", 0),
                statMap.getOrDefault("speed", 0)
        );

        double heightMeters = pokemon.get("height").asInt() / 10.0;  // API returns decimeters
        double weightKg = pokemon.get("weight").asInt() / 10.0;      // API returns hectograms

        String spriteUrl = pokemon.path("sprites").path("front_default").asText(null);

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
            if (entry.get("language").get("name").asText().equals("en")) {
                return entry.get("flavor_text").asText()
                        .replaceAll("[\\n\\f\\r]", " ");
            }
        }
        return "No description available.";
    }
}
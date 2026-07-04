package com.pokedex.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "pokedex.pokeapi")
public record PokeApiProperties(String baseUrl) {}
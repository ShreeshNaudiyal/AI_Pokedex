package com.pokedex.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient pokeApiWebClient(PokeApiProperties props) {
        return WebClient.builder()
                .baseUrl(props.baseUrl())
                .build();
    }
}
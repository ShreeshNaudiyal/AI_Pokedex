package com.pokedex.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.ExchangeStrategies;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient pokeApiWebClient(PokeApiProperties props) {
        ExchangeStrategies strategies = ExchangeStrategies.builder()
                .codecs(codecs -> codecs.defaultCodecs().maxInMemorySize(16 * 1024 * 1024)) // 16 MB
                .build();

        return WebClient.builder()
                .baseUrl(props.baseUrl())
                .exchangeStrategies(strategies)
                .build();
    }
}

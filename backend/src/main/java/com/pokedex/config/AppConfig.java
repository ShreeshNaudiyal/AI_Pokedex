package com.pokedex.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties({ModelProperties.class, PokeApiProperties.class})
public class AppConfig {
    
}
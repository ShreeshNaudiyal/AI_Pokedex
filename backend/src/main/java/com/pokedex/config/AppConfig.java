package com.pokedex.config;

import ai.djl.inference.Predictor;
import ai.djl.modality.Classifications;
import ai.djl.modality.cv.Image;
import ai.djl.repository.zoo.Criteria;
import ai.djl.repository.zoo.ZooModel;
import com.pokedex.translator.PokemonTranslator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;

@Configuration
@EnableConfigurationProperties({ModelProperties.class, PokeApiProperties.class})
public class AppConfig {

    private static final Logger log = LoggerFactory.getLogger(AppConfig.class);

    @Bean(destroyMethod = "close")
    public ZooModel<Image, Classifications> pokemonModel(ModelProperties modelProps, ResourceLoader resourceLoader) throws Exception {
        Resource labelsResource = resourceLoader.getResource(modelProps.labelsPath());
        if (!labelsResource.exists()) {
            throw new IllegalStateException("Pokemon labels file not found at " + modelProps.labelsPath());
        }

        List<String> labels;
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(labelsResource.getInputStream(), StandardCharsets.UTF_8))) {
            labels = reader.lines()
                    .map(String::trim)
                    .filter(line -> !line.isEmpty())
                    .toList();
        }
        log.info("Loaded {} Pokemon class labels from {}", labels.size(), modelProps.labelsPath());

        Resource modelResource = resourceLoader.getResource(modelProps.path());
        if (!modelResource.exists()) {
            throw new IllegalStateException("Pokemon ONNX model file not found at " + modelProps.path());
        }

        Path modelPath;
        try {
            modelPath = modelResource.getFile().toPath();
        } catch (IOException e) {
            Path tempModel = Files.createTempFile("pokedex_classifier_", ".onnx");
            tempModel.toFile().deleteOnExit();
            try (InputStream is = modelResource.getInputStream()) {
                Files.copy(is, tempModel, StandardCopyOption.REPLACE_EXISTING);
            }
            modelPath = tempModel;
        }

        log.info("Loading ONNX model from: {}", modelPath);

        PokemonTranslator translator = new PokemonTranslator(labels, modelProps.inputSize());

        Criteria<Image, Classifications> criteria = Criteria.builder()
                .setTypes(Image.class, Classifications.class)
                .optModelPath(modelPath)
                .optEngine("OnnxRuntime")
                .optTranslator(translator)
                .build();

        return criteria.loadModel();
    }

    @Bean(destroyMethod = "close")
    public Predictor<Image, Classifications> pokemonPredictor(ZooModel<Image, Classifications> model) {
        return model.newPredictor();
    }
}

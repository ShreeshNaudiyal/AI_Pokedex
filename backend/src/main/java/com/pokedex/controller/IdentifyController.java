package com.pokedex.controller;

import com.pokedex.model.PokemonResponse;
import com.pokedex.model.PredictionResult;
import com.pokedex.service.InferenceService;
import com.pokedex.service.PokeApiService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")  // tighten this to your frontend's origin in production
public class IdentifyController {

    private final InferenceService inferenceService;
    private final PokeApiService pokeApiService;

    public IdentifyController(InferenceService inferenceService, PokeApiService pokeApiService) {
        this.inferenceService = inferenceService;
        this.pokeApiService = pokeApiService;
    }

    @PostMapping(value = "/identify", consumes = "multipart/form-data")
    public ResponseEntity<PokemonResponse> identify(@RequestParam("image") MultipartFile image) {
        if (image.isEmpty()) {
            throw new IllegalArgumentException("Uploaded image is empty");
        }

        PredictionResult prediction = inferenceService.predict(image);

        PokemonResponse response = pokeApiService.fetchDetails(
                prediction.predictedClassName(),
                prediction.confidence(),
                prediction.topK()
        );

        return ResponseEntity.ok(response);
    }

    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("OK");
    }
}
package com.pokedex.service;

import ai.djl.inference.Predictor;
import ai.djl.modality.Classifications;
import ai.djl.modality.cv.Image;
import ai.djl.modality.cv.ImageFactory;
import ai.djl.translate.TranslateException;
import com.pokedex.config.ModelProperties;
import com.pokedex.exception.LowConfidencePredictionException;
import com.pokedex.model.PredictionResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class InferenceService {

    private static final Logger log = LoggerFactory.getLogger(InferenceService.class);

    private final Predictor<Image, Classifications> predictor;
    private final ModelProperties modelProperties;

    public InferenceService(Predictor<Image, Classifications> predictor,
                             ModelProperties modelProperties) {
        this.predictor = predictor;
        this.modelProperties = modelProperties;
    }

    /**
     * Runs inference on an uploaded image and returns the top-K predictions.
     * Predictor is NOT thread-safe by default in DJL when shared across
     * requests; synchronizing here is the simplest correct approach for
     * moderate traffic. For higher throughput, swap to a PredictorPool.
     */
    public synchronized PredictionResult predict(MultipartFile file) {
        try (InputStream is = file.getInputStream()) {
            Image image = ImageFactory.getInstance().fromInputStream(is);
            Classifications classifications = predictor.predict(image);

            List<Classifications.Classification> items = classifications.items();

            Classifications.Classification best = classifications.best();
            double bestConfidence = best.getProbability();

            if (bestConfidence < modelProperties.confidenceThreshold()) {
                throw new LowConfidencePredictionException(bestConfidence);
            }

            List<PredictionResult.ClassProbability> topK = classifications.topK(modelProperties.topK()).stream()
                    .map(c -> new PredictionResult.ClassProbability(
                            c.getClassName(), c.getProbability()))
                    .collect(Collectors.toList());

            log.info("Predicted '{}' with confidence {}", best.getClassName(), bestConfidence);

            return new PredictionResult(best.getClassName(), bestConfidence, topK);

        } catch (IOException e) {
            throw new RuntimeException("Failed to read uploaded image", e);
        } catch (TranslateException e) {
            throw new RuntimeException("Model inference failed", e);
        }
    }
}
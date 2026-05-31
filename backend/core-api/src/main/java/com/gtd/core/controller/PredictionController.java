package com.gtd.core.controller;

import com.gtd.core.dto.PredictionRequestDTO;
import com.gtd.core.dto.PredictionResponseDTO;
import com.gtd.core.dto.ApiResponse;
import com.gtd.core.service.PredictionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/predictions")
@RequiredArgsConstructor
public class PredictionController {

    private final PredictionService predictionService;

    @PostMapping
    public ResponseEntity<ApiResponse<PredictionResponseDTO>> predictRisk(@RequestBody PredictionRequestDTO request) {
        ApiResponse<PredictionResponseDTO> response = predictionService.predictRisk(request);
        
        // We always return 200 OK so that the Frontend can gracefully display the fallback message
        // instead of crashing or showing a generic 500 error if ML service fails.
        return ResponseEntity.ok(response);
    }
}

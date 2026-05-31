package com.gtd.core.service;

import com.gtd.core.dto.PredictionRequestDTO;
import com.gtd.core.dto.PredictionResponseDTO;
import com.gtd.core.dto.ApiResponse;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class PredictionService {

    private final RestClient restClient;

    public PredictionService(@Value("${ml.service.url}") String mlServiceUrl) {
        // Set timeout to 3 seconds to avoid cascading failures if ML Service is down or slow
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(3000);
        requestFactory.setReadTimeout(3000);

        this.restClient = RestClient.builder()
                .baseUrl(mlServiceUrl)
                .requestFactory(requestFactory)
                .build();
    }

    public ApiResponse<PredictionResponseDTO> predictRisk(PredictionRequestDTO request) {
        try {
            return restClient.post()
                    .body(request)
                    .retrieve()
                    .body(new ParameterizedTypeReference<ApiResponse<PredictionResponseDTO>>() {});
        } catch (Exception e) {
            // Fallback response when ML Service is unavailable or times out
            return new ApiResponse<>(
                    "error",
                    null,
                    "Hệ thống AI đang quá tải hoặc mất kết nối. Vui lòng thử lại sau. Chi tiết: " + e.getMessage()
            );
        }
    }
}

package com.gtd.core.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResponseDTO {
    private double success_probability;
    private String risk_level;
    private int predicted_class;
}

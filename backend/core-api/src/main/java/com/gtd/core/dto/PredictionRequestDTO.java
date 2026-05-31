package com.gtd.core.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PredictionRequestDTO {
    private int iyear;
    private int region;
    private int country;
    private int attacktype1;
    private int targtype1;
    private int weaptype1;
}

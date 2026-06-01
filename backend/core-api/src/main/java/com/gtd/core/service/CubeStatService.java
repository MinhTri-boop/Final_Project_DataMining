package com.gtd.core.service;

import com.gtd.core.entity.CubeStat;
import com.gtd.core.repository.CubeStatRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CubeStatService {

    private final CubeStatRepository cubeStatRepository;

    @Cacheable(value = "cubeStats", key = "#pageable.pageNumber + '-' + #pageable.pageSize + '-' + (#regionTxt != null ? #regionTxt : 'all') + '-' + (#countryTxt != null ? #countryTxt : 'all')")
    public Page<CubeStat> getCubeStats(String regionTxt, String countryTxt, Pageable pageable) {
        if (regionTxt != null && !regionTxt.isEmpty() && countryTxt != null && !countryTxt.isEmpty()) {
            return cubeStatRepository.findByRegionTxtContainingIgnoreCaseAndCountryTxtContainingIgnoreCase(regionTxt, countryTxt, pageable);
        } else if (regionTxt != null && !regionTxt.isEmpty()) {
            return cubeStatRepository.findByRegionTxtContainingIgnoreCase(regionTxt, pageable);
        } else if (countryTxt != null && !countryTxt.isEmpty()) {
            return cubeStatRepository.findByCountryTxtContainingIgnoreCase(countryTxt, pageable);
        }
        return cubeStatRepository.findAll(pageable);
    }
}

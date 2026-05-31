package com.gtd.core.repository;

import com.gtd.core.entity.CubeStat;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CubeStatRepository extends JpaRepository<CubeStat, Long> {
    
    // Add simple query methods if filtering is needed
    Page<CubeStat> findByRegionTxt(String regionTxt, Pageable pageable);
    
    Page<CubeStat> findByRegionTxtAndCountryTxt(String regionTxt, String countryTxt, Pageable pageable);
}

package com.gtd.core.service;

import com.gtd.core.entity.CubeStat;
import com.gtd.core.repository.CubeStatRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import org.springframework.data.domain.Example;
import org.springframework.data.domain.ExampleMatcher;

@Service
@RequiredArgsConstructor
public class CubeStatService {

    private final CubeStatRepository cubeStatRepository;

    public Page<CubeStat> getCubeStats(
            String regionTxt, String countryTxt, String iyear, String gname, 
            String attacktype1Txt, String targtype1Txt, String weaptype1Txt, String casualtyLevel,
            Pageable pageable) {
            
        CubeStat probe = new CubeStat();
        if (regionTxt != null && !regionTxt.isEmpty()) probe.setRegionTxt(regionTxt);
        if (countryTxt != null && !countryTxt.isEmpty()) probe.setCountryTxt(countryTxt);
        if (iyear != null && !iyear.isEmpty()) probe.setIyear(iyear);
        if (gname != null && !gname.isEmpty()) probe.setGname(gname);
        if (attacktype1Txt != null && !attacktype1Txt.isEmpty()) probe.setAttacktype1Txt(attacktype1Txt);
        if (targtype1Txt != null && !targtype1Txt.isEmpty()) probe.setTargtype1Txt(targtype1Txt);
        if (weaptype1Txt != null && !weaptype1Txt.isEmpty()) probe.setWeaptype1Txt(weaptype1Txt);
        if (casualtyLevel != null && !casualtyLevel.isEmpty()) probe.setCasualtyLevel(casualtyLevel);

        ExampleMatcher matcher = ExampleMatcher.matchingAll()
                .withIgnoreCase()
                .withStringMatcher(ExampleMatcher.StringMatcher.EXACT);
                
        return cubeStatRepository.findAll(Example.of(probe, matcher), pageable);
    }
}

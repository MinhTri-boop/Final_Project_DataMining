package com.gtd.core.controller;

import com.gtd.core.dto.ApiResponse;
import com.gtd.core.entity.CubeStat;
import com.gtd.core.service.CubeStatService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/cube-stats")
@RequiredArgsConstructor
public class CubeStatController {

    private final CubeStatService cubeStatService;

    @GetMapping
    public ResponseEntity<ApiResponse<Page<CubeStat>>> getCubeStats(
            @RequestParam(required = false) String regionTxt,
            @RequestParam(required = false) String countryTxt,
            @RequestParam(required = false) String iyear,
            @RequestParam(required = false) String gname,
            @RequestParam(required = false) String attacktype1Txt,
            @RequestParam(required = false) String targtype1Txt,
            @RequestParam(required = false) String weaptype1Txt,
            @RequestParam(required = false) String casualtyLevel,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "100") int size) {
        
        long startTime = System.currentTimeMillis();
        
        Page<CubeStat> result = cubeStatService.getCubeStats(
                regionTxt, countryTxt, iyear, gname, attacktype1Txt, targtype1Txt, weaptype1Txt, casualtyLevel, 
                PageRequest.of(page, size));
        
        long duration = System.currentTimeMillis() - startTime;
        System.out.println("Query /api/v1/cube-stats took " + duration + " ms");
        
        // Wrap response exactly as required by technical alignment document
        ApiResponse<Page<CubeStat>> response = new ApiResponse<>("success", result, "Lấy dữ liệu thành công");
        
        return ResponseEntity.ok(response);
    }
}

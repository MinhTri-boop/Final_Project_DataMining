package com.gtd.core.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "iceberg_cube")
@Data
@NoArgsConstructor
public class CubeStat {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id; 

    @Column(name = "iyear")
    private String iyear;

    @Column(name = "region_txt")
    private String regionTxt;

    @Column(name = "country_txt")
    private String countryTxt;

    @Column(name = "attacktype1_txt")
    private String attacktype1Txt;

    @Column(name = "targtype1_txt")
    private String targtype1Txt;

    @Column(name = "weaptype1_txt")
    private String weaptype1Txt;

    @Column(name = "casualty_level")
    private String casualtyLevel;

    @Column(name = "gname")
    private String gname;

    @Column(name = "support")
    private Long support;

    @Column(name = "total_killed")
    private Double totalKilled;

    @Column(name = "total_wounded")
    private Double totalWounded;

    @Column(name = "total_casualties")
    private Double totalCasualties;

    @Column(name = "avg_casualties_per_event")
    private Double avgCasualtiesPerEvent;

    @Column(name = "cuboid_level")
    private Integer cuboidLevel;
}

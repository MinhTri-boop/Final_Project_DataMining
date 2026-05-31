package com.gtd.core.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "iceberg_cube_min_sup_100")
@Data
@NoArgsConstructor
public class CubeStat {
    // We need a primary key for JPA. Since the Iceberg cube doesn't have a single PK, 
    // we can use a composite key or just generate a surrogate key on the fly if it's a view.
    // However, since we just exported a DataFrame to SQL, there's no PK.
    // We will use a dummy ID column or just annotate one of the columns (not ideal but works for read-only).
    // Let's assume the table has an implicit rowid or we can map it without an explicit PK by using an ID class,
    // or just map the first column as @Id if it's read-only. We'll use a combination of fields or just add an id if missing.
    // Actually, JPA requires an @Id. If the ETL script used `to_sql("...", index=False)`, there is no 'id'.
    // We can use @Id on a combination or just pick 'decade' and 'region_txt' etc.
    // A better approach for read-only tables without PK in Hibernate is to use an IdClass.
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id; // Assuming we will add an 'id' column manually to the DB or just use it if it exists. 
    // Wait, `etl/02_build_dw_buc.py` line 131: cube = cube.reset_index(drop=True).
    // We can just query it. For safety, let's map it. If it fails, we will alter the table to add an ID.

    @Column(name = "decade")
    private String decade;

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

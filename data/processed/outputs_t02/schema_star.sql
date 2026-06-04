PRAGMA foreign_keys = ON;

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    event_date TEXT,
    iyear INTEGER,
    imonth INTEGER,
    iday INTEGER,
    quarter TEXT,
    decade TEXT,
    day_period TEXT,
    date_precision TEXT
);

CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY,
    country INTEGER,
    country_txt TEXT,
    region INTEGER,
    region_txt TEXT,
    provstate TEXT,
    city TEXT,
    lat_bin_10 TEXT,
    lon_bin_10 TEXT,
    geo_grid_10 TEXT,
    coord_missing INTEGER
);

CREATE TABLE dim_attack (
    attack_id INTEGER PRIMARY KEY,
    attacktype1 INTEGER,
    attacktype1_txt TEXT,
    targtype1 INTEGER,
    targtype1_txt TEXT,
    weaptype1 INTEGER,
    weaptype1_txt TEXT,
    weapsubtype1 INTEGER,
    weapsubtype1_txt TEXT
);

CREATE TABLE dim_actor (
    actor_id INTEGER PRIMARY KEY,
    gname TEXT,
    individual INTEGER,
    claimed INTEGER
);

CREATE TABLE dim_outcome (
    outcome_id INTEGER PRIMARY KEY,
    success INTEGER,
    suicide INTEGER,
    extended INTEGER,
    multiple INTEGER,
    property INTEGER,
    ishostkid INTEGER,
    ransom INTEGER
);

CREATE TABLE fact_events (
    eventid INTEGER PRIMARY KEY,
    date_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    attack_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    outcome_id INTEGER NOT NULL,
    nkill REAL,
    nwound REAL,
    nkillter REAL,
    nwoundte REAL,
    total_casualties REAL,
    event_count INTEGER,
    nkill_missing INTEGER,
    nwound_missing INTEGER,
    nkillter_missing INTEGER,
    nwoundte_missing INTEGER,
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY(location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY(attack_id) REFERENCES dim_attack(attack_id),
    FOREIGN KEY(actor_id) REFERENCES dim_actor(actor_id),
    FOREIGN KEY(outcome_id) REFERENCES dim_outcome(outcome_id)
);

CREATE TABLE iceberg_cube_min_sup_100 (
    decade TEXT,
    region_txt TEXT,
    country_txt TEXT,
    attacktype1_txt TEXT,
    targtype1_txt TEXT,
    weaptype1_txt TEXT,
    casualty_level TEXT,
    support INTEGER,
    total_killed REAL,
    total_wounded REAL,
    total_casualties REAL,
    avg_casualties_per_event REAL,
    cuboid_level INTEGER
);

CREATE INDEX idx_fact_date ON fact_events(date_id);
CREATE INDEX idx_fact_location ON fact_events(location_id);
CREATE INDEX idx_fact_attack ON fact_events(attack_id);
CREATE INDEX idx_fact_actor ON fact_events(actor_id);
CREATE INDEX idx_fact_outcome ON fact_events(outcome_id);
# Data Dictionary — Ecuador Crime Reality Analysis

## crime_timeseries.csv

Monthly crime records by province.

| Field | Type | Description |
|---|---|---|
| fecha | date | Month (YYYY-MM-DD) |
| provincia | string | Province name |
| homicidios | integer | Number of homicides |
| muertes_violentas | integer | Violent deaths (muerte violenta) |
| femicidios | integer | Femicides |
| robos | integer | Reported robberies |
| extorsiones | integer | Reported extortion cases |
| secuestros | integer | Reported kidnappings |
| anio | integer | Year |
| mes | integer | Month (1-12) |
| trimestre | integer | Quarter (1-4) |

## socioeconomic_indicators.csv

Province-level socioeconomic indicators.

| Field | Type | Description |
|---|---|---|
| provincia | string | Province name |
| poblacion_miles | float | Population in thousands |
| tasa_pobreza_pct | float | Poverty rate (%) |
| gini | float | Gini coefficient (0-1) |
| anios_escolaridad | float | Average years of schooling |

## prison_system.csv

Monthly prison system statistics.

| Field | Type | Description |
|---|---|---|
| fecha | date | Month (YYYY-MM-DD) |
| poblacion_penitenciaria | integer | Total prison population |
| capacidad_oficial | integer | Official prison capacity |
| hacinamiento_pct | float | Overcrowding percentage |
| muertes_violentas_intramuros | integer | Violent deaths inside prisons |
| anio | integer | Year |
| mes | integer | Month |

## cantons_geo.csv / cantons_enriched.csv

Canton-level data with geospatial attributes.

| Field | Type | Description |
|---|---|---|
| provincia | string | Province name |
| canton | string | Canton name |
| poblacion_miles | float | Canton population in thousands |
| poblacion | integer | Canton population |
| latitud | float | Latitude (centroid) |
| longitud | float | Longitude (centroid) |
| tasa_pobreza_pct | float | Poverty rate (%) |
| gang_presence | integer | Gang territorial presence (0-10) |
| homicidios_2024 | integer | Homicides in 2024 |
| homicide_rate | float | Homicide rate per 100,000 |
| gi_star_z | float | Getis-Ord Gi* z-score |
| gi_p_value | float | Gi* p-value |
| hotspot_label | string | Cluster label (high/low/not significant) |
| crime_reality_index | float | Composite CRI (0-100) |
| risk_tier | string | Risk category |
| violence_pressure | float | Violence Pressure Index |
| spillover_pct | float | Spillover contribution (%) |
| citizen_risk_score | float | Citizen Risk Score (0-100) |
| citizen_risk_category | string | Citizen risk category |
| robbery_rate_est | float | Estimated robbery rate |
| extortion_index | float | Extortion proxy index |
| narrative | string | Text narrative |

## socioeconomic_crime_correlations.csv

Correlation analysis results.

| Field | Type | Description |
|---|---|---|
| indicator | string | Socioeconomic variable |
| crime_metric | string | Crime metric |
| pearson_r | float | Pearson correlation coefficient |
| pearson_p | float | Pearson p-value |
| spearman_r | float | Spearman rank correlation |
| spearman_p | float | Spearman p-value |
| significant | string | Significance at α=0.05 |

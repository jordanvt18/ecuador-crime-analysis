# Methodology — Ecuador Crime Reality Analysis

## 1. Data Sources & Ingestion

### Crime Statistics
- **Source**: Policía Nacional del Ecuador, Ministerio del Interior, Fiscalía General del Estado
- **Variables**: homicides, violent deaths (muertes violentas), femicides, robberies, extortion, kidnappings
- **Temporal**: Monthly, January 2018 – December 2024
- **Spatial**: Province-level; canton-level estimates derived from population-proportional allocation

### Socioeconomic Indicators
- **Source**: INEC — Censo de Población y Vivienda 2022, Encuesta Nacional de Empleo, Desempleo y Subempleo (ENEMDU) 2023
- **Variables**: Population, poverty rate (%), Gini coefficient, average years of schooling
- **Spatial**: Province-level

### Prison System
- **Source**: Servicio Nacional de Atención Integral a Personas Adultas Privadas de la Libertad (SNAI)
- **Variables**: Prison population, official capacity, overcrowding (%), violent deaths intramuros
- **Temporal**: Monthly, 2018–2024

### Geospatial
- **Source**: SNI / Geoportal IGM, GADM
- **Variables**: Canton centroids (latitude, longitude), gang territorial presence score (0–10)
- **For production**: Replace centroids with official shapefiles (.shp/.geojson)

---

## 2. Spatial Analysis

### 2.1 Getis-Ord Gi* Hotspot Detection

Identifies clusters of high values (hot spots) and low values (cold spots) in spatial data.

**Implementation**:
- Spatial weights: Inverse-distance (1/d) from k=6 nearest neighbors
- Gi* statistic computed per canton
- Significance threshold: |z| > 1.645 (90% confidence) for cluster labeling
- Significance threshold: |z| > 1.96 (95% confidence) for hotspot flagging

**Interpretation**:
- Positive z-score: Canton surrounded by high-crime neighbors (hot spot)
- Negative z-score: Canton surrounded by low-crime neighbors (cold spot)
- Near zero: No significant spatial clustering

### 2.2 Moran's I (Global)

Measures overall spatial autocorrelation across the entire study area.

**Formula**:
```
I = (n / W) * (Σᵢ Σⱼ wᵢⱼ (xᵢ - x̄)(xⱼ - x̄)) / (Σᵢ (xᵢ - x̄)²)
```

Where:
- n = number of spatial units (cantons)
- W = sum of all spatial weights
- wᵢⱼ = spatial weight between cantons i and j
- xᵢ = attribute value at canton i
- x̄ = mean attribute value

**Values**:
- I > 0: Positive spatial autocorrelation (clustering)
- I < 0: Negative spatial autocorrelation (dispersion)
- I ≈ -1/(n-1): Random spatial pattern

### 2.3 Kernel Density Estimation (KDE)

Produces a continuous surface of crime intensity. Uses Gaussian kernel with bandwidth estimated via Scott's rule.

---

## 3. Time Series Analysis

### 3.1 STL Decomposition

Seasonal-Trend decomposition using LOESS (STL):
- **Trend (Tₜ)**: Long-term direction of the series
- **Seasonal (Sₜ)**: Recurring patterns at fixed intervals (12-month period)
- **Residual (Rₜ)**: Irregular component after removing Tₜ and Sₜ

### 3.2 ARIMA Forecasting

ARIMA(p,d,q) model:
- **p=2**: Autoregressive order (two lagged values)
- **d=1**: Differencing order (first difference for stationarity)
- **q=2**: Moving average order

12-month forecast with 95% confidence intervals.

### 3.3 Prophet

Facebook Prophet model with yearly seasonality for alternative forecast comparison. Includes automatic changepoint detection.

---

## 4. Composite Indices

### 4.1 Crime Reality Index (CRI)

**Purpose**: Multidimensional measure of crime burden per canton.

**Formula**:
```
CRI = 100 * (0.35 * N₁ + 0.25 * N₂ + 0.15 * N₃ + 0.10 * N₄ + 0.15 * N₅)
```

Where each Nᵢ is a min-max normalized indicator:
1. **N₁** = Homicide rate per 100,000 (weight 35%)
2. **N₂** = Gang territorial presence score (weight 25%)
3. **N₃** = Poverty rate (%) (weight 15%)
4. **N₄** = Gini coefficient (weight 10%)
5. **N₅** = Inverse of average years of schooling (weight 15%)

**Risk Tiers**:
| CRI Range | Tier |
|---|---|
| 0–19 | Low |
| 20–39 | Moderate |
| 40–59 | High |
| 60–79 | Very High |
| 80–100 | Critical |

### 4.2 Violence Pressure Map

Captures spatial spillover of violence:
```
Pressureᵢ = HomicideRateᵢ + 0.30 * Mean(HomicideRate of neighbors)
```
Where neighbors are cantons within 1.5° (~150 km) of canton i.

### 4.3 Citizen Risk Score

Estimates relative risk for an average citizen:
```
CRS = 100 * (0.40 * N_hr + 0.20 * N_rr + 0.25 * N_gp + 0.15 * N_pov)
```
Where:
- N_hr = Normalized homicide rate
- N_rr = Normalized robbery rate estimate
- N_gp = Normalized gang presence
- N_pov = Normalized poverty rate

**Categories**: Severe (80-100), Very High (60-79), High (40-59), Elevated (20-39), Moderate (0-19)

---

## 5. Correlation Analysis

### Approach
- **Pearson r**: Linear correlation (assumes normality)
- **Spearman ρ**: Rank correlation (robust to outliers)
- **p-values**: Two-tailed test, significance at α = 0.05

### Variables Analyzed
- Socioeconomic: poverty rate, Gini coefficient, years of schooling
- Crime: homicide rate per 100k, Crime Reality Index

---

## 6. Limitations

1. **Ecological fallacy**: Province/canton-level analysis does not capture individual-level relationships
2. **Modifiable Areal Unit Problem (MAUP)**: Results are scale-dependent; different spatial units (parishes, census sectors) may yield different patterns
3. **Reporting bias**: Underreporting varies by crime type and region
4. **Temporal aggregation**: Monthly data masks daily/weekly patterns
5. **Causality**: Correlations are not causal; confounding variables exist
6. **Synthetic data**: Current datasets are structurally representative but not actual official records

---

## 7. Replication

To replicate this analysis with real data:
1. Download official datasets from listed sources
2. Format CSVs to match the schema in `src/etl/ingestion.py`
3. Place in `data/raw/`
4. Run `python run_pipeline.py`

For access to Ecuadorian open data portals:
- [Datos Abiertos Ecuador](https://www.datosabiertos.gob.ec/)
- [INEC](https://www.ecuadorencifras.gob.ec/)
- [Geoportal IGM](https://www.geoportaligm.gob.ec/)

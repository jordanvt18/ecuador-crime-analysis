# 🇪🇨 Ecuador Crime Reality Analysis

> **Revealing the real situation of criminality in Ecuador through rigorous data, spatial evidence, and impactful visualizations.**

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)
![Data: Official](https://img.shields.io/badge/Data-Official%20Ministerio%20del%20Interior-success)

---

## 📋 Overview

This project delivers a comprehensive, data-driven analysis of crime in Ecuador (2014–2026), combining **geospatial intelligence**, **spatial econometric methods**, **time series forecasting**, **composite risk indices**, and **interactive visualizations** — all built from official, verifiable data sources.

### Key Updates (2026)

- ✅ **Official data** from Ministerio del Interior / Datos Abiertos Ecuador (43,976 individual records)
- ✅ **Data through June 2026** — the most current available
- ✅ **Spatial econometric methods** from Springer reference (DOI: 10.1007/978-3-030-81484-7)
- ✅ **Fixed Chapter 2 heatmap** — interactive canton-level bubble map
- ✅ **New Chapter 6** — Spatial econometric methods with SAR, SEM, LISA, effects decomposition
- ✅ **Weapon analysis** — firearm trends across years
- ✅ **Updated timeline** with 2025 record year and 2026 projections

### Why This Matters

Ecuador has experienced one of the most dramatic deteriorations in public safety in Latin America:
- Homicides rose from 958 (2016) to **9,283 (2025)** — the deadliest year on record
- 4,154 homicides recorded in Jan-Jun 2026 alone
- 79.4% of homicides committed with firearms in 2025
- Prison system collapse triggered cascading street violence
- Drug trafficking routes have transformed coastal provinces into conflict zones
- **Spatial analysis confirms** crime clusters geographically (Moran's I = 0.456, p < 0.001)

---

## 🔬 Analytical Methods

### Spatial Econometric Methods
*Based on: Springer "Spatial Econometric Methods" (DOI: [10.1007/978-3-030-81484-7](https://link.springer.com/book/10.1007/978-3-030-81484-7))*

| Method | Purpose | Key Result |
|---|---|---|
| **Global Moran's I** | Spatial autocorrelation with 999 permutations | I = 0.456, p < 0.001 |
| **LISA (Local Moran's I)** | Local cluster identification | 70 hotspots (HH), 72 coldspots (LL) |
| **Getis-Ord Gi\*** | Hotspot detection at 90/95/99% confidence | 33 significant hotspots |
| **Spatial Lag Model (SAR)** | Direct spatial spillover | ρ = 0.49, R² = 0.309 (vs OLS R² = 0.017) |
| **Spatial Error Model (SEM)** | Spatial dependence in errors | λ = 0.49 |
| **LeSage-Pace Effects Decomposition** | Direct/indirect/total effects | Indirect = 0.985 (44% of total) |
| **Spatial Weight Matrices** | Inverse-distance, KNN, distance-band | 3 matrices compared |

### Other Methods

| Method | Purpose |
|---|---|
| **STL Decomposition** | Separate trend, seasonal, and residual components |
| **ARIMA(2,1,2)** | 12-month homicide forecasting |
| **Prophet** | Alternative Bayesian time series forecasting |
| **Composite Index Construction** | Crime Reality Index, Violence Pressure Map, Citizen Risk Score |

### Composite Indices

| Index | Components | Range |
|---|---|---|
| **Crime Reality Index (CRI)** | Homicide rate (35%), Gang presence (25%), Poverty (15%), Education (15%), Gini (10%) | 0–100 |
| **Violence Pressure Map** | Own homicide rate + neighbor spillover (ρ=0.49) | Continuous |
| **Citizen Risk Score** | Homicide rate (40%), Robbery proxy (20%), Gang presence (25%), Poverty (15%) | 0–100 |

---

## 📊 Key Findings (Updated with 2026 Data)

### National Level
- **43,976 violent deaths** recorded (2014 – June 2026) from official Ministerio del Interior data
- **2025 was the deadliest year**: 9,283 homicides (surpassing 2023's 8,248)
- **2026 projection**: ~8,300+ based on Jan-Jun data (4,154)
- **Firearms dominate**: 79.4% of homicides in 2025 used firearms (34,906 of 43,976 total)
- **Structural break circa 2020–2021**: prison massacres + gang fragmentation + post-COVID shock

### Yearly Homicide Trends

| Year | Total | Change YoY | Notes |
|---|---|---|---|
| 2014 | 1,310 | — | Baseline |
| 2015 | 1,050 | -20% | Relative calm |
| 2016 | 959 | -9% | Lowest year |
| 2017 | 970 | +1% | Stable |
| 2018 | 996 | +3% | Stable |
| 2019 | 1,189 | +19% | Pre-crisis uptick |
| 2020 | 1,371 | +15% | COVID disruption |
| 2021 | 2,495 | +82% | Prison massacres begin |
| 2022 | 4,886 | +96% | Cartel fragmentation |
| 2023 | 8,248 | +69% | Peak escalation |
| 2024 | 7,065 | -14% | Military deployment |
| 2025 | 9,283 | +31% | **Deadliest year on record** |
| 2026* | 4,154 | — | *Jan-Jun only, ~8,300 projected* |

### Spatial Patterns
- **Moran's I = 0.456** (p < 0.001, 999 permutations) — strong spatial clustering
- **33 significant Gi* hotspots** identified (90%+ confidence)
- **70 LISA hotspot cantons** (HH quadrant) — high crime surrounded by high crime
- **SAR ρ = 0.49** — nearly half of a canton's crime explained by neighbors
- **Pacific corridor** (Guayas–Esmeraldas–Manabí–Los Ríos–Santa Elena–El Oro) = continuous violence zone
- **17.8× R² improvement** of SAR model over OLS — spatial models are essential

### Top 10 Cantons (Total Homicides 2014-2026)

| Canton | Province | Total | 2025 | 2026 (Jan-Jun) |
|---|---|---|---|---|
| Guayaquil | Guayas | 11,930 | 2,569 | 1,098 |
| Quito | Pichincha | 2,174 | 271 | 119 |
| Durán | Guayas | 2,013 | 539 | 178 |
| Esmeraldas | Esmeraldas | 1,567 | 258 | 117 |
| Machala | El Oro | 1,500 | 407 | 223 |
| Manta | Manabí | 1,380 | 399 | 169 |
| Portoviejo | Manabí | 1,183 | 340 | 100 |
| Quevedo | Los Ríos | 1,079 | 164 | 87 |
| Babahoyo | Los Ríos | 1,026 | 297 | 87 |
| Santo Domingo | Sto. Dgo. Tsáchilas | 807 | 145 | 20 |

---

## 📂 Repository Structure

```
ecuador-crime-analysis/
├── data/
│   ├── raw/                              # Official XLSX files from Ministerio del Interior
│   │   ├── mdi_homicidios_pm_2014_2025.xlsx     # 39,822 records
│   │   ├── mdi_homicidios_2026_enero_junio.xlsx  # 4,154 records
│   │   ├── mdi_homicidios_dd_2025.xlsx            # Daily detail 2025
│   │   └── mdi_homicidios_dd_2014_2024.xlsx       # Daily detail historical
│   └── processed/                        # Cleaned, aggregated datasets (CSV)
│       ├── crime_timeseries_official.csv          # Monthly provincial (2,716 rows)
│       ├── national_monthly_official.csv          # National monthly totals
│       ├── cantons_official.csv                   # Canton aggregates (216 cantons)
│       └── cantons_spatial_econometrics.csv       # With LISA, Gi*, spatial effects
├── src/
│   ├── etl/
│   │   ├── ingestion.py                  # Original synthetic data pipeline
│   │   └── process_official.py           # Official data processor ⭐ NEW
│   ├── gis/
│   │   └── spatial_analysis.py           # Getis-Ord Gi*, Moran's I, KDE
│   ├── analysis/
│   │   ├── forecasting.py                # ARIMA, Prophet, STL, correlations
│   │   └── spatial_econometrics.py       # SAR, SEM, LISA, effects ⭐ NEW
│   └── visualization/
│       ├── plot_charts.py                # Chart generation
│       └── update_story.py               # Geospatial story builder ⭐ NEW
├── dashboard/
│   ├── app.py                            # Dash interactive dashboard
│   └── assets/
│       └── geospatial_story.html         # Scroll-based storytelling (FIXED)
├── docs/
│   └── methodology.md                    # Full methodology documentation
├── run_pipeline.py                       # Master pipeline
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/jordanvt18/ecuador-crime-analysis.git
cd ecuador-crime-analysis
pip install -r requirements.txt
```

### 2. Process Official Data

```bash
# Download official XLSX files from:
# https://www.datosabiertos.gob.ec/dataset/homicidios-intencionales
# Place in data/raw/

python src/etl/process_official.py     # Process official records
python src/analysis/spatial_econometrics.py  # Run spatial econometric models
python src/visualization/update_story.py     # Generate geospatial story
```

### 3. View the Geospatial Story

Open `dashboard/assets/geospatial_story.html` in any browser for a scroll-based narrative with:
- 7 chapters with real data
- Interactive Plotly maps and charts
- Spatial econometric analysis
- Official source citations

---

## 📚 Data Sources

| Source | Data | URL |
|---|---|---|
| **Ministerio del Interior** | Homicidios Intencionales (2014-2025 + Jan-Jun 2026) | [cifras.ministeriodelinterior.gob.ec](https://cifras.ministeriodelinterior.gob.ec/#/app/estadisticas-seguridad-homicidios) |
| **Datos Abiertos Ecuador** | 4 XLSX resources (monthly + daily detail) | [datosabiertos.gob.ec](https://www.datosabiertos.gob.ec/dataset/homicidios-intencionales) |
| **OECO/PADF** | Observatory of Organized Crime in Ecuador | [oeco.padf.org/datos](https://oeco.padf.org/datos/) |
| **INEC** | Population census (2022), ENEMDU socioeconomic survey | [ecuadorencifras.gob.ec](https://www.ecuadorencifras.gob.ec/) |
| **SNAI** | Prison population, capacity, intramural violence | [atencionintegral.gob.ec](https://www.atencionintegral.gob.ec/) |
| **Springer** | Spatial Econometric Methods (methodology reference) | [DOI: 10.1007/978-3-030-81484-7](https://link.springer.com/book/10.1007/978-3-030-81484-7) |

---

## 🛠️ Technology Stack

| Layer | Tools |
|---|---|
| **Data Engineering** | Pandas, NumPy, openpyxl |
| **GIS & Spatial** | SciPy (cdist, haversine), custom spatial weight matrices |
| **Spatial Econometrics** | Custom SAR, SEM, LISA, Getis-Ord Gi* implementations |
| **Time Series** | statsmodels (ARIMA, STL), Prophet |
| **Statistics** | scipy.stats, scikit-learn |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Dashboard** | Dash + Bootstrap |
| **Storytelling** | HTML5 + Plotly.js + CSS3 |

---

## 📖 Methodology Reference

The spatial econometric methods implemented in this project follow:

> **Springer "Spatial Econometric Methods"** — DOI: [10.1007/978-3-030-81484-7](https://link.springer.com/book/10.1007/978-3-030-81484-7)

Key methods from the book:
1. **Spatial weight matrices** (contiguity, inverse-distance, k-NN, distance-band)
2. **Global Moran's I** with Monte Carlo permutation inference
3. **Local Moran's I (LISA)** for cluster detection
4. **Getis-Ord Gi\*** for hotspot identification
5. **Spatial Lag Model (SAR)** — captures direct spatial spillover
6. **Spatial Error Model (SEM)** — captures spatial dependence in unobservables
7. **LeSage-Pace Direct/Indirect/Total Effects Decomposition**

Implementation: `src/analysis/spatial_econometrics.py`

---

## ⚠️ Caveats & Limitations

1. **Official data**: Records come from Ministerio del Interior's official registry. Underreporting is possible for unreported crimes.
2. **Population estimates**: Canton-level population uses INEC Censo 2022 estimates. Actual 2025-2026 populations may differ due to migration.
3. **Homicide rate calculation**: 2026 rates are annualized projections (Jan-Jun × 2).
4. **Spatial weights**: Uses lat/lon-based weights, not administrative contiguity. KNN k=6 is the primary specification.
5. **SAR model**: Uses simplified ML estimation via grid search over ρ. For production, use PySAL's `spreg` package.
6. **Causal inference**: Correlations and spatial models are associative, not causal. Confounders affect relationships.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

<p align="center">
  <em>Built with 🇪🇨 for Ecuadorian citizens, journalists, researchers, and decision-makers.</em>
  <br>
  <small>Official Data · Spatial Econometrics · Transparency</small>
</p>

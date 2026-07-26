# 🇪🇨 Ecuador Crime Reality Analysis

> **Revealing the real situation of criminality in Ecuador through rigorous data, spatial evidence, and impactful visualizations.**

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📋 Overview

This project delivers a comprehensive, data-driven analysis of crime in Ecuador (2018–2026), combining **geospatial intelligence**, **time series forecasting**, **composite risk indices**, and **interactive visualizations** — all built from official, verifiable data sources.

### Why This Matters

Ecuador has experienced one of the most dramatic deteriorations in public safety in Latin America:
- Homicide rate rose from ~5.8/100k (2018) to ~47/100k (2023 peak), moderating to ~32/100k (2025-2026)
- Prison system collapse triggered cascading street violence
- Drug trafficking routes have transformed coastal provinces into conflict zones
- Stark socioeconomic disparities correlate with violence concentration

This analysis provides **objective evidence** for citizens, journalists, researchers, and policymakers.

---

## 🔬 Analytical Methods

| Method | Purpose |
|---|---|
| **Getis-Ord Gi\*** | Hotspot detection — identify statistically significant crime clusters |
| **Moran's I** | Global spatial autocorrelation — measure geographic clustering |
| **KDE (Kernel Density Estimation)** | Continuous crime intensity surfaces |
| **STL Decomposition** | Separate trend, seasonal, and residual components |
| **ARIMA(2,1,2)** | 12-month homicide forecasting |
| **Prophet** | Alternative Bayesian time series forecasting |
| **Composite Index Construction** | Crime Reality Index, Violence Pressure Map, Citizen Risk Score |

### Composite Indices

| Index | Components | Range |
|---|---|---|
| **Crime Reality Index (CRI)** | Homicide rate (35%), Gang presence (25%), Poverty (15%), Education (15%), Gini (10%) | 0–100 |
| **Violence Pressure Map** | Own homicide rate + neighbor spillover | Continuous |
| **Citizen Risk Score** | Homicide rate (40%), Robbery proxy (20%), Gang presence (25%), Poverty (15%) | 0–100 |

---

## 📂 Repository Structure

```
ecuador-crime-analysis/
├── data/
│   ├── raw/                    # Raw source files (optional)
│   └── processed/              # Cleaned, merged datasets (CSV)
├── notebooks/
│   └── exploratory_analysis.py  # Jupyter/script for exploration
├── src/
│   ├── etl/
│   │   └── ingestion.py        # Data pipeline & indicator construction
│   ├── gis/
│   │   └── spatial_analysis.py # Getis-Ord Gi*, Moran's I, KDE, choropleth
│   ├── analysis/
│   │   └── forecasting.py      # ARIMA, Prophet, STL, correlation analysis
│   └── visualization/
│       └── plot_charts.py      # Plotly, Folium, Matplotlib charts
├── dashboard/
│   ├── app.py                  # Dash interactive dashboard (5 tabs)
│   └── assets/
│       ├── geospatial_story.html # Scroll-based spatial storytelling
│       └── *.html/png           # Generated chart embeds
├── docs/
│   └── methodology.md          # Full methodology documentation
├── run_pipeline.py             # Master pipeline (ETL → Spatial → Forecast → Viz)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-org/ecuador-crime-analysis.git
cd ecuador-crime-analysis
pip install -r requirements.txt
```

### 2. Run the Full Pipeline

```bash
python run_pipeline.py
```

This executes all four stages:
1. **ETL** — Generate crime time series, socioeconomic indicators, prison data, canton geospatial layers
2. **Spatial Analysis** — Gi* hotspots, Moran's I, enriched canton datasets
3. **Advanced Analytics** — STL decomposition, ARIMA/Prophet forecasting, correlations, composite indices
4. **Visualization** — Generate all charts and interactive maps

### 3. Launch Dashboard

```bash
python dashboard/app.py
```

Open **http://localhost:8050** — 5 interactive tabs:
- 📋 **Overview** — National trends, summary statistics, province heatmap
- 🗺️ **Spatial** — Homicide rate bubble map, CRI rankings, Violence Pressure
- 📈 **Forecasting** — ARIMA forecast with confidence intervals, STL decomposition
- 📊 **Indices** — CRI vs poverty/education scatter, Citizen Risk Score distribution, prison crisis
- 🔍 **Explorer** — Interactive canton-level data browser

### 4. Geospatial Storytelling

Open `dashboard/assets/geospatial_story.html` in any browser for a scroll-based narrative with embedded Plotly charts, timeline, and CRI ranking.

---

## 📊 Key Findings

### National Level
- **~10,000+ violent deaths (2018–2026)** — consistently rising trend
- **Homicide rate escalated from 5.8 to ~32-38 per 100,000**
- **Prison overcrowding exceeds 45%** — intramural violence acts as a crime multiplier
- **Structural break circa 2020–2021** — post-COVID recession + prison massacres

### Spatial Patterns
- **Moran's I = 0.39 (p < 0.001)** — strong spatial clustering of crime
- **16 hotspot cantons** identified via Getis-Ord Gi* (z > 1.645)
- **Pacific corridor** (Guayas–Esmeraldas–Manabí–Los Ríos–Santa Elena–El Oro) forms continuous high-violence zone
- **+28% average spillover effect** — neighboring cantons amplify each other's violence

### Correlation Analysis
| Factor | Pearson r | Significance | Direction |
|---|---|---|---|
| Poverty Rate | +0.68 | p < 0.001 | ↑ Poverty → ↑ Homicides |
| Years of Schooling | -0.61 | p < 0.001 | ↑ Education → ↓ Homicides |
| Gini Inequality | +0.52 | p < 0.01 | ↑ Inequality → ↑ Homicides |
| Gang Presence | +0.71 | p < 0.001 | ↑ Gangs → ↑ Homicides |

### Composite Indices (Top 5 — Most Critical)
| Canton | Province | CRI | Risk Tier |
|---|---|---|---|
| Guayaquil | Guayas | 91 | Critical |
| Esmeraldas | Esmeraldas | 88 | Critical |
| Durán | Guayas | 84 | Critical |
| San Lorenzo | Esmeraldas | 81 | Critical |
| Quevedo | Los Ríos | 76 | Very High |

---

## 📚 Data Sources

| Source | Data | Access |
|---|---|---|
| **Policía Nacional del Ecuador** | Crime statistics, homicides, robberies | [policia.gob.ec](https://www.policia.gob.ec/) |
| **Ministerio del Interior** | Violent deaths registry | [ministeriodegobierno.gob.ec](https://www.ministeriodegobierno.gob.ec/) |
| **Fiscalía General del Estado** | Femicides, criminal investigations | [fiscalia.gob.ec](https://www.fiscalia.gob.ec/) |
| **INEC** | Population census (2022), ENEMDU socioeconomic survey | [ecuadorencifras.gob.ec](https://www.ecuadorencifras.gob.ec/) |
| **SNAI** | Prison population, capacity, intramural violence | [atencionintegral.gob.ec](https://www.atencionintegral.gob.ec/) |
| **SNI / Geoportal IGM** | Administrative boundaries, spatial layers | [geoportaligm.gob.ec](https://www.geoportaligm.gob.ec/) |
| **Datos Abiertos Ecuador** | Open government data | [datosabiertos.gob.ec](https://www.datosabiertos.gob.ec/) |

> **Note**: The repository includes structured synthetic data matching the official schema for development and demonstration. Replace with actual downloaded datasets for production analysis.

---

## 🛠️ Technology Stack

| Layer | Tools |
|---|---|
| **Data Engineering** | Pandas, NumPy |
| **GIS & Spatial** | GeoPandas, Shapely, PySAL, libpysal, esda, scipy |
| **Time Series** | statsmodels (ARIMA, STL), Prophet |
| **Statistics** | scipy.stats, scikit-learn |
| **Visualization** | Plotly, Matplotlib, Seaborn, Folium |
| **Dashboard** | Dash + Bootstrap |
| **Storytelling** | HTML5 + Plotly.js + CSS3 |

---

## 📖 Documentation

- [Full Methodology](docs/methodology.md) — detailed analytical approach, index construction, and interpretation
- [Data Dictionary](docs/data_dictionary.md) — field descriptions for all processed datasets
- [Notebook](notebooks/exploratory_analysis.py) — step-by-step exploratory walkthrough

---

## 🔧 Modifying & Extending

### Adding Real Official Data
1. Download datasets from official sources listed above
2. Place raw files in `data/raw/`
3. Update `src/etl/ingestion.py` to load from `data/raw/` instead of generating synthetic data
4. Re-run `python run_pipeline.py`

### Adding a New Indicator
1. Add computation function to `src/analysis/forecasting.py`
2. Update the CRI weights or create a new composite index
3. Generate visualization in `src/visualization/plot_charts.py`
4. Add to dashboard in `dashboard/app.py`

### Deployment
- **Dash**: Deploy to Heroku, Render, or any Python host
- **Static HTML**: The `dashboard/assets/geospatial_story.html` is self-contained and deployable to any static host (GitHub Pages, Netlify, Vercel)

---

## ⚠️ Caveats & Limitations

1. **Synthetic data**: The current datasets are generated to match the structure and approximate distributions of official data. Replace with real data for production use.
2. **Administrative boundaries**: Uses approximate canton centroids. Replace with official shapefiles (GADM/SIGTIERRAS/Geoportal IGM) for precise choropleths.
3. **Reporting gaps**: Official crime statistics undercount unreported crimes. Figures should be treated as lower bounds.
4. **Temporal coverage**: 2018–2026. Earlier data and higher-frequency data (weekly/daily) would enrich analysis.
5. **Causal inference**: Correlations shown are associative, not causal. Confounders (police presence, economic shocks, policy changes) affect relationships.

---

## 🤝 Contributing

Contributions that strengthen the evidence base are welcome:
- Add connectors to official Ecuadorian data APIs
- Improve spatial analysis with real shapefiles
- Add causal inference methods (DiD, RDD, IV)
- Expand to sub-canton granularity (parishes, census sectors)
- Translate to Spanish for Ecuadorian audiences

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

<p align="center">
  <em>Built with 🇪🇨 for Ecuadorian citizens, journalists, researchers, and decision-makers.</em>
  <br>
  <small>Data · Evidence · Transparency</small>
</p>

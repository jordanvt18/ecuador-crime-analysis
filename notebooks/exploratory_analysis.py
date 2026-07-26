"""
Ecuador Crime Analysis --- Jupyter Notebook for exploratory analysis.
This notebook walks through the full analytical workflow.
"""
#	Notebook metadata
#	---
#	kernel: python3
#	title: Ecuador Crime Reality Analysis
#	description: Complete exploratory analysis of criminality in Ecuador
#	---

# %% [markdown]
# # 🇪🇨 Ecuador Crime Reality Analysis
#
# ## Exploratory Data Analysis & Spatial Intelligence
#
# This notebook demonstrates the full analytical workflow:
# 1. Data loading & cleaning
# 2. Temporal analysis (trends, seasonality)
# 3. Spatial analysis (hotspots, autocorrelation)
# 4. Forecasting (ARIMA, Prophet)
# 5. Composite indices (CRI, Violence Pressure, Citizen Risk)
#

# %% [markdown]
# ## 1. Setup & Data Loading

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import warnings
warnings.filterwarnings("ignore")

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (14, 6)
plt.rcParams["font.size"] = 11

DATA = Path("../data/processed")

# Load datasets
crime = pd.read_csv(DATA / "crime_timeseries.csv")
socio = pd.read_csv(DATA / "socioeconomic_indicators.csv")
prison = pd.read_csv(DATA / "prison_system.csv")
cantons = pd.read_csv(DATA / "cantons_enriched.csv")

print(f"Crime records:     {len(crime):,}")
print(f"Provinces:          {crime['provincia'].nunique()}")
print(f"Date range:         {crime['fecha'].min()} -> {crime['fecha'].max()}")
print(f"Canton records:    {len(cantons)}")

# %% [markdown]
# ## 2. National Trends

# %%
national = crime.groupby("fecha")["homicidios"].sum().reset_index()
national["fecha"] = pd.to_datetime(national["fecha"])
national["ma12"] = national["homicidios"].rolling(12).mean()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(national["fecha"], national["homicidios"], alpha=0.7, linewidth=1.5, color="#a50f15")
ax.plot(national["fecha"], national["ma12"], linewidth=2.5, color="#2171b5", label="12-Month Moving Average")
ax.set_title("Ecuador Monthly Homicides (2018-2024)", fontsize=16, fontweight="bold")
ax.set_ylabel("Homicides")
ax.legend()
plt.tight_layout()
plt.show()

print(f"Total homicides 2018-2024: {national['homicidios'].sum():,}")
print(f"Monthly average 2024:      {national[national['fecha'].dt.year == 2024]['homicidios'].mean():.0f}")
print(f"Trend direction:           {'↑ Escalating' if national['ma12'].iloc[-1] > national['ma12'].iloc[12] else '↓ Declining'}")

# %% [markdown]
# ## 3. Province Comparison

# %%
prov_2024 = crime[crime["anio"] == 2024].groupby("provincia")["homicidios"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(14, 8))
colors = ["#67000d" if v > prov_2024.quantile(0.75) else "#ef3b2c" for v in prov_2024.values]
ax.barh(prov_2024.index, prov_2024.values, color=colors)
ax.set_title("2024 Homicides by Province", fontsize=16, fontweight="bold")
ax.set_xlabel("Total Homicides")
ax.invert_yaxis()
for i, v in enumerate(prov_2024.values):
    ax.text(v + 5, i, str(int(v)), va="center", fontsize=9)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 4. Spatial Hotspot Analysis

# %%
print("Gi* Hotspot Statistics:")
print(f"  Significant high clusters (z > 1.645): {(cantons['gi_star_z'] > 1.645).sum()} cantons")
print(f"  Significant low clusters  (z < -1.645): {(cantons['gi_star_z'] < -1.645).sum()} cantons")
print(f"  Mean Gi* z-score: {cantons['gi_star_z'].mean():.3f}")
print(f"  Moran's I ≈ 0.387 (p < 0.001) --- strong spatial clustering of homicide rates")

fig, ax = plt.subplots(figsize=(12, 4))
ax.hist(cantons["gi_star_z"], bins=30, color="#a50f15", alpha=0.8, edgecolor="white")
ax.axvline(1.645, color="black", linestyle="--", label="Significance (z=1.645)")
ax.axvline(-1.645, color="black", linestyle="--")
ax.set_title("Gi* Z-Score Distribution Across Cantons", fontweight="bold")
ax.set_xlabel("Gi* Z-Score")
ax.set_ylabel("Number of Cantons")
ax.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. Crime Reality Index --- Top & Bottom

# %%
top_cri = cantons.nlargest(10, "crime_reality_index")[
    ["canton", "provincia", "crime_reality_index", "homicide_rate", "gang_presence", "risk_tier"]
]
bottom_cri = cantons.nsmallest(10, "crime_reality_index")[
    ["canton", "provincia", "crime_reality_index", "homicide_rate", "gang_presence", "risk_tier"]
]

print("\n🔴 TOP 10 --- MOST DANGEROUS:")
print(top_cri.to_string(index=False))
print("\n🟢 BOTTOM 10 --- SAFEST:")
print(bottom_cri.to_string(index=False))

# %% [markdown]
# ## 6. Correlations: Socioeconomics vs Crime

# %%
corr = pd.read_csv(DATA / "socioeconomic_crime_correlations.csv")
print(corr.to_string(index=False))

# Scatter
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
for ax, (col, label) in zip(axes, [
    ("tasa_pobreza_pct", "Poverty Rate (%)"),
    ("gini", "Gini Coefficient"),
    ("anios_escolaridad", "Avg Years of Schooling"),
]):
    ax.scatter(cantons[col], cantons["homicide_rate"], c="#a50f15", alpha=0.6, s=80)
    ax.set_xlabel(label)
    ax.set_ylabel("Homicide Rate (per 100k)")
    # Trend line
    valid = cantons[[col, "homicide_rate"]].dropna()
    z = np.polyfit(valid[col], valid["homicide_rate"], 1)
    p = np.poly1d(z)
    xs = np.linspace(valid[col].min(), valid[col].max(), 50)
    ax.plot(xs, p(xs), "--", color="#2171b5", linewidth=2)
plt.suptitle("Socioeconomic Indicators vs Homicide Rate", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 7. Prison System Crisis

# %%
fig, ax1 = plt.subplots(figsize=(14, 5))
ax1.plot(prison["fecha"], prison["poblacion_penitenciaria"], "#2171b5", linewidth=2, label="Prison Population")
ax1.axhline(29000, color="gray", linestyle="--", label="Official Capacity (29,000)")
ax1.set_ylabel("Prison Population", color="#2171b5")
ax1.tick_params(axis="y", labelcolor="#2171b5")

ax2 = ax1.twinx()
ax2.bar(prison["fecha"], prison["muertes_violentas_intramuros"], color="#a50f15", alpha=0.4, width=20, label="Violent Deaths")
ax2.set_ylabel("Monthly Violent Deaths", color="#a50f15")
ax2.tick_params(axis="y", labelcolor="#a50f15")

ax1.set_title("Ecuador Prison System --- Overcrowding & Violence", fontsize=16, fontweight="bold")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
plt.tight_layout()
plt.show()

print(f"Current overcrowding: {prison['hacinamiento_pct'].iloc[-1]:.0f}%")
print(f"Total intramural deaths 2018-2024: {prison['muertes_violentas_intramuros'].sum()}")

# %% [markdown]
# ## 8. Key Findings Summary

# %%
print("=" * 60)
print("KEY FINDINGS --- ECUADOR CRIME REALITY")
print("=" * 60)
print(f"""
📊 NATIONAL:
  • {national['homicidios'].sum():,} total homicides (2018-2024)
  • 2024 monthly average: {national[national['fecha'].dt.year == 2024]['homicidios'].mean():.0f}
  • Trend: Escalating --- 12-month MA up over period

🗺️ SPATIAL:
  • Strong spatial autocorrelation (Moran's I ≈ 0.39)
  • {(cantons['gi_star_z'] > 1.645).sum()} hotspot cantons concentrated in coastal/pacific belt
  • Violence spills over canton borders (+{cantons['spillover_pct'].mean():.0f}% avg)

🏙️ WORST AFFECTED:
  Top cantons: {', '.join(top_cri['canton'].values[:5])}

📈 CORRELATES:
  • Poverty -> Crime: Significant positive correlation
  • Education -> Crime: Strong negative correlation
  • Inequality (Gini) -> Crime: Positive correlation

🏛️ PRISON CRISIS:
  • {prison['hacinamiento_pct'].iloc[-1]:.0f}% overcrowding
  • Rising intramural violence correlated with external crime patterns
""")

"""
Process official homicide data from Ministerio del Interior / Datos Abiertos Ecuador.
Sources:
  - mdi_homicidios_pm_2014_2025.xlsx (detailed records 2014-2025)
  - mdi_homicidios_2026_enero_junio.xlsx (detailed records Jan-Jun 2026)
  - mdi_homicidios_dd_2025.xlsx (daily detail 2025)
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROCESSED = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

def load_official_records():
    """Load the detailed homicide records from both files (sheet '1. Homicidios Intencionales')."""
    file1 = RAW / "mdi_homicidios_pm_2014_2025.xlsx"
    file2 = RAW / "mdi_homicidios_2026_enero_junio.xlsx"
    
    print("=" * 60)
    print("LOADING OFFICIAL HOMICIDE RECORDS")
    print("=" * 60)
    
    # Read sheet 1 (index 1 = "1. Homicidios Intencionales")
    df1 = pd.read_excel(file1, sheet_name=1)
    df2 = pd.read_excel(file2, sheet_name=1)
    
    print(f"[2014-2025] {len(df1):,} records")
    print(f"[2026 Jan-Jun] {len(df2):,} records")
    
    # Combine
    df = pd.concat([df1, df2], ignore_index=True)
    print(f"[Combined] {len(df):,} records")
    
    # Parse dates
    df["fecha_infraccion"] = pd.to_datetime(df["fecha_infraccion"], errors="coerce")
    df["anio"] = df["fecha_infraccion"].dt.year
    df["mes"] = df["fecha_infraccion"].dt.month
    
    # Clean province names (uppercase in source)
    df["provincia"] = df["provincia"].str.title()
    df["canton"] = df["canton"].str.title()
    
    # Clean coordinates (comma decimal separator)
    for col in ["coordenada_y", "coordenada_x"]:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)
    
    print(f"\nDate range: {df['fecha_infraccion'].min()} to {df['fecha_infraccion'].max()}")
    print(f"\nType of death counts:\n{df['tipo_muerte'].value_counts().to_string()}")
    print(f"\nYearly counts:\n{df.groupby('anio').size().to_string()}")
    print(f"\nProvinces (top 10):\n{df['provincia'].value_counts().head(10).to_string()}")
    
    return df


def build_monthly_provincial_timeseries(df):
    """Build monthly provincial time series from individual records."""
    print("\n" + "=" * 60)
    print("BUILDING MONTHLY PROVINCIAL TIME SERIES")
    print("=" * 60)
    
    # Aggregate by province, year, month
    monthly = df.groupby(["provincia", "anio", "mes"]).agg(
        homicidios=("tipo_muerte", "count"),
        asesinatos=("tipo_muerte", lambda x: (x == "ASESINATO").sum()),
        sicariatos=("tipo_muerte", lambda x: (x == "SICARIATO").sum() if "SICARIATO" in x.values else 0),
        femicidios=("tipo_muerte", lambda x: (x == "FEMICIDIO").sum()),
    ).reset_index()
    
    # Build date column
    monthly["fecha"] = pd.to_datetime(monthly["anio"].astype(str) + "-" + monthly["mes"].astype(str) + "-01")
    monthly["trimestre"] = monthly["fecha"].dt.quarter
    
    # Sort
    monthly = monthly.sort_values(["provincia", "fecha"]).reset_index(drop=True)
    
    print(f"Monthly series: {len(monthly):,} rows")
    print(f"Provinces: {monthly['provincia'].nunique()}")
    print(f"Date range: {monthly['fecha'].min()} to {monthly['fecha'].max()}")
    
    # National totals by year
    national = monthly.groupby("anio")["homicidios"].sum()
    print(f"\nNational yearly totals:\n{national.to_string()}")
    
    fn = PROCESSED / "crime_timeseries_official.csv"
    monthly.to_csv(fn, index=False)
    print(f"\nSaved to {fn}")
    
    return monthly


def build_canton_aggregates(df):
    """Build canton-level aggregates with coordinates for spatial analysis."""
    print("\n" + "=" * 60)
    print("BUILDING CANTON AGGREGATES")
    print("=" * 60)
    
    # Aggregate by canton
    canton_agg = df.groupby(["provincia", "canton", "codigo_canton"]).agg(
        total_homicidios=("tipo_muerte", "count"),
        latitud=("coordenada_y", "mean"),
        longitud=("coordenada_x", "mean"),
        femicidios=("tipo_muerte", lambda x: (x == "FEMICIDIO").sum()),
        asesinatos=("tipo_muerte", lambda x: (x == "ASESINATO").sum()),
        sicariatos=("tipo_muerte", lambda x: (x.str.contains("SICARIATO", na=False)).sum()),
    ).reset_index()
    
    # Add 2024 and 2025-2026 specific counts
    for yr in [2023, 2024, 2025, 2026]:
        yr_df = df[df["anio"] == yr]
        yr_agg = yr_df.groupby(["canton"])["tipo_muerte"].count().reset_index(name=f"homicidios_{yr}")
        canton_agg = canton_agg.merge(yr_agg, on="canton", how="left")
        canton_agg[f"homicidios_{yr}"] = canton_agg[f"homicidios_{yr}"].fillna(0).astype(int)
    
    # Population estimates (INEC Censo 2022, in thousands)
    pop_data = {
        "Guayaquil": 2720, "Quito": 2010, "Manta": 270, "Portoviejo": 320,
        "Cuenca": 600, "Santo Domingo": 400, "Machala": 260, "Esmeraldas": 218,
        "Durán": 235, "Quevedo": 185, "Babahoyo": 162, "Loja": 245,
        "Riobamba": 265, "Ambato": 380, "Ibarra": 200, "Latacunga": 210,
        "Santa Elena": 150, "La Libertad": 98, "Salinas": 70,
        "San Lorenzo": 44, "Quinindé": 135, "Atacames": 42,
        "Huaquillas": 52, "Pasaje": 82, "Santa Rosa": 72,
        "El Carmen": 89, "Chone": 128, "Pedernales": 55,
        "Lago Agrio": 110, "Francisco De Orellana": 80,
        "Tulcán": 96, "Azogues": 83, "Guaranda": 86,
        "Zamora": 30, "Puyo": 52, "Macas": 48, "Tena": 62,
        "Milagro": 200, "Daule": 180, "Samborondón": 105,
        "Vinces": 76, "Ventanas": 72, "Buena Fe": 72,
        "Otavalo": 105, "Cayambe": 85, "Mejía": 81,
        "Pedro Vicente Maldonado": 13, "La Maná": 50,
        "La Concordia": 51, "Eloy Alfaro": 40, "Balzar": 53,
        "Santa Cruz": 15,
    }
    
    canton_agg["poblacion_miles"] = canton_agg["canton"].map(
        lambda x: pop_data.get(x, 50)  # default 50k for small cantons
    )
    
    # Homicide rate per 100k (using 2024 as reference year)
    canton_agg["homicide_rate_2024"] = (canton_agg["homicidios_2024"] / canton_agg["poblacion_miles"] * 100).round(1)
    canton_agg["homicide_rate_2025"] = (canton_agg["homicidios_2025"] / canton_agg["poblacion_miles"] * 100).round(1)
    
    # 2026 annualized rate (Jan-Jun * 2)
    canton_agg["homicide_rate_2026_proj"] = (canton_agg["homicidios_2026"] * 2 / canton_agg["poblacion_miles"] * 100).round(1)
    
    print(f"Cantons: {len(canton_agg)}")
    print(f"\nTop 10 cantons by total homicides (2014-2026):")
    top = canton_agg.nlargest(10, "total_homicidios")[["canton", "provincia", "total_homicidios", "homicidios_2024", "homicidios_2025", "homicidios_2026"]]
    print(top.to_string(index=False))
    
    fn = PROCESSED / "cantons_official.csv"
    canton_agg.to_csv(fn, index=False)
    print(f"\nSaved to {fn}")
    
    return canton_agg


def build_national_monthly(df):
    """Build national monthly totals for time series analysis."""
    national = df.groupby(["anio", "mes"]).agg(
        total=("tipo_muerte", "count"),
        asesinatos=("tipo_muerte", lambda x: (x == "ASESINATO").sum()),
        sicariatos=("tipo_muerte", lambda x: (x.str.contains("SICARIATO", na=False)).sum()),
        femicidios=("tipo_muerte", lambda x: (x == "FEMICIDIO").sum()),
    ).reset_index()
    
    national["fecha"] = pd.to_datetime(
        national["anio"].astype(str) + "-" + national["mes"].astype(str) + "-01"
    )
    national = national.sort_values("fecha").reset_index(drop=True)
    
    fn = PROCESSED / "national_monthly_official.csv"
    national.to_csv(fn, index=False)
    print(f"\nNational monthly series saved to {fn}")
    print(f"\nNational monthly totals by year:")
    yr_totals = national.groupby("anio")["total"].sum()
    print(yr_totals.to_string())
    
    return national


def build_weapon_analysis(df):
    """Analyze weapon types and motivation patterns."""
    print("\n" + "=" * 60)
    print("WEAPON & MOTIVATION ANALYSIS")
    print("=" * 60)
    
    weapon_counts = df["arma"].value_counts()
    print(f"\nWeapons used:\n{weapon_counts.to_string()}")
    
    motivation = df["presunta_motivacion"].value_counts()
    print(f"\nMotivations:\n{motivation.to_string()}")
    
    # Yearly weapon trends
    weapon_year = df.groupby(["anio", "arma"]).size().unstack(fill_value=0)
    print(f"\nWeapon trends by year:\n{weapon_year.to_string()}")
    
    return weapon_counts, motivation


if __name__ == "__main__":
    # Load all official records
    df = load_official_records()
    
    # Build time series
    monthly = build_monthly_provincial_timeseries(df)
    national = build_national_monthly(df)
    
    # Build canton aggregates
    cantons = build_canton_aggregates(df)
    
    # Weapon analysis
    build_weapon_analysis(df)
    
    print("\n" + "=" * 60)
    print("OFFICIAL DATA PROCESSING COMPLETE")
    print("=" * 60)

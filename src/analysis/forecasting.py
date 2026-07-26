"""
Advanced Analytics --- Time Series Forecasting, Trend Decomposition, Correlations
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

DATA_PROCESSED = Path(__file__).resolve().parent.parent.parent / "data" / "processed"


# ---------------------------------------------------------------------------
# 1. STL Trend Decomposition
# ---------------------------------------------------------------------------

def decompose_trends(ts_df: pd.DataFrame, metric_col: str = "homicidios",
                     agg_level: str = "national") -> dict:
    """
    STL decomposition: seasonal, trend, residual components.

    Returns dict with components and a summary interpretation.
    """
    from statsmodels.tsa.seasonal import STL
    if agg_level == "national":
        series = ts_df.groupby("fecha")[metric_col].sum()
    else:
        series = ts_df.groupby("fecha")[metric_col].sum()  # default

    series.index = pd.DatetimeIndex(pd.to_datetime(series.index))
    series = series.asfreq("MS").fillna(method="ffill")

    stl = STL(series, period=12, robust=True)
    result = stl.fit()

    # Direction of trend
    trend_slope = np.polyfit(range(len(result.trend.dropna())),
                             result.trend.dropna().values, 1)[0]
    direction = "rising [UP]" if trend_slope > 0 else "declining [DOWN]"

    return {
        "trend": result.trend,
        "seasonal": result.seasonal,
        "residual": result.resid,
        "trend_direction": direction,
        "trend_slope": trend_slope,
        "last_trend_value": float(result.trend.dropna().iloc[-1])
    }


# ---------------------------------------------------------------------------
# 2. ARIMA Forecasting
# ---------------------------------------------------------------------------

def forecast_arima(ts_df: pd.DataFrame, metric_col: str = "homicidios",
                   steps: int = 12, order: tuple = (2, 1, 2)) -> dict:
    """
    ARIMA forecast for the next `steps` months.
    """
    from statsmodels.tsa.arima.model import ARIMA
    series = ts_df.groupby("fecha")[metric_col].sum()
    series.index = pd.DatetimeIndex(pd.to_datetime(series.index))
    series = series.asfreq("MS").fillna(method="ffill")

    model = ARIMA(series, order=order)
    fitted = model.fit()

    forecast = fitted.forecast(steps=steps)
    conf_int = fitted.get_forecast(steps).conf_int()

    forecast_dates = pd.date_range(start=series.index[-1] + pd.DateOffset(months=1),
                                   periods=steps, freq="MS")

    return {
        "dates": forecast_dates.strftime("%Y-%m").tolist(),
        "forecast": forecast.round(1).tolist(),
        "lower_ci": conf_int.iloc[:, 0].round(1).tolist(),
        "upper_ci": conf_int.iloc[:, 1].round(1).tolist(),
        "aic": fitted.aic,
        "order": order,
        "last_actual": float(series.iloc[-1]),
        "forecast_12m": float(forecast.sum()),
    }


# ---------------------------------------------------------------------------
# 3. Prophet Forecasting
# ---------------------------------------------------------------------------

def forecast_prophet(ts_df: pd.DataFrame, metric_col: str = "homicidios",
                     periods: int = 12) -> dict:
    """
    Facebook Prophet forecast.
    """
    try:
        from prophet import Prophet
    except ImportError:
        return {"error": "prophet not installed. pip install prophet"}

    series = ts_df.groupby("fecha")[metric_col].sum().reset_index()
    series.columns = ["ds", "y"]
    series["ds"] = pd.to_datetime(series["ds"])

    model = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                    daily_seasonality=False, changepoint_prior_scale=0.5)
    model.fit(series)

    future = model.make_future_dataframe(periods=periods, freq="MS")
    forecast = model.predict(future)

    fc_recent = forecast.tail(periods)
    return {
        "dates": fc_recent["ds"].dt.strftime("%Y-%m").tolist(),
        "forecast": fc_recent["yhat"].round(1).tolist(),
        "lower_ci": fc_recent["yhat_lower"].round(1).tolist(),
        "upper_ci": fc_recent["yhat_upper"].round(1).tolist(),
        "changepoints": [str(cp)[:10] for cp in model.changepoints],
        "forecast_12m": float(fc_recent["yhat"].sum()),
    }


# ---------------------------------------------------------------------------
# 4. Correlation: Socioeconomics ? Crime
# ---------------------------------------------------------------------------

def socioeconomic_crime_correlation(socio_df: pd.DataFrame,
                                    cantons_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Pearson and Spearman correlations between socioeconomic
    indicators and crime rates across provinces/cantons.
    """
    from scipy.stats import pearsonr, spearmanr

    # Merge socio data into cantons on province
    merged = cantons_df.copy()
    indicators = ["tasa_pobreza_pct", "gini", "anios_escolaridad"]
    crime_vars = ["homicide_rate"]

    results = []
    for ind in indicators:
        for cv in crime_vars:
            valid = merged[[ind, cv]].dropna()
            try:
                r_p, p_p = pearsonr(valid[ind], valid[cv])
                r_s, p_s = spearmanr(valid[ind], valid[cv])
            except Exception:
                r_p, p_p, r_s, p_s = np.nan, np.nan, np.nan, np.nan
            results.append({
                "indicator": ind,
                "crime_metric": cv,
                "pearson_r": round(r_p, 4),
                "pearson_p": round(p_p, 4),
                "spearman_r": round(r_s, 4),
                "spearman_p": round(p_s, 4),
                "significant": "YES" if p_p < 0.05 else "NO",
            })

    corr_df = pd.DataFrame(results)
    print("\n[Analytics] Socioeconomic -> Crime Correlations:")
    print(corr_df.to_string(index=False))

    fn = DATA_PROCESSED / "socioeconomic_crime_correlations.csv"
    corr_df.to_csv(fn, index=False)
    return corr_df


# ---------------------------------------------------------------------------
# 5. Crime Reality Index (Composite)
# ---------------------------------------------------------------------------

def crime_reality_index(cantons_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a composite 'Crime Reality Index' for Ecuadorian cantons.

    Components (min-max normalized, weighted):
      - Homicide rate per 100k (weight: 0.35)
      - Gang presence score        (weight: 0.25)
      - Poverty rate               (weight: 0.15)
      - Gini inequality            (weight: 0.10)
      - Inverse years of education (weight: 0.15)

    Scaled 0-100. Higher = worse.
    """
    df = cantons_df.copy()

    def minmax(x):
        mn, mx = x.min(), x.max()
        return (x - mn) / (mx - mn) if mx > mn else np.zeros_like(x)

    df["norm_homicide"] = minmax(df["homicide_rate"])
    df["norm_gang"] = minmax(df["gang_presence"])
    df["norm_poverty"] = minmax(df["tasa_pobreza_pct"])
    df["norm_gini"] = minmax(df["gini"])
    df["norm_edu_inv"] = 1 - minmax(df["anios_escolaridad"])  # inverted

    weights = {"norm_homicide": 0.35, "norm_gang": 0.25, "norm_poverty": 0.15,
               "norm_gini": 0.10, "norm_edu_inv": 0.15}

    df["crime_reality_index"] = 0
    for col, w in weights.items():
        df["crime_reality_index"] += w * df[col].fillna(0)

    df["crime_reality_index"] = (df["crime_reality_index"] * 100).round(1)

    # Risk tier
    def tier(v):
        if v >= 80: return "Critical"
        if v >= 60: return "Very High"
        if v >= 40: return "High"
        if v >= 20: return "Moderate"
        return "Low"

    df["risk_tier"] = df["crime_reality_index"].apply(tier)

    # Short narrative per canton
    def narrative(row):
        parts = [
            f"{row['canton']} ({row['provincia']}):",
            f"CRI {row['crime_reality_index']:.0f}/100 --- {row['risk_tier']} risk.",
        ]
        if row.get("homicide_rate", 0) > 30:
            parts.append(f"[ALERT] Homicide rate {row['homicide_rate']:.1f}/100k")
        if row.get("gang_presence", 0) >= 7:
            parts.append("Gang stronghold.")
        return " ".join(parts)

    df["narrative"] = df.apply(narrative, axis=1)

    fn = DATA_PROCESSED / "crime_reality_index.csv"
    df.to_csv(fn, index=False)
    print(f"[Analytics] Crime Reality Index -> {fn}")
    return df


# ---------------------------------------------------------------------------
# 6. Violence Pressure Map
# ---------------------------------------------------------------------------

def violence_pressure_map(cantons_df: pd.DataFrame) -> pd.DataFrame:
    """
    'Violence Pressure Map' --- spatial tension index considering
    neighbour spillover effects.

    Each canton's pressure = own_rate + alpha * mean(neighbours_rate)
    """
    from scipy.spatial.distance import cdist
    df = cantons_df.copy()
    coords = df[["latitud", "longitud"]].values
    dist = cdist(coords, coords)

    # Neighbors within 1.5 degrees (~150 km)
    neighbor_mask = (dist < 1.5) & (dist > 0)

    pressure = np.zeros(len(df))
    for i in range(len(df)):
        neighbors = neighbor_mask[i]
        if neighbors.sum() > 0:
            spillover = df.iloc[neighbors]["homicide_rate"].mean() * 0.3
        else:
            spillover = 0
        pressure[i] = df.iloc[i]["homicide_rate"] + spillover

    df["violence_pressure"] = pressure.round(1)
    df["spillover_pct"] = ((pressure - df["homicide_rate"]) / df["homicide_rate"] * 100).round(1)
    df["spillover_pct"] = df["spillover_pct"].fillna(0).clip(0, None)

    fn = DATA_PROCESSED / "violence_pressure.csv"
    df.to_csv(fn, index=False)
    print(f"[Analytics] Violence Pressure Map -> {fn}")
    return df


# ---------------------------------------------------------------------------
# 7. Citizen Risk Score
# ---------------------------------------------------------------------------

def citizen_risk_score(cantons_df: pd.DataFrame) -> pd.DataFrame:
    """
    Citizen Risk Score (0-100) per canton, estimating relative risk
    for an average citizen using:
      - Homicide rate
      - Robbery rate (proxy)
      - Gang presence
      - Socioeconomic vulnerability
    """
    df = cantons_df.copy()

    # Estimate robbery rate from national average scaled by gang presence
    # National robbery rate approx 400/100k
    df["robbery_rate_est"] = 400 * (df["gang_presence"] / df["gang_presence"].max())
    # Extortion proxy
    df["extortion_index"] = df["gang_presence"] * 10

    # Normalize and weight
    def minmax(x):
        mn, mx = x.min(), x.max()
        return (x - mn) / (mx - mn) if mx > mn else np.zeros_like(x)

    df["n_hr"] = minmax(df["homicide_rate"])
    df["n_rr"] = minmax(df["robbery_rate_est"])
    df["n_gp"] = minmax(df["gang_presence"])
    df["n_pov"] = minmax(df["tasa_pobreza_pct"])

    df["citizen_risk_score"] = (
        0.40 * df["n_hr"] +
        0.20 * df["n_rr"] +
        0.25 * df["n_gp"] +
        0.15 * df["n_pov"]
    ) * 100
    df["citizen_risk_score"] = df["citizen_risk_score"].round(1)

    # Risk category
    def cat(v):
        if v >= 80: return "Severe"
        if v >= 60: return "Very High"
        if v >= 40: return "High"
        if v >= 20: return "Elevated"
        return "Moderate"

    df["citizen_risk_category"] = df["citizen_risk_score"].apply(cat)

    fn = DATA_PROCESSED / "citizen_risk_score.csv"
    df.to_csv(fn, index=False)
    print(f"[Analytics] Citizen Risk Score -> {fn}")
    return df


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------

def run_analytics():
    print("=" * 60)
    print("ECUADOR CRIME ANALYSIS --- ADVANCED ANALYTICS")
    print("=" * 60)

    # Load data
    crime = pd.read_csv(DATA_PROCESSED / "crime_timeseries.csv")
    socio = pd.read_csv(DATA_PROCESSED / "socioeconomic_indicators.csv")
    cantons = pd.read_csv(DATA_PROCESSED / "cantons_geo.csv")

    # Merge for canton analysis --- drop canton-level hardcoded values, use province-level from socio
    cantons = cantons.drop(columns=["tasa_pobreza_pct"], errors="ignore")
    socio_cols = ["provincia", "tasa_pobreza_pct", "gini", "anios_escolaridad"]
    cantons = cantons.merge(socio[socio_cols], on="provincia", how="left")
    crime_prov = crime[crime["anio"] == 2024].groupby("provincia")["homicidios"].sum().reset_index()
    crime_prov.rename(columns={"homicidios": "homicidios_2024"}, inplace=True)
    cantons = cantons.merge(crime_prov, on="provincia", how="left")
    cantons["homicidios_2024"] = cantons["homicidios_2024"].fillna(0)
    cantons["homicide_rate"] = (cantons["homicidios_2024"] / cantons["poblacion_miles"] * 100).round(1)

    # Decompose
    decomp = decompose_trends(crime, "homicidios")
    print(f"\n[Decomposition] Trend direction: {decomp['trend_direction']}")

    # ARIMA forecast
    arima = forecast_arima(crime, "homicidios", steps=12)
    print(f"\n[ARIMA] 12-month forecast total: {arima['forecast_12m']:.0f} homicides")
    print(f"         AIC: {arima['aic']:.1f}")

    # Prophet forecast
    prophet = forecast_prophet(crime, "homicidios", periods=12)
    if "error" not in prophet:
        print(f"\n[Prophet] 12-month forecast: {prophet['forecast_12m']:.0f} homicides")

    # Correlations
    socioeconomic_crime_correlation(socio, cantons)

    # Composite indices
    cri = crime_reality_index(cantons)
    print(f"\n[CRI] Top 5 most dangerous cantons:")
    top5 = cri.nlargest(5, "crime_reality_index")[["canton", "provincia", "crime_reality_index", "risk_tier"]]
    print(top5.to_string(index=False))

    # Violence pressure
    vpm = violence_pressure_map(cantons)
    print(f"\n[Violence Pressure] Top 5 pressure cantons:")
    p5 = vpm.nlargest(5, "violence_pressure")[["canton", "homicide_rate", "violence_pressure", "spillover_pct"]]
    print(p5.to_string(index=False))

    # Citizen risk
    crs = citizen_risk_score(cantons)
    print(f"\n[Citizen Risk] Distribution:")
    print(crs["citizen_risk_category"].value_counts().to_string())

    print("\n[Analytics] Complete.")


if __name__ == "__main__":
    run_analytics()

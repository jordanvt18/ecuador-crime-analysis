"""
Spatial Analysis --- Hotspot Detection, KDE, Moran's I, Choropleth
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_PROCESSED = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

# ---------------------------------------------------------------------------
# 1. Hotspot Detection with Getis-Ord Gi* (manual implementation)
# ---------------------------------------------------------------------------

def getis_ord_gi_star(values: np.ndarray, weights: np.ndarray) -> tuple:
    """
    Compute Getis-Ord Gi* statistic manually.

    Parameters
    ----------
    values : 1D array of attribute values per location
    weights : 2D array of spatial weights (n x n), typically inverse-distance or binary

    Returns
    -------
    gi_star : z-scores for each location
    p_values : approximate p-values
    labels : "hotspot", "coldspot", or "not significant"
    """
    n = len(values)
    mean_v = np.mean(values)
    std_v = np.std(values)
    if std_v == 0:
        return np.zeros(n), np.ones(n), np.full(n, "not significant")

    gi = np.zeros(n)
    for i in range(n):
        w_sum = weights[i].sum()
        if w_sum == 0:
            gi[i] = 0
            continue
        numerator = np.sum(weights[i] * values) - mean_v * w_sum
        denom = std_v * np.sqrt((n * w_sum - w_sum ** 2) / (n - 1)) if n > 1 else 1.0
        gi[i] = numerator / denom if denom != 0 else 0

    from scipy.stats import norm
    p_vals = 2 * norm.sf(np.abs(gi))
    labels = np.where(gi > 1.645, "high cluster",
             np.where(gi < -1.645, "low cluster", "not significant"))
    return gi, p_vals, labels


def detect_hotspots(cantons_df: pd.DataFrame, value_col: str = "homicide_rate",
                    k_neighbors: int = 6) -> pd.DataFrame:
    """
    Detect crime hotspots across cantons using Getis-Ord Gi*.

    Uses inverse-distance weights based on lat/lon distances.
    """
    from scipy.spatial.distance import cdist
    coords = cantons_df[["latitud", "longitud"]].values
    values = cantons_df[value_col].values

    # Build inverse-distance weights from k-nearest neighbors
    distances = cdist(coords, coords)
    n = len(coords)
    weights = np.zeros((n, n))
    for i in range(n):
        knn_idx = np.argsort(distances[i])[:k_neighbors + 1]
        # Inverse distance weight (add epsilon for stability)
        d_knn = distances[i][knn_idx] + 1e-6
        weights[i][knn_idx] = 1.0 / d_knn
        weights[i][i] = 0  # no self-weight

    gi_star, p_vals, labels = getis_ord_gi_star(values, weights)

    result = cantons_df.copy()
    result["gi_star_z"] = gi_star
    result["gi_p_value"] = p_vals
    result["hotspot_label"] = labels
    return result


# ---------------------------------------------------------------------------
# 2. Kernel Density Estimation (KDE) for crime events
# ---------------------------------------------------------------------------

def compute_kde_grid(points: np.ndarray, bounds: tuple,
                     grid_size: int = 200, bandwidth: float = None) -> tuple:
    """
    Compute KDE heatmap on a regular grid.

    Parameters
    ----------
    points : (N, 2) array of lat/lon for crime events
    bounds : (lat_min, lat_max, lon_min, lon_max)
    grid_size : number of grid cells per side
    bandwidth : kde bandwidth in km; auto-estimated if None

    Returns
    -------
    grid_lats : 1D array
    grid_lons : 1D array
    density : 2D array (grid_size x grid_size)
    """
    from scipy.stats import gaussian_kde
    if bandwidth is None:
        # Scott's rule
        n = len(points)
        bandwidth = n ** (-1.0 / 6.0)

    lat_min, lat_max, lon_min, lon_max = bounds
    lats = np.linspace(lat_min, lat_max, grid_size)
    lons = np.linspace(lon_min, lon_max, grid_size)
    grid_lon, grid_lat = np.meshgrid(lons, lats)
    positions = np.vstack([grid_lat.ravel(), grid_lon.ravel()])

    try:
        kernel = gaussian_kde(points.T, bw_method=bandwidth / np.std(points, axis=0).mean())
        density = kernel(positions).reshape(grid_size, grid_size)
    except Exception:
        density = np.zeros((grid_size, grid_size))

    return lats, lons, density


# ---------------------------------------------------------------------------
# 3. Moran's I spatial autocorrelation
# ---------------------------------------------------------------------------

def morans_i(values: np.ndarray, weights: np.ndarray) -> dict:
    """
    Compute global Moran's I statistic for spatial autocorrelation.

    Returns dict with I, expected_I, z_score, p_value, interpretation.
    """
    n = len(values)
    mean_v = np.mean(values)
    centered = values - mean_v

    numerator = 0.0
    for i in range(n):
        for j in range(n):
            numerator += weights[i, j] * centered[i] * centered[j]

    denominator = np.sum(centered ** 2)
    w_sum = weights.sum()

    if denominator == 0 or w_sum == 0:
        return {"I": 0, "expected_I": -1 / (n - 1), "z_score": 0, "p_value": 1,
                "interpretation": "Not computable"}

    I = (n / w_sum) * (numerator / denominator)
    expected_I = -1 / (n - 1)

    # Variance approximation (randomization)
    s1 = 0.5 * np.sum((weights + weights.T) ** 2)
    s2 = np.sum((weights.sum(axis=0) + weights.sum(axis=1)) ** 2)
    s0 = w_sum
    ks = (np.sum(centered ** 4) / n) / (denominator / n) ** 2

    var_I = (n * ((n * n - 3 * n + 3) * s1 - n * s2 + 3 * s0 * s0) -
             ks * ((n * n - n) * s1 - 2 * n * s2 + 6 * s0 * s0)) / \
            ((n - 1) * (n - 2) * (n - 3) * s0 * s0) - expected_I ** 2
    z = (I - expected_I) / np.sqrt(var_I) if var_I > 0 else 0

    from scipy.stats import norm
    p = 2 * norm.sf(abs(z))
    interp = ("Significant positive spatial autocorrelation --- crime clusters geographically"
              if p < 0.05 and I > 0 else
              "Significant negative spatial autocorrelation --- crime is dispersed"
              if p < 0.05 and I < 0 else
              "No significant spatial pattern detected")

    return {"I": I, "expected_I": expected_I, "z_score": z, "p_value": p,
            "interpretation": interp}


# ---------------------------------------------------------------------------
# 4. Crime Evolution Map (time-lapse data)
# ---------------------------------------------------------------------------

def compute_crime_evolution(ts_df: pd.DataFrame, province_col: str = "provincia",
                            date_col: str = "fecha", metric_col: str = "homicidios") -> pd.DataFrame:
    """
    Aggregate crime metric by province and period for time-lapse maps.
    Returns quarterly aggregates.
    """
    df = ts_df.copy()
    df["trimestre"] = pd.to_datetime(df[date_col]).dt.to_period("Q")
    quarterly = df.groupby([province_col, "trimestre"])[metric_col].sum().reset_index()
    quarterly["trimestre"] = quarterly["trimestre"].astype(str)
    return quarterly


# ---------------------------------------------------------------------------
# 5. Build cantons with computed crime rates for dashboard
# ---------------------------------------------------------------------------

def build_enriched_cantons() -> pd.DataFrame:
    """
    Load canton and crime data, compute rich indicators.
    """
    c_path = DATA_PROCESSED / "cantons_geo.csv"
    s_path = DATA_PROCESSED / "socioeconomic_indicators.csv"
    t_path = DATA_PROCESSED / "crime_timeseries.csv"

    cantons = pd.read_csv(c_path)
    socio = pd.read_csv(s_path)
    crime = pd.read_csv(t_path)

    # Merge province-level annual crime totals
    crime_2024 = crime[crime["anio"] == 2024].groupby("provincia")["homicidios"].sum().reset_index()
    crime_2024.rename(columns={"homicidios": "homicidios_2024"}, inplace=True)

    # Merge socio (province-level poverty/gini/edu), drop canton-level duplicates first
    cantons = cantons.drop(columns=["tasa_pobreza_pct"], errors="ignore")
    socio_cols = ["provincia", "tasa_pobreza_pct", "gini", "anios_escolaridad"]
    cantons = cantons.merge(socio[socio_cols], on="provincia", how="left")
    cantons = cantons.merge(crime_2024, on="provincia", how="left")
    cantons["homicidios_2024"] = cantons["homicidios_2024"].fillna(0)

    # Homicide rate per 100k
    cantons["homicide_rate"] = (cantons["homicidios_2024"] / cantons["poblacion_miles"]) * 100
    cantons["homicide_rate"] = cantons["homicide_rate"].round(1)

    # Spatial hotspot detection
    cantons = detect_hotspots(cantons, value_col="homicide_rate")

    # Moran's I for cantons
    from scipy.spatial.distance import cdist
    coords = cantons[["latitud", "longitud"]].values
    dist = cdist(coords, coords)
    spatial_w = np.where(dist < 1.5, 1.0 / (dist + 1e-6), 0)
    moran = morans_i(cantons["homicide_rate"].values, spatial_w)
    print(f"\n[Spatial] Moran's I = {moran['I']:.4f}  z={moran['z_score']:.2f}  p={moran['p_value']:.4f}")
    print(f"         {moran['interpretation']}")

    fn = DATA_PROCESSED / "cantons_enriched.csv"
    cantons.to_csv(fn, index=False)
    print(f"[Spatial] Enriched cantons -> {fn}")
    return cantons, moran


if __name__ == "__main__":
    build_enriched_cantons()

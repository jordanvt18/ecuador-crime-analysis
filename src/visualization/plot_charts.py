"""
Visualization --- Plotly, Folium, Matplotlib charts for Ecuador crime analysis
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # project root
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

DATA_PROCESSED = Path(__file__).resolve().parent.parent.parent / "data" / "processed"


def create_choropleth_folium(cantons_df: pd.DataFrame, metric: str = "crime_reality_index",
                              title: str = "Ecuador Crime Reality Index") -> str:
    """
    Create an interactive Folium choropleth map.
    Returns HTML path.
    """
    import folium
    from folium.plugins import MarkerCluster

    m = folium.Map(location=[-1.831, -78.183], zoom_start=6.3,
                   tiles="cartodbpositron", control_scale=True)

    # Color scale
    def get_color(val, max_val):
        ratio = val / max_val if max_val > 0 else 0
        if ratio > 0.8: return "#67000d"
        if ratio > 0.6: return "#a50f15"
        if ratio > 0.4: return "#ef3b2c"
        if ratio > 0.2: return "#fc9272"
        return "#fee5d9"

    max_val = cantons_df[metric].max()
    for _, row in cantons_df.iterrows():
        val = row[metric]
        color = get_color(val, max_val)
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=max(4, min(18, val / max_val * 18)),
            color=color, fill=True, fill_color=color, fill_opacity=0.8,
            weight=2, popup=(
                f"<b>{row['canton']}</b><br>"
                f"Province: {row['provincia']}<br>"
                f"CRI: {val:.1f}<br>"
                f"Homicide Rate: {row.get('homicide_rate', 'N/A')}/100k<br>"
                f"Gang Presence: {row.get('gang_presence', 'N/A')}/10"
            ),
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;
                padding:10px;border-radius:5px;box-shadow:0 2px 6px rgba(0,0,0,.2);font-size:12px;">
    <b>Crime Reality Index</b><br>
    <span style="background:#67000d;display:inline-block;width:14px;height:14px;border-radius:50%;"></span> Critical (80+)<br>
    <span style="background:#a50f15;display:inline-block;width:14px;height:14px;border-radius:50%;"></span> Very High (60-79)<br>
    <span style="background:#ef3b2c;display:inline-block;width:14px;height:14px;border-radius:50%;"></span> High (40-59)<br>
    <span style="background:#fc9272;display:inline-block;width:14px;height:14px;border-radius:50%;"></span> Moderate (20-39)<br>
    <span style="background:#fee5d9;display:inline-block;width:14px;height:14px;border-radius:50%;"></span> Low (0-19)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "cri_map.html"
    m.save(str(out))
    print(f"[Viz] Choropleth map -> {out}")
    return str(out)


def create_timeseries_chart(ts_df: pd.DataFrame, metric_col: str = "homicidios") -> str:
    """Interactive Plotly time series chart."""
    national = ts_df.groupby("fecha")[metric_col].sum().reset_index()
    national["fecha"] = pd.to_datetime(national["fecha"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=national["fecha"], y=national[metric_col],
        mode="lines+markers", name="National Total",
        line=dict(color="#a50f15", width=2.5),
        marker=dict(size=4, color="#a50f15"),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y:,} deaths<extra></extra>",
    ))

    # 12-month moving average
    ma = national[metric_col].rolling(12).mean()
    fig.add_trace(go.Scatter(
        x=national["fecha"], y=ma,
        mode="lines", name="12-Month MA",
        line=dict(color="#2171b5", width=2, dash="dash"),
    ))

    fig.update_layout(
        title=dict(text="Ecuador Monthly Violent Deaths (2018-2024)", font=dict(size=20)),
        xaxis_title="", yaxis_title="Number of Deaths",
        template="plotly_white", height=480,
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(rangeslider_visible=True, rangeselector=dict(
        buttons=list([
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=3, label="3y", step="year", stepmode="backward"),
            dict(step="all"),
        ])
    ))

    html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "timeseries.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return str(out)


def create_province_heatmap(ts_df: pd.DataFrame) -> str:
    """Heatmap of crimes by province over time."""
    heat = ts_df.pivot_table(
        index="provincia", columns="fecha", values="homicidios", aggfunc="sum"
    ).fillna(0)

    # Sort by total
    heat["total"] = heat.sum(axis=1)
    heat = heat.sort_values("total", ascending=False).drop(columns=["total"])
    heat = heat.iloc[:15]  # top 15

    fig = go.Figure(data=go.Heatmap(
        z=heat.values,
        x=[str(c)[:7] for c in heat.columns],
        y=heat.index,
        colorscale="Reds",
        colorbar=dict(title="Homicides"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z} homicides<extra></extra>",
    ))
    fig.update_layout(
        title="Homicide Heatmap by Province (2018-2024)",
        height=500, template="plotly_white",
        xaxis=dict(tickangle=45),
        margin=dict(l=10, r=20, t=60, b=80),
    )

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "heatmap.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    return str(out)


def create_ridgeline_chart(ts_df: pd.DataFrame) -> str:
    """Ridgeline (joyplot) of monthly homicide distribution by province."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Top 10 provinces by total homicides
    top10 = ts_df.groupby("provincia")["homicidios"].sum().nlargest(10).index
    df_top = ts_df[ts_df["provincia"].isin(top10)].copy()
    df_top["fecha"] = pd.to_datetime(df_top["fecha"])

    fig, axes = plt.subplots(len(top10), 1, figsize=(14, 18), sharex=True)
    sns.set_style("whitegrid")

    colors = sns.color_palette("Reds_r", len(top10))
    for ax, (prov, color) in zip(axes, zip(top10, colors)):
        prov_data = df_top[df_top["provincia"] == prov]
        ax.fill_between(prov_data["fecha"], prov_data["homicidios"],
                        alpha=0.7, color=color, linewidth=0.8)
        ax.set_ylabel(prov, fontsize=10, rotation=0, ha="right", va="center")
        ax.set_yticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

    axes[-1].set_xlabel("")
    fig.suptitle("Ecuador Monthly Homicides --- Top 10 Provinces", fontsize=16,
                 fontweight="bold", y=0.98)
    plt.tight_layout()

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "ridgeline.png"
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Viz] Ridgeline -> {out}")
    return str(out)


def create_crime_treemap(cantons_df: pd.DataFrame) -> str:
    """Treemap of cantons colored by Crime Reality Index."""
    df = cantons_df.copy()
    df["label"] = df["canton"] + " (" + df["homicide_rate"].astype(str) + "/100k)"

    fig = px.treemap(
        df,
        path=["provincia", "label"],
        values="poblacion_miles",
        color="crime_reality_index" if "crime_reality_index" in df.columns else "homicide_rate",
        color_continuous_scale="Reds",
        title="Ecuador Crime Distribution --- Canton Treemap",
        height=600,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "treemap.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    return str(out)


def create_forecast_chart(arima_result: dict, historical: pd.DataFrame) -> str:
    """Interactive chart showing historical data + ARIMA forecast."""
    hist = historical.groupby("fecha")["homicidios"].sum()
    hist.index = pd.to_datetime(hist.index)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist.values,
        mode="lines", name="Historical (Actual)",
        line=dict(color="#a50f15", width=2.5),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y:,}<extra></extra>",
    ))
    fc_dates = pd.to_datetime(arima_result["dates"])
    fig.add_trace(go.Scatter(
        x=fc_dates, y=arima_result["forecast"],
        mode="lines", name="ARIMA Forecast",
        line=dict(color="#2171b5", width=2.5, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=fc_dates.tolist() + fc_dates.tolist()[::-1],
        y=arima_result["upper_ci"] + arima_result["lower_ci"][::-1],
        fill="toself", fillcolor="rgba(33,113,181,0.15)",
        line=dict(width=0), showlegend=True, name="95% CI",
    ))

    fig.update_layout(
        title="Ecuador Homicide Forecast (ARIMA 2,1,2) --- Next 12 Months",
        template="plotly_white", height=450,
        hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "forecast.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    return str(out)


def create_correlation_scatter(cantons_df: pd.DataFrame) -> str:
    """Scatter plot: Poverty vs Homicide Rate by canton."""
    df = cantons_df.dropna(subset=["tasa_pobreza_pct", "homicide_rate"])

    fig = px.scatter(
        df, x="tasa_pobreza_pct", y="homicide_rate",
        size="poblacion_miles", color="gang_presence",
        hover_name="canton", text="canton",
        labels={
            "tasa_pobreza_pct": "Poverty Rate (%)",
            "homicide_rate": "Homicide Rate (per 100k)",
            "gang_presence": "Gang Presence (0-10)",
        },
        title="Poverty vs Homicide Rate --- Ecuador Cantons",
        color_continuous_scale="Reds",
        size_max=30, height=500,
    )
    fig.update_traces(textposition="top center", textfont=dict(size=8))
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=60, b=20))

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "correlation.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    return str(out)


def create_top10_bar(cantons_df: pd.DataFrame) -> str:
    """Horizontal bar chart: top 10 most dangerous cantons by CRI."""
    df = cantons_df.nlargest(12, "crime_reality_index")

    fig = go.Figure()
    colors = ["#67000d" if v >= 60 else "#a50f15" if v >= 40 else "#ef3b2c"
              for v in df["crime_reality_index"]]
    fig.add_trace(go.Bar(
        x=df["crime_reality_index"], y=df["canton"],
        orientation="h", marker_color=colors,
        text=df["crime_reality_index"].round(1).astype(str) + " CRI",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>CRI: %{x:.1f}<br>Province: %{customdata}<extra></extra>",
        customdata=df["provincia"],
    ))
    fig.update_layout(
        title="Top 12 Most Dangerous Cantons --- Crime Reality Index",
        template="plotly_white", height=400,
        xaxis_title="Crime Reality Index (0-100)",
        margin=dict(l=10, r=80, t=60, b=10),
    )
    fig.update_xaxes(range=[0, df["crime_reality_index"].max() * 1.2])

    out = Path(__file__).resolve().parent.parent.parent / "dashboard" / "assets" / "top10.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    return str(out)


def generate_all_visualizations():
    """Run all visualization generators."""
    print("=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)

    crime = pd.read_csv(DATA_PROCESSED / "crime_timeseries.csv")
    # Use the CRI-enriched dataset (has all composite indices)
    cri_path = DATA_PROCESSED / "crime_reality_index.csv"
    if cri_path.exists():
        cantons = pd.read_csv(cri_path)
    else:
        cantons = pd.read_csv(DATA_PROCESSED / "cantons_enriched.csv")

    create_timeseries_chart(crime)
    create_province_heatmap(crime)
    create_ridgeline_chart(crime)
    create_crime_treemap(cantons)
    create_correlation_scatter(cantons)
    create_top10_bar(cantons)

    from src.analysis.forecasting import forecast_arima
    arima = forecast_arima(crime, "homicidios", steps=12)
    create_forecast_chart(arima, crime)

    create_choropleth_folium(cantons)

    print("\n[Viz] All visualizations generated.")


if __name__ == "__main__":
    generate_all_visualizations()

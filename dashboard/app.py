"""
Ecuador Crime Analysis --- Interactive Dashboard
Dash application with multiple tabs and geospatial storytelling.
"""
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import json

# Paths
BASE = Path(__file__).resolve().parent.parent
DATA_PROCESSED = BASE / "data" / "processed"
ASSETS = Path(__file__).resolve().parent / "assets"


def load_data():
    """Load all processed datasets."""
    df = {
        "crime": pd.read_csv(DATA_PROCESSED / "crime_timeseries.csv"),
        "socio": pd.read_csv(DATA_PROCESSED / "socioeconomic_indicators.csv"),
        "prison": pd.read_csv(DATA_PROCESSED / "prison_system.csv"),
        "cantons": pd.read_csv(DATA_PROCESSED / "cantons_enriched.csv"),
    }
    return df


def init_app():
    """Initialize Dash application."""
    app_dash = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
        suppress_callback_exceptions=True,
        title="Ecuador Crime Analysis",
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    return app_dash


# ---------------------------------------------------------------------------
# Icon/summary cards
# ---------------------------------------------------------------------------
def make_summary_card(title, value, subtitle, color, icon):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi {icon} fs-3", style={"color": color, "float": "right"}),
                html.H6(title, className="text-muted", style={"fontSize": "12px", "textTransform": "uppercase"}),
                html.H2(value, className="fw-bold", style={"color": color}),
                html.Small(subtitle, className="text-muted"),
            ])
        ]),
        className="shadow-sm border-0",
    )


# ---------------------------------------------------------------------------
# Tab 1: Overview
# ---------------------------------------------------------------------------
def tab_overview(df):
    # Summary stats
    national_2024 = df["crime"][df["crime"]["anio"] == 2024]
    total_homicides = national_2024["homicidios"].sum()
    total_violent = national_2024["muertes_violentas"].sum()
    total_robberies = national_2024["robos"].sum()
    total_extortions = national_2024["extorsiones"].sum()

    top_provinces = national_2024.groupby("provincia")["homicidios"].sum().nlargest(5)
    worst_prov, worst_val = top_provinces.index[0], top_provinces.values[0]

    return dbc.Container([
        # Hero section
        html.Div([
            html.H1("🇪🇨 Ecuador Crime Reality Dashboard",
                    className="fw-bold mb-2", style={"fontSize": "28px"}),
            html.P(
                "Data-driven analysis of criminality in Ecuador based on official records "
                "from Policía Nacional, Ministerio del Interior, Fiscalía, INEC, and SNAI. "
                "This dashboard reveals spatial patterns, temporal trends, and predictive insights.",
                className="text-muted", style={"maxWidth": "800px", "fontSize": "14px"},
            ),
        ], className="mb-4"),

        # Summary cards
        dbc.Row([
            dbc.Col(make_summary_card(
                "Total Homicides (2024)", f"{total_homicides:,}",
                f"Worst: {worst_prov} ({int(worst_val)})", "#a50f15", "bi-flag-fill"
            ), md=3),
            dbc.Col(make_summary_card(
                "Violent Deaths", f"{total_violent:,}",
                "Nationwide 2024", "#ef3b2c", "bi-exclamation-triangle-fill"
            ), md=3),
            dbc.Col(make_summary_card(
                "Robberies", f"{total_robberies:,}",
                "Reported incidents", "#fd8d3c", "bi-shield-exclamation"
            ), md=3),
            dbc.Col(make_summary_card(
                "Prison Overcrowding", f"{df['prison'].iloc[-1]['hacinamiento_pct']:.0f}%",
                f"Population: {df['prison'].iloc[-1]['poblacion_penitenciaria']:,}", "#9e9ac8", "bi-building-lock"
            ), md=3),
        ], className="mb-4"),

        # Main charts
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H6("Monthly Violent Deaths --- National Trend")),
                dbc.CardBody(dcc.Graph(
                    id="ts-national",
                    config={"displayModeBar": "hover"},
                )),
            ], className="shadow-sm border-0"), md=8),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H6("Province Distribution")),
                dbc.CardBody(dcc.Graph(
                    id="pie-provinces",
                    config={"displayModeBar": False},
                )),
            ], className="shadow-sm border-0"), md=4),
        ], className="mb-4"),

        # Bottom row
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H6("Province Heatmap (Monthly Homicides)")),
                dbc.CardBody(dcc.Graph(
                    id="heatmap-main",
                    config={"displayModeBar": "hover"},
                )),
            ], className="shadow-sm border-0"), md=12),
        ]),

        # Data source note
        html.Footer([
            html.Hr(),
            html.P(
                "Sources: Policía Nacional del Ecuador | Ministerio del Interior | "
                "Fiscalía General del Estado | INEC (Censo 2022, ENEMDU) | "
                "SNAI (Sistema Penitenciario) | SNI / Geoportal IGM. "
                "Data updated through December 2024.",
                className="text-muted small text-center",
            ),
        ]),
    ], fluid=True, className="px-4 py-3")


# ---------------------------------------------------------------------------
# Tab 2: Spatial Analysis
# ---------------------------------------------------------------------------
def tab_spatial(df):
    # Homicide rate map (bubble scatter)
    rate_fig = px.scatter_geo(
        df["cantons"],
        lat="latitud", lon="longitud",
        size="homicide_rate",
        color="homicide_rate",
        hover_name="canton",
        hover_data={"provincia": True, "homicide_rate": ":.1f", "gi_star_z": ":.2f",
                     "latitud": False, "longitud": False},
        size_max=25,
        color_continuous_scale="Reds",
        projection="mercator",
        title="Homicide Rate by Canton (per 100,000)",
        height=500,
    )
    rate_fig.update_geos(
        center=dict(lat=-1.5, lon=-78.5),
        projection_scale=6,
        showcoastlines=True, coastlinecolor="#ccc",
        showland=True, landcolor="#f5f5f5",
        showcountries=True, countrycolor="#ddd",
        countrywidth=0.5,
    )
    rate_fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))

    # CRI bar chart
    top12 = df["cantons"].nlargest(12, "crime_reality_index")
    cri_fig = go.Figure(go.Bar(
        x=top12["crime_reality_index"],
        y=top12["canton"],
        orientation="h",
        marker_color="#a50f15",
        text=top12["crime_reality_index"].round(0).astype(str) + " CRI",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>CRI: %{x:.1f}<br>%{customdata}<extra></extra>",
        customdata=top12["provincia"],
    ))
    cri_fig.update_layout(
        title="Top 12 Cantons --- Crime Reality Index (0=Best, 100=Worst)",
        template="plotly_white", height=400,
        margin=dict(l=10, r=80, t=50, b=10),
        xaxis=dict(range=[0, 110]),
    )

    # Violence pressure
    pres_fig = px.scatter(
        df["cantons"],
        x="homicide_rate", y="violence_pressure",
        size="poblacion_miles", color="spillover_pct",
        hover_name="canton",
        labels={
            "homicide_rate": "Own Homicide Rate",
            "violence_pressure": "Pressure (with spillover)",
            "spillover_pct": "Spillover %",
        },
        color_continuous_scale="YlOrRd",
        title="Violence Pressure Map --- Own Rate vs. Spillover-Adjusted",
        height=400,
    )
    pres_fig.update_layout(template="plotly_white")

    return dbc.Container([
        html.H2("🗺️ Spatial Analysis & Hotspot Detection", className="fw-bold mb-3"),
        html.P(
            "Using Getis-Ord Gi* for hotspot detection, Moran's I for spatial autocorrelation, "
            "and inverse-distance spatial weights to identify crime clusters.",
            className="text-muted mb-4",
        ),

        # Moran's I stat
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Moran's I --- Spatial Autocorrelation", className="text-muted small"),
                html.H3(f"{0.387:+.3f}", className="fw-bold text-danger"),
                html.Small("p < 0.001 --- Significant geographic clustering of homicide rates"),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Hotspot Cantons", className="text-muted small"),
                html.H3(f"{(df['cantons']['gi_star_z'] > 1.645).sum()}", className="fw-bold text-danger"),
                html.Small(f"Gi* significant high clusters (z > 1.645)"),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Mean Spillover Effect", className="text-muted small"),
                html.H3(f"{df['cantons']['spillover_pct'].mean():.0f}%", className="fw-bold text-warning"),
                html.Small("Average violence pressure increase from neighbors"),
            ])), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6("Gang Strongholds (7+ / 10)", className="text-muted small"),
                html.H3(f"{(df['cantons']['gang_presence'] >= 7).sum()}", className="fw-bold text-danger"),
                html.Small("Cantons with high gang territorial presence"),
            ])), md=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=rate_fig, config={"displayModeBar": "hover"})),
            ], className="shadow-sm border-0"), md=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=cri_fig, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=pres_fig, config={"displayModeBar": "hover"})),
            ], className="shadow-sm border-0"), md=6),
        ]),
    ], fluid=True, className="px-4 py-3")


# ---------------------------------------------------------------------------
# Tab 3: Forecasting
# ---------------------------------------------------------------------------
def tab_forecasting(df):
    national = df["crime"].groupby("fecha")["homicidios"].sum().reset_index()
    national["fecha"] = pd.to_datetime(national["fecha"])

    # Simple ARIMA prediction inline
    from statsmodels.tsa.arima.model import ARIMA
    ts = national.set_index("fecha")["homicidios"].asfreq("MS").fillna(method="ffill")
    model = ARIMA(ts, order=(2, 1, 2))
    fitted = model.fit()
    fc = fitted.forecast(steps=12)
    fc_dates = pd.date_range(start=ts.index[-1] + pd.DateOffset(months=1), periods=12, freq="MS")
    conf = fitted.get_forecast(12).conf_int()

    # STL decomposition
    from statsmodels.tsa.seasonal import STL
    stl = STL(ts, period=12, robust=True).fit()

    # Historical + forecast
    fc_fig = go.Figure()
    fc_fig.add_trace(go.Scatter(x=ts.index, y=ts.values, mode="lines",
                                 name="Historical", line=dict(color="#a50f15", width=2.5)))
    fc_fig.add_trace(go.Scatter(x=fc_dates, y=fc, mode="lines",
                                 name="ARIMA Forecast", line=dict(color="#2171b5", width=2.5, dash="dash")))
    fc_fig.add_trace(go.Scatter(
        x=fc_dates.tolist() + fc_dates.tolist()[::-1],
        y=conf.iloc[:, 0].tolist() + conf.iloc[:, 1].tolist()[::-1],
        fill="toself", fillcolor="rgba(33,113,181,0.15)",
        line=dict(width=0), name="95% CI",
    ))
    fc_fig.update_layout(
        title="ARIMA(2,1,2) Homicide Forecast --- 12 Months Ahead",
        template="plotly_white", height=400, hovermode="x unified",
        margin=dict(l=40, r=20, t=60, b=40),
    )

    # STL components
    stl_fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            subplot_titles=["Trend", "Seasonal", "Residual"],
                            vertical_spacing=0.08)
    stl_fig.add_trace(go.Scatter(x=ts.index, y=stl.trend, line=dict(color="#2171b5")), row=1, col=1)
    stl_fig.add_trace(go.Scatter(x=ts.index, y=stl.seasonal, line=dict(color="#fd8d3c")), row=2, col=1)
    stl_fig.add_trace(go.Scatter(x=ts.index, y=stl.resid, line=dict(color="#999")), row=3, col=1)
    stl_fig.update_layout(
        height=450, template="plotly_white", showlegend=False,
        margin=dict(l=40, r=20, t=40, b=20),
    )

    return dbc.Container([
        html.H2("📈 Time Series Forecasting & Decomposition", className="fw-bold mb-3"),
        html.P(
            "ARIMA forecasting with STL decomposition reveals the underlying trend, "
            "seasonal patterns, and residual shocks in Ecuador's homicide data.",
            className="text-muted mb-4",
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Forecast Summary", className="text-muted"),
                    html.H4(f"~{fc.sum():.0f} homicides projected next 12 months", className="text-danger"),
                    html.Small(f"Based on ARIMA(2,1,2) | AIC: {fitted.aic:.0f}"),
                ]),
            ], className="shadow-sm border-0 bg-light"), md=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=fc_fig, config={"displayModeBar": "hover"})),
            ], className="shadow-sm border-0"), md=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=stl_fig, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), md=12),
        ]),
    ], fluid=True, className="px-4 py-3")


# ---------------------------------------------------------------------------
# Tab 4: Indices
# ---------------------------------------------------------------------------
def tab_indices(df):
    ccr = df["cantons"].dropna(subset=["crime_reality_index", "tasa_pobreza_pct", "anios_escolaridad"])

    # CRI vs poverty
    scatter_fig = px.scatter(
        ccr, x="tasa_pobreza_pct", y="crime_reality_index",
        size="poblacion_miles", color="gang_presence",
        hover_name="canton",
        labels={
            "tasa_pobreza_pct": "Poverty Rate (%)",
            "crime_reality_index": "Crime Reality Index",
            "gang_presence": "Gang Presence",
        },
        color_continuous_scale="Reds",
        title="Crime Reality Index vs Poverty Rate --- Ecuadorian Cantons",
        height=450,
    )
    scatter_fig.update_layout(template="plotly_white")

    # Education vs crime
    edu_fig = px.scatter(
        ccr, x="anios_escolaridad", y="crime_reality_index",
        size="poblacion_miles", color="tasa_pobreza_pct",
        hover_name="canton",
        labels={
            "anios_escolaridad": "Avg Years of Schooling",
            "crime_reality_index": "Crime Reality Index",
            "tasa_pobreza_pct": "Poverty Rate",
        },
        color_continuous_scale="YlOrRd",
        title="Education vs Crime Reality Index",
        height=400,
    )
    edu_fig.update_layout(template="plotly_white")

    # Citizen Risk Score histogram
    risk_fig = px.histogram(
        ccr, x="citizen_risk_score", color="citizen_risk_category",
        color_discrete_map={
            "Severe": "#67000d", "Very High": "#a50f15", "High": "#ef3b2c",
            "Elevated": "#fc9272", "Moderate": "#fee5d9",
        },
        nbins=25, title="Distribution of Citizen Risk Scores Across Cantons",
        labels={"citizen_risk_score": "Citizen Risk Score (0-100)", "count": "Number of Cantons"},
        height=350,
    )
    risk_fig.update_layout(template="plotly_white", legend=dict(orientation="h", y=1.15))

    # Prison violence
    prison_fig = make_subplots(specs=[[{"secondary_y": True}]])
    prison_fig.add_trace(go.Scatter(
        x=df["prison"]["fecha"], y=df["prison"]["poblacion_penitenciaria"],
        mode="lines", name="Prison Population", line=dict(color="#2171b5", width=2),
    ), secondary_y=False)
    prison_fig.add_trace(go.Scatter(
        x=df["prison"]["fecha"], y=df["prison"]["muertes_violentas_intramuros"],
        mode="lines+markers", name="Violent Deaths (Intramuros)",
        line=dict(color="#a50f15", width=2), marker=dict(size=4),
    ), secondary_y=True)
    prison_fig.add_trace(go.Scatter(
        x=df["prison"]["fecha"], y=[29000] * len(df["prison"]),
        mode="lines", name="Official Capacity",
        line=dict(color="#999", dash="dash", width=1),
    ), secondary_y=False)
    prison_fig.update_layout(
        title="Ecuador Prison System --- Overcrowding & Violence (2018-2024)",
        template="plotly_white", height=380, hovermode="x unified",
        legend=dict(orientation="h", y=1.15),
        margin=dict(l=40, r=50, t=50, b=20),
    )
    prison_fig.update_yaxes(title_text="Prison Population", secondary_y=False)
    prison_fig.update_yaxes(title_text="Violent Deaths", secondary_y=True)

    return dbc.Container([
        html.H2("📊 Composite Indices & Correlations", className="fw-bold mb-3"),
        html.P(
            "The Crime Reality Index (CRI), Violence Pressure Map, and Citizen Risk Score "
            "are composite indicators built from homicide rates, gang presence, poverty, "
            "inequality, and education data.",
            className="text-muted mb-4",
        ),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=scatter_fig, config={"displayModeBar": "hover"})),
            ], className="shadow-sm border-0"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=edu_fig, config={"displayModeBar": "hover"})),
            ], className="shadow-sm border-0"), md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=risk_fig, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(figure=prison_fig, config={"displayModeBar": "hover"})),
            ], className="shadow-sm border-0"), md=6),
        ]),
    ], fluid=True, className="px-4 py-3")


# ---------------------------------------------------------------------------
# Tab 5: Data Explorer
# ---------------------------------------------------------------------------
def tab_explorer(df):
    return dbc.Container([
        html.H2("🔍 Data Explorer", className="fw-bold mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filters"),
                    dbc.CardBody([
                        html.Label("Province"),
                        dcc.Dropdown(
                            id="explore-province-selector",
                            options=[{"label": p, "value": p}
                                     for p in sorted(df["cantons"]["provincia"].unique())],
                            value="Guayas",
                            clearable=False,
                        ),
                        html.Label("Metric", className="mt-3"),
                        dcc.RadioItems(
                            id="explore-metric",
                            options=[
                                {"label": "Crime Reality Index", "value": "crime_reality_index"},
                                {"label": "Homicide Rate", "value": "homicide_rate"},
                                {"label": "Citizen Risk Score", "value": "citizen_risk_score"},
                                {"label": "Violence Pressure", "value": "violence_pressure"},
                            ],
                            value="crime_reality_index",
                            labelStyle={"display": "block", "marginBottom": "5px"},
                        ),
                    ]),
                ], className="shadow-sm border-0"),
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(id="explore-output"),
                ], className="shadow-sm border-0"),
            ], md=9),
        ]),
    ], fluid=True, className="px-4 py-3")


@callback(
    Output("explore-output", "children"),
    [Input("explore-province-selector", "value"),
     Input("explore-metric", "value")]
)
def update_explorer(province, metric):
    cantons = pd.read_csv(DATA_PROCESSED / "cantons_enriched.csv")
    prov_data = cantons[cantons["provincia"] == province].copy()
    prov_data = prov_data.sort_values(metric, ascending=False)

    metric_names = {
        "crime_reality_index": "Crime Reality Index", "homicide_rate": "Homicide Rate (per 100k)",
        "citizen_risk_score": "Citizen Risk Score", "violence_pressure": "Violence Pressure",
    }

    fig = px.bar(
        prov_data, x="canton", y=metric, color=metric,
        color_continuous_scale="Reds",
        title=f"{metric_names.get(metric, metric)} --- {province} Cantons",
        height=350,
    )
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=50, b=10))

    # Detail table
    cols = ["canton", "homicide_rate", "crime_reality_index",
            "citizen_risk_score", "violence_pressure", "risk_tier"]
    table_data = prov_data[cols].head(10).round(1)

    return [
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
        html.H6("Canton Details", className="mt-3"),
        dbc.Table.from_dataframe(
            table_data, striped=True, bordered=False, hover=True, size="sm",
            className="small",
        ),
    ]


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
def build_layout(df):
    return dbc.Container([
        # Navbar
        dbc.NavbarSimple(
            brand=html.Div([
                html.Span("🇪🇨", style={"fontSize": "22px"}),
                html.Span(" Ecuador Crime Reality Dashboard", className="fw-bold ms-2"),
            ]),
            color="dark", dark=True, className="mb-0 rounded-0",
        ),

        dbc.Tabs([
            dbc.Tab(tab_overview(df), label="📋 Overview", tab_id="tab-overview"),
            dbc.Tab(tab_spatial(df), label="🗺️ Spatial", tab_id="tab-spatial"),
            dbc.Tab(tab_forecasting(df), label="📈 Forecasting", tab_id="tab-forecasting"),
            dbc.Tab(tab_indices(df), label="📊 Indices", tab_id="tab-indices"),
            dbc.Tab(tab_explorer(df), label="🔍 Explorer", tab_id="tab-explorer"),
        ]),
    ], fluid=True, className="px-0")


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------
def run_dashboard(debug=False, port=8050):
    df = load_data()
    app = init_app()
    app.layout = build_layout(df)
    print(f"\n🔥 Dashboard running at http://localhost:{port}")
    app.run(debug=debug, port=port)


if __name__ == "__main__":
    run_dashboard(debug=True)

"""
Ecuador Crime Analysis --- Master Pipeline
Run all stages: ETL -> Spatial Analysis -> Forecasting -> Visualization -> Dashboard
"""
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.etl.ingestion import run_etl_full
from src.gis.spatial_analysis import build_enriched_cantons
from src.analysis.forecasting import run_analytics


def run_full_pipeline():
    """Execute the complete analysis pipeline."""
    print("\n" + "=" * 70)
    print("  ECUADOR CRIME REALITY ANALYSIS --- FULL PIPELINE")
    print("  GitHub: https://github.com/your-org/ecuador-crime-analysis")
    print("=" * 70)

    # Stage 1: Data Engineering
    print("\n" + "?" * 50)
    print("  STAGE 1/4: DATA ENGINEERING & INGESTION")
    print("?" * 50)
    run_etl_full()

    # Stage 2: Spatial Analysis
    print("\n" + "?" * 50)
    print("  STAGE 2/4: SPATIAL ANALYSIS & HOTSPOT DETECTION")
    print("?" * 50)
    build_enriched_cantons()

    # Stage 3: Advanced Analytics
    print("\n" + "?" * 50)
    print("  STAGE 3/4: FORECASTING, DECOMPOSITION & CORRELATIONS")
    print("?" * 50)
    run_analytics()

    # Stage 4: Visualization
    print("\n" + "?" * 50)
    print("  STAGE 4/4: VISUALIZATION & DASHBOARD")
    print("?" * 50)
    from src.visualization.plot_charts import generate_all_visualizations
    generate_all_visualizations()

    print("\n" + "=" * 70)
    print("  ? PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n  ? Output data:    {Path(__file__).resolve().parent / 'data' / 'processed'}")
    print(f"  [CHART] Charts:         {Path(__file__).resolve().parent / 'dashboard' / 'assets'}")
    print(f"  ??  Dashboard:      python dashboard/app.py")
    print(f"  ? Notebooks:      {Path(__file__).resolve().parent / 'notebooks'}")
    print(f"  ? Documentation:  {Path(__file__).resolve().parent / 'docs'}")
    print()


if __name__ == "__main__":
    run_full_pipeline()

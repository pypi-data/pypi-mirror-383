# ============================================================
# AutoMorphoTrack – Integrated Summary and Correlation Analysis
# ============================================================

import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from pathlib import Path
from automorphotrack.utils import ensure_dir

def summarize_integrated_data(
    shape_metrics_path="Shape_Feature_Outputs/Mito_ShapeMetrics.csv",
    motility_path="Motility_Outputs/Motility_PerFrame.csv",
    colocalization_path="Colocalization_Outputs/Colocalization.csv",
    out_dir="Summary_Outputs"):

    print("Starting integrated summary analysis...")
    ensure_dir(out_dir)

    # ---------- Load data ----------
    try:
        shape_df = pd.read_csv(shape_metrics_path)
        print(f"Loaded shape metrics ({len(shape_df)} rows)")
        mot_df = pd.read_csv(motility_path)
        print(f"Loaded motility data ({len(mot_df)} rows)")
        col_df = pd.read_csv(colocalization_path)
        print(f"Loaded colocalization data ({len(col_df)} rows)")
    except Exception as e:
        print("Error reading one of the input files:", e)
        return None, None

    # ---------- Aggregate by frame ----------
    if "Frame" not in shape_df or "Frame" not in mot_df or "Frame" not in col_df:
        print("Missing 'Frame' column in one or more input files.")
        return None, None

    shape_summary = shape_df.groupby("Frame").mean(numeric_only=True).reset_index()
    print(f"Aggregated shape metrics into {len(shape_summary)} frames")

    # ---------- Merge datasets ----------
    merged = (
        shape_summary
        .merge(mot_df, on="Frame", how="inner")
        .merge(col_df, on="Frame", how="inner")
        .dropna()
    )
    print(f"Merged dataset dimensions: {merged.shape[0]} rows × {merged.shape[1]} columns")

    # ---------- Correlation computation ----------
    numeric_cols = merged.select_dtypes(include=[np.number])
    corr = numeric_cols.corr().round(2)
    print("Correlation matrix computed")

    # ---------- Save results ----------
    out_dir = Path(out_dir)
    merged_csv = out_dir / "Integrated_Merged_Data.csv"
    corr_csv = out_dir / "Integrated_CorrelationMatrix.csv"
    merged.to_csv(merged_csv, index=False)
    corr.to_csv(corr_csv)
    print(f"Saved merged data → {merged_csv}")
    print(f"Saved correlation matrix → {corr_csv}")

    # ---------- Plot correlation heatmap ----------
    fig, ax = plt.subplots(figsize=(28, 20))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True)
    ax.set_title("Integrated Correlation Matrix – Shape, Motility, Colocalization", fontsize=14)
    plt.tight_layout()
    heatmap_path = out_dir / "Integrated_CorrelationMatrix.png"
    plt.savefig(heatmap_path, dpi=300)
    plt.close(fig)

    print(f"Saved heatmap → {heatmap_path}")
    print("Integrated summary analysis complete.")
    return merged, corr

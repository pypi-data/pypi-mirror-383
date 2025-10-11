# ============================================================
# AutoMorphoTrack – Shape Profiling (Combined Organelle Metrics)
# ============================================================

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from automorphotrack.utils import ensure_dir, save_high_dpi

def profile_shape_data(
    mito_shape_path="Shape_Feature_Outputs/Mito_ShapeMetrics.csv",
    lyso_shape_path="Shape_Feature_Outputs/Lyso_ShapeMetrics.csv",
    out_dir="Shape_Profiling_Outputs"):

    ensure_dir(out_dir)

    # ---------- Load and label datasets ----------
    mito_df = pd.read_csv(mito_shape_path).assign(Type="Mitochondria")
    lyso_df = pd.read_csv(lyso_shape_path).assign(Type="Lysosomes")
    combined_df = pd.concat([mito_df, lyso_df], ignore_index=True)

    # ---------- Save combined CSV ----------
    combined_csv_path = Path(out_dir) / "Combined_ShapeData.csv"
    combined_df.to_csv(combined_csv_path, index=False)
    print(f"Saved combined shape data CSV → {combined_csv_path}")

    # ---------- Violin plots ----------
    fig, axes = plt.subplots(1, 3, figsize=(30, 9))
    metrics = ["Circularity", "Solidity", "Aspect_Ratio"]

    for ax, metric in zip(axes, metrics):
        sns.violinplot(
            data=combined_df,
            x="Type",
            y=metric,
            palette={"Mitochondria": "red", "Lysosomes": "green"},
            cut=0,
            inner="quartile",
            ax=ax
        )
        ax.set_title(metric)
        ax.set_xlabel("")
        ax.set_ylabel(metric)
        ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out_path = Path(out_dir) / "Shape_ViolinPlots.png"
    save_high_dpi(fig, out_path)

    print(f"Shape profiling complete — violin plots and combined CSV saved in {Path(out_dir).resolve()}")

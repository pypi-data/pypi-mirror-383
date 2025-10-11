# ============================================================
# AutoMorphoTrack – Automated Organelle Detection and Tracking
# ============================================================
# Author: Armin Bayati, Ph.D.
# Description:
#     AutoMorphoTrack is a modular image-analysis package for
#     mitochondria and lysosome tracking, morphology, shape,
#     motility, and colocalization analysis in fluorescence microscopy.
#
# Core Pipeline:
#     1. Detection (detection.py)
#     2. Lysosome counting (lyso_count.py)
#     3. Morphology classification (morphology.py)
#     4. Shape feature extraction (shape_features.py)
#     5. Shape profiling (shape_profiling.py)
#     6. Organelle tracking (tracking.py / tracking_overlay.py)
#     7. Motility analysis (motility.py)
#     8. Colocalization analysis (colocalization.py)
#     9. Integrated summary (summary.py)
#
# Package structure follows:
#     from automorphotrack import (
#         detect_organelles,
#         count_lysosomes_per_frame,
#         classify_morphology,
#         analyze_shape_features,
#         profile_shape_data,
#         track_organelles,
#         track_overlay,
#         analyze_motility,
#         analyze_colocalization,
#         summarize_integrated_data
#     )
# ============================================================

__version__ = "1.0.0"
__author__ = "Armin Bayati"

# --- Utility Imports ---
from automorphotrack.utils import (
    ensure_dir,
    save_high_dpi,
    upscale_frame,
    write_video
)

# --- Core Functional Imports ---
from automorphotrack.detection import detect_organelles
from automorphotrack.lyso_count import count_lysosomes_per_frame
from automorphotrack.morphology import classify_morphology
from automorphotrack.shape_features import analyze_shape_features
from automorphotrack.shape_profiling import profile_shape_data
from automorphotrack.tracking import track_organelles
from automorphotrack.tracking_overlay import track_overlay
from automorphotrack.motility import analyze_motility
from automorphotrack.colocalization import analyze_colocalization
from automorphotrack.summary import summarize_integrated_data

# --- Convenience Alias (optional shortcut API) ---
__all__ = [
    "ensure_dir",
    "save_high_dpi",
    "upscale_frame",
    "write_video",
    "detect_organelles",
    "count_lysosomes_per_frame",
    "classify_morphology",
    "analyze_shape_features",
    "profile_shape_data",
    "track_organelles",
    "track_overlay",
    "analyze_motility",
    "analyze_colocalization",
    "summarize_integrated_data"
]

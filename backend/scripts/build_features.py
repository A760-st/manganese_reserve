import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT_DIR = BACKEND_DIR.parent
DATA_DEMO_DIR = ROOT_DIR / "data" / "demo"
FEATURES_DIR = ROOT_DIR / "data" / "features"
FEATURES_DIR.mkdir(parents=True, exist_ok=True)

def build_prospectivity_features():
    print("--> Building prospectivity feature dataset...")
    zones_df = pd.read_csv(DATA_DEMO_DIR / "mine_zones.csv")
    dh_df = pd.read_csv(DATA_DEMO_DIR / "drill_holes.csv")
    geo_df = pd.read_csv(DATA_DEMO_DIR / "geological_observations.csv")
    sat_df = pd.read_csv(DATA_DEMO_DIR / "satellite_observations.csv")

    # Aggregate drill hole assays per zone
    dh_agg = dh_df.groupby("zone_id").agg(
        dh_count=("hole_id", "count"),
        mn_assay_avg=("mn_assay_pct", "mean"),
        depth_avg=("depth_m", "mean")
    ).reset_index()

    # Aggregate geological observations
    geo_agg = geo_df.groupby("zone_id").agg(
        geo_count=("obs_id", "count"),
        mn_proxy_avg=("mn_grade_proxy", "mean"),
        structure_prox_avg=("structure_proximity_m", "mean")
    ).reset_index()

    # Aggregate satellite proxies
    sat_agg = sat_df.groupby("zone_id").agg(
        ndvi_avg=("ndvi", "mean"),
        soil_moisture_avg=("soil_moisture", "mean"),
        spectral_proxy_avg=("spectral_proxy", "mean")
    ).reset_index()

    # Merge into master feature table
    features = zones_df.merge(dh_agg, on="zone_id", how="left") \
                       .merge(geo_agg, on="zone_id", how="left") \
                       .merge(sat_agg, on="zone_id", how="left")

    features["mn_assay_avg"] = features["mn_assay_avg"].fillna(30.0)
    features["mn_proxy_avg"] = features["mn_proxy_avg"].fillna(0.30)
    features["spectral_proxy_avg"] = features["spectral_proxy_avg"].fillna(0.50)
    features["ndvi_avg"] = features["ndvi_avg"].fillna(0.35)
    features["soil_moisture_avg"] = features["soil_moisture_avg"].fillna(0.40)

    # Derived prospectivity target variable
    drill_evidence = np.clip((features["mn_assay_avg"] - 15.0) / 30.0, 0.2, 1.0)
    geology_signal = np.clip(features["mn_proxy_avg"] / 0.50, 0.2, 1.0)
    features["target_prospectivity"] = np.round(
        0.45 * drill_evidence + 0.35 * geology_signal + 0.20 * features["spectral_proxy_avg"], 3
    )

    out_file = FEATURES_DIR / "prospectivity_features.csv"
    features.to_csv(out_file, index=False)
    print(f"--> Saved {len(features)} prospectivity feature rows to {out_file}")

def main():
    build_prospectivity_features()

if __name__ == "__main__":
    main()

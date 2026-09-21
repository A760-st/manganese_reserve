import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ROOT_DIR = BACKEND_DIR.parent
FEATURES_DIR = ROOT_DIR / "data" / "features"
MODELS_DIR = ROOT_DIR / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

from app.db.database import engine, Base, SessionLocal
from app.db.models import ModelRegistryModel

def train_prospectivity_model():
    print("--> Training prospectivity ML model...")
    feat_file = FEATURES_DIR / "prospectivity_features.csv"
    if not feat_file.exists():
        print(f"Features file missing: {feat_file}")
        return

    df = pd.read_csv(feat_file)
    feature_cols = ["mn_assay_avg", "mn_proxy_avg", "spectral_proxy_avg", "elevation_m", "slope_deg", "ndvi_avg"]
    X = df[feature_cols]
    y = df["target_prospectivity"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Baseline & Primary Gradient Boosting Regressor
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    print(f"--> Prospectivity Model Trained. MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")

    # Save model artifact
    model_path = MODELS_DIR / "prospectivity_gbr.joblib"
    joblib.dump(model, model_path)
    print(f"--> Saved model artifact to {model_path}")

    # Update database model registry
    db = SessionLocal()
    try:
        metrics_json = json.dumps({"MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)})
        entry = db.query(ModelRegistryModel).filter_by(version="demo-prospectivity-1.0.0").first()
        if not entry:
            db.add(ModelRegistryModel(
                version="demo-prospectivity-1.0.0",
                task="prospectivity prediction",
                training_dataset="demo-joined-v1 (20 mine zones, 240 drill holes)",
                validation="80/20 train/test split design",
                trained_at=datetime.now(timezone.utc).isoformat(),
                metrics_json=metrics_json,
                is_active=True
            ))
        else:
            entry.metrics_json = metrics_json
            entry.trained_at = datetime.now(timezone.utc).isoformat()
        db.commit()
        print("--> Updated database Model Registry entry.")
    finally:
        db.close()

def main():
    Base.metadata.create_all(bind=engine)
    train_prospectivity_model()

if __name__ == "__main__":
    main()

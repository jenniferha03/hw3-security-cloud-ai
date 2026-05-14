"""
Train Isolation Forest on alarm CSV and save model + feature metadata locally.

- Uses numeric feature columns only (excludes id, is_false_alarm).
- IsolationForest: outliers (prediction -1) are treated as *anomalies*; in this
  homework narrative we align them with *likely false alarms* for reporting.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "model"
CSV_PATH = DATA_DIR / "alarms.csv"
MODEL_PATH = MODEL_DIR / "isolation_forest.joblib"
FEATURE_META_PATH = MODEL_DIR / "feature_columns.json"

EXCLUDE = {"id", "label", "is_false_alarm"}


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CSV_PATH}. Run: python scripts/generate_alarms_csv.py"
        )
    df = pd.read_csv(CSV_PATH)
    feature_cols = [c for c in df.columns if c.lower() not in EXCLUDE]
    if not feature_cols:
        raise ValueError("No feature columns found after excluding id/labels.")

    X = df[feature_cols].astype(float).values

    # Unsupervised: contamination ~ expected false-alarm rate for demo
    model = IsolationForest(
        n_estimators=200,
        random_state=42,
        contamination=0.12,
    )
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    FEATURE_META_PATH.write_text(
        json.dumps({"feature_columns": feature_cols, "version": 1}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved feature metadata to {FEATURE_META_PATH}")

    if "is_false_alarm" in df.columns:
        pred = model.predict(X)
        actual_false = df["is_false_alarm"].astype(bool).values
        flagged = pred == -1
        agree = (flagged == actual_false).mean()
        print(
            "\n--- Illustrative: P(outlier flag) matches ground-truth is_false_alarm ---"
        )
        print(f"Agreement rate: {agree:.3f} (unsupervised model; not tuned for this label)")


if __name__ == "__main__":
    main()

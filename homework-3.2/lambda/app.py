"""
POST /verify — JSON body with alarm feature fields (see feature_columns.json).
Loads Isolation Forest + feature order from S3 (cached under /tmp).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import boto3
import joblib
import numpy as np

MODEL_PATH = Path("/tmp/isolation_forest.joblib")
META_PATH = Path("/tmp/feature_columns.json")
S3 = boto3.client("s3")


def _ensure_model() -> None:
    bucket = os.environ.get("MODEL_BUCKET", "").strip()
    key_model = os.environ.get("MODEL_KEY", "models/isolation_forest.joblib").strip()
    key_meta = os.environ.get("META_KEY", "models/feature_columns.json").strip()
    if not bucket:
        raise RuntimeError("MODEL_BUCKET environment variable is not set")

    if not MODEL_PATH.exists():
        S3.download_file(bucket, key_model, str(MODEL_PATH))
    if not META_PATH.exists():
        S3.download_file(bucket, key_meta, str(META_PATH))


def _load_meta() -> list[str]:
    data = json.loads(META_PATH.read_text(encoding="utf-8"))
    cols = data.get("feature_columns")
    if not cols or not isinstance(cols, list):
        raise ValueError("feature_columns.json missing 'feature_columns' list")
    return [str(c) for c in cols]


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    try:
        _ensure_model()
        feature_columns = _load_meta()
        model = joblib.load(MODEL_PATH)

        vec = []
        missing = []
        for c in feature_columns:
            if c not in body:
                missing.append(c)
            else:
                try:
                    vec.append(float(body[c]))
                except (TypeError, ValueError):
                    return _response(
                        400,
                        {"error": f"Feature '{c}' must be numeric", "required": feature_columns},
                    )
        if missing:
            return _response(
                400,
                {
                    "error": "Missing required feature fields",
                    "required": feature_columns,
                    "missing": missing,
                },
            )

        x = np.asarray([vec], dtype=float)
        pred = model.predict(x)[0]
        score = float(model.decision_function(x)[0])
        # sklearn: -1 = outlier (anomaly) -> treat as likely false alarm for this homework
        is_anomaly = pred == -1
        likely_false_alarm = bool(is_anomaly)

        return _response(
            200,
            {
                "likely_false_alarm": likely_false_alarm,
                "isolation_forest_prediction": int(pred),
                "anomaly_score": score,
                "interpretation": "prediction -1 means outlier (anomaly); mapped to likely_false_alarm for assignment narrative.",
            },
        )
    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }

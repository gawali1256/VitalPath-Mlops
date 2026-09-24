from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from backend.app.config import settings
from mlops.features import FEATURE_COLUMNS, encode_inputs


class ModelNotFoundError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def load_bundle(model_path: str | None = None) -> dict:
    path = Path(model_path or settings.model_path)
    if not path.exists():
        local_fallback = Path(__file__).resolve().parents[3] / "mlops" / "models" / "current" / "model.joblib"
        path = local_fallback
    if not path.exists():
        raise ModelNotFoundError(f"No model found at {path}. Run `python mlops/train.py` first.")
    bundle = joblib.load(path)
    metadata_path = path.parent / "metadata.json"
    bundle["metadata"] = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.exists()
        else {"name": "vitalpath-health-models", "version": "unknown", "trained_at": "", "algorithm": "unknown", "features": FEATURE_COLUMNS, "metrics": {}}
    )
    bundle["resolved_path"] = str(path)
    return bundle


def predict(payload: dict) -> dict:
    bundle = load_bundle()
    features = encode_inputs(payload)
    frame = pd.DataFrame([features], columns=FEATURE_COLUMNS)
    risk_code = int(bundle["risk_model"].predict(frame)[0])
    intensity_code = int(bundle["intensity_model"].predict(frame)[0])
    risk_proba = bundle["risk_model"].predict_proba(frame)[0]
    return {
        "bmi": features["bmi"],
        "risk_level": bundle["risk_labels"][risk_code],
        "risk_confidence": round(float(max(risk_proba)), 3),
        "recommended_intensity": bundle["intensity_labels"][intensity_code],
        "model_version": bundle["metadata"].get("version", "unknown"),
        "features": features,
    }

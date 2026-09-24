"""Offline evaluation gate used by CI before an image is built."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mlops.data import generate_dataset
from mlops.features import FEATURE_COLUMNS


MIN_RISK_ACCURACY = 0.85
MIN_INTENSITY_F1 = 0.80


def evaluate(model_path: Path | None = None) -> dict:
    model_path = model_path or ROOT / "mlops" / "models" / "current" / "model.joblib"
    bundle = joblib.load(model_path)
    holdout = generate_dataset(n_samples=800, seed=99)
    x = holdout[FEATURE_COLUMNS]
    risk_pred = bundle["risk_model"].predict(x)
    intensity_pred = bundle["intensity_model"].predict(x)

    result = {
        "risk_accuracy": round(float(accuracy_score(holdout["risk_level"], risk_pred)), 4),
        "intensity_f1_macro": round(
            float(f1_score(holdout["intensity"], intensity_pred, average="macro")), 4
        ),
        "model_path": str(model_path),
    }

    metadata_path = model_path.parent / "metadata.json"
    if metadata_path.exists():
        result["trained_metrics"] = json.loads(metadata_path.read_text(encoding="utf-8")).get("metrics")

    if result["risk_accuracy"] < MIN_RISK_ACCURACY:
        raise SystemExit(f"Evaluation failed: risk accuracy {result['risk_accuracy']} < {MIN_RISK_ACCURACY}")
    if result["intensity_f1_macro"] < MIN_INTENSITY_F1:
        raise SystemExit(
            f"Evaluation failed: intensity F1 {result['intensity_f1_macro']} < {MIN_INTENSITY_F1}"
        )
    print(json.dumps({"status": "passed", **result}, indent=2))
    return result


if __name__ == "__main__":
    evaluate()

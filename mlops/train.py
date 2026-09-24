"""Train risk and intensity models, then publish them to the local model registry."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mlops.data import generate_dataset
from mlops.features import FEATURE_COLUMNS, INTENSITY_LABELS, RISK_LABELS


def _build_classifier(random_state: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=120,
                    max_depth=8,
                    min_samples_leaf=3,
                    random_state=random_state,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def train(n_samples: int = 2500, seed: int = 42, registry_dir: Path | None = None) -> dict:
    registry_dir = registry_dir or ROOT / "mlops" / "models" / "current"
    registry_dir.mkdir(parents=True, exist_ok=True)

    data = generate_dataset(n_samples=n_samples, seed=seed)
    x = data[FEATURE_COLUMNS]
    y_risk = data["risk_level"]
    y_intensity = data["intensity"]

    x_train, x_test, y_risk_train, y_risk_test, y_int_train, y_int_test = train_test_split(
        x,
        y_risk,
        y_intensity,
        test_size=0.2,
        random_state=seed,
        stratify=y_risk,
    )

    risk_model = _build_classifier(seed)
    intensity_model = _build_classifier(seed + 1)
    risk_model.fit(x_train, y_risk_train)
    intensity_model.fit(x_train, y_int_train)

    risk_pred = risk_model.predict(x_test)
    intensity_pred = intensity_model.predict(x_test)

    metrics = {
        "risk_accuracy": round(float(accuracy_score(y_risk_test, risk_pred)), 4),
        "risk_f1_macro": round(float(f1_score(y_risk_test, risk_pred, average="macro")), 4),
        "intensity_accuracy": round(float(accuracy_score(y_int_test, intensity_pred)), 4),
        "intensity_f1_macro": round(float(f1_score(y_int_test, intensity_pred, average="macro")), 4),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
    }

    bundle = {
        "risk_model": risk_model,
        "intensity_model": intensity_model,
        "feature_columns": FEATURE_COLUMNS,
        "risk_labels": RISK_LABELS,
        "intensity_labels": INTENSITY_LABELS,
    }
    model_path = registry_dir / "model.joblib"
    joblib.dump(bundle, model_path)

    metadata = {
        "name": "vitalpath-health-models",
        "version": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "RandomForestClassifier",
        "features": FEATURE_COLUMNS,
        "metrics": metrics,
        "risk_report": classification_report(
            y_risk_test, risk_pred, target_names=list(RISK_LABELS.values()), output_dict=True
        ),
        "model_path": str(model_path),
        "seed": seed,
        "n_samples": n_samples,
    }
    (registry_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    _maybe_log_mlflow(bundle, metrics, metadata, model_path)
    print(json.dumps({"status": "trained", **metrics, "registry": str(registry_dir)}, indent=2))

    if metrics["risk_accuracy"] < 0.85:
        raise SystemExit(f"Risk model accuracy {metrics['risk_accuracy']} is below the 0.85 gate")
    return metadata


def _maybe_log_mlflow(bundle: dict, metrics: dict, metadata: dict, model_path: Path) -> None:
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        return
    try:
        import mlflow
        import mlflow.sklearn
    except ImportError:
        print("MLflow is not installed; skipping experiment logging")
        return

    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("vitalpath-health")
        with mlflow.start_run(run_name=f"train-{metadata['version']}"):
            mlflow.log_params(
                {
                    "algorithm": metadata["algorithm"],
                    "n_samples": metadata["n_samples"],
                    "seed": metadata["seed"],
                }
            )
            mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, (int, float, np.floating))})
            mlflow.log_artifact(str(model_path))
            mlflow.sklearn.log_model(bundle["risk_model"], artifact_path="risk_model")
    except Exception as exc:
        print(f"MLflow logging skipped: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train VitalPath health models")
    parser.add_argument("--n-samples", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--registry", type=Path, default=None)
    args = parser.parse_args()
    train(n_samples=args.n_samples, seed=args.seed, registry_dir=args.registry)


if __name__ == "__main__":
    main()

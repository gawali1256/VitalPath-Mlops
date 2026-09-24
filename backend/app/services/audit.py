import json
from datetime import datetime, timezone
from pathlib import Path

from backend.app.config import settings


def log_prediction(payload: dict, result: dict) -> None:
    path = Path(settings.log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "inputs": payload,
        "bmi": result.get("bmi"),
        "risk_level": result.get("risk_level"),
        "recommended_intensity": result.get("recommended_intensity"),
        "model_version": result.get("model_version"),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")

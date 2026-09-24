from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mlops.train import train


@pytest.fixture(scope="session")
def trained_model(tmp_path_factory):
    registry = tmp_path_factory.mktemp("registry")
    train(n_samples=600, seed=7, registry_dir=registry)
    return registry / "model.joblib"


@pytest.fixture()
def client(trained_model, monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_PATH", str(trained_model))
    monkeypatch.setenv("LOG_PATH", str(tmp_path / "predictions.jsonl"))

    from backend.app import config
    from backend.app.services import predictor

    config.settings.model_path = Path(trained_model)
    config.settings.log_path = tmp_path / "predictions.jsonl"
    predictor.load_bundle.cache_clear()

    from backend.app.main import app

    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_assess_returns_bmi_and_exercises(client):
    payload = {
        "age": 29,
        "gender": "female",
        "height_cm": 165,
        "weight_kg": 62,
        "activity_level": "moderate",
        "sleep_hours": 7.5,
        "goal": "maintain",
    }
    response = client.post("/api/assess", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["bmi"] == 22.8
    assert body["bmi_category"] == "healthy"
    assert body["risk_level"] in {"low", "moderate", "high"}
    assert len(body["exercises"]) >= 3
    assert body["model_version"]

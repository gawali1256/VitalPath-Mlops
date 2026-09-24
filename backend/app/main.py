from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.config import settings

STATIC_DIR = Path(__file__).parent / "static"
from backend.app.schemas import AssessmentResponse, HealthInput, ModelInfo
from backend.app.services.audit import log_prediction
from backend.app.services.bmi import bmi_category, calculate_bmi, health_narrative
from backend.app.services.exercises import recommend_exercises
from backend.app.services.predictor import ModelNotFoundError, load_bundle, predict

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allow_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "vitalpath-api"}


@app.get("/ready")
def ready() -> dict:
    try:
        bundle = load_bundle()
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready", "model_version": bundle["metadata"].get("version")}


@app.get("/api/model", response_model=ModelInfo)
def model_info() -> ModelInfo:
    try:
        metadata = load_bundle()["metadata"]
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ModelInfo(
        name=metadata.get("name", "vitalpath-health-models"),
        version=metadata.get("version", "unknown"),
        trained_at=metadata.get("trained_at", ""),
        algorithm=metadata.get("algorithm", "unknown"),
        features=metadata.get("features", []),
        metrics=metadata.get("metrics", {}),
    )


@app.post("/api/assess", response_model=AssessmentResponse)
def assess(payload: HealthInput) -> AssessmentResponse:
    try:
        prediction = predict(payload.model_dump())
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    bmi = calculate_bmi(payload.height_cm, payload.weight_kg)
    category = bmi_category(bmi)
    status, summary = health_narrative(
        bmi, category, prediction["risk_level"], payload.activity_level, payload.sleep_hours
    )
    weekly_focus, exercises = recommend_exercises(category, prediction["recommended_intensity"], payload.goal)
    response = AssessmentResponse(
        bmi=bmi,
        bmi_category=category,
        health_status=status,
        summary=summary,
        risk_level=prediction["risk_level"],
        risk_confidence=prediction["risk_confidence"],
        recommended_intensity=prediction["recommended_intensity"],
        weekly_focus=weekly_focus,
        exercises=exercises,
        model_version=prediction["model_version"],
    )
    log_prediction(payload.model_dump(), response.model_dump())
    return response


@app.get("/api/metrics")
def metrics() -> dict:
    log_path = Path(settings.log_path)
    count = 0
    if log_path.exists():
        count = sum(1 for _ in log_path.open(encoding="utf-8"))
    return {"prediction_count": count, "log_path": str(log_path)}

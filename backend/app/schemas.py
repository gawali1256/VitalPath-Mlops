from typing import Literal

from pydantic import BaseModel, Field


class HealthInput(BaseModel):
    age: int = Field(..., ge=14, le=90)
    gender: Literal["female", "male", "other"]
    height_cm: float = Field(..., ge=120, le=230)
    weight_kg: float = Field(..., ge=30, le=250)
    activity_level: Literal["sedentary", "light", "moderate", "active"]
    sleep_hours: float = Field(..., ge=3, le=14)
    goal: Literal["lose", "maintain", "gain"]


class ExerciseItem(BaseModel):
    name: str
    minutes: int
    frequency_per_week: int
    why: str


class AssessmentResponse(BaseModel):
    bmi: float
    bmi_category: str
    health_status: str
    summary: str
    risk_level: str
    risk_confidence: float
    recommended_intensity: str
    weekly_focus: str
    exercises: list[ExerciseItem]
    model_version: str


class ModelInfo(BaseModel):
    name: str
    version: str
    trained_at: str
    algorithm: str
    features: list[str]
    metrics: dict

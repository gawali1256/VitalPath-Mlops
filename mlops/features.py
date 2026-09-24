"""Shared feature definitions used by training and serving."""

FEATURE_COLUMNS = [
    "age",
    "gender_code",
    "height_cm",
    "weight_kg",
    "bmi",
    "activity_code",
    "sleep_hours",
    "goal_code",
]

GENDER_MAP = {"female": 0, "male": 1, "other": 2}
ACTIVITY_MAP = {
    "sedentary": 0,
    "light": 1,
    "moderate": 2,
    "active": 3,
}
GOAL_MAP = {"lose": 0, "maintain": 1, "gain": 2}

RISK_LABELS = {0: "low", 1: "moderate", 2: "high"}
INTENSITY_LABELS = {0: "gentle", 1: "moderate", 2: "vigorous"}


def encode_inputs(payload: dict) -> dict:
    """Turn a user form payload into numeric model features."""
    height_m = payload["height_cm"] / 100.0
    bmi = payload["weight_kg"] / (height_m**2)
    return {
        "age": float(payload["age"]),
        "gender_code": float(GENDER_MAP[payload["gender"]]),
        "height_cm": float(payload["height_cm"]),
        "weight_kg": float(payload["weight_kg"]),
        "bmi": round(bmi, 2),
        "activity_code": float(ACTIVITY_MAP[payload["activity_level"]]),
        "sleep_hours": float(payload["sleep_hours"]),
        "goal_code": float(GOAL_MAP[payload["goal"]]),
    }

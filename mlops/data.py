"""Synthetic health records used to train the risk and intensity models."""

from __future__ import annotations

import numpy as np
import pandas as pd

from mlops.features import FEATURE_COLUMNS


def _bmi(height_cm: np.ndarray, weight_kg: np.ndarray) -> np.ndarray:
    return weight_kg / ((height_cm / 100.0) ** 2)


def _label_risk(bmi: np.ndarray, age: np.ndarray, activity: np.ndarray, sleep: np.ndarray) -> np.ndarray:
    """Deterministic clinical-style rules so the model has a learnable signal."""
    risk = np.ones(len(bmi), dtype=int)

    healthy = (bmi >= 18.5) & (bmi < 25) & (activity >= 2) & (sleep >= 7)
    risk[healthy] = 0

    high = (bmi >= 30) | (bmi < 17) | ((sleep < 5.5) & (bmi >= 28)) | ((age >= 55) & (bmi >= 28) & (activity == 0))
    risk[high] = 2
    return risk


def _label_intensity(risk: np.ndarray, activity: np.ndarray, bmi: np.ndarray, goal: np.ndarray) -> np.ndarray:
    intensity = np.ones(len(risk), dtype=int)
    intensity[risk == 2] = 0
    intensity[(risk == 0) & (activity >= 2)] = 2
    intensity[(goal == 2) & (bmi < 25) & (risk < 2)] = 1
    intensity[(bmi >= 35)] = 0
    return intensity


def generate_dataset(n_samples: int = 2500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 71, size=n_samples)
    gender_code = rng.integers(0, 3, size=n_samples)
    height_cm = rng.normal(168, 10, size=n_samples).clip(145, 200)
    weight_kg = rng.normal(72, 16, size=n_samples).clip(42, 145)
    activity_code = rng.integers(0, 4, size=n_samples)
    sleep_hours = rng.normal(7.0, 1.1, size=n_samples).clip(4.0, 10.0)
    goal_code = rng.integers(0, 3, size=n_samples)
    bmi = _bmi(height_cm, weight_kg)

    risk = _label_risk(bmi, age, activity_code, sleep_hours)
    intensity = _label_intensity(risk, activity_code, bmi, goal_code)

    frame = pd.DataFrame(
        {
            "age": age,
            "gender_code": gender_code,
            "height_cm": height_cm.round(1),
            "weight_kg": weight_kg.round(1),
            "bmi": bmi.round(2),
            "activity_code": activity_code,
            "sleep_hours": sleep_hours.round(1),
            "goal_code": goal_code,
            "risk_level": risk,
            "intensity": intensity,
        }
    )
    assert list(frame[FEATURE_COLUMNS].columns) == FEATURE_COLUMNS
    return frame

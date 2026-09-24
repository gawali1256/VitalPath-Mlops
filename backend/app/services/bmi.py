def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m**2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy"
    if bmi < 30:
        return "overweight"
    return "obese"


def health_narrative(bmi: float, category: str, risk_level: str, activity_level: str, sleep_hours: float) -> tuple[str, str]:
    status_map = {
        "underweight": "Needs nourishment and strength work",
        "healthy": "Body mass is in a healthy range",
        "overweight": "Body mass is above the healthy range",
        "obese": "Body mass is in a higher-risk range",
    }
    sleep_note = (
        "Sleep looks adequate."
        if sleep_hours >= 7
        else "Sleep is below the usual 7-hour target and can raise recovery risk."
    )
    activity_note = {
        "sedentary": "Daily movement is low, so start with short walks.",
        "light": "You already move a little; add two structured sessions.",
        "moderate": "Your activity base is solid; keep consistency high.",
        "active": "You are already active; protect recovery while training.",
    }[activity_level]

    status = status_map[category]
    if risk_level == "high":
        status = f"{status} — start gently and consider a clinician check"
    elif risk_level == "low" and category == "healthy":
        status = "Overall health markers look favorable"

    summary = (
        f"BMI is {bmi} ({category}). Predicted lifestyle risk is {risk_level}. "
        f"{activity_note} {sleep_note}"
    )
    return status, summary

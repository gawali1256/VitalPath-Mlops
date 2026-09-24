from backend.app.schemas import ExerciseItem


CATALOG: dict[str, list[dict]] = {
    "underweight": [
        {
            "name": "Full-body strength circuit",
            "minutes": 35,
            "frequency_per_week": 3,
            "why": "Builds muscle and healthy weight with compound movements.",
        },
        {
            "name": "Yoga or mobility flow",
            "minutes": 25,
            "frequency_per_week": 2,
            "why": "Improves joint control without burning excess calories.",
        },
        {
            "name": "Brisk walk after meals",
            "minutes": 20,
            "frequency_per_week": 5,
            "why": "Supports appetite and recovery without over-taxing energy.",
        },
    ],
    "healthy": [
        {
            "name": "Zone-2 cardio (jog, cycle, or swim)",
            "minutes": 30,
            "frequency_per_week": 3,
            "why": "Maintains heart health while you stay in a healthy BMI range.",
        },
        {
            "name": "Strength training",
            "minutes": 40,
            "frequency_per_week": 2,
            "why": "Preserves muscle and metabolic health.",
        },
        {
            "name": "Mobility and core work",
            "minutes": 15,
            "frequency_per_week": 3,
            "why": "Keeps posture and daily movement quality high.",
        },
    ],
    "overweight": [
        {
            "name": "Brisk walking intervals",
            "minutes": 30,
            "frequency_per_week": 4,
            "why": "Low-barrier cardio that steadily lowers body-mass load.",
        },
        {
            "name": "Bodyweight strength (squats, rows, pushes)",
            "minutes": 25,
            "frequency_per_week": 3,
            "why": "Protects muscle while you work toward a healthier BMI.",
        },
        {
            "name": "Cycling or swimming",
            "minutes": 25,
            "frequency_per_week": 2,
            "why": "Joint-friendly calorie burn if walking feels hard on knees.",
        },
    ],
    "obese": [
        {
            "name": "Easy outdoor or indoor walking",
            "minutes": 20,
            "frequency_per_week": 5,
            "why": "Builds a daily habit with the lowest injury risk.",
        },
        {
            "name": "Chair or wall-supported strength",
            "minutes": 20,
            "frequency_per_week": 3,
            "why": "Improves strength without high impact.",
        },
        {
            "name": "Water aerobics or gentle swim",
            "minutes": 25,
            "frequency_per_week": 2,
            "why": "Unloads the joints while still moving the whole body.",
        },
    ],
}

GOAL_FOCUS = {
    "lose": "Create a small weekly calorie deficit with mostly aerobic work and two strength days.",
    "maintain": "Hold current body mass with a balanced mix of cardio, strength, and recovery.",
    "gain": "Prioritize progressive strength training and slightly higher daily calories.",
}


def recommend_exercises(category: str, intensity: str, goal: str) -> tuple[str, list[ExerciseItem]]:
    plan = [ExerciseItem(**item) for item in CATALOG[category]]
    if intensity == "gentle":
        for item in plan:
            item.minutes = max(15, item.minutes - 10)
            item.frequency_per_week = min(item.frequency_per_week, 4)
    elif intensity == "vigorous" and category in {"healthy", "overweight"}:
        plan[0].minutes += 10
        plan[0].frequency_per_week = min(plan[0].frequency_per_week + 1, 5)

    if goal == "gain":
        plan = sorted(plan, key=lambda item: ("strength" not in item.name.lower(), item.name))
    return GOAL_FOCUS[goal], plan

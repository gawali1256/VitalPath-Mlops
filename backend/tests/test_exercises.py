from backend.app.services.exercises import recommend_exercises


def test_obese_plan_stays_low_impact():
    focus, plan = recommend_exercises("obese", "gentle", "lose")
    names = " ".join(item.name.lower() for item in plan)
    assert "walk" in names
    assert all(item.minutes <= 25 for item in plan)
    assert "deficit" in focus


def test_gain_goal_prefers_strength():
    _, plan = recommend_exercises("underweight", "moderate", "gain")
    assert any("strength" in item.name.lower() for item in plan)

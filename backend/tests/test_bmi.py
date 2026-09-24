from backend.app.services.bmi import bmi_category, calculate_bmi


def test_healthy_bmi():
    assert calculate_bmi(170, 65) == 22.5
    assert bmi_category(22.5) == "healthy"


def test_underweight_and_obese_bands():
    assert bmi_category(17.2) == "underweight"
    assert bmi_category(27.4) == "overweight"
    assert bmi_category(32.0) == "obese"

"""NutritionOrder generator.

Diet orders for patients whose conditions warrant them (diabetic, low-sodium,
renal, or weight-management diets).

Output keys: id, patient_id, encounter_id, datetime, diet_code, diet_display.
"""
import random

from generators._rng import new_uuid

# condition key -> (SNOMED diet code, display)
_DIET_RULES = {
    "type2_diabetes": ("160670007", "Diabetic diet"),
    "type1_diabetes": ("160670007", "Diabetic diet"),
    "hypertension": ("386264003", "Low sodium diet"),
    "heart_failure": ("386264003", "Low sodium diet"),
    "ckd": ("284858000", "Renal diet"),
    "obesity": ("435801000124108", "Weight reduction diet"),
}


def generate_nutrition_order_for_patient(
    patient_id: str, encounter_id: str, order_datetime: str, condition_keys: set[str]
) -> list[dict]:
    """Generate a single diet order when a diet-relevant condition is present."""
    matches = [_DIET_RULES[k] for k in condition_keys if k in _DIET_RULES]
    if not matches:
        return []
    code, display = random.choice(matches)
    return [
        {
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "datetime": order_datetime,
            "diet_code": code,
            "diet_display": display,
        }
    ]

"""Flag generator.

Clinical alerts surfaced to care teams, driven by conditions that warrant them
(anticoagulation bleeding risk, controlled-substance monitoring, infection
precautions).

Output keys: id, patient_id, encounter_id, code, display, category_code,
category_display.
"""
import random

from generators._rng import new_uuid

# condition key -> (category code, category display, alert text, probability)
_FLAG_RULES = {
    "atrial_fibrillation": ("clinical", "Clinical", "Anticoagulation therapy, bleeding risk", 0.5),
    "opioid_use_disorder": ("behavioral", "Behavioral", "Controlled substance monitoring", 0.6),
    "hiv": ("clinical", "Clinical", "Standard precautions", 0.4),
    "epilepsy": ("clinical", "Clinical", "Seizure precautions", 0.5),
}


def generate_flags_for_patient(
    patient_id: str, encounter_id: str, condition_keys: set[str]
) -> list[dict]:
    """Generate clinical alert flags implied by a patient's conditions."""
    results: list[dict] = []
    for key in condition_keys:
        rule = _FLAG_RULES.get(key)
        if not rule:
            continue
        cat_code, cat_display, display, prob = rule
        if random.random() > prob:
            continue
        results.append(
            {
                "id": new_uuid(),
                "patient_id": patient_id,
                "encounter_id": encounter_id,
                "display": display,
                "category_code": cat_code,
                "category_display": cat_display,
            }
        )
    return results

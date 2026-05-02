"""Condition generator.

Generates 1-2 conditions per patient. The pool of available conditions is
filtered to those whose typical_age_min is <= the patient's age, preventing
clinically implausible diagnoses (e.g. atrial fibrillation in a child).

When a condition_filter is supplied, that condition is always the primary
diagnosis; a random age-appropriate comorbidity is added ~40% of the time.
The `linked_obs_types` list on each condition dict drives which observation
types are generated for that patient's encounters.

Output keys: id, patient_id, practitioner_id, snomed_code, icd10_code, display,
category_code, category_display, clinical_status, verification_status,
onset_date, recorded_date, linked_obs_types.
"""
import random
from datetime import date, timedelta

from data.conditions import CONDITIONS, ConditionDef, conditions_for_age, find_condition
from generators._rng import new_uuid

_CLINICAL_STATUS_WEIGHTS = [("active", 0.75), ("inactive", 0.15), ("resolved", 0.10)]
_CATEGORY_CODES = [
    ("problem-list-item", "Problem List Item"),
    ("encounter-diagnosis", "Encounter Diagnosis"),
]


def generate_conditions_for_patient(
    patient_id: str,
    practitioner_id: str,
    patient_age: int,
    condition_filter: str | None = None,
) -> list[dict]:
    """Generates 1-2 age-appropriate conditions for a patient.

    If condition_filter is given, that condition is always included as the
    primary diagnosis. A random age-appropriate comorbidity is added ~40% of
    the time. Raises ValueError if the filter matches no known condition.
    """
    # If no conditions match (very young patient), pick from youngest-appropriate ones
    eligible = conditions_for_age(patient_age)
    if not eligible:
        eligible = sorted(CONDITIONS, key=lambda c: c.typical_age_min)[:3]

    selected: list[ConditionDef] = []

    if condition_filter:
        primary = find_condition(condition_filter)
        if primary is None:
            raise ValueError(f"Unknown condition: '{condition_filter}'")
        selected.append(primary)

    # ~40% chance of a random age-appropriate comorbidity
    if random.random() < 0.40:
        pool = [c for c in eligible if c not in selected]
        if pool:
            selected.append(random.choice(pool))

    # Guarantee at least one condition
    if not selected:
        selected.append(random.choice(eligible))

    return [_make_condition(patient_id, practitioner_id, cond) for cond in selected]


def _make_condition(patient_id: str, practitioner_id: str, cond: ConditionDef) -> dict:
    status = random.choices(
        [s[0] for s in _CLINICAL_STATUS_WEIGHTS],
        weights=[s[1] for s in _CLINICAL_STATUS_WEIGHTS],
        k=1,
    )[0]
    cat_code, cat_display = random.choice(_CATEGORY_CODES)

    # Onset: chronic conditions established 30 days to 10 years ago
    onset = date.today() - timedelta(days=random.randint(30, 3650))
    # Recorded date trails onset by 1-60 days (diagnosis lag)
    recorded = onset + timedelta(days=random.randint(1, 60))

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "practitioner_id": practitioner_id,
        "snomed_code": cond.snomed_code,
        "icd10_code": cond.icd10_code,
        "display": cond.display,
        "category_code": cat_code,
        "category_display": cat_display,
        "clinical_status": status,
        "verification_status": "confirmed",
        "onset_date": onset.strftime("%Y-%m-%d"),
        "recorded_date": recorded.strftime("%Y-%m-%d"),
        "linked_obs_types": list(cond.linked_obs_types),
    }

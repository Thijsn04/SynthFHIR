"""Condition generator.

Generates 1-2 conditions per patient. When a condition_filter is supplied, that
condition is always the primary diagnosis; a random comorbidity is added ~40% of
the time. The `linked_obs_types` list on each condition dict drives which
observation types are generated for that patient's encounters.
Output keys: id, patient_id, practitioner_id, snomed_code, icd10_code, display,
category_code, category_display, clinical_status, verification_status,
onset_date, recorded_date, linked_obs_types.
"""
import random
import uuid
from datetime import date, timedelta

from data.conditions import CONDITIONS, ConditionDef, find_condition

_CLINICAL_STATUS_WEIGHTS = [("active", 0.75), ("inactive", 0.15), ("resolved", 0.10)]
_CATEGORY_CODES = [
    ("problem-list-item", "Problem List Item"),
    ("encounter-diagnosis", "Encounter Diagnosis"),
]


def generate_conditions_for_patient(
    patient_id: str,
    practitioner_id: str,
    condition_filter: str | None = None,
) -> list[dict]:
    """Generates 1-2 conditions for a patient.

    If condition_filter is given, that condition is always included as the primary
    diagnosis. A random comorbidity is added ~40% of the time regardless.
    """
    selected: list[ConditionDef] = []

    if condition_filter:
        primary = find_condition(condition_filter)
        if primary:
            selected.append(primary)

    # ~40% chance of a random comorbidity on top of the primary
    if random.random() < 0.40:
        pool = [c for c in CONDITIONS if c not in selected]
        if pool:
            selected.append(random.choice(pool))

    # Guarantee at least one condition
    if not selected:
        selected.append(random.choice(CONDITIONS))

    return [_make_condition(patient_id, practitioner_id, cond) for cond in selected]


def _make_condition(patient_id: str, practitioner_id: str, cond: ConditionDef) -> dict:
    status = random.choices(
        [s[0] for s in _CLINICAL_STATUS_WEIGHTS],
        weights=[s[1] for s in _CLINICAL_STATUS_WEIGHTS],
        k=1,
    )[0]
    cat_code, cat_display = random.choice(_CATEGORY_CODES)
    onset = date.today() - timedelta(days=random.randint(30, 3650))

    return {
        "id": str(uuid.uuid4()),
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
        "recorded_date": onset.strftime("%Y-%m-%d"),
        "linked_obs_types": list(cond.linked_obs_types),
    }

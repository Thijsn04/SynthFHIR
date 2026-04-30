"""Observation generator.

Generates vitals and lab results for a single encounter. Every encounter always
receives the four baseline vitals (systolic BP, diastolic BP, heart rate, body
temperature). Active conditions contribute their linked observation types, and
values are biased toward the abnormal range for those conditions.
Output keys: id, patient_id, encounter_id, practitioner_id, loinc_code, display,
category_code, category_display, status, effective_datetime, value, unit,
ucum_code, interpretation_code, interpretation_display.
"""
import random
import uuid

from data.observations import OBSERVATIONS, ObservationDef

# Vital signs included in every encounter regardless of conditions
_BASELINE_OBS = ["systolic_bp", "diastolic_bp", "heart_rate", "body_temperature"]


def generate_observations_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    conditions: list[dict],
) -> list[dict]:
    """Generates observations for a single encounter.

    Always includes baseline vitals. Adds condition-specific labs for any active
    conditions, biasing values toward the abnormal range for those conditions.
    """
    obs_keys: set[str] = set(_BASELINE_OBS)

    active_condition_obs: set[str] = set()
    for cond in conditions:
        if cond.get("clinical_status") == "active":
            keys = cond.get("linked_obs_types", [])
            obs_keys.update(keys)
            active_condition_obs.update(keys)

    result = []
    for key in obs_keys:
        obs_def = OBSERVATIONS.get(key)
        if obs_def is None:
            continue
        is_abnormal = key in active_condition_obs
        result.append(
            _make(patient_id, encounter_id, practitioner_id, effective_datetime, obs_def, is_abnormal)
        )
    return result


def _make(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    is_abnormal: bool,
) -> dict:
    value_range = obs.abnormal_range if is_abnormal else obs.normal_range
    value = round(random.uniform(*value_range), obs.decimal_places)
    interp_code, interp_display = _interpret(value, obs.low_threshold, obs.high_threshold)

    return {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "practitioner_id": practitioner_id,
        "loinc_code": obs.loinc_code,
        "display": obs.display,
        "category_code": obs.category_code,
        "category_display": obs.category_display,
        "status": "final",
        "effective_datetime": effective_datetime,
        "value": value,
        "unit": obs.unit,
        "ucum_code": obs.ucum_code,
        "interpretation_code": interp_code,
        "interpretation_display": interp_display,
    }


def _interpret(value: float, low: float | None, high: float | None) -> tuple[str, str]:
    if low is not None and value < low:
        return ("L", "Low")
    if high is not None and value > high:
        return ("H", "High")
    return ("N", "Normal")

"""Observation generator.

Generates vitals and lab results for a single encounter. Every encounter always
receives the five baseline vitals (systolic BP, diastolic BP, heart rate,
respiratory rate, body temperature). Active conditions contribute their linked
observation types, and values are biased toward the abnormal range.

Key improvements over v1:
- Triangular distribution instead of uniform — values cluster realistically.
- Per-patient baseline (obs_baseline from patient dict) ensures longitudinal
  consistency: the same patient's BP stays in a similar range across visits.
- Height is taken from the patient baseline; body_weight and bmi are generated
  together so BMI = weight / (height_m ** 2) is always consistent.

Output keys: id, patient_id, encounter_id, practitioner_id, loinc_code, display,
category_code, category_display, status, effective_datetime, value, unit,
ucum_code, interpretation_code, interpretation_display.
"""
import random

from data.observations import OBSERVATIONS, ObservationDef
from generators._rng import new_uuid

# Vital signs included in every encounter regardless of conditions
_BASELINE_OBS = ["systolic_bp", "diastolic_bp", "heart_rate", "respiratory_rate", "body_temperature"]

# Fraction of the normal range to use as per-encounter jitter around the patient baseline
_BASELINE_JITTER_FRACTION = 0.08


def generate_observations_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    conditions: list[dict],
    obs_baseline: dict | None = None,
    height_cm: float | None = None,
) -> list[dict]:
    """Generates observations for a single encounter.

    Always includes baseline vitals using the patient's personal baseline
    (if provided) with small per-encounter jitter. Adds condition-specific
    labs for any active conditions, biasing values toward the abnormal range.
    Height is always recorded; BMI is derived from weight and height.
    """
    obs_keys: set[str] = set(_BASELINE_OBS) | {"height"}

    active_condition_obs: set[str] = set()
    for cond in conditions:
        if cond.get("clinical_status") == "active":
            keys = cond.get("linked_obs_types", [])
            obs_keys.update(keys)
            active_condition_obs.update(keys)

    result = []
    weight_kg: float | None = None

    for key in obs_keys:
        obs_def = OBSERVATIONS.get(key)
        if obs_def is None:
            continue

        is_abnormal = key in active_condition_obs

        # Height: use patient's fixed height, not a random draw
        if key == "height" and height_cm is not None:
            obs = _make_fixed(patient_id, encounter_id, practitioner_id, effective_datetime,
                              obs_def, height_cm)
            result.append(obs)
            continue

        # body_weight: generate first, then derive BMI
        if key == "body_weight":
            obs, weight_kg = _make_weight(patient_id, encounter_id, practitioner_id,
                                          effective_datetime, obs_def, is_abnormal, obs_baseline)
            result.append(obs)
            continue

        # BMI: skip here — we append it after weight is known
        if key == "bmi":
            continue

        personal_mid = obs_baseline.get(key) if obs_baseline else None
        obs = _make(patient_id, encounter_id, practitioner_id, effective_datetime,
                    obs_def, is_abnormal, personal_mid)
        result.append(obs)

    # Append BMI derived from weight + height (always consistent)
    if "bmi" in obs_keys or "body_weight" in obs_keys:
        bmi_def = OBSERVATIONS.get("bmi")
        if bmi_def and weight_kg is not None and height_cm is not None:
            height_m = height_cm / 100
            bmi_value = round(weight_kg / (height_m ** 2), 1)
            interp_code, interp_display = _interpret(bmi_value, bmi_def.low_threshold, bmi_def.high_threshold)
            result.append({
                "id": new_uuid(),
                "patient_id": patient_id,
                "encounter_id": encounter_id,
                "practitioner_id": practitioner_id,
                "loinc_code": bmi_def.loinc_code,
                "display": bmi_def.display,
                "category_code": bmi_def.category_code,
                "category_display": bmi_def.category_display,
                "status": "final",
                "effective_datetime": effective_datetime,
                "value": bmi_value,
                "unit": bmi_def.unit,
                "ucum_code": bmi_def.ucum_code,
                "interpretation_code": interp_code,
                "interpretation_display": interp_display,
            })

    return result


def _make(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    is_abnormal: bool,
    personal_mid: float | None,
) -> dict:
    if is_abnormal:
        lo, hi = obs.abnormal_range
        mid = (lo + hi) / 2
        value = round(random.triangular(lo, hi, mid), obs.decimal_places)
    elif personal_mid is not None:
        # Jitter around the patient's personal normal midpoint
        span = obs.normal_range[1] - obs.normal_range[0]
        jitter = span * _BASELINE_JITTER_FRACTION
        lo = max(obs.normal_range[0], personal_mid - jitter)
        hi = min(obs.normal_range[1], personal_mid + jitter)
        value = round(random.triangular(lo, hi, personal_mid), obs.decimal_places)
    else:
        lo, hi = obs.normal_range
        mid = (lo + hi) / 2
        value = round(random.triangular(lo, hi, mid), obs.decimal_places)

    interp_code, interp_display = _interpret(value, obs.low_threshold, obs.high_threshold)
    return _build(patient_id, encounter_id, practitioner_id, effective_datetime, obs, value,
                  interp_code, interp_display)


def _make_fixed(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    fixed_value: float,
) -> dict:
    interp_code, interp_display = _interpret(fixed_value, obs.low_threshold, obs.high_threshold)
    return _build(patient_id, encounter_id, practitioner_id, effective_datetime, obs,
                  round(fixed_value, obs.decimal_places), interp_code, interp_display)


def _make_weight(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    is_abnormal: bool,
    obs_baseline: dict | None,
) -> tuple[dict, float]:
    if is_abnormal:
        lo, hi = obs.abnormal_range
        weight = round(random.triangular(lo, hi, (lo + hi) / 2), obs.decimal_places)
    else:
        lo, hi = obs.normal_range
        weight = round(random.triangular(lo, hi, (lo + hi) / 2), obs.decimal_places)

    interp_code, interp_display = _interpret(weight, obs.low_threshold, obs.high_threshold)
    d = _build(patient_id, encounter_id, practitioner_id, effective_datetime, obs, weight,
               interp_code, interp_display)
    return d, weight


def _build(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    value: float,
    interp_code: str,
    interp_display: str,
) -> dict:
    return {
        "id": new_uuid(),
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

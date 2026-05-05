"""Observation generator.

Generates vitals and lab results for a single encounter. Every encounter always
receives the five baseline vitals (systolic BP, diastolic BP, heart rate,
respiratory rate, body temperature). Active conditions contribute their linked
observation types, and values are biased toward the abnormal range.

Key improvements over v1:
- Triangular distribution instead of uniform — values cluster realistically.
- Per-patient baseline (obs_baseline from patient dict) ensures longitudinal
  consistency: the same patient's BP stays in a similar range across visits.
- Height is taken from the patient baseline; body_weight uses a stable baseline
  weight with small per-encounter jitter so BMI = weight / (height_m ** 2) is
  always consistent and weight does not jump between visits.
- Condition-aware biasing: after conditions are resolved, update_obs_baseline_for_conditions
  should be called in cohort_gen.py so the personal midpoint sits in the clinically
  appropriate range (e.g. elevated BP for hypertension patients).
- ServiceRequest basedOn: optional sr_basedOn dict maps obs_key → SR id.

Output keys: id, patient_id, encounter_id, practitioner_id, loinc_code, display,
category_code, category_display, status, effective_datetime, value, unit,
ucum_code, interpretation_code, interpretation_display, [based_on_service_request_id].
"""
import random

from data.observations import OBSERVATIONS, ObservationDef
from generators._rng import new_uuid

# Vital signs included in every encounter regardless of conditions.
_BASELINE_OBS = ["heart_rate", "respiratory_rate", "body_temperature"]

_BP_PANEL_LOINC = "85354-9"
_BP_PANEL_DISPLAY = "Blood pressure panel with all children optional"

# Fraction of the (normal or abnormal) range used as per-encounter jitter
_BASELINE_JITTER_FRACTION = 0.08

# Per-encounter weight jitter in kg — small bounded perturbation around the
# patient's stable weight baseline (reflects real-world between-visit variability).
_WEIGHT_JITTER_KG = 1.5


def update_obs_baseline_for_conditions(obs_baseline: dict, conditions: list[dict]) -> None:
    """Adjust obs_baseline in-place so personal midpoints reflect active conditions.

    Called in cohort_gen.py after conditions are generated, before encounters.
    This ensures every encounter draws from the clinically appropriate range.
    """
    active_keys = {c.get("condition_key", "") for c in conditions
                   if c.get("clinical_status") == "active"}

    # Hypertension / atrial fibrillation / coronary artery disease / heart failure / stroke
    # → elevated BP baseline in the hypertensive abnormal range
    bp_elevating = {
        "hypertension", "atrial_fibrillation", "coronary_artery_disease",
        "heart_failure", "ischemic_stroke", "peripheral_artery_disease",
        "pulmonary_hypertension",
    }
    if active_keys & bp_elevating:
        obs_baseline["systolic_bp"] = round(random.triangular(135, 165, 148), 0)
        obs_baseline["diastolic_bp"] = round(random.triangular(85, 105, 93), 0)

    # Atrial fibrillation / hyperthyroidism → elevated heart rate
    hr_elevating = {"atrial_fibrillation", "hyperthyroidism", "heart_failure"}
    if active_keys & hr_elevating:
        obs_baseline["heart_rate"] = round(random.triangular(90, 140, 108), 0)

    # Hypothyroidism → low heart rate
    if "hypothyroidism" in active_keys and "atrial_fibrillation" not in active_keys:
        obs_baseline["heart_rate"] = round(random.triangular(45, 65, 56), 0)

    # COPD / asthma / pulmonary hypertension / covid19_long → reduced O2 sat, elevated RR
    o2_reducing = {"copd", "asthma", "pulmonary_hypertension", "covid19_long", "lung_cancer"}
    if active_keys & o2_reducing:
        obs_baseline["oxygen_saturation"] = round(random.triangular(88, 95, 92), 0)
        obs_baseline["respiratory_rate"] = round(random.triangular(18, 28, 22), 0)

    # Pneumonia / active infection → fever + elevated RR
    if "pneumonia" in active_keys:
        obs_baseline["body_temperature"] = round(random.triangular(38.0, 39.5, 38.8), 1)
        obs_baseline["respiratory_rate"] = round(random.triangular(20, 32, 25), 0)

    # Obesity → elevated weight baseline already set; no further change needed
    # (weight_kg was derived from BMI target in patient_gen)


def generate_observations_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    conditions: list[dict],
    obs_baseline: dict | None = None,
    height_cm: float | None = None,
    sr_basedOn: dict[str, str] | None = None,
) -> list[dict]:
    """Generates observations for a single encounter.

    Always includes baseline vitals using the patient's personal baseline
    (if provided) with small per-encounter jitter. Adds condition-specific
    labs for any active conditions, biasing values toward the abnormal range.
    Height is always recorded; weight uses the stable baseline with small jitter;
    BMI is derived from weight and height.

    sr_basedOn: maps obs_key → ServiceRequest.id for the basedOn reference.
    """
    obs_keys: set[str] = set(_BASELINE_OBS) | {"height"}

    active_condition_obs: set[str] = set()
    for cond in conditions:
        if cond.get("clinical_status") == "active":
            keys = cond.get("linked_obs_types", [])
            obs_keys.update(keys)
            active_condition_obs.update(keys)

    # BP panel replaces separate systolic/diastolic observations.
    bp_abnormal = "systolic_bp" in active_condition_obs or "diastolic_bp" in active_condition_obs
    obs_keys.discard("systolic_bp")
    obs_keys.discard("diastolic_bp")

    result: list[dict] = []
    weight_kg: float | None = None

    # Always generate the BP panel
    result.append(_make_bp_panel(
        patient_id, encounter_id, practitioner_id, effective_datetime,
        is_abnormal=bp_abnormal,
        obs_baseline=obs_baseline,
    ))

    for key in obs_keys:
        obs_def = OBSERVATIONS.get(key)
        if obs_def is None:
            continue

        is_abnormal = key in active_condition_obs
        sr_id = (sr_basedOn or {}).get(key)

        # Height: use patient's fixed height
        if key == "height" and height_cm is not None:
            obs = _make_fixed(patient_id, encounter_id, practitioner_id, effective_datetime,
                              obs_def, height_cm, sr_id=sr_id)
            result.append(obs)
            continue

        # body_weight: use stable baseline + small jitter; derive BMI after
        if key == "body_weight":
            obs, weight_kg = _make_weight(
                patient_id, encounter_id, practitioner_id,
                effective_datetime, obs_def, obs_baseline, sr_id=sr_id,
            )
            result.append(obs)
            continue

        # BMI: skip here — appended after weight is known
        if key == "bmi":
            continue

        personal_mid = obs_baseline.get(key) if obs_baseline else None
        obs = _make(patient_id, encounter_id, practitioner_id, effective_datetime,
                    obs_def, is_abnormal, personal_mid, sr_id=sr_id)
        result.append(obs)

    # Append BMI derived from weight + height (always consistent)
    if "bmi" in obs_keys or "body_weight" in obs_keys:
        bmi_def = OBSERVATIONS.get("bmi")
        if bmi_def and weight_kg is not None and height_cm is not None:
            height_m = height_cm / 100
            bmi_value = round(weight_kg / (height_m ** 2), 1)
            interp_code, interp_disp = _interpret(bmi_value, bmi_def.low_threshold, bmi_def.high_threshold)
            bmi_obs: dict = {
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
                "interpretation_display": interp_disp,
                "ref_range_low": bmi_def.normal_range[0],
                "ref_range_high": bmi_def.normal_range[1],
                "ref_range_unit": bmi_def.unit,
                "ref_range_ucum": bmi_def.ucum_code,
            }
            sr_bmi = (sr_basedOn or {}).get("bmi")
            if sr_bmi:
                bmi_obs["based_on_service_request_id"] = sr_bmi
            result.append(bmi_obs)

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_bp_panel(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    is_abnormal: bool,
    obs_baseline: dict | None,
) -> dict:
    sys_def = OBSERVATIONS["systolic_bp"]
    dia_def = OBSERVATIONS["diastolic_bp"]

    def _draw(obs_def: ObservationDef, personal_mid: float | None) -> float:
        if personal_mid is not None:
            # Use personal mid (may be in abnormal range if updated by update_obs_baseline_for_conditions)
            span = (obs_def.abnormal_range[1] - obs_def.abnormal_range[0]
                    if is_abnormal else obs_def.normal_range[1] - obs_def.normal_range[0])
            jitter = span * _BASELINE_JITTER_FRACTION
            if is_abnormal:
                lo = max(obs_def.abnormal_range[0], personal_mid - jitter)
                hi = min(obs_def.abnormal_range[1], personal_mid + jitter)
            else:
                lo = max(obs_def.normal_range[0], personal_mid - jitter)
                hi = min(obs_def.normal_range[1], personal_mid + jitter)
            return round(random.triangular(lo, hi, personal_mid), obs_def.decimal_places)
        if is_abnormal:
            lo, hi = obs_def.abnormal_range
        else:
            lo, hi = obs_def.normal_range
        return round(random.triangular(lo, hi, (lo + hi) / 2), obs_def.decimal_places)

    sys_mid = obs_baseline.get("systolic_bp") if obs_baseline else None
    dia_mid = obs_baseline.get("diastolic_bp") if obs_baseline else None
    sys_val = _draw(sys_def, sys_mid)
    dia_val = _draw(dia_def, dia_mid)

    sys_interp, sys_interp_disp = _interpret(sys_val, sys_def.low_threshold, sys_def.high_threshold)
    dia_interp, dia_interp_disp = _interpret(dia_val, dia_def.low_threshold, dia_def.high_threshold)

    panel_interp_code = sys_interp or dia_interp
    panel_interp_disp = sys_interp_disp or dia_interp_disp

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "practitioner_id": practitioner_id,
        "loinc_code": _BP_PANEL_LOINC,
        "display": _BP_PANEL_DISPLAY,
        "category_code": "vital-signs",
        "category_display": "Vital Signs",
        "status": "final",
        "effective_datetime": effective_datetime,
        "value": 0,
        "unit": "",
        "ucum_code": "",
        "interpretation_code": panel_interp_code,
        "interpretation_display": panel_interp_disp,
        "components": [
            {
                "loinc_code": sys_def.loinc_code,
                "display": sys_def.display,
                "value": sys_val,
                "unit": sys_def.unit,
                "ucum_code": sys_def.ucum_code,
                "interpretation_code": sys_interp,
                "interpretation_display": sys_interp_disp,
            },
            {
                "loinc_code": dia_def.loinc_code,
                "display": dia_def.display,
                "value": dia_val,
                "unit": dia_def.unit,
                "ucum_code": dia_def.ucum_code,
                "interpretation_code": dia_interp,
                "interpretation_display": dia_interp_disp,
            },
        ],
    }


def _make(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    is_abnormal: bool,
    personal_mid: float | None,
    sr_id: str | None = None,
) -> dict:
    if personal_mid is not None:
        # Clamp the personal midpoint to whichever range applies, then jitter within it
        rng = obs.abnormal_range if is_abnormal else obs.normal_range
        mid = max(rng[0], min(rng[1], personal_mid))
        span = rng[1] - rng[0]
        jitter = span * _BASELINE_JITTER_FRACTION
        lo = max(rng[0], mid - jitter)
        hi = min(rng[1], mid + jitter)
        value = round(random.triangular(lo, hi, mid), obs.decimal_places)
    elif is_abnormal:
        lo, hi = obs.abnormal_range
        value = round(random.triangular(lo, hi, (lo + hi) / 2), obs.decimal_places)
    else:
        lo, hi = obs.normal_range
        value = round(random.triangular(lo, hi, (lo + hi) / 2), obs.decimal_places)

    interp_code, interp_display = _interpret(value, obs.low_threshold, obs.high_threshold)
    d = _build(patient_id, encounter_id, practitioner_id, effective_datetime, obs, value,
               interp_code, interp_display)
    if sr_id:
        d["based_on_service_request_id"] = sr_id
    return d


def _make_fixed(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    fixed_value: float,
    sr_id: str | None = None,
) -> dict:
    interp_code, interp_display = _interpret(fixed_value, obs.low_threshold, obs.high_threshold)
    d = _build(patient_id, encounter_id, practitioner_id, effective_datetime, obs,
               round(fixed_value, obs.decimal_places), interp_code, interp_display)
    if sr_id:
        d["based_on_service_request_id"] = sr_id
    return d


def _make_weight(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    obs: ObservationDef,
    obs_baseline: dict | None,
    sr_id: str | None = None,
) -> tuple[dict, float]:
    """Use stable baseline weight with small per-encounter jitter."""
    baseline_weight = obs_baseline.get("weight_kg") if obs_baseline else None
    if baseline_weight is not None:
        jitter = random.uniform(-_WEIGHT_JITTER_KG, _WEIGHT_JITTER_KG)
        weight = round(max(30.0, baseline_weight + jitter), obs.decimal_places)
    else:
        lo, hi = obs.normal_range
        weight = round(random.triangular(lo, hi, (lo + hi) / 2), obs.decimal_places)

    interp_code, interp_display = _interpret(weight, obs.low_threshold, obs.high_threshold)
    d = _build(patient_id, encounter_id, practitioner_id, effective_datetime, obs, weight,
               interp_code, interp_display)
    if sr_id:
        d["based_on_service_request_id"] = sr_id
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
    d: dict = {
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
        "ref_range_low": obs.normal_range[0],
        "ref_range_high": obs.normal_range[1],
        "ref_range_unit": obs.unit,
        "ref_range_ucum": obs.ucum_code,
    }
    if obs.category_code == "survey":
        d["value_type"] = "integer"
    return d


def _interpret(value: float, low: float | None, high: float | None) -> tuple[str, str]:
    if low is not None and value < low:
        return ("L", "Low")
    if high is not None and value > high:
        return ("H", "High")
    return ("", "")

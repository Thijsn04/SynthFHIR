"""Condition generator.

Generates age-appropriate conditions per patient using an epidemiologically-grounded
comorbidity graph instead of a flat 40% random coin flip. The number of conditions
is drawn from an age-stratified distribution reflecting real US ambulatory burden.

When a condition_filter is supplied, that condition is always the primary diagnosis;
additional comorbidities are selected using the weighted adjacency matrix.

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

# Epidemiologically-grounded comorbidity graph.
# P(B | A is present) derived from clinical literature (see ROADMAP.md Domain 1).
# Only includes conditions in the CONDITIONS catalog.
_COMORBIDITY_GRAPH: dict[str, list[tuple[str, float]]] = {
    "type2_diabetes": [
        ("hypertension", 0.70),
        ("hyperlipidemia", 0.58),
        ("obesity", 0.55),
        ("ckd", 0.30),
        ("depression", 0.25),
        ("coronary_artery_disease", 0.20),
        ("sleep_apnea", 0.15),
        ("atrial_fibrillation", 0.10),
        ("hypothyroidism", 0.10),
        ("gout", 0.08),
        ("anxiety_disorder", 0.15),
        ("heart_failure", 0.10),
        ("peripheral_artery_disease", 0.08),
    ],
    "hypertension": [
        ("hyperlipidemia", 0.55),
        ("type2_diabetes", 0.28),
        ("ckd", 0.40),
        ("obesity", 0.40),
        ("coronary_artery_disease", 0.25),
        ("atrial_fibrillation", 0.20),
        ("depression", 0.20),
        ("sleep_apnea", 0.15),
        ("heart_failure", 0.15),
        ("peripheral_artery_disease", 0.10),
        ("ischemic_stroke", 0.08),
        ("gout", 0.08),
    ],
    "ckd": [
        ("hypertension", 0.80),
        ("type2_diabetes", 0.44),
        ("hyperlipidemia", 0.50),
        ("anemia", 0.35),
        ("depression", 0.25),
        ("coronary_artery_disease", 0.25),
        ("atrial_fibrillation", 0.20),
        ("heart_failure", 0.20),
        ("gout", 0.15),
    ],
    "hyperlipidemia": [
        ("coronary_artery_disease", 0.35),
        ("type2_diabetes", 0.20),
        ("hypertension", 0.50),
        ("obesity", 0.35),
        ("hypothyroidism", 0.08),
        ("atrial_fibrillation", 0.10),
    ],
    "depression": [
        ("anxiety_disorder", 0.50),
        ("type2_diabetes", 0.20),
        ("hypertension", 0.20),
        ("obesity", 0.25),
        ("chronic_pain", 0.35),
        ("sleep_apnea", 0.20),
        ("hypothyroidism", 0.12),
        ("migraine", 0.20),
        ("fibromyalgia", 0.25),
        ("ptsd", 0.30),
        ("opioid_use_disorder", 0.10),
        ("coronary_artery_disease", 0.10),
    ],
    "anxiety_disorder": [
        ("depression", 0.45),
        ("migraine", 0.25),
        ("asthma", 0.20),
        ("gerd", 0.20),
        ("chronic_pain", 0.30),
        ("ptsd", 0.25),
        ("sleep_apnea", 0.15),
        ("hypothyroidism", 0.10),
        ("fibromyalgia", 0.20),
        ("ibs", 0.20),
    ],
    "obesity": [
        ("hypertension", 0.55),
        ("type2_diabetes", 0.40),
        ("hyperlipidemia", 0.45),
        ("sleep_apnea", 0.40),
        ("osteoarthritis", 0.35),
        ("depression", 0.25),
        ("gerd", 0.30),
        ("coronary_artery_disease", 0.20),
        ("gout", 0.12),
        ("atrial_fibrillation", 0.10),
    ],
    "copd": [
        ("depression", 0.30),
        ("hypertension", 0.40),
        ("coronary_artery_disease", 0.30),
        ("atrial_fibrillation", 0.20),
        ("pulmonary_hypertension", 0.25),
        ("anxiety_disorder", 0.25),
        ("heart_failure", 0.20),
        ("lung_cancer", 0.10),
        ("sleep_apnea", 0.15),
    ],
    "asthma": [
        ("anxiety_disorder", 0.20),
        ("depression", 0.20),
        ("gerd", 0.25),
        ("obesity", 0.25),
        ("sleep_apnea", 0.20),
    ],
    "atrial_fibrillation": [
        ("hypertension", 0.70),
        ("heart_failure", 0.35),
        ("coronary_artery_disease", 0.35),
        ("hyperlipidemia", 0.45),
        ("type2_diabetes", 0.25),
        ("ckd", 0.25),
        ("sleep_apnea", 0.30),
        ("ischemic_stroke", 0.08),
    ],
    "osteoarthritis": [
        ("obesity", 0.50),
        ("hypertension", 0.40),
        ("type2_diabetes", 0.25),
        ("depression", 0.20),
        ("gout", 0.10),
        ("chronic_pain", 0.40),
    ],
    "coronary_artery_disease": [
        ("hypertension", 0.75),
        ("hyperlipidemia", 0.70),
        ("type2_diabetes", 0.35),
        ("atrial_fibrillation", 0.25),
        ("heart_failure", 0.30),
        ("peripheral_artery_disease", 0.20),
        ("depression", 0.20),
        ("ischemic_stroke", 0.10),
    ],
    "heart_failure": [
        ("hypertension", 0.70),
        ("coronary_artery_disease", 0.60),
        ("atrial_fibrillation", 0.45),
        ("type2_diabetes", 0.35),
        ("ckd", 0.40),
        ("hyperlipidemia", 0.45),
        ("sleep_apnea", 0.25),
        ("depression", 0.20),
        ("anemia", 0.20),
    ],
    "rheumatoid_arthritis": [
        ("depression", 0.30),
        ("hypertension", 0.30),
        ("fibromyalgia", 0.20),
        ("anemia", 0.25),
        ("chronic_pain", 0.40),
        ("osteoarthritis", 0.25),
    ],
    "lupus": [
        ("depression", 0.35),
        ("anxiety_disorder", 0.25),
        ("hypertension", 0.40),
        ("ckd", 0.30),
        ("hypothyroidism", 0.15),
        ("fibromyalgia", 0.20),
        ("anemia", 0.40),
    ],
    "hypothyroidism": [
        ("depression", 0.30),
        ("obesity", 0.35),
        ("hypertension", 0.25),
        ("hyperlipidemia", 0.35),
        ("type2_diabetes", 0.20),
        ("anemia", 0.15),
        ("fibromyalgia", 0.15),
    ],
    "sleep_apnea": [
        ("obesity", 0.70),
        ("hypertension", 0.55),
        ("type2_diabetes", 0.30),
        ("atrial_fibrillation", 0.25),
        ("depression", 0.20),
        ("coronary_artery_disease", 0.20),
        ("heart_failure", 0.15),
        ("gerd", 0.25),
    ],
    "migraine": [
        ("depression", 0.30),
        ("anxiety_disorder", 0.35),
        ("sleep_apnea", 0.15),
        ("epilepsy", 0.12),
        ("ptsd", 0.15),
    ],
    "chronic_pain": [
        ("depression", 0.40),
        ("anxiety_disorder", 0.35),
        ("fibromyalgia", 0.30),
        ("opioid_use_disorder", 0.12),
        ("sleep_apnea", 0.15),
        ("osteoarthritis", 0.35),
    ],
    "type1_diabetes": [
        ("hypothyroidism", 0.25),
        ("ckd", 0.20),
        ("hypertension", 0.40),
        ("depression", 0.25),
        ("hyperlipidemia", 0.35),
        ("celiac_disease", 0.05),
    ],
    "gout": [
        ("hypertension", 0.55),
        ("ckd", 0.30),
        ("type2_diabetes", 0.25),
        ("obesity", 0.40),
        ("hyperlipidemia", 0.40),
        ("coronary_artery_disease", 0.20),
    ],
    "hiv": [
        ("depression", 0.40),
        ("hypertension", 0.25),
        ("hyperlipidemia", 0.35),
        ("opioid_use_disorder", 0.15),
        ("anxiety_disorder", 0.30),
        ("hepatitis_c", 0.20),
    ],
    "hepatitis_c": [
        ("depression", 0.35),
        ("opioid_use_disorder", 0.40),
        ("hiv", 0.10),
        ("hypertension", 0.20),
        ("type2_diabetes", 0.20),
    ],
    "ptsd": [
        ("depression", 0.50),
        ("anxiety_disorder", 0.50),
        ("opioid_use_disorder", 0.20),
        ("chronic_pain", 0.25),
        ("sleep_apnea", 0.20),
        ("migraine", 0.15),
    ],
    "fibromyalgia": [
        ("depression", 0.40),
        ("anxiety_disorder", 0.35),
        ("chronic_pain", 0.50),
        ("sleep_apnea", 0.25),
        ("ibs", 0.30),
        ("migraine", 0.25),
        ("hypothyroidism", 0.15),
    ],
    "crohns_disease": [
        ("depression", 0.30),
        ("anxiety_disorder", 0.25),
        ("anemia", 0.35),
        ("rheumatoid_arthritis", 0.08),
    ],
    "opioid_use_disorder": [
        ("depression", 0.45),
        ("anxiety_disorder", 0.35),
        ("hepatitis_c", 0.25),
        ("chronic_pain", 0.40),
        ("ptsd", 0.30),
        ("hiv", 0.08),
    ],
    "anemia": [
        ("ckd", 0.30),
        ("heart_failure", 0.20),
        ("depression", 0.20),
        ("hypothyroidism", 0.15),
        ("crohns_disease", 0.10),
    ],
    "peripheral_artery_disease": [
        ("coronary_artery_disease", 0.50),
        ("hypertension", 0.60),
        ("type2_diabetes", 0.40),
        ("hyperlipidemia", 0.55),
        ("ischemic_stroke", 0.15),
    ],
    "pulmonary_hypertension": [
        ("copd", 0.40),
        ("heart_failure", 0.35),
        ("atrial_fibrillation", 0.20),
        ("sleep_apnea", 0.25),
    ],
}

# Baseline comorbidity probability for condition pairs not in the graph
_BASELINE_COMORBIDITY_P = 0.05

# Age-stratified number-of-conditions distribution: (weights for [1, 2, 3, 4, 5])
# Derived from RQ3 findings (ROADMAP.md Domain 1).
_N_CONDITIONS_BY_AGE: list[tuple[tuple[int, int], list[int]]] = [
    ((0,   17),  [80, 17, 2, 1, 0]),   # children: almost always 0-1 chronic conditions
    ((18,  44),  [50, 30, 14, 5, 1]),   # young adults
    ((45,  64),  [25, 35, 25, 12, 3]),  # middle-aged
    ((65,  79),  [10, 25, 35, 22, 8]),  # older adults
    ((80, 200),  [5,  15, 30, 30, 20]), # elderly: heavy multimorbidity burden
]


def _draw_condition_count(age: int) -> int:
    for (lo, hi), weights in _N_CONDITIONS_BY_AGE:
        if lo <= age <= hi:
            return random.choices([1, 2, 3, 4, 5], weights=weights, k=1)[0]
    return 1


def _comorbidity_weight(primary_keys: list[str], candidate_key: str) -> float:
    """Return the highest conditional probability of candidate given any primary condition."""
    best = _BASELINE_COMORBIDITY_P
    for pk in primary_keys:
        for (ck, prob) in _COMORBIDITY_GRAPH.get(pk, []):
            if ck == candidate_key:
                best = max(best, prob)
    return best


def generate_conditions_for_patient(
    patient_id: str,
    practitioner_id: str,
    patient_age: int,
    condition_filter: str | None = None,
) -> list[dict]:
    """Generate age-appropriate conditions using the comorbidity graph.

    If condition_filter is given, that condition is always the primary diagnosis.
    Additional comorbidities are drawn using weighted conditional probabilities
    from the epidemiological adjacency matrix. The count is age-stratified.
    Raises ValueError if the filter matches no known condition.
    """
    eligible = conditions_for_age(patient_age)
    if not eligible:
        eligible = sorted(CONDITIONS, key=lambda c: c.typical_age_min)[:3]

    eligible_keys = {c.key for c in eligible}
    eligible_by_key = {c.key: c for c in eligible}

    selected: list[ConditionDef] = []

    if condition_filter:
        primary = find_condition(condition_filter)
        if primary is None:
            raise ValueError(f"Unknown condition: '{condition_filter}'")
        selected.append(primary)
    else:
        selected.append(random.choice(eligible))

    n_target = _draw_condition_count(patient_age)

    # Iteratively add comorbidities using the graph weights
    while len(selected) < n_target:
        selected_keys = [c.key for c in selected]
        remaining = [c for c in eligible if c.key not in selected_keys]
        if not remaining:
            break

        weights = [_comorbidity_weight(selected_keys, c.key) for c in remaining]
        # Normalise to probabilities and decide per-candidate independently
        # to avoid always filling up to n_target
        added = False
        for cond, w in zip(remaining, weights):
            if cond.key not in eligible_keys:
                continue
            if random.random() < w:
                selected.append(eligible_by_key.get(cond.key, cond))
                added = True
                if len(selected) >= n_target:
                    break
        if not added:
            break  # no further comorbidities materialized this round

    return [_make_condition(patient_id, practitioner_id, cond) for cond in selected]


def _make_condition(patient_id: str, practitioner_id: str, cond: ConditionDef) -> dict:
    status = random.choices(
        [s[0] for s in _CLINICAL_STATUS_WEIGHTS],
        weights=[s[1] for s in _CLINICAL_STATUS_WEIGHTS],
        k=1,
    )[0]
    cat_code, cat_display = random.choice(_CATEGORY_CODES)

    onset = date.today() - timedelta(days=random.randint(30, 3650))
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
        "condition_key": cond.key,
    }

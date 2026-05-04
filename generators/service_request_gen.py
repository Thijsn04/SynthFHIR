"""ServiceRequest generator.

Generates lab/imaging/referral orders linked to an encounter. Each active
condition contributes 1 condition-appropriate order. A general health
maintenance order is always included.

Output keys: id, patient_id, encounter_id, practitioner_id, status, intent,
snomed_code, display, category_code, category_display, authored_on,
priority, reason_snomed, reason_display.
"""
import random
from datetime import date, timedelta

from generators._rng import new_uuid

_SNOMED_TO_KEY = {
    "44054006":  "type2_diabetes",
    "38341003":  "hypertension",
    "55822004":  "hyperlipidemia",
    "49436004":  "atrial_fibrillation",
    "195967001": "asthma",
    "709044004": "ckd",
    "13645005":  "copd",
    "35489007":  "depression",
    "396275006": "osteoarthritis",
    "414916001": "obesity",
}

# condition_key → plausible lab/imaging/referral orders
# (snomed_code, display, category_code, category_display)
_ORDERS_BY_CONDITION: dict[str, list[tuple[str, str, str, str]]] = {
    "type2_diabetes": [
        ("104177005", "Blood glucose level",               "108252007", "Laboratory procedure"),
        ("43396009",  "Hemoglobin A1c measurement",        "108252007", "Laboratory procedure"),
        ("306206005", "Referral to ophthalmology service", "3457005",   "Patient referral"),
    ],
    "hypertension": [
        ("104177005", "Blood pressure monitoring",         "108252007", "Laboratory procedure"),
        ("252076005", "12-lead ECG",                       "363679005", "Imaging"),
        ("306206005", "Referral to cardiology service",    "3457005",   "Patient referral"),
    ],
    "hyperlipidemia": [
        ("104567005", "Lipid panel",                       "108252007", "Laboratory procedure"),
        ("306206005", "Referral to nutrition service",     "3457005",   "Patient referral"),
    ],
    "atrial_fibrillation": [
        ("252076005", "Electrocardiogram",                 "363679005", "Imaging"),
        ("40701008",  "Echocardiography",                  "363679005", "Imaging"),
        ("306206005", "Referral to cardiology service",    "3457005",   "Patient referral"),
    ],
    "asthma": [
        ("23426006",  "Spirometry",                        "108252007", "Laboratory procedure"),
        ("306206005", "Referral to pulmonology service",   "3457005",   "Patient referral"),
    ],
    "ckd": [
        ("43396009",  "Creatinine measurement",            "108252007", "Laboratory procedure"),
        ("252416005", "Renal ultrasound",                  "363679005", "Imaging"),
        ("306206005", "Referral to nephrology service",    "3457005",   "Patient referral"),
    ],
    "copd": [
        ("23426006",  "Spirometry",                        "108252007", "Laboratory procedure"),
        ("306206005", "Referral to pulmonology service",   "3457005",   "Patient referral"),
    ],
    "depression": [
        ("410604004", "Depression screening",              "108252007", "Laboratory procedure"),
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral"),
    ],
    "osteoarthritis": [
        ("312241001", "X-ray joint",                       "363679005", "Imaging"),
        ("306206005", "Referral to orthopedics service",   "3457005",   "Patient referral"),
    ],
    "obesity": [
        ("281686009", "Physical activity assessment",      "108252007", "Laboratory procedure"),
        ("306206005", "Referral to nutrition service",     "3457005",   "Patient referral"),
    ],
}

_GENERAL_ORDER = ("310249009", "Complete blood count", "108252007", "Laboratory procedure")
_PRIORITIES = [("routine", 0.7), ("urgent", 0.2), ("asap", 0.1)]


def generate_service_requests_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    conditions: list[dict],
    authored_on: str | None = None,
) -> list[dict]:
    """Return 1–3 ServiceRequest records for the given encounter."""
    if authored_on is None:
        days_ago = random.randint(0, 30)
        authored_on = (date.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    # Always include the general CBC order
    selected: list[tuple[str, str, str, str]] = [_GENERAL_ORDER]

    for cond in conditions:
        key = _SNOMED_TO_KEY.get(cond.get("snomed_code", ""))
        if not key:
            continue
        pool = _ORDERS_BY_CONDITION.get(key, [])
        if pool:
            selected.append(random.choice(pool))

    # Deduplicate by SNOMED code
    seen: set[str] = set()
    unique: list[tuple[str, str, str, str]] = []
    for item in selected:
        if item[0] not in seen:
            seen.add(item[0])
            unique.append(item)

    priority = random.choices(
        [p[0] for p in _PRIORITIES],
        weights=[p[1] for p in _PRIORITIES],
        k=1,
    )[0]

    results = []
    for snomed_code, display, cat_code, cat_display in unique:
        # Pick a condition to use as reasonCode (if any)
        reason = next(
            (c for c in conditions if c.get("clinical_status") == "active"),
            None,
        )
        results.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "practitioner_id": practitioner_id,
            "status": "active",
            "intent": "order",
            "snomed_code": snomed_code,
            "display": display,
            "category_code": cat_code,
            "category_display": cat_display,
            "authored_on": authored_on,
            "priority": priority,
            "reason_snomed": reason["snomed_code"] if reason else None,
            "reason_display": reason["display"] if reason else None,
        })

    return results

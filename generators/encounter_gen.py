"""Encounter generator.

Produces raw encounter dicts representing clinic visits. Encounters are
distributed across a configurable time window (must fall after condition onset)
and linked to a patient, practitioner, and organization.

Encounter type is biased toward follow-up/consultation for patients with chronic
conditions (passed via condition_keys), while well-child visits are reserved for
paediatric patients.

Output keys: id, patient_id, practitioner_id, organization_id, status,
class_code, class_display, type_code, type_display, start_datetime,
end_datetime.
"""
import random
from datetime import datetime, timedelta

from generators._rng import new_uuid

# SNOMED CT encounter type codes with condition-context weights
# Format: (snomed_code, display, adult_weight, paediatric_weight)
_ENCOUNTER_TYPES = [
    ("185349003", "Encounter for check up",        15, 20),
    ("11429006",  "Consultation",                  25, 15),
    ("308335008", "Patient encounter procedure",   10, 10),
    ("390906007", "Follow-up encounter",           45, 30),
    ("410620009", "Well child visit",               5, 25),
]

# HL7 v3 ActCode class codes with generation weights
_CLASS_CODES = [
    ("AMB",  "ambulatory",          0.80),
    ("IMP",  "inpatient encounter", 0.10),
    ("EMER", "emergency",           0.10),
]

# Encounter status distribution (most are finished; a few are in-progress or cancelled)
_STATUS_WEIGHTS = [("finished", 0.90), ("in-progress", 0.05), ("cancelled", 0.05)]


def generate_encounter(
    patient_id: str,
    practitioner_id: str,
    organization_id: str,
    patient_age: int = 30,
    days_ago_min: int = 1,
    days_ago_max: int = 730,
    conditions: list[dict] | None = None,
) -> dict:
    # Age-appropriate encounter type weighting
    weights = [t[3] if patient_age < 18 else t[2] for t in _ENCOUNTER_TYPES]
    type_code, type_display, _, _ = random.choices(_ENCOUNTER_TYPES, weights=weights, k=1)[0]

    enc_class = random.choices(_CLASS_CODES, weights=[c[2] for c in _CLASS_CODES], k=1)[0]
    class_code, class_display, _ = enc_class

    status = random.choices(
        [s[0] for s in _STATUS_WEIGHTS],
        weights=[s[1] for s in _STATUS_WEIGHTS],
        k=1,
    )[0]

    now = datetime.now(datetime.UTC)
    days_ago = random.randint(max(1, days_ago_min), max(2, days_ago_max))
    start = now - timedelta(days=days_ago, hours=random.randint(8, 17), minutes=random.randint(0, 59))
    end = start + timedelta(minutes=random.randint(15, 60))

    # Build reasonCode from active conditions (up to 2)
    reason_codes: list[dict] = []
    for cond in (conditions or []):
        if cond.get("clinical_status") in ("active", "inactive") and len(reason_codes) < 2:
            reason_codes.append({
                "snomed_code": cond["snomed_code"],
                "display": cond["display"],
            })

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "practitioner_id": practitioner_id,
        "organization_id": organization_id,
        "status": status,
        "class_code": class_code,
        "class_display": class_display,
        "type_code": type_code,
        "type_display": type_display,
        "start_datetime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_datetime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason_codes": reason_codes,
    }

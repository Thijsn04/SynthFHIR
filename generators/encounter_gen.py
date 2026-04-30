"""Encounter generator.

Produces raw encounter dicts representing clinic visits. Encounters are
randomly distributed across a configurable time window and linked to a
patient, practitioner, and organization.
Output keys: id, patient_id, practitioner_id, organization_id, status,
class_code, class_display, type_code, type_display, start_datetime,
end_datetime.
"""
import random
import uuid
from datetime import datetime, timedelta, timezone

# SNOMED CT encounter type codes
_ENCOUNTER_TYPES = [
    ("185349003", "Encounter for check up"),
    ("11429006",  "Consultation"),
    ("308335008", "Patient encounter procedure"),
    ("390906007", "Follow-up encounter"),
    ("410620009", "Well child visit"),
]

# HL7 v3 ActCode class codes with generation weights
_CLASS_CODES = [
    ("AMB",  "ambulatory",         0.80),
    ("IMP",  "inpatient encounter", 0.10),
    ("EMER", "emergency",           0.10),
]


def generate_encounter(
    patient_id: str,
    practitioner_id: str,
    organization_id: str,
    days_ago_min: int = 1,
    days_ago_max: int = 730,
) -> dict:
    type_code, type_display = random.choice(_ENCOUNTER_TYPES)
    enc_class = random.choices(_CLASS_CODES, weights=[c[2] for c in _CLASS_CODES], k=1)[0]
    class_code, class_display, _ = enc_class

    now = datetime.now(timezone.utc)
    start = now - timedelta(
        days=random.randint(days_ago_min, days_ago_max),
        hours=random.randint(8, 17),
        minutes=random.randint(0, 59),
    )
    end = start + timedelta(minutes=random.randint(15, 60))

    return {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "practitioner_id": practitioner_id,
        "organization_id": organization_id,
        "status": "finished",
        "class_code": class_code,
        "class_display": class_display,
        "type_code": type_code,
        "type_display": type_display,
        "start_datetime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_datetime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

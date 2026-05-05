"""Appointment generator.

Produces raw Appointment dicts for each clinic visit. Every Appointment is
linked to a fulfilling Encounter — the appointment precedes the encounter
start by 0–2 days (same-day for outpatient, short lead for referrals).

Output keys: id, patient_id, practitioner_id, organization_id, location_id,
encounter_id, status, service_type_code, service_type_display,
appointment_type_code, appointment_type_display, start, end,
reason_snomed, reason_display.
"""
import random
from datetime import datetime, timedelta

from generators._rng import new_uuid

_SERVICE_TYPES = [
    ("394814009", "General practice",   0.45),
    ("394802001", "General medicine",   0.20),
    ("394579002", "Cardiology",         0.10),
    ("310114002", "Nephrology service", 0.05),
    ("394618009", "Hospital medicine",  0.10),
    ("408443003", "General medical practice", 0.10),
]

_APPOINTMENT_TYPES = [
    ("ROUTINE",  "Routine appointment",                  0.70),
    ("FOLLOWUP", "A follow up visit",                    0.20),
    ("WALKIN",   "A previously scheduled walk-in visit", 0.10),
]


def generate_appointment(
    encounter: dict,
    patient_id: str,
    practitioner_id: str,
    organization_id: str,
    location_id: str | None = None,
) -> dict:
    """Generate an Appointment that pre-dates the given Encounter."""
    start_dt = datetime.fromisoformat(encounter["start_datetime"].replace("Z", "+00:00"))
    # Appointment scheduled same day (outpatient) or up to 2 days before (referral)
    appt_start = start_dt - timedelta(days=random.randint(0, 2), hours=random.randint(0, 1))
    appt_end = appt_start + timedelta(minutes=random.randint(20, 60))

    svc = random.choices(_SERVICE_TYPES, weights=[s[2] for s in _SERVICE_TYPES], k=1)[0]
    appt_type = random.choices(_APPOINTMENT_TYPES, weights=[t[2] for t in _APPOINTMENT_TYPES], k=1)[0]

    reason_codes = encounter.get("reason_codes", [])
    reason = reason_codes[0] if reason_codes else None

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "practitioner_id": practitioner_id,
        "organization_id": organization_id,
        "location_id": location_id,
        "encounter_id": encounter["id"],
        "status": "fulfilled",
        "service_type_code": svc[0],
        "service_type_display": svc[1],
        "appointment_type_code": appt_type[0],
        "appointment_type_display": appt_type[1],
        "start": appt_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": appt_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason_snomed": reason["snomed_code"] if reason else None,
        "reason_display": reason["display"] if reason else None,
    }

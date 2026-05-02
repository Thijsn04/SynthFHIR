"""Immunization generator.

Produces age-appropriate immunization records for a patient based on the CDC
CVX vaccine catalog in data/immunizations.py. Each eligible vaccine is included
with a probability equal to its `prevalence` field, simulating realistic
vaccination coverage rates.

Output keys: id, patient_id, practitioner_id, cvx_code, display, status,
occurrence_date, lot_number.
"""
import random
from datetime import date, timedelta

from data.immunizations import IMMUNIZATIONS
from generators._rng import fake, new_uuid


def generate_immunizations_for_patient(
    patient_id: str,
    practitioner_id: str,
    patient_age: int,
) -> list[dict]:
    """Return immunization records for all age-eligible vaccines the patient likely received."""
    results: list[dict] = []

    for imm in IMMUNIZATIONS:
        if not (imm.min_age <= patient_age <= imm.max_age):
            continue
        if random.random() > imm.prevalence:
            continue

        # Administration date: somewhere in the past, age-appropriate
        max_days_ago = min(patient_age * 365, 10 * 365)
        days_ago = random.randint(30, max(31, max_days_ago))
        occurrence = (date.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        results.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "practitioner_id": practitioner_id,
            "cvx_code": imm.cvx_code,
            "display": imm.display,
            "status": "completed",
            "occurrence_date": occurrence,
            "lot_number": fake.bothify("LOT-??####").upper(),
        })

    return results

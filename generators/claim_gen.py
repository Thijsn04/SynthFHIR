"""Claim generator.

One professional Claim per encounter, linking the patient, their Coverage, and
the billing organization, with a single service-line item.

Output keys: id, patient_id, encounter_id, organization_id, practitioner_id,
coverage_id, created, item_code, item_display, amount.
"""
import random

from generators._rng import new_uuid

# A few common CPT-style professional service lines with rough charge amounts.
_SERVICE_LINES = [
    ("99213", "Office visit, established patient, low complexity", 120, 220),
    ("99214", "Office visit, established patient, moderate complexity", 180, 320),
    ("99203", "Office visit, new patient, low complexity", 150, 260),
    ("99215", "Office visit, established patient, high complexity", 250, 450),
]


def generate_claims_for_encounters(
    encounters: list[dict], coverage_by_patient: dict[str, str]
) -> list[dict]:
    """One Claim per encounter that has a linked Coverage."""
    results: list[dict] = []
    for enc in encounters:
        coverage_id = coverage_by_patient.get(enc["patient_id"])
        if not coverage_id:
            continue
        code, display, low, high = random.choice(_SERVICE_LINES)
        results.append(
            {
                "id": new_uuid(),
                "patient_id": enc["patient_id"],
                "encounter_id": enc["id"],
                "organization_id": enc.get("organization_id", ""),
                "practitioner_id": enc.get("practitioner_id", ""),
                "coverage_id": coverage_id,
                "created": enc.get("start_datetime", "")[:10],
                "item_code": code,
                "item_display": display,
                "amount": round(random.uniform(low, high), 2),
            }
        )
    return results

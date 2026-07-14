"""Composition generator.

A clinical document Composition per patient, of type "Summary of episode note",
with a problem-list section referencing the patient's conditions. This is the
backbone of a FHIR document.

Output keys: id, patient_id, encounter_id, author_id, organization_id, date,
title, condition_ids.
"""
from generators._rng import new_uuid


def generate_composition_for_patient(
    patient_id: str,
    encounter_id: str,
    author_id: str,
    organization_id: str,
    date: str,
    conditions: list[dict],
) -> list[dict]:
    """Generate one summary Composition referencing the patient's conditions."""
    return [
        {
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "author_id": author_id,
            "organization_id": organization_id,
            "date": date,
            "title": "Summary of Care Document",
            "condition_ids": [c["id"] for c in conditions],
        }
    ]

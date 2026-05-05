"""List generator.

Produces FHIR List resources — problem list, medication list, and allergy list —
aggregating resource IDs already generated for a patient.

Output keys: id, patient_id, title, code, code_display, status, mode,
entry_resource_type, entry_ids.
"""
from generators._rng import new_uuid


def generate_lists_for_patient(
    patient_id: str,
    conditions: list[dict],
    medications: list[dict],
    allergies: list[dict],
) -> list[dict]:
    """Return up to three List resources: problem list, medication list, allergy list."""
    lists: list[dict] = []

    if conditions:
        lists.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "title": "Problem List",
            "code": "11450-4",
            "code_display": "Problem list - Reported",
            "status": "current",
            "mode": "working",
            "entry_resource_type": "Condition",
            "entry_ids": [c["id"] for c in conditions],
        })

    if medications:
        lists.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "title": "Current Medications",
            "code": "10160-0",
            "code_display": "History of Medication use Narrative",
            "status": "current",
            "mode": "working",
            "entry_resource_type": "MedicationRequest",
            "entry_ids": [m["id"] for m in medications],
        })

    if allergies:
        lists.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "title": "Allergy List",
            "code": "48765-2",
            "code_display": "Allergies and adverse reactions Document",
            "status": "current",
            "mode": "working",
            "entry_resource_type": "AllergyIntolerance",
            "entry_ids": [a["id"] for a in allergies],
        })

    return lists

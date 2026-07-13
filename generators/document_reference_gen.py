"""DocumentReference generator.

Produces one clinical note per encounter. US Core requires DocumentReference for
clinical notes, and it is one of the most common resources in real datasets. The
note text is a short synthesized summary of the encounter's active conditions.

Output keys: id, patient_id, encounter_id, practitioner_id, organization_id,
type_code, type_display, date, note_text.
"""
import random

from generators._rng import new_uuid

# LOINC document type codes for common clinical notes.
_NOTE_TYPES = [
    ("11506-3", "Progress note"),
    ("34133-9", "Summarization of episode note"),
    ("34117-2", "History and physical note"),
    ("11488-4", "Consult note"),
]


def generate_document_reference_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    organization_id: str,
    effective_datetime: str,
    conditions: list[dict],
) -> dict:
    """Generate a single clinical-note DocumentReference for an encounter."""
    type_code, type_display = random.choice(_NOTE_TYPES)

    active = [c["display"] for c in conditions if c.get("clinical_status") == "active"]
    if active:
        assessment = ", ".join(active[:4])
        note_text = (
            f"{type_display}. Chief concern reviewed. Assessment: {assessment}. "
            "Plan: continue current management, reinforce adherence, and follow up as scheduled."
        )
    else:
        note_text = (
            f"{type_display}. Routine visit with no active problems documented. "
            "Plan: health maintenance and age-appropriate screening."
        )

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "practitioner_id": practitioner_id,
        "organization_id": organization_id,
        "type_code": type_code,
        "type_display": type_display,
        "date": effective_datetime,
        "note_text": note_text,
    }

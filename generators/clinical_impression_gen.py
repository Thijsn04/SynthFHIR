"""ClinicalImpression generator.

A clinician's summary assessment at an encounter, referencing the patient's
active problems as findings.

Output keys: id, patient_id, encounter_id, effective_datetime, summary,
finding_ids.
"""
from generators._rng import new_uuid


def generate_clinical_impression_for_patient(
    patient_id: str, encounter_id: str, effective_datetime: str, conditions: list[dict]
) -> list[dict]:
    """Generate one ClinicalImpression summarizing active conditions."""
    active = [c for c in conditions if c.get("clinical_status") == "active"]
    if not active:
        return []
    names = ", ".join(c["display"] for c in active[:5])
    return [
        {
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "effective_datetime": effective_datetime,
            "summary": f"Active problems reviewed: {names}. Stable on current management.",
            "finding_ids": [c["id"] for c in active],
        }
    ]

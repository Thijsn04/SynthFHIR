"""MedicationStatement generator.

A MedicationStatement records that a patient is (or was) taking a medication, as
opposed to a prescription order. One is produced per medication the patient has
been prescribed, derived from the corresponding MedicationRequest.

Output keys: id, patient_id, medication_request_id, encounter_id, rxnorm_code,
display, status, effective_start.
"""
from generators._rng import new_uuid


def generate_statements_for_medications(medications: list[dict]) -> list[dict]:
    """One MedicationStatement per MedicationRequest."""
    results: list[dict] = []
    for med in medications:
        active = med.get("status") == "active"
        results.append(
            {
                "id": new_uuid(),
                "patient_id": med["patient_id"],
                "medication_request_id": med["id"],
                "encounter_id": med.get("encounter_id", ""),
                "rxnorm_code": med["rxnorm_code"],
                "display": med["display"],
                "status": "active" if active else "completed",
                "effective_start": med.get("authored_on", ""),
            }
        )
    return results

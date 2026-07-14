"""MedicationAdministration generator.

Records that a dose of a medication was administered, typically during an
inpatient or clinic encounter. Produced for a share of active medications.

Output keys: id, patient_id, medication_request_id, encounter_id, practitioner_id,
rxnorm_code, display, effective_datetime, dose_value, dose_unit.
"""
import random

from generators._rng import new_uuid

_ADMINISTERED_PROBABILITY = 0.4


def generate_administrations_for_medications(medications: list[dict]) -> list[dict]:
    """Generate MedicationAdministration records for a share of active medications."""
    results: list[dict] = []
    for med in medications:
        if med.get("status") != "active":
            continue
        if random.random() > _ADMINISTERED_PROBABILITY:
            continue
        results.append(
            {
                "id": new_uuid(),
                "patient_id": med["patient_id"],
                "medication_request_id": med["id"],
                "encounter_id": med.get("encounter_id", ""),
                "practitioner_id": med.get("practitioner_id", ""),
                "rxnorm_code": med["rxnorm_code"],
                "display": med["display"],
                "effective_datetime": (med.get("authored_on", "") or "") + "T09:00:00Z",
                "dose_value": med.get("dose_value"),
                "dose_unit": med.get("dose_unit"),
            }
        )
    return results

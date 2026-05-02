"""R5 Immunization resource mapper. Spec: https://hl7.org/fhir/R5/immunization.html

R5 differences from R4:
  1. Profile URL uses 5.0 path segment.
  2. performer.actor is preferred over performer.function for primary source tracking.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Immunization"


def map_immunization(imm: dict) -> dict:
    return {
        "resourceType": "Immunization",
        "id": imm["id"],
        "meta": build_meta(_PROFILE),
        "status": imm["status"],
        "vaccineCode": {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/sid/cvx",
                    "code": imm["cvx_code"],
                    "display": imm["display"],
                }
            ],
            "text": imm["display"],
        },
        "patient": ref("Patient", imm["patient_id"]),
        "occurrenceDateTime": imm["occurrence_date"],
        "primarySource": True,
        "lotNumber": imm["lot_number"],
        "performer": [
            {
                "actor": ref("Practitioner", imm["practitioner_id"]),
            }
        ],
    }

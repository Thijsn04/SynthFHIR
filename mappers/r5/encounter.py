"""R5 Encounter resource mapper. Spec: https://hl7.org/fhir/R5/encounter.html

R5 structural difference from R4:
  Encounter.class changed from a single Coding to an array of CodeableConcept.
  R4:  "class": { "system": "...", "code": "AMB", "display": "..." }
  R5:  "class": [{ "coding": [{ "system": "...", "code": "AMB", "display": "..." }] }]
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Encounter"


def map_encounter(enc: dict) -> dict:
    return {
        "resourceType": "Encounter",
        "id": enc["id"],
        "meta": build_meta(_PROFILE),
        "status": enc["status"],
        # R5: class is now an array of CodeableConcept
        "class": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": enc["class_code"],
                        "display": enc["class_display"],
                    }
                ]
            }
        ],
        "type": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": enc["type_code"],
                        "display": enc["type_display"],
                    }
                ],
                "text": enc["type_display"],
            }
        ],
        "subject": ref("Patient", enc["patient_id"]),
        "participant": [
            {"individual": ref("Practitioner", enc["practitioner_id"])}
        ],
        "period": {
            "start": enc["start_datetime"],
            "end": enc["end_datetime"],
        },
        "serviceProvider": ref("Organization", enc["organization_id"]),
    }

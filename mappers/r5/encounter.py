"""R5 Encounter resource mapper. Spec: https://hl7.org/fhir/R5/encounter.html

R5 structural differences from R4:
  1. Encounter.class changed from a single Coding to an array of CodeableConcept.
     R4:  "class": { "system": "...", "code": "AMB", "display": "..." }
     R5:  "class": [{ "coding": [{ "system": "...", "code": "AMB", "display": "..." }] }]
  2. Encounter.participant.individual renamed to actor.
  3. Encounter.period renamed to actualPeriod.
  4. Status code "finished" (R4) renamed to "completed" (R5).
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Encounter"

# R4 "finished" → R5 "completed"; all other codes are shared
_STATUS_MAP = {"finished": "completed"}


def map_encounter(enc: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "Encounter",
        "id": enc["id"],
        "meta": build_meta(_PROFILE),
        "status": _STATUS_MAP.get(enc["status"], enc["status"]),
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
        # R5: participant.individual renamed to actor
        "participant": [
            {"actor": ref("Practitioner", enc["practitioner_id"])}
        ],
        # R5: period renamed to actualPeriod
        "actualPeriod": {
            "start": enc["start_datetime"],
            "end": enc["end_datetime"],
        },
        "serviceProvider": ref("Organization", enc["organization_id"]),
    }

    # R5: reasonCode replaced by reason[].concept (CodeableReference)
    if enc.get("reason_codes"):
        resource["reason"] = [
            {
                "concept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": rc["snomed_code"],
                            "display": rc["display"],
                        }
                    ],
                    "text": rc["display"],
                }
            }
            for rc in enc["reason_codes"]
        ]

    if enc.get("location_id"):
        resource["location"] = [
            {"location": ref("Location", enc["location_id"]), "status": "completed"}
        ]

    return resource

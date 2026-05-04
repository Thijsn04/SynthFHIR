"""R5 ServiceRequest resource mapper. Spec: https://hl7.org/fhir/R5/servicerequest.html

R5 differences from R4:
  1. Profile URL uses 5.0 path segment.
  2. ServiceRequest.reasonCode replaced by ServiceRequest.reason (CodeableReference).
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/ServiceRequest"


def map_service_request(sr: dict) -> dict:
    resource: dict = {
        "resourceType": "ServiceRequest",
        "id": sr["id"],
        "meta": build_meta(_PROFILE),
        "status": sr["status"],
        "intent": sr["intent"],
        "category": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": sr["category_code"],
                        "display": sr["category_display"],
                    }
                ],
                "text": sr["category_display"],
            }
        ],
        "priority": sr["priority"],
        "code": {
            "concept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": sr["snomed_code"],
                        "display": sr["display"],
                    }
                ],
                "text": sr["display"],
            }
        },
        "subject": ref("Patient", sr["patient_id"]),
        "encounter": ref("Encounter", sr["encounter_id"]),
        "authoredOn": sr["authored_on"],
        "requester": ref("Practitioner", sr["practitioner_id"]),
    }

    # R5: reason is CodeableReference
    if sr.get("reason_snomed"):
        resource["reason"] = [
            {
                "concept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": sr["reason_snomed"],
                            "display": sr["reason_display"],
                        }
                    ],
                    "text": sr["reason_display"],
                }
            }
        ]

    return resource

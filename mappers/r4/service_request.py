"""R4 ServiceRequest resource mapper. Spec: https://hl7.org/fhir/R4/servicerequest.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/ServiceRequest"


def map_service_request(sr: dict, us_core: bool = False) -> dict:
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
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": sr["snomed_code"],
                    "display": sr["display"],
                }
            ],
            "text": sr["display"],
        },
        "subject": ref("Patient", sr["patient_id"]),
        "encounter": ref("Encounter", sr["encounter_id"]),
        "authoredOn": sr["authored_on"],
        "requester": ref("Practitioner", sr["practitioner_id"]),
    }

    if sr.get("reason_snomed"):
        resource["reasonCode"] = [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": sr["reason_snomed"],
                        "display": sr["reason_display"],
                    }
                ],
                "text": sr["reason_display"],
            }
        ]

    return resource

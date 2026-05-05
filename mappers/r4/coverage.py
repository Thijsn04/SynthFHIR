"""R4 Coverage resource mapper. Spec: https://hl7.org/fhir/R4/coverage.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Coverage"


def map_coverage(cov: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Coverage",
        "id": cov["id"],
        "meta": build_meta(_PROFILE),
        "status": cov["status"],
        "type": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": cov["type_code"],
                    "display": cov["type_display"],
                }
            ],
            "text": cov["type_display"],
        },
        "subscriber": ref("Patient", cov["patient_id"]),
        "subscriberId": cov["subscriber_id"],
        "beneficiary": ref("Patient", cov["patient_id"]),
        "relationship": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                    "code": "self",
                    "display": "Self",
                }
            ]
        },
        "period": {
            "start": cov["period_start"],
            "end": cov["period_end"],
        },
        "payor": [
            {
                "display": cov["payer_display"],
                "identifier": {
                    "system": "http://hl7.org/fhir/sid/us-npi",
                    "value": cov["payer_code"],
                },
            }
        ],
        "class": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                            "code": "plan",
                            "display": "Plan",
                        }
                    ]
                },
                "value": cov["class_value"],
                "name": cov["plan_name"],
            }
        ],
    }

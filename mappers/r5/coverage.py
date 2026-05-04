"""R5 Coverage resource mapper. Spec: https://hl7.org/fhir/R5/coverage.html

R5 differences from R4:
  1. Profile URL uses 5.0 path segment.
  2. Coverage.kind added (insurance | self-pay | other).
  3. payor changed from Reference array to insurer (single Reference).
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Coverage"

_KIND_MAP = {
    "Medicare":   "insurance",
    "Medicaid":   "insurance",
    "commercial": "insurance",
}


def map_coverage(cov: dict) -> dict:
    return {
        "resourceType": "Coverage",
        "id": cov["id"],
        "meta": build_meta(_PROFILE),
        "status": cov["status"],
        # R5 new field
        "kind": _KIND_MAP.get(cov["kind"], "insurance"),
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
        "subscriberId": [{"value": cov["subscriber_id"]}],
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
        # R5: payor renamed to insurer (single Reference)
        "insurer": {
            "display": cov["payer_display"],
            "identifier": {
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": cov["payer_code"],
            },
        },
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

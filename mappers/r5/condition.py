"""R5 Condition resource mapper. Spec: https://hl7.org/fhir/R5/condition.html

R5 difference from R4: canonical profile URL only.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Condition"


def map_condition(cond: dict) -> dict:
    return {
        "resourceType": "Condition",
        "id": cond["id"],
        "meta": build_meta(_PROFILE),
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": cond["clinical_status"],
                    "display": cond["clinical_status"].title(),
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": cond["verification_status"],
                    "display": cond["verification_status"].title(),
                }
            ]
        },
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": cond["category_code"],
                        "display": cond["category_display"],
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": cond["snomed_code"],
                    "display": cond["display"],
                },
                {
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": cond["icd10_code"],
                    "display": cond["display"],
                },
            ],
            "text": cond["display"],
        },
        "subject": ref("Patient", cond["patient_id"]),
        "onsetDateTime": cond["onset_date"],
        "recordedDate": cond["recorded_date"],
        "recorder": ref("Practitioner", cond["practitioner_id"]),
    }

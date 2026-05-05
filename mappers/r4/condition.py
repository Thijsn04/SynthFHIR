"""R4 Condition resource mapper. Spec: https://hl7.org/fhir/R4/condition.html

US Core: two profiles depending on category —
  problem-list-item   → us-core-condition-problems-health-concerns
  encounter-diagnosis → us-core-condition-encounter-diagnosis
"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Condition"


def map_condition(cond: dict, us_core: bool = False) -> dict:
    if us_core:
        cat = cond.get("category_code", "problem-list-item")
        if cat == "encounter-diagnosis":
            profile = US_CORE_PROFILES["Condition-encounter-diagnosis"]
        else:
            profile = US_CORE_PROFILES["Condition-problems"]
    else:
        profile = _PROFILE

    return {
        "resourceType": "Condition",
        "id": cond["id"],
        "meta": build_meta(profile),
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
        # Dual-coded: SNOMED CT for clinical meaning + ICD-10-CM for billing
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
        **( {"encounter": ref("Encounter", cond["encounter_id"])} if cond.get("encounter_id") else {} ),
    }

"""R4 Immunization resource mapper. Spec: https://hl7.org/fhir/R4/immunization.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Immunization"


def map_immunization(imm: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "Immunization",
        "id": imm["id"],
        "meta": build_meta(US_CORE_PROFILES["Immunization"] if us_core else _PROFILE),
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

    # US Core Immunization: statusReason required when status != "completed"
    if us_core and imm.get("status") != "completed":
        resource["statusReason"] = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                    "code": "IMMUNE",
                    "display": "Immunity",
                }
            ]
        }

    return resource

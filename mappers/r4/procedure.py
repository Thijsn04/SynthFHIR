"""R4 Procedure resource mapper. Spec: https://hl7.org/fhir/R4/procedure.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Procedure"


def map_procedure(proc: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "Procedure",
        "id": proc["id"],
        "meta": build_meta(US_CORE_PROFILES["Procedure"] if us_core else _PROFILE),
        "status": proc["status"],
        "category": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": proc["category_snomed"],
                    "display": proc["category_display"],
                }
            ],
            "text": proc["category_display"],
        },
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": proc["snomed_code"],
                    "display": proc["display"],
                }
            ],
            "text": proc["display"],
        },
        "subject": ref("Patient", proc["patient_id"]),
        "encounter": ref("Encounter", proc["encounter_id"]),
        "performedDateTime": proc["performed_datetime"],
        "performer": [
            {"actor": ref("Practitioner", proc["practitioner_id"])}
        ],
    }

    if proc.get("body_site_code"):
        resource["bodySite"] = [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": proc["body_site_code"],
                        "display": proc["body_site_display"],
                    }
                ],
                "text": proc["body_site_display"],
            }
        ]

    return resource

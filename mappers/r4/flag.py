"""R4 Flag resource mapper. Spec: https://hl7.org/fhir/R4/flag.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Flag"
_FLAG_CATEGORY = "http://terminology.hl7.org/CodeSystem/flag-category"


def map_flag(flag: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "Flag",
        "id": flag["id"],
        "meta": build_meta(_PROFILE),
        "status": "active",
        "category": [
            {
                "coding": [
                    {"system": _FLAG_CATEGORY, "code": flag["category_code"], "display": flag["category_display"]}
                ]
            }
        ],
        "code": {"text": flag["display"]},
        "subject": ref("Patient", flag["patient_id"]),
    }
    if flag.get("encounter_id"):
        resource["encounter"] = ref("Encounter", flag["encounter_id"])
    return resource

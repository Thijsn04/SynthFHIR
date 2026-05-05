"""R4 List resource mapper. Spec: https://hl7.org/fhir/R4/list.html"""
from mappers._helpers import build_meta, ref, utcnow

_PROFILE = "http://hl7.org/fhir/StructureDefinition/List"


def map_list(lst: dict) -> dict:
    return {
        "resourceType": "List",
        "id": lst["id"],
        "meta": build_meta(_PROFILE),
        "status": lst["status"],
        "mode": lst["mode"],
        "title": lst["title"],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": lst["code"],
                    "display": lst["code_display"],
                }
            ],
            "text": lst["code_display"],
        },
        "subject": ref("Patient", lst["patient_id"]),
        "date": utcnow(),
        "entry": [
            {"item": ref(lst["entry_resource_type"], eid)}
            for eid in lst.get("entry_ids", [])
        ],
    }

"""R5 Composition resource mapper. Spec: https://hl7.org/fhir/R5/composition.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Composition"
_LOINC = "http://loinc.org"


def map_composition(comp: dict, us_core: bool = False) -> dict:
    section = {
        "title": "Problem List",
        "code": {"coding": [{"system": _LOINC, "code": "11450-4", "display": "Problem list"}]},
        "text": {
            "status": "generated",
            "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Active problem list</div>",
        },
    }
    if comp["condition_ids"]:
        section["entry"] = [ref("Condition", cid) for cid in comp["condition_ids"]]

    resource = {
        "resourceType": "Composition",
        "id": comp["id"],
        "meta": build_meta(_PROFILE),
        "status": "final",
        "type": {
            "coding": [{"system": _LOINC, "code": "34133-9", "display": "Summarization of episode note"}]
        },
        "subject": [ref("Patient", comp["patient_id"])],
        "date": comp["date"],
        "author": [ref("Practitioner", comp["author_id"])],
        "title": comp["title"],
        "section": [section],
    }
    if comp.get("encounter_id"):
        resource["encounter"] = ref("Encounter", comp["encounter_id"])
    return resource

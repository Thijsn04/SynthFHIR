"""R4 ClinicalImpression mapper. Spec: https://hl7.org/fhir/R4/clinicalimpression.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/ClinicalImpression"


def map_clinical_impression(ci: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "ClinicalImpression",
        "id": ci["id"],
        "meta": build_meta(_PROFILE),
        "status": "completed",
        "subject": ref("Patient", ci["patient_id"]),
        "date": ci["effective_datetime"],
        "summary": ci["summary"],
        "finding": [{"itemReference": ref("Condition", cid)} for cid in ci["finding_ids"]],
    }
    if ci.get("encounter_id"):
        resource["encounter"] = ref("Encounter", ci["encounter_id"])
    return resource

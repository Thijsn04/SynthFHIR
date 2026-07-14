"""R5 Specimen resource mapper. Spec: https://hl7.org/fhir/R5/specimen.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Specimen"
_SNOMED = "http://snomed.info/sct"


def map_specimen(spec: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "Specimen",
        "id": spec["id"],
        "meta": build_meta(_PROFILE),
        "status": "available",
        "type": {
            "coding": [{"system": _SNOMED, "code": spec["type_code"], "display": spec["type_display"]}],
            "text": spec["type_display"],
        },
        "subject": ref("Patient", spec["patient_id"]),
    }
    if spec.get("collected_datetime"):
        resource["collection"] = {"collectedDateTime": spec["collected_datetime"]}
    return resource

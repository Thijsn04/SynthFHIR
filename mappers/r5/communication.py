"""R5 Communication resource mapper. Spec: https://hl7.org/fhir/R5/communication.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Communication"
_CATEGORY = "http://terminology.hl7.org/CodeSystem/communication-category"


def map_communication(comm: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "Communication",
        "id": comm["id"],
        "meta": build_meta(_PROFILE),
        "status": "completed",
        "category": [
            {"coding": [{"system": _CATEGORY, "code": comm["category_code"], "display": comm["category_display"]}]}
        ],
        "subject": ref("Patient", comm["patient_id"]),
        "sent": comm["sent"],
        "payload": [{"contentString": comm["payload"]}],
    }
    if comm.get("sender_id"):
        resource["sender"] = ref("Practitioner", comm["sender_id"])
    if comm.get("encounter_id"):
        resource["encounter"] = ref("Encounter", comm["encounter_id"])
    return resource

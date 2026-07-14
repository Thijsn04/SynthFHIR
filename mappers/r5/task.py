"""R5 Task resource mapper. Spec: https://hl7.org/fhir/R5/task.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Task"
_TASK_CODE = "http://hl7.org/fhir/CodeSystem/task-code"


def map_task(task: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "Task",
        "id": task["id"],
        "meta": build_meta(_PROFILE),
        "status": task["status"],
        "intent": "order",
        "code": {
            "coding": [{"system": _TASK_CODE, "code": task["code"], "display": task["code"].title()}],
            "text": task["display"],
        },
        "description": task["display"],
        "for": ref("Patient", task["patient_id"]),
        "authoredOn": task["authored_on"],
    }
    if task.get("encounter_id"):
        resource["encounter"] = ref("Encounter", task["encounter_id"])
    if task.get("requester_id"):
        resource["requester"] = ref("Practitioner", task["requester_id"])
    return resource

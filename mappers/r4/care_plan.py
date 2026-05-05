"""R4 CarePlan resource mapper. Spec: https://hl7.org/fhir/R4/careplan.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/CarePlan"


def map_care_plan(cp: dict) -> dict:
    resource: dict = {
        "resourceType": "CarePlan",
        "id": cp["id"],
        "meta": build_meta(_PROFILE),
        "status": cp["status"],
        "intent": cp["intent"],
        "title": cp["title"],
        "description": cp.get("description", ""),
        "subject": ref("Patient", cp["patient_id"]),
        "period": {
            "start": cp["period_start"],
            "end": cp["period_end"],
        },
        "careTeam": [ref("CareTeam", cp["care_team_id"])],
        "addresses": [ref("Condition", cid) for cid in cp.get("condition_ids", [])],
    }

    if cp.get("activities"):
        resource["activity"] = [
            {
                "detail": {
                    "kind": "ServiceRequest",
                    "status": "not-started",
                    "description": act,
                }
            }
            for act in cp["activities"]
        ]

    return resource

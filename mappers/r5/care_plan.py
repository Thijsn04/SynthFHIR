"""R5 CarePlan resource mapper. Spec: https://hl7.org/fhir/R5/careplan.html

R5 is structurally very similar to R4 for CarePlan; only the profile URL differs.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/CarePlan"


def map_care_plan(cp: dict, us_core: bool = False) -> dict:
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
        "addresses": [
            {"reference": ref("Condition", cid)}
            for cid in cp.get("condition_ids", [])
        ],
    }

    if cp.get("activities"):
        resource["activity"] = [
            {
                "plannedActivityDetail": {
                    "kind": "ServiceRequest",
                    "status": "not-started",
                    "description": act,
                }
            }
            for act in cp["activities"]
        ]

    return resource

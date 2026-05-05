"""R4 CarePlan resource mapper. Spec: https://hl7.org/fhir/R4/careplan.html

US Core CarePlan requires:
  - category containing "assess-plan" from http://hl7.org/fhir/us/core/CodeSystem/careplan-category
  - text element (narrative) with status and div
"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/CarePlan"

_US_CORE_CATEGORY = {
    "coding": [
        {
            "system": "http://hl7.org/fhir/us/core/CodeSystem/careplan-category",
            "code": "assess-plan",
            "display": "Assessment and Plan of Treatment",
        }
    ]
}


def map_care_plan(cp: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "CarePlan",
        "id": cp["id"],
        "meta": build_meta(US_CORE_PROFILES["CarePlan"] if us_core else _PROFILE),
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

    # US Core CarePlan: required category and narrative text
    if us_core:
        resource["category"] = [_US_CORE_CATEGORY]
        resource["text"] = {
            "status": "generated",
            "div": (
                f'<div xmlns="http://www.w3.org/1999/xhtml">'
                f"<p><b>{cp['title']}</b></p>"
                f"<p>{cp.get('description', '')}</p>"
                f"</div>"
            ),
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

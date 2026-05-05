"""R4 Goal resource mapper. Spec: https://hl7.org/fhir/R4/goal.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Goal"

_ACHIEVEMENT_CODES: dict[str, tuple[str, str]] = {
    "in-progress": ("in-progress", "In Progress"),
    "improving":   ("improving",   "Improving"),
    "worsening":   ("worsening",   "Worsening"),
    "no-change":   ("no-change",   "No Change"),
    "achieved":    ("achieved",    "Achieved"),
    "not-achieved": ("not-achieved", "Not Achieved"),
}


def map_goal(goal: dict, us_core: bool = False) -> dict:
    ach_code, ach_display = _ACHIEVEMENT_CODES.get(
        goal.get("achievement_status", "in-progress"),
        ("in-progress", "In Progress"),
    )

    resource: dict = {
        "resourceType": "Goal",
        "id": goal["id"],
        "meta": build_meta(US_CORE_PROFILES["Goal"] if us_core else _PROFILE),
        "lifecycleStatus": goal["lifecycle_status"],
        "achievementStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/goal-achievement",
                    "code": ach_code,
                    "display": ach_display,
                }
            ],
            "text": ach_display,
        },
        "description": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": goal["snomed_code"],
                    "display": goal["display"],
                }
            ],
            "text": goal["description"],
        },
        "subject": ref("Patient", goal["patient_id"]),
        "startDate": goal["start_date"],
        "target": [{"dueDate": goal["target_date"]}],
    }

    if goal.get("condition_id"):
        resource["addresses"] = [ref("Condition", goal["condition_id"])]

    return resource

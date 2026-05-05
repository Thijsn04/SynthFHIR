"""CareTeam generator.

Produces a multi-provider care team linked to a patient, practitioners, and
conditions. One CareTeam is generated per patient, naming the primary condition
in the team's title.

Output keys: id, patient_id, practitioner_ids, status, name, condition_ids.
"""
from generators._rng import new_uuid


def generate_care_team(
    patient_id: str,
    practitioner_ids: list[str],
    conditions: list[dict],
) -> dict:
    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "practitioner_ids": list(practitioner_ids),
        "status": "active",
        "name": _care_team_name(conditions),
        "condition_ids": [c["id"] for c in conditions],
    }


def _care_team_name(conditions: list[dict]) -> str:
    if not conditions:
        return "Primary Care Team"
    primary = conditions[0].get("display", "")
    if len(conditions) > 1:
        return f"{primary} & Comorbidity Management Team"
    return f"{primary} Care Team"

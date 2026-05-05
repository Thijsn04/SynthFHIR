"""EpisodeOfCare generator.

Groups all of a patient's Encounters into a single longitudinal episode
spanning from the earliest to the most recent encounter. One episode per
patient, representing their ongoing care relationship with the organization.

Output keys: id, patient_id, organization_id, status, type_code,
type_display, period_start, period_end, condition_ids, encounter_ids.
"""
from generators._rng import new_uuid


def generate_episode_of_care(
    patient_id: str,
    organization_id: str,
    encounters: list[dict],
    conditions: list[dict],
) -> dict:
    """Generate an EpisodeOfCare grouping all encounters for one patient."""
    sorted_encs = sorted(encounters, key=lambda e: e["start_datetime"])
    period_start = sorted_encs[0]["start_datetime"][:10] if sorted_encs else None
    period_end = sorted_encs[-1]["end_datetime"][:10] if sorted_encs else None

    # Link up to 3 active conditions as the episode's diagnosis list
    active_conds = [c for c in conditions if c.get("clinical_status") == "active"]

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "organization_id": organization_id,
        "status": "active",
        "type_code": "394814009",
        "type_display": "General practice",
        "period_start": period_start,
        "period_end": period_end,
        "condition_ids": [c["id"] for c in active_conds[:3]],
        "encounter_ids": [e["id"] for e in sorted_encs],
    }

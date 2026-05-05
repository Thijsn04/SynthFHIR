"""Provenance generator.

Creates one Provenance record per patient, covering the patient's conditions,
encounters, and medications as targets to record which practitioner and
organization generated the clinical data.

Output keys: id, target_ids, recorded, practitioner_id, organization_id,
activity_code, activity_display.
"""
from generators._rng import new_uuid


def generate_provenance(
    target_ids: list[str],
    practitioner_id: str,
    organization_id: str,
    recorded: str,
) -> dict:
    """One Provenance covering a list of target resource IDs."""
    return {
        "id": new_uuid(),
        "target_ids": list(target_ids),
        "recorded": recorded,
        "practitioner_id": practitioner_id,
        "organization_id": organization_id,
        "activity_code": "CREATE",
        "activity_display": "create",
    }

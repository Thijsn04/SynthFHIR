"""Group generator.

A single Group enumerating every patient in the cohort, useful for population
level workflows and bulk data.

Output keys: id, member_ids, quantity.
"""
from generators._rng import new_uuid


def generate_cohort_group(patients: list[dict]) -> list[dict]:
    """One Group whose members are all the cohort's patients."""
    if not patients:
        return []
    return [
        {
            "id": new_uuid(),
            "member_ids": [p["id"] for p in patients],
            "quantity": len(patients),
        }
    ]

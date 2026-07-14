"""Medication resource generator.

Produces standalone Medication resources (one per distinct drug prescribed in the
cohort). US Core allows MedicationRequest to reference a Medication resource
rather than only carrying an inline code. These act as the cohort's drug catalog.

Output keys: id, rxnorm_code, display, dose_form.
"""
from generators._rng import new_uuid


def generate_medications_catalog(medication_requests: list[dict]) -> list[dict]:
    """One Medication resource per distinct RxNorm code across all requests."""
    seen: dict[str, dict] = {}
    for req in medication_requests:
        code = req.get("rxnorm_code")
        if not code or code in seen:
            continue
        seen[code] = {
            "id": new_uuid(),
            "rxnorm_code": code,
            "display": req.get("display", ""),
            "dose_form": req.get("dose_form", ""),
        }
    return list(seen.values())

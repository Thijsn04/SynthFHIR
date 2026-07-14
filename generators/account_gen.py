"""Account generator.

A patient billing account, one per patient, that claims and charges roll up to.

Output keys: id, patient_id, organization_id, name, status.
"""
from generators._rng import new_uuid


def generate_account_for_patient(patient_id: str, organization_id: str, patient_name: str) -> dict:
    """One billing Account per patient."""
    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "organization_id": organization_id,
        "name": f"Billing account for {patient_name}",
        "status": "active",
    }

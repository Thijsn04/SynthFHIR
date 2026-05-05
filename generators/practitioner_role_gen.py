"""PractitionerRole generator.

Links a Practitioner to an Organization with a FHIR role code and inherits the
practitioner's SNOMED specialty. One role is generated per practitioner per
organization.

Output keys: id, practitioner_id, organization_id, role_code, role_display,
specialty_code, specialty_display, active.
"""
from generators._rng import new_uuid


def generate_practitioner_role(practitioner: dict, organization_id: str) -> dict:
    return {
        "id": new_uuid(),
        "practitioner_id": practitioner["id"],
        "organization_id": organization_id,
        "role_code": "doctor",
        "role_display": "Doctor",
        "specialty_code": practitioner["specialty_code"],
        "specialty_display": practitioner["specialty_display"],
        "active": True,
    }

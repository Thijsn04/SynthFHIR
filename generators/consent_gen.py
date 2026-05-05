"""Consent generator.

Produces HIPAA privacy consent records for every patient and, with 40%
probability, an additional research consent.

Output keys: id, patient_id, organization_id, status, scope_code, scope_display,
category_code, category_display, datetime, policy_uri, provision_type.
"""
import random
from datetime import date, timedelta

from generators._rng import new_uuid


def generate_consents_for_patient(
    patient_id: str,
    organization_id: str,
) -> list[dict]:
    """Return 1–2 Consent resources per patient."""
    today = date.today()
    consents: list[dict] = []

    consents.append({
        "id": new_uuid(),
        "patient_id": patient_id,
        "organization_id": organization_id,
        "status": "active",
        "scope_code": "patient-privacy",
        "scope_display": "Privacy Consent",
        "category_code": "59284-0",
        "category_display": "Patient Consent",
        "datetime": (today - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "policy_uri": "http://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/",
        "provision_type": "permit",
    })

    if random.random() < 0.40:
        consents.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "organization_id": organization_id,
            "status": "active",
            "scope_code": "research",
            "scope_display": "Research Consent",
            "category_code": "57016-8",
            "category_display": "Privacy policy acknowledgement Document",
            "datetime": (today - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "policy_uri": "urn:synthfhir:research-consent",
            "provision_type": "permit",
        })

    return consents

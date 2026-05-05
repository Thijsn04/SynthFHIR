"""Location generator.

Produces raw location dicts representing rooms, wards, and buildings within an
organization. Locations share the organization's address by default.

Output keys: id, organization_id, name, type_code, type_display, status, phone,
address_line, city, state, postal_code, country.
"""
import random

from generators._rng import e164_phone, fake, new_uuid

_LOCATION_TYPES = [
    ("wi", "Wing"),
    ("ro", "Room"),
    ("bu", "Building"),
    ("fl", "Floor"),
    ("si", "Site"),
    ("wa", "Ward"),
]

_WARD_NAMES = [
    "Cardiology Unit",
    "Emergency Department",
    "Intensive Care Unit",
    "Medical/Surgical Unit",
    "Outpatient Clinic",
    "Radiology Department",
    "Laboratory Services",
    "Oncology Unit",
    "Neurology Ward",
    "Orthopedic Unit",
    "Pulmonary Medicine",
    "Nephrology Unit",
    "Primary Care Clinic",
    "Mental Health Services",
    "Pediatrics Ward",
]


def generate_location(organization_id: str, address: dict | None = None) -> dict:
    type_code, type_display = random.choice(_LOCATION_TYPES)
    name = random.choice(_WARD_NAMES)
    addr = address or {}

    return {
        "id": new_uuid(),
        "organization_id": organization_id,
        "name": name,
        "type_code": type_code,
        "type_display": type_display,
        "status": "active",
        "phone": e164_phone(),
        "address_line": addr.get("address_line") or fake.street_address(),
        "city": addr.get("city") or fake.city(),
        "state": addr.get("state") or fake.state_abbr(),
        "postal_code": addr.get("postal_code") or fake.postcode(),
        "country": "US",
    }


def generate_locations_for_organization(org: dict, count: int = 2) -> list[dict]:
    """Generate `count` locations sharing the organization's address."""
    addr = {
        "address_line": org.get("address_line"),
        "city": org.get("city"),
        "state": org.get("state"),
        "postal_code": org.get("postal_code"),
    }
    return [generate_location(org["id"], addr) for _ in range(count)]

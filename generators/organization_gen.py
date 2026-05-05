"""Organization generator.

Produces raw organization dicts representing healthcare facilities.
Output keys: id, name, type_code, type_display, phone, email,
address_line, city, state, postal_code, country.
"""
import random

from generators._rng import e164_phone, fake, new_uuid

_ORG_SUFFIXES = ["Clinic", "Medical Center", "Health System", "Hospital", "Family Practice"]

_ORG_TYPES = [
    ("prov", "Healthcare Provider"),
    ("prov", "Healthcare Provider"),
    ("prov", "Healthcare Provider"),
    ("govt", "Government"),
    ("edu",  "Educational Institute"),
]


def generate_organization() -> dict:
    type_code, type_display = random.choice(_ORG_TYPES)
    suffix = random.choice(_ORG_SUFFIXES)
    city = fake.city()

    return {
        "id": new_uuid(),
        "name": f"{city} {fake.last_name()} {suffix}",
        "type_code": type_code,
        "type_display": type_display,
        "npi": fake.numerify("##########"),
        "phone": e164_phone(),
        "email": fake.company_email(),
        "address_line": fake.street_address(),
        "city": city,
        "state": fake.state_abbr(),
        "postal_code": fake.postcode(),
        "country": "US",
    }

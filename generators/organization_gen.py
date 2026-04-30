"""Organization generator.

Produces raw organization dicts representing healthcare facilities.
Output keys: id, name, type_code, type_display, phone, email,
address_line, city, state, postal_code, country.
"""
import random
import uuid

from faker import Faker

fake = Faker("en_US")

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
        "id": str(uuid.uuid4()),
        "name": f"{city} {fake.last_name()} {suffix}",
        "type_code": type_code,
        "type_display": type_display,
        "phone": fake.phone_number(),
        "email": fake.company_email(),
        "address_line": fake.street_address(),
        "city": city,
        "state": fake.state_abbr(),
        "postal_code": fake.postcode(),
        "country": "US",
    }

"""RelatedPerson generator.

Generates family members and emergency contacts with age- and marital-status-aware
logic: minors always get both parents, married adults have an 85% chance of a
linked spouse, and any patient has a 60% chance of a named emergency contact.
Related persons default to sharing the patient's address (same household).
Output keys: id, patient_id, relationship_code, relationship_display, first_name,
last_name, gender, birth_date, phone, email, address_line, city, state,
postal_code, country.
"""
import random
import uuid
from datetime import date

from faker import Faker

fake = Faker("en_US")

# HL7 v3 RoleCode values used for family relationships
_PARENT_RELS = [
    ("MTH", "mother", "female"),
    ("FTH", "father", "male"),
]


def generate_related_persons(patient: dict) -> list[dict]:
    """Generates family/contact RelatedPersons based on the patient's age and marital status."""
    related: list[dict] = []

    try:
        age = date.today().year - int(patient["birth_date"][:4])
    except (ValueError, KeyError):
        age = 30

    # Minors always get both parents
    if age < 18:
        for rel_code, rel_display, rel_gender in _PARENT_RELS:
            related.append(
                _make(patient, rel_code, rel_display, rel_gender,
                      age_min=age + 18, age_max=min(age + 50, 100))
            )

    # Married adults have a high chance of a linked spouse
    if age >= 18 and patient.get("marital_code") == "M" and random.random() < 0.85:
        spouse_gender = "female" if patient["gender"] == "male" else "male"
        related.append(
            _make(patient, "SPS", "spouse", spouse_gender,
                  age_min=max(18, age - 15), age_max=min(age + 15, 100))
        )

    # Any patient has a 60% chance of a named emergency contact
    if random.random() < 0.60:
        ec_gender = random.choice(["male", "female"])
        related.append(
            _make(patient, "C", "emergency contact", ec_gender,
                  age_min=18, age_max=75)
        )

    return related


def _make(
    patient: dict,
    rel_code: str,
    rel_display: str,
    gender: str,
    age_min: int,
    age_max: int,
) -> dict:
    age_min = max(0, age_min)
    age_max = max(age_min + 1, min(age_max, 100))

    first_name = fake.first_name_male() if gender == "male" else fake.first_name_female()
    # Related persons often share the patient's last name
    last_name = patient["last_name"] if random.random() < 0.6 else fake.last_name()

    return {
        "id": str(uuid.uuid4()),
        "patient_id": patient["id"],
        "relationship_code": rel_code,
        "relationship_display": rel_display,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "birth_date": fake.date_of_birth(
            minimum_age=age_min, maximum_age=age_max
        ).strftime("%Y-%m-%d"),
        "phone": fake.phone_number(),
        "email": fake.email(),
        # Share the patient's address by default (same household)
        "address_line": patient.get("address_line", fake.street_address()),
        "city": patient.get("city", fake.city()),
        "state": patient.get("state", fake.state_abbr()),
        "postal_code": patient.get("postal_code", fake.postcode()),
        "country": "US",
    }

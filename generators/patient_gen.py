"""Patient generator.

Produces raw patient dicts with demographics, contact details, and identifiers.
The output dict is version-agnostic; R4/R5 mappers in mappers/r4/ and mappers/r5/
convert it to a spec-compliant FHIR Patient resource.

Output keys: id, mrn, prefix, first_name, middle_name, last_name, suffix,
gender, birth_date, deceased, marital_code, marital_display, phone_home,
phone_mobile, email, address_line, city, state, postal_code, country,
language_code, language_display.
"""
import random
import uuid

from faker import Faker

fake = Faker("en_US")

_GENDERS = ["male", "female", "other", "unknown"]
_GENDER_WEIGHTS = [47, 47, 4, 2]

_MARITAL_STATUSES = [
    ("M", "Married"),
    ("S", "Never Married"),
    ("D", "Divorced"),
    ("W", "Widowed"),
    ("L", "Legally Separated"),
    ("T", "Domestic partner"),
    ("U", "unmarried"),
]

_LANGUAGES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("zh", "Chinese"),
    ("ar", "Arabic"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
]
_LANGUAGE_WEIGHTS = [70, 14, 3, 3, 3, 3, 2, 2]


def _pick(seq: list, weights: list | None = None):
    return random.choices(seq, weights=weights, k=1)[0]


def generate_patient(age_min: int = 0, age_max: int = 100) -> dict:
    gender = _pick(_GENDERS, _GENDER_WEIGHTS)

    if gender == "male":
        first_name = fake.first_name_male()
        prefix = _pick(["Mr.", "Dr.", None, None])
    elif gender == "female":
        first_name = fake.first_name_female()
        prefix = _pick(["Ms.", "Mrs.", "Dr.", None])
    else:
        first_name = fake.first_name()
        prefix = None

    middle_name = fake.first_name()
    last_name = fake.last_name()
    suffix = _pick([None, None, None, None, "Jr.", "Sr.", "II", "III", "MD", "PhD"])

    marital_code, marital_display = _pick(_MARITAL_STATUSES)
    lang_code, lang_display = _pick(_LANGUAGES, _LANGUAGE_WEIGHTS)
    deceased: bool | None = True if random.random() < 0.05 else None

    return {
        "id": str(uuid.uuid4()),
        "mrn": fake.numerify("MRN-#######"),
        "prefix": prefix,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "suffix": suffix,
        "gender": gender,
        "birth_date": fake.date_of_birth(
            minimum_age=age_min, maximum_age=age_max
        ).strftime("%Y-%m-%d"),
        "deceased": deceased,
        "marital_code": marital_code,
        "marital_display": marital_display,
        "phone_home": fake.phone_number(),
        "phone_mobile": fake.phone_number(),
        "email": fake.email(),
        "address_line": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "postal_code": fake.postcode(),
        "country": "US",
        "language_code": lang_code,
        "language_display": lang_display,
    }


def generate_patients(count: int, age_min: int = 0, age_max: int = 100) -> list[dict]:
    return [generate_patient(age_min, age_max) for _ in range(count)]

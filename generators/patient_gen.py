"""Patient generator.

Produces raw patient dicts with demographics, contact details, identifiers,
and a per-patient observation baseline used by the observation generator to
produce longitudinally consistent vital-sign values.

Output keys: id, mrn, prefix, first_name, middle_name, last_name, suffix,
gender, birth_date, age, deceased, marital_code, marital_display, phone_home,
phone_mobile, email, address_line, city, state, postal_code, country,
language_code, language_display, race_code, race_display, ethnicity_code,
ethnicity_display, birth_sex, height_cm, obs_baseline.
"""
import random

from generators._rng import e164_phone, fake, new_uuid

_GENDERS = ["male", "female", "other", "unknown"]
_GENDER_WEIGHTS = [47, 47, 4, 2]

# Marital statuses and the minimum age at which each is plausible
_MARITAL_STATUSES_ADULT = [
    ("M", "Married"),
    ("S", "Never Married"),
    ("D", "Divorced"),
    ("W", "Widowed"),
    ("L", "Legally Separated"),
    ("T", "Domestic partner"),
]
_MARITAL_STATUS_MINOR = ("S", "Never Married")

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

# OMB race categories (urn:oid:2.16.840.1.113883.6.238)
_RACES = [
    ("2106-3", "White"),
    ("2054-5", "Black or African American"),
    ("2028-9", "Asian"),
    ("1002-5", "American Indian or Alaska Native"),
    ("2076-8", "Native Hawaiian or Other Pacific Islander"),
    ("2131-1", "Other Race"),
]
_RACE_WEIGHTS = [60, 13, 6, 1, 0.5, 2]

# OMB ethnicity categories
_ETHNICITIES = [
    ("2135-2", "Hispanic or Latino"),
    ("2186-5", "Not Hispanic or Latino"),
]
_ETHNICITY_WEIGHTS = [18, 82]

# Birth sex codes (HL7 v2 administrative sex)
_BIRTH_SEX_BY_GENDER = {
    "male": "M",
    "female": "F",
    "other": "OTH",
    "unknown": "UNK",
}


def _pick(seq: list, weights: list | None = None):
    return random.choices(seq, weights=weights, k=1)[0]


def _generate_obs_baseline(gender: str, age: int) -> dict:
    """Generate per-patient normal midpoints for longitudinally stable vitals.

    Values are drawn from the centre of each normal range, then nudged by a
    small random offset so each patient has their own consistent baseline.
    """
    # Systolic BP rises slightly with age
    sbp_mid = 100 + min(age * 0.3, 18) + random.uniform(-8, 8)
    dbp_mid = 65 + min(age * 0.15, 10) + random.uniform(-5, 5)

    # Height: males taller on average
    if gender == "male":
        height = random.triangular(160, 195, 177)
    elif gender == "female":
        height = random.triangular(148, 180, 163)
    else:
        height = random.triangular(154, 188, 170)

    return {
        "systolic_bp": round(sbp_mid, 0),
        "diastolic_bp": round(dbp_mid, 0),
        "heart_rate": round(random.triangular(58, 98, 72), 0),
        "respiratory_rate": round(random.triangular(12, 20, 15), 0),
        "body_temperature": round(random.triangular(36.1, 37.2, 36.7), 1),
        "oxygen_saturation": round(random.triangular(96, 100, 98), 0),
        "height_cm": round(height, 1),
    }


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

    birth_date = fake.date_of_birth(minimum_age=age_min, maximum_age=age_max)
    from datetime import date
    age = (date.today() - birth_date).days // 365

    # Age-aware marital status: minors are always "Never Married"
    if age < 18:
        marital_code, marital_display = _MARITAL_STATUS_MINOR
    else:
        marital_code, marital_display = _pick(_MARITAL_STATUSES_ADULT)

    # Deceased probability scales with age (roughly actuarial)
    deceased_prob = min(0.01 + age * 0.001, 0.25)
    deceased: bool | None = True if random.random() < deceased_prob else None

    race_code, race_display = _pick(_RACES, _RACE_WEIGHTS)
    ethnicity_code, ethnicity_display = _pick(_ETHNICITIES, _ETHNICITY_WEIGHTS)
    lang_code, lang_display = _pick(_LANGUAGES, _LANGUAGE_WEIGHTS)

    obs_baseline = _generate_obs_baseline(gender, age)

    return {
        "id": new_uuid(),
        "mrn": fake.numerify("MRN-#######"),
        "prefix": prefix,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "suffix": suffix,
        "gender": gender,
        "birth_date": birth_date.strftime("%Y-%m-%d"),
        "age": age,
        "deceased": deceased,
        "marital_code": marital_code,
        "marital_display": marital_display,
        "phone_home": e164_phone(),
        "phone_mobile": e164_phone(),
        "email": fake.email(),
        "address_line": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "postal_code": fake.postcode(),
        "country": "US",
        "language_code": lang_code,
        "language_display": lang_display,
        "race_code": race_code,
        "race_display": race_display,
        "ethnicity_code": ethnicity_code,
        "ethnicity_display": ethnicity_display,
        "birth_sex": _BIRTH_SEX_BY_GENDER.get(gender, "UNK"),
        "height_cm": obs_baseline["height_cm"],
        "obs_baseline": obs_baseline,
    }


def generate_patients(count: int, age_min: int = 0, age_max: int = 100) -> list[dict]:
    return [generate_patient(age_min, age_max) for _ in range(count)]

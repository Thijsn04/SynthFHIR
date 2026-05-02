"""Practitioner generator.

Produces raw practitioner dicts with NPI, specialty (SNOMED CT), and
qualification (HL7 v2-0360). Each practitioner is linked to one organization.
Output keys: id, npi, prefix, first_name, last_name, gender, specialty_code,
specialty_display, qualification_code, qualification_display, phone, email,
organization_id.
"""
import random

from generators._rng import e164_phone, fake, new_uuid

# SNOMED CT specialty codes
_SPECIALTIES = [
    ("419772000", "Family practice"),
    ("419192003", "Internal medicine"),
    ("408443003", "General medical practice"),
    ("394814009", "General practice"),
    ("408467006", "Adult cardiology"),
    ("394591006", "Neurology"),
    ("394583002", "Dermatology"),
    ("394585009", "Obstetrics and gynecology"),
    ("394801008", "Orthopedic surgery"),
    ("394592004", "Clinical oncology"),
    ("394602003", "Rehabilitation"),
    ("394609007", "General surgery"),
    ("394807007", "Psychiatry"),
    ("418112009", "Pulmonary medicine"),
    ("394589003", "Nephrology"),
    ("394805004", "Clinical pharmacology"),
]

# HL7 v2-0360 qualification codes
_QUALIFICATIONS = [
    ("MD", "Doctor of Medicine"),
    ("DO", "Doctor of Osteopathic Medicine"),
    ("NP", "Nurse Practitioner"),
    ("PA", "Physician Assistant"),
]


def generate_practitioner(organization_id: str) -> dict:
    gender = random.choice(["male", "female"])
    first_name = fake.first_name_male() if gender == "male" else fake.first_name_female()
    specialty_code, specialty_display = random.choice(_SPECIALTIES)
    qual_code, qual_display = random.choice(_QUALIFICATIONS)

    return {
        "id": new_uuid(),
        "npi": fake.numerify("##########"),
        "prefix": "Dr.",
        "first_name": first_name,
        "last_name": fake.last_name(),
        "gender": gender,
        "specialty_code": specialty_code,
        "specialty_display": specialty_display,
        "qualification_code": qual_code,
        "qualification_display": qual_display,
        "phone": e164_phone(),
        "email": fake.email(),
        "organization_id": organization_id,
    }

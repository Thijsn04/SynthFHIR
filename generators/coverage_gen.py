"""Coverage generator.

Generates an insurance Coverage resource for each patient. Simulates
realistic US payer distribution: Medicare (age 65+), Medicaid (low income
probability), or commercial insurance.

Output keys: id, patient_id, status, kind, subscriber_id, payer_display,
payer_code, type_code, type_display, plan_name, class_value, class_name,
period_start, period_end.
"""
import random
from datetime import date, timedelta

from generators._rng import fake, new_uuid

_COMMERCIAL_PAYERS = [
    ("UHC",    "United Healthcare",       "1234567890"),
    ("BCBS",   "Blue Cross Blue Shield",  "2345678901"),
    ("AETNA",  "Aetna",                   "3456789012"),
    ("CIGNA",  "Cigna",                   "4567890123"),
    ("HUM",    "Humana",                  "5678901234"),
    ("CVS",    "CVS Health/Aetna",        "6789012345"),
    ("MOLINA", "Molina Healthcare",       "7890123456"),
]

_PLAN_NAMES = {
    "Medicare":  ["Medicare Part A & B", "Medicare Advantage Plan", "Medicare Supplement Plan F"],
    "Medicaid":  ["Medicaid Managed Care", "Medicaid Fee-for-Service", "CHIP"],
    "commercial": [
        "PPO Gold Plan", "HMO Silver Plan", "EPO Bronze Plan",
        "HDHP + HSA", "POS Platinum Plan",
    ],
}


def generate_coverage_for_patient(patient_id: str, patient_age: int) -> dict:
    """Return a single Coverage record for the patient."""
    # Payer selection: Medicare 65+, Medicaid ~15% otherwise, else commercial
    if patient_age >= 65:
        kind = "Medicare"
        payer_display = "Centers for Medicare & Medicaid Services"
        payer_code = "CMS"
        type_code = "MANDPOL"
        type_display = "Mandatory Policy"
        plan_name = random.choice(_PLAN_NAMES["Medicare"])
        class_value = f"MCRE-{random.randint(10000, 99999)}"
        class_name = "Medicare Beneficiary"
    elif random.random() < 0.15:
        kind = "Medicaid"
        payer_display = "State Medicaid Program"
        payer_code = "MEDICAID"
        type_code = "MANDPOL"
        type_display = "Mandatory Policy"
        plan_name = random.choice(_PLAN_NAMES["Medicaid"])
        class_value = f"MCAD-{random.randint(10000, 99999)}"
        class_name = "Medicaid Beneficiary"
    else:
        payer_tuple = random.choice(_COMMERCIAL_PAYERS)
        payer_code, payer_display, _ = payer_tuple
        kind = "commercial"
        type_code = "HMO"
        type_display = "Health Maintenance Organization"
        plan_name = random.choice(_PLAN_NAMES["commercial"])
        class_value = fake.bothify("GRP-######")
        class_name = "Group Plan"

    today = date.today()
    period_start = (today - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
    period_end = (today + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "status": "active",
        "kind": kind,
        "subscriber_id": fake.bothify("SUB-########").upper(),
        "payer_display": payer_display,
        "payer_code": payer_code,
        "type_code": type_code,
        "type_display": type_display,
        "plan_name": plan_name,
        "class_value": class_value,
        "class_name": class_name,
        "period_start": period_start,
        "period_end": period_end,
    }

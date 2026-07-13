"""MedicationDispense generator.

Models the pharmacy dispensing step that follows a MedicationRequest. Most, but
not all, prescriptions are dispensed, so a dispense is generated probabilistically
per medication. US Core v6 includes MedicationDispense.

Output keys: id, patient_id, medication_request_id, practitioner_id, rxnorm_code,
display, quantity, days_supply, when_handed_over, dose_value, dose_unit,
frequency_code.
"""
import random
from datetime import datetime, timedelta

from generators._rng import new_uuid

# Share of prescriptions that are actually dispensed.
_DISPENSE_PROBABILITY = 0.85

# Common outpatient supply durations in days.
_DAYS_SUPPLY = [30, 30, 30, 90, 90]


def generate_dispense_for_medication(medication: dict) -> dict | None:
    """Generate a MedicationDispense for a medication, or None if not dispensed."""
    if random.random() > _DISPENSE_PROBABILITY:
        return None

    days_supply = random.choice(_DAYS_SUPPLY)
    quantity = days_supply  # one unit per day is a reasonable default

    authored_on = medication.get("authored_on")
    when_handed_over = _plus_days(authored_on, random.randint(0, 3))

    return {
        "id": new_uuid(),
        "patient_id": medication["patient_id"],
        "medication_request_id": medication["id"],
        "practitioner_id": medication.get("practitioner_id", ""),
        "rxnorm_code": medication["rxnorm_code"],
        "display": medication["display"],
        "quantity": quantity,
        "days_supply": days_supply,
        "when_handed_over": when_handed_over,
        "dose_value": medication.get("dose_value"),
        "dose_unit": medication.get("dose_unit"),
        "frequency_code": medication.get("frequency_code"),
    }


def generate_dispenses_for_medications(medications: list[dict]) -> list[dict]:
    """Generate dispenses for a list of medications, skipping those not dispensed."""
    results = []
    for med in medications:
        dispense = generate_dispense_for_medication(med)
        if dispense is not None:
            results.append(dispense)
    return results


def _plus_days(date_str: str | None, days: int) -> str:
    """Add days to a YYYY-MM-DD string, returning YYYY-MM-DD. Falls back gracefully."""
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d") + timedelta(days=days)
        return d.strftime("%Y-%m-%d")
    except ValueError:
        return date_str[:10]

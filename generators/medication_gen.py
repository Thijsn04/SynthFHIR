"""MedicationRequest generator.

For each active condition, picks 1-2 first-line medications from the catalog
in data/medications.py and produces raw MedicationRequest dicts.

Output keys: id, patient_id, practitioner_id, encounter_id, status,
intent, rxnorm_code, display, dose_form, dose_value, dose_unit, frequency,
frequency_code, authored_on.
"""
import random
from datetime import date, timedelta

from data.medications import MEDICATIONS_BY_CONDITION
from generators._rng import new_uuid


def generate_medications_for_patient(
    patient_id: str,
    practitioner_id: str,
    encounter_id: str,
    conditions: list[dict],
) -> list[dict]:
    """Generate MedicationRequests for all active conditions."""
    results: list[dict] = []
    seen_rx: set[str] = set()  # avoid duplicate medications across comorbidities

    for cond in conditions:
        if cond.get("clinical_status") not in ("active", "inactive"):
            continue
        cond_key = _key_from_condition(cond)
        if cond_key is None:
            continue

        catalog = MEDICATIONS_BY_CONDITION.get(cond_key, [])
        if not catalog:
            continue

        num_meds = random.randint(1, min(2, len(catalog)))
        picks = random.sample(catalog, k=num_meds)
        for med in picks:
            if med.rxnorm_code in seen_rx:
                continue
            seen_rx.add(med.rxnorm_code)

            # Authored date is within the condition's active window
            days_ago = random.randint(30, 365)
            authored = (date.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

            supply_days = random.choice([30, 60, 90])
            results.append({
                "id": new_uuid(),
                "patient_id": patient_id,
                "practitioner_id": practitioner_id,
                "encounter_id": encounter_id,
                "status": "active" if cond.get("clinical_status") == "active" else "stopped",
                "intent": "order",
                "rxnorm_code": med.rxnorm_code,
                "display": med.display,
                "dose_form": med.dose_form,
                "dose_value": med.dose_value,
                "dose_unit": med.dose_unit,
                "frequency": med.frequency,
                "frequency_code": med.frequency_code,
                "authored_on": authored,
                "dispense_quantity": supply_days,
                "dispense_quantity_unit": "d",
                "dispense_supply_days": supply_days,
                "num_refills": random.randint(0, 5),
            })

    return results


def _key_from_condition(cond: dict) -> str | None:
    """Map a condition dict back to a medication catalog key via SNOMED code."""
    _SNOMED_TO_KEY = {
        "44054006":  "type2_diabetes",
        "38341003":  "hypertension",
        "55822004":  "hyperlipidemia",
        "49436004":  "atrial_fibrillation",
        "195967001": "asthma",
        "709044004": "ckd",
        "13645005":  "copd",
        "35489007":  "depression",
        "396275006": "osteoarthritis",
        "414916001": "obesity",
    }
    return _SNOMED_TO_KEY.get(cond.get("snomed_code", ""))

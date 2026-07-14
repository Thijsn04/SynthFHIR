"""Device generator.

Implantable devices for patients whose conditions commonly lead to them: cardiac
devices for arrhythmia and heart failure, coronary stents for coronary disease,
and joint prostheses for osteoarthritis. Modeled after US Core Implantable Device.

Output keys: id, patient_id, type_code, type_display, udi_di, udi_carrier, status.
"""
import random

from generators._rng import fake, new_uuid

# condition key -> (SNOMED device type code, display, probability)
_DEVICE_RULES = {
    "atrial_fibrillation": ("72506001", "Implantable defibrillator", 0.30),
    "heart_failure": ("14106009", "Cardiac pacemaker", 0.35),
    "coronary_artery_disease": ("705643001", "Cardiac stent", 0.40),
    "acute_mi": ("705643001", "Cardiac stent", 0.50),
    "osteoarthritis": ("304120007", "Prosthetic joint implant", 0.30),
}


def generate_devices_for_patient(patient_id: str, condition_keys: set[str]) -> list[dict]:
    """Generate implantable devices implied by a patient's conditions."""
    results: list[dict] = []
    seen: set[str] = set()
    for key in condition_keys:
        rule = _DEVICE_RULES.get(key)
        if not rule:
            continue
        code, display, prob = rule
        if code in seen or random.random() > prob:
            continue
        seen.add(code)
        di = fake.numerify("########")
        results.append(
            {
                "id": new_uuid(),
                "patient_id": patient_id,
                "type_code": code,
                "type_display": display,
                "udi_di": di,
                "udi_carrier": f"(01){di}(11)230101(17)280101(10)LOT{fake.numerify('####')}",
                "status": "active",
            }
        )
    return results

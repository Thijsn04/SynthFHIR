"""Procedure generator.

Generates Procedure resources for a single encounter. Every encounter gets
a general physical examination. Condition-specific procedures are sampled
from the catalog in data/procedures.py.

Output keys: id, patient_id, encounter_id, practitioner_id, status,
snomed_code, display, category_snomed, category_display, performed_datetime,
body_site_code, body_site_display.
"""
import random

from data.procedures import GENERAL_PROCEDURES, PROCEDURES_BY_CONDITION, ProcedureDef
from generators._rng import new_uuid

# Map condition SNOMED code to catalog key
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


def generate_procedures_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    performed_datetime: str,
    conditions: list[dict],
) -> list[dict]:
    """Return procedure records for the given encounter."""
    selected: list[ProcedureDef] = list(GENERAL_PROCEDURES)

    for cond in conditions:
        key = _SNOMED_TO_KEY.get(cond.get("snomed_code", ""))
        if not key:
            continue
        pool = PROCEDURES_BY_CONDITION.get(key, [])
        if pool:
            selected.append(random.choice(pool))

    # Deduplicate by SNOMED code
    seen: set[str] = set()
    unique: list[ProcedureDef] = []
    for p in selected:
        if p.snomed_code not in seen:
            seen.add(p.snomed_code)
            unique.append(p)

    return [_make(patient_id, encounter_id, practitioner_id, performed_datetime, p) for p in unique]


def _make(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    performed_datetime: str,
    proc: ProcedureDef,
) -> dict:
    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "practitioner_id": practitioner_id,
        "status": "completed",
        "snomed_code": proc.snomed_code,
        "display": proc.display,
        "category_snomed": proc.category_snomed,
        "category_display": proc.category_display,
        "performed_datetime": performed_datetime,
        "body_site_code": proc.body_site_code,
        "body_site_display": proc.body_site_display,
    }

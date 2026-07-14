"""Specimen generator.

Lab results imply a specimen was collected. One Specimen is produced per lab
DiagnosticReport, representing the sample the report was run on.

Output keys: id, patient_id, encounter_id, collected_datetime, type_code,
type_display.
"""
import random

from generators._rng import new_uuid

# SNOMED specimen types with a rough outpatient prevalence weighting.
_SPECIMEN_TYPES = [
    ("119297000", "Blood specimen", 70),
    ("122575003", "Urine specimen", 20),
    ("119334006", "Sputum specimen", 5),
    ("258580003", "Whole blood sample", 5),
]


def generate_specimens_for_reports(diagnostic_reports: list[dict]) -> list[dict]:
    """One Specimen per lab DiagnosticReport."""
    results: list[dict] = []
    for report in diagnostic_reports:
        code, display = _pick_type()
        results.append(
            {
                "id": new_uuid(),
                "patient_id": report["patient_id"],
                "encounter_id": report.get("encounter_id", ""),
                "collected_datetime": report.get("effective_datetime", ""),
                "type_code": code,
                "type_display": display,
            }
        )
    return results


def _pick_type() -> tuple[str, str]:
    codes = [(c, d) for c, d, _ in _SPECIMEN_TYPES]
    weights = [w for _, _, w in _SPECIMEN_TYPES]
    return random.choices(codes, weights=weights, k=1)[0]

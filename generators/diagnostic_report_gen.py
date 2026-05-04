"""DiagnosticReport generator.

Groups all laboratory-category observations from an encounter under a single
DiagnosticReport resource. Vital-signs observations remain standalone.

Output keys: id, patient_id, encounter_id, practitioner_id, status,
category_code, category_display, loinc_code, display, effective_datetime,
issued, observation_ids.
"""

from generators._rng import new_uuid


# LOINC panel code for a general comprehensive metabolic panel
_PANEL_LOINC = "24323-8"
_PANEL_DISPLAY = "Comprehensive metabolic panel"


def generate_diagnostic_reports_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    effective_datetime: str,
    observations: list[dict],
) -> list[dict]:
    """Create one DiagnosticReport grouping all lab observations for this encounter."""
    lab_obs_ids = [
        obs["id"]
        for obs in observations
        if obs.get("category_code") == "laboratory"
    ]
    if not lab_obs_ids:
        return []

    return [{
        "id": new_uuid(),
        "patient_id": patient_id,
        "encounter_id": encounter_id,
        "practitioner_id": practitioner_id,
        "status": "final",
        "category_code": "LAB",
        "category_display": "Laboratory",
        "loinc_code": _PANEL_LOINC,
        "display": _PANEL_DISPLAY,
        "effective_datetime": effective_datetime,
        "issued": effective_datetime,
        "observation_ids": lab_obs_ids,
    }]

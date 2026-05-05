"""CarePlan generator.

Produces chronic disease management plans linked to a patient, care team, and
conditions. Activities are drawn from a condition-keyed catalog of common
management tasks.

Output keys: id, patient_id, care_team_id, condition_ids, status, intent, title,
description, period_start, period_end, activities.
"""
from datetime import date, timedelta

from generators._rng import new_uuid

_ACTIVITIES: dict[str, list[str]] = {
    "type2_diabetes": [
        "Monitor HbA1c every 3 months",
        "Annual dilated eye exam",
        "Annual foot exam",
        "Regular blood pressure monitoring",
    ],
    "hypertension": [
        "Regular blood pressure monitoring",
        "Dietary sodium restriction",
        "Physical activity 150 min/week",
        "Medication adherence review",
    ],
    "ckd": [
        "Monitor eGFR every 3 months",
        "Nephrology referral",
        "Dietary protein restriction",
        "Blood pressure control to <130/80",
    ],
    "hyperlipidemia": [
        "Annual fasting lipid panel",
        "Dietary saturated fat reduction",
        "Statin therapy adherence monitoring",
    ],
    "copd": [
        "Spirometry every 6 months",
        "Smoking cessation counseling",
        "Influenza and pneumococcal vaccination",
        "Inhaler technique review",
    ],
    "depression": [
        "PHQ-9 screening each visit",
        "Psychotherapy referral",
        "Medication management review",
    ],
    "asthma": [
        "Peak flow monitoring",
        "Ensure rescue inhaler availability",
        "Allergen avoidance counseling",
    ],
    "obesity": [
        "Monthly weight monitoring",
        "Dietary counseling referral",
        "Physical activity plan",
    ],
    "atrial_fibrillation": [
        "Anticoagulation monitoring",
        "Cardiology follow-up",
        "Rate/rhythm control assessment",
    ],
}


def generate_care_plan(
    patient_id: str,
    care_team_id: str,
    conditions: list[dict],
) -> dict:
    primary = conditions[0] if conditions else {}
    recorded = primary.get("recorded_date", date.today().strftime("%Y-%m-%d"))
    period_end = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")

    activities: list[str] = []
    for cond in conditions:
        key = cond.get("condition_key", "")
        activities.extend(_ACTIVITIES.get(key, [])[:2])

    condition_names = ", ".join(c.get("display", "") for c in conditions[:3])

    return {
        "id": new_uuid(),
        "patient_id": patient_id,
        "care_team_id": care_team_id,
        "condition_ids": [c["id"] for c in conditions],
        "status": "active",
        "intent": "plan",
        "title": "Chronic Disease Management Plan",
        "description": f"Comprehensive care plan for management of {condition_names}",
        "period_start": recorded,
        "period_end": period_end,
        "activities": activities[:6],
    }

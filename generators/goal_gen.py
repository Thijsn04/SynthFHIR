"""Goal generator.

Produces clinical goals linked to a patient, CarePlan, and individual conditions.
Goals are drawn from a condition-keyed catalog of evidence-based clinical targets.

Output keys: id, patient_id, care_plan_id, condition_id, description, snomed_code,
display, lifecycle_status, achievement_status, target_date, start_date.
"""
import random
from datetime import date, timedelta

from generators._rng import new_uuid

# condition_key → list of (description, snomed_code, display)
_CONDITION_GOALS: dict[str, list[tuple[str, str, str]]] = {
    "type2_diabetes": [
        ("Achieve HbA1c below 7%", "2137158", "Glycosylated hemoglobin"),
        ("Achieve blood pressure below 130/80 mmHg", "59621000", "Blood pressure"),
    ],
    "hypertension": [
        ("Achieve blood pressure below 130/80 mmHg", "59621000", "Blood pressure"),
    ],
    "hyperlipidemia": [
        ("Reduce LDL cholesterol below 100 mg/dL", "166830008", "LDL cholesterol level"),
    ],
    "ckd": [
        ("Maintain eGFR above 30 mL/min/1.73 m2", "80321009", "Glomerular filtration rate"),
        ("Achieve blood pressure below 130/80 mmHg", "59621000", "Blood pressure"),
    ],
    "obesity": [
        ("Achieve 5% body weight reduction", "444862003", "Body weight"),
    ],
    "copd": [
        ("Achieve oxygen saturation above 95%", "103228002", "Oxygen saturation"),
        ("Smoking cessation", "8517006", "Ex-smoker"),
    ],
    "depression": [
        ("Reduce PHQ-9 score by 50%", "273930002", "Depression screening test"),
    ],
    "asthma": [
        ("Achieve well-controlled asthma status", "195967001", "Asthma"),
    ],
    "atrial_fibrillation": [
        ("Achieve heart rate below 80 bpm at rest", "364075005", "Heart rate"),
    ],
    "osteoarthritis": [
        ("Reduce pain score by 2 points", "57676002", "Joint pain"),
    ],
}

_LIFECYCLE = ["proposed", "active", "completed", "on-hold"]
_LIFECYCLE_W = [0.10, 0.65, 0.15, 0.10]

_ACHIEVEMENT = ["in-progress", "improving", "worsening", "no-change"]
_ACHIEVEMENT_W = [0.45, 0.30, 0.15, 0.10]


def generate_goals_for_patient(
    patient_id: str,
    care_plan_id: str,
    conditions: list[dict],
) -> list[dict]:
    goals: list[dict] = []
    for cond in conditions:
        key = cond.get("condition_key", "")
        cond_goals = _CONDITION_GOALS.get(key, [])
        for desc, snomed_code, display in cond_goals[:1]:
            target = (date.today() + timedelta(days=random.randint(90, 365))).strftime("%Y-%m-%d")
            goals.append({
                "id": new_uuid(),
                "patient_id": patient_id,
                "care_plan_id": care_plan_id,
                "condition_id": cond["id"],
                "description": desc,
                "snomed_code": snomed_code,
                "display": display,
                "lifecycle_status": random.choices(_LIFECYCLE, weights=_LIFECYCLE_W, k=1)[0],
                "achievement_status": random.choices(_ACHIEVEMENT, weights=_ACHIEVEMENT_W, k=1)[0],
                "target_date": target,
                "start_date": cond.get("recorded_date", date.today().strftime("%Y-%m-%d")),
            })
    return goals

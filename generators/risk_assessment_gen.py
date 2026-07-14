"""RiskAssessment generator.

A cardiovascular risk assessment for patients with cardiometabolic risk factors.
The predicted probability rises with the number of contributing conditions.

Output keys: id, patient_id, encounter_id, effective_datetime, outcome_code,
outcome_display, probability.
"""
import random

from generators._rng import new_uuid

_RISK_FACTORS = {
    "type2_diabetes", "type1_diabetes", "hypertension", "hyperlipidemia",
    "obesity", "coronary_artery_disease", "sleep_apnea",
}


def generate_risk_assessment_for_patient(
    patient_id: str, encounter_id: str, effective_datetime: str, condition_keys: set[str]
) -> list[dict]:
    """Generate a cardiovascular RiskAssessment when risk factors are present."""
    factors = condition_keys & _RISK_FACTORS
    if not factors:
        return []
    base = 0.05 + 0.06 * len(factors) + random.uniform(-0.02, 0.05)
    probability = round(min(base, 0.9), 3)
    return [
        {
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "effective_datetime": effective_datetime,
            "outcome_code": "22298006",
            "outcome_display": "Myocardial infarction",
            "probability": probability,
        }
    ]

"""Clinical condition catalog.

Each ConditionDef maps a query-friendly key to FHIR-conformant codes and lists
the observation types that are clinically ordered for that condition. The
`linked_obs_types` keys reference entries in data/observations.py.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ConditionDef:
    key: str
    display: str
    snomed_code: str
    icd10_code: str
    linked_obs_types: tuple[str, ...]
    typical_age_min: int = 0


CONDITIONS: list[ConditionDef] = [
    ConditionDef(
        key="type2_diabetes",
        display="Type 2 Diabetes Mellitus",
        snomed_code="44054006",
        icd10_code="E11.9",
        linked_obs_types=("blood_glucose", "hba1c", "systolic_bp", "diastolic_bp"),
        typical_age_min=30,
    ),
    ConditionDef(
        key="hypertension",
        display="Essential Hypertension",
        snomed_code="38341003",
        icd10_code="I10",
        linked_obs_types=("systolic_bp", "diastolic_bp", "heart_rate"),
        typical_age_min=25,
    ),
    ConditionDef(
        key="asthma",
        display="Asthma",
        snomed_code="195967001",
        icd10_code="J45.909",
        linked_obs_types=("fev1", "oxygen_saturation"),
        typical_age_min=5,
    ),
    ConditionDef(
        key="ckd",
        display="Chronic Kidney Disease",
        snomed_code="709044004",
        icd10_code="N18.9",
        linked_obs_types=("egfr", "creatinine", "systolic_bp", "diastolic_bp"),
        typical_age_min=40,
    ),
    ConditionDef(
        key="hyperlipidemia",
        display="Hyperlipidemia",
        snomed_code="55822004",
        icd10_code="E78.5",
        linked_obs_types=("cholesterol_total", "ldl", "hdl"),
        typical_age_min=30,
    ),
    ConditionDef(
        key="depression",
        display="Major Depressive Disorder",
        snomed_code="35489007",
        icd10_code="F32.9",
        linked_obs_types=(),
        typical_age_min=15,
    ),
    ConditionDef(
        key="osteoarthritis",
        display="Osteoarthritis",
        snomed_code="396275006",
        icd10_code="M19.90",
        linked_obs_types=("body_weight", "bmi"),
        typical_age_min=45,
    ),
    ConditionDef(
        key="copd",
        display="Chronic Obstructive Pulmonary Disease",
        snomed_code="13645005",
        icd10_code="J44.1",
        linked_obs_types=("fev1", "oxygen_saturation"),
        typical_age_min=40,
    ),
    ConditionDef(
        key="atrial_fibrillation",
        display="Atrial Fibrillation",
        snomed_code="49436004",
        icd10_code="I48.91",
        linked_obs_types=("heart_rate", "systolic_bp", "diastolic_bp"),
        typical_age_min=50,
    ),
    ConditionDef(
        key="obesity",
        display="Obesity",
        snomed_code="414916001",
        icd10_code="E66.9",
        linked_obs_types=("body_weight", "bmi", "systolic_bp", "diastolic_bp"),
        typical_age_min=18,
    ),
]

CONDITIONS_BY_KEY: dict[str, ConditionDef] = {c.key: c for c in CONDITIONS}
VALID_CONDITION_KEYS: frozenset[str] = frozenset(CONDITIONS_BY_KEY)


def find_condition(query: str) -> ConditionDef | None:
    """Case-insensitive partial match against a condition key or display name."""
    q = query.lower().strip()
    if q in CONDITIONS_BY_KEY:
        return CONDITIONS_BY_KEY[q]
    for cond in CONDITIONS:
        if q in cond.key or q in cond.display.lower():
            return cond
    return None

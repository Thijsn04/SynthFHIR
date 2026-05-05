"""Clinical condition catalog.

Each ConditionDef maps a query-friendly key to FHIR-conformant codes and lists
the observation types that are clinically ordered for that condition. The
`linked_obs_types` keys reference entries in data/observations.py.
`typical_age_min` is enforced during condition assignment to prevent clinically
implausible diagnoses (e.g. atrial fibrillation in a 5-year-old).
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
        linked_obs_types=("fev1", "oxygen_saturation", "respiratory_rate"),
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
        linked_obs_types=("phq9", "gad7"),
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
        linked_obs_types=("fev1", "oxygen_saturation", "respiratory_rate", "body_temperature"),
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

    # --- Mental health ---
    ConditionDef(
        key="anxiety_disorder",
        display="Generalized Anxiety Disorder",
        snomed_code="197480006",
        icd10_code="F41.1",
        linked_obs_types=("gad7", "phq9"),
        typical_age_min=15,
    ),
    ConditionDef(
        key="bipolar_disorder",
        display="Bipolar Disorder",
        snomed_code="13746004",
        icd10_code="F31.9",
        linked_obs_types=("phq9",),
        typical_age_min=18,
    ),
    ConditionDef(
        key="ptsd",
        display="Post-Traumatic Stress Disorder",
        snomed_code="47505003",
        icd10_code="F43.10",
        linked_obs_types=("phq9", "gad7"),
        typical_age_min=15,
    ),
    ConditionDef(
        key="adhd",
        display="Attention Deficit Hyperactivity Disorder",
        snomed_code="406506008",
        icd10_code="F90.9",
        linked_obs_types=(),
        typical_age_min=5,
    ),
    ConditionDef(
        key="schizophrenia",
        display="Schizophrenia",
        snomed_code="58214004",
        icd10_code="F20.9",
        linked_obs_types=("body_weight", "bmi"),
        typical_age_min=18,
    ),
    ConditionDef(
        key="opioid_use_disorder",
        display="Opioid Use Disorder",
        snomed_code="762176005",
        icd10_code="F11.20",
        linked_obs_types=("heart_rate", "body_temperature"),
        typical_age_min=18,
    ),

    # --- Acute / episodic ---
    ConditionDef(
        key="pneumonia",
        display="Pneumonia",
        snomed_code="233604007",
        icd10_code="J18.9",
        linked_obs_types=("body_temperature", "respiratory_rate", "oxygen_saturation"),
        typical_age_min=0,
    ),
    ConditionDef(
        key="uti",
        display="Urinary Tract Infection",
        snomed_code="68566005",
        icd10_code="N39.0",
        linked_obs_types=("body_temperature",),
        typical_age_min=0,
    ),
    ConditionDef(
        key="acute_mi",
        display="Acute Myocardial Infarction",
        snomed_code="57054005",
        icd10_code="I21.9",
        linked_obs_types=("heart_rate", "systolic_bp", "diastolic_bp"),
        typical_age_min=40,
    ),
    ConditionDef(
        key="ischemic_stroke",
        display="Ischemic Stroke",
        snomed_code="422504002",
        icd10_code="I63.9",
        linked_obs_types=("systolic_bp", "diastolic_bp"),
        typical_age_min=40,
    ),
    ConditionDef(
        key="heart_failure",
        display="Heart Failure",
        snomed_code="84114007",
        icd10_code="I50.9",
        linked_obs_types=("systolic_bp", "diastolic_bp", "heart_rate", "body_weight"),
        typical_age_min=50,
    ),
    ConditionDef(
        key="gerd",
        display="Gastroesophageal Reflux Disease",
        snomed_code="235595009",
        icd10_code="K21.0",
        linked_obs_types=("body_weight",),
        typical_age_min=20,
    ),

    # --- Cancer ---
    ConditionDef(
        key="breast_cancer",
        display="Malignant Neoplasm of Breast",
        snomed_code="254837009",
        icd10_code="C50.919",
        linked_obs_types=("hemoglobin",),
        typical_age_min=30,
    ),
    ConditionDef(
        key="lung_cancer",
        display="Malignant Neoplasm of Lung",
        snomed_code="254637007",
        icd10_code="C34.10",
        linked_obs_types=("fev1", "oxygen_saturation", "hemoglobin"),
        typical_age_min=40,
    ),
    ConditionDef(
        key="colorectal_cancer",
        display="Malignant Neoplasm of Colon",
        snomed_code="363406005",
        icd10_code="C18.9",
        linked_obs_types=("hemoglobin",),
        typical_age_min=40,
    ),
    ConditionDef(
        key="prostate_cancer",
        display="Malignant Neoplasm of Prostate",
        snomed_code="399068003",
        icd10_code="C61",
        linked_obs_types=(),
        typical_age_min=50,
    ),
    ConditionDef(
        key="melanoma",
        display="Malignant Melanoma of Skin",
        snomed_code="372244006",
        icd10_code="C43.9",
        linked_obs_types=(),
        typical_age_min=25,
    ),

    # --- Neurological ---
    ConditionDef(
        key="parkinsons",
        display="Parkinson's Disease",
        snomed_code="49049000",
        icd10_code="G20",
        linked_obs_types=("heart_rate", "body_weight"),
        typical_age_min=55,
    ),
    ConditionDef(
        key="alzheimers",
        display="Alzheimer's Disease",
        snomed_code="26929004",
        icd10_code="G30.9",
        linked_obs_types=("body_weight",),
        typical_age_min=65,
    ),
    ConditionDef(
        key="epilepsy",
        display="Epilepsy",
        snomed_code="84757009",
        icd10_code="G40.909",
        linked_obs_types=(),
        typical_age_min=0,
    ),
    ConditionDef(
        key="migraine",
        display="Migraine",
        snomed_code="37796009",
        icd10_code="G43.909",
        linked_obs_types=(),
        typical_age_min=10,
    ),

    # --- Musculoskeletal / autoimmune ---
    ConditionDef(
        key="rheumatoid_arthritis",
        display="Rheumatoid Arthritis",
        snomed_code="69896004",
        icd10_code="M06.9",
        linked_obs_types=("creatinine", "body_temperature", "hemoglobin"),
        typical_age_min=25,
    ),
    ConditionDef(
        key="lupus",
        display="Systemic Lupus Erythematosus",
        snomed_code="55464009",
        icd10_code="M32.9",
        linked_obs_types=("creatinine", "systolic_bp", "diastolic_bp", "hemoglobin"),
        typical_age_min=18,
    ),
    ConditionDef(
        key="multiple_sclerosis",
        display="Multiple Sclerosis",
        snomed_code="24700007",
        icd10_code="G35",
        linked_obs_types=(),
        typical_age_min=20,
    ),
    ConditionDef(
        key="fibromyalgia",
        display="Fibromyalgia",
        snomed_code="203082005",
        icd10_code="M79.3",
        linked_obs_types=("phq9",),
        typical_age_min=20,
    ),

    # --- GI ---
    ConditionDef(
        key="crohns_disease",
        display="Crohn's Disease",
        snomed_code="34000006",
        icd10_code="K50.90",
        linked_obs_types=("body_weight", "body_temperature", "hemoglobin"),
        typical_age_min=15,
    ),
    ConditionDef(
        key="ibs",
        display="Irritable Bowel Syndrome",
        snomed_code="10743008",
        icd10_code="K58.9",
        linked_obs_types=("body_weight",),
        typical_age_min=15,
    ),

    # --- Endocrine / metabolic ---
    ConditionDef(
        key="hypothyroidism",
        display="Hypothyroidism",
        snomed_code="40930008",
        icd10_code="E03.9",
        linked_obs_types=("tsh_high", "body_weight", "heart_rate"),
        typical_age_min=20,
    ),
    ConditionDef(
        key="hyperthyroidism",
        display="Hyperthyroidism",
        snomed_code="34486009",
        icd10_code="E05.90",
        linked_obs_types=("tsh", "heart_rate", "body_weight"),
        typical_age_min=20,
    ),
    ConditionDef(
        key="type1_diabetes",
        display="Type 1 Diabetes Mellitus",
        snomed_code="46635009",
        icd10_code="E10.9",
        linked_obs_types=("blood_glucose", "hba1c", "systolic_bp", "diastolic_bp"),
        typical_age_min=5,
    ),
    ConditionDef(
        key="gout",
        display="Gout",
        snomed_code="90560007",
        icd10_code="M10.9",
        linked_obs_types=("creatinine",),
        typical_age_min=30,
    ),

    # --- Infectious disease ---
    ConditionDef(
        key="hiv",
        display="Human Immunodeficiency Virus Infection",
        snomed_code="86406008",
        icd10_code="B20",
        linked_obs_types=("hemoglobin",),
        typical_age_min=18,
    ),
    ConditionDef(
        key="hepatitis_c",
        display="Chronic Hepatitis C",
        snomed_code="50711007",
        icd10_code="B18.2",
        linked_obs_types=("alt",),
        typical_age_min=18,
    ),
    ConditionDef(
        key="covid19_long",
        display="Post-COVID-19 Condition",
        snomed_code="1119303003",
        icd10_code="U09.9",
        linked_obs_types=("oxygen_saturation", "respiratory_rate", "heart_rate"),
        typical_age_min=18,
    ),

    # --- Respiratory / sleep ---
    ConditionDef(
        key="sleep_apnea",
        display="Obstructive Sleep Apnea",
        snomed_code="73430006",
        icd10_code="G47.33",
        linked_obs_types=("oxygen_saturation", "body_weight", "bmi"),
        typical_age_min=25,
    ),
    ConditionDef(
        key="pulmonary_hypertension",
        display="Pulmonary Hypertension",
        snomed_code="70995007",
        icd10_code="I27.0",
        linked_obs_types=("systolic_bp", "oxygen_saturation"),
        typical_age_min=25,
    ),

    # --- Cardiovascular ---
    ConditionDef(
        key="coronary_artery_disease",
        display="Coronary Artery Disease",
        snomed_code="53741008",
        icd10_code="I25.10",
        linked_obs_types=("systolic_bp", "diastolic_bp", "heart_rate", "cholesterol_total", "ldl"),
        typical_age_min=40,
    ),
    ConditionDef(
        key="peripheral_artery_disease",
        display="Peripheral Artery Disease",
        snomed_code="400047006",
        icd10_code="I73.9",
        linked_obs_types=("systolic_bp", "diastolic_bp"),
        typical_age_min=45,
    ),

    # --- Hematological / other ---
    ConditionDef(
        key="anemia",
        display="Anemia",
        snomed_code="271737000",
        icd10_code="D64.9",
        linked_obs_types=("hemoglobin",),
        typical_age_min=0,
    ),
    ConditionDef(
        key="chronic_pain",
        display="Chronic Pain Syndrome",
        snomed_code="82423001",
        icd10_code="G89.29",
        linked_obs_types=("phq9",),
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


def conditions_for_age(patient_age: int) -> list[ConditionDef]:
    """Return conditions whose typical_age_min is <= patient_age."""
    return [c for c in CONDITIONS if c.typical_age_min <= patient_age]

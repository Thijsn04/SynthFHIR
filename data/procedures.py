"""Procedure catalog keyed by condition.

Each ProcedureDef maps to a SNOMED CT coded clinical procedure commonly
performed for a given condition. Used by procedure_gen.py to generate
Procedure resources linked to encounters.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcedureDef:
    snomed_code: str
    display: str
    category_snomed: str   # SNOMED procedure category code
    category_display: str
    body_site_code: str | None = None
    body_site_display: str | None = None


# condition_key → list of plausible procedures
PROCEDURES_BY_CONDITION: dict[str, list[ProcedureDef]] = {
    "type2_diabetes": [
        ProcedureDef("73761001",  "Colonoscopy",                                "108290001", "Procedure on nervous system"),
        ProcedureDef("43396009",  "Hemoglobin A1c measurement",                 "108252007", "Laboratory procedure"),
        ProcedureDef("410411004", "Diabetes mellitus education",                "409073007", "Education"),
        ProcedureDef("274804006", "Examination of feet",                        "225317008", "Routine patient examination"),
        ProcedureDef("252416005", "Ophthalmoscopy",                             "363680008", "Imaging procedure"),
    ],
    "hypertension": [
        ProcedureDef("75367002",  "Blood pressure measurement",                 "386053000", "Evaluation procedure"),
        ProcedureDef("252076005", "Electrocardiogram",                          "363679005", "Imaging"),
        ProcedureDef("38341003",  "Hypertension monitoring",                    "225317008", "Routine patient examination"),
    ],
    "asthma": [
        ProcedureDef("23426006",  "Spirometry",                                 "386053000", "Evaluation procedure",
                     "39607008", "Lung structure"),
        ProcedureDef("415068001", "Peak expiratory flow rate measurement",      "386053000", "Evaluation procedure",
                     "39607008", "Lung structure"),
        ProcedureDef("229070002", "Asthma management",                          "409073007", "Education"),
    ],
    "ckd": [
        ProcedureDef("108241001", "Dialysis procedure",                         "108252007", "Laboratory procedure",
                     "64033007", "Kidney structure"),
        ProcedureDef("252416005", "Renal ultrasound",                           "363679005", "Imaging",
                     "64033007", "Kidney structure"),
        ProcedureDef("43396009",  "Creatinine measurement",                     "108252007", "Laboratory procedure"),
    ],
    "hyperlipidemia": [
        ProcedureDef("104567005", "Lipid panel",                                "108252007", "Laboratory procedure"),
        ProcedureDef("171207006", "Dietary advice",                             "409073007", "Education"),
    ],
    "depression": [
        ProcedureDef("228557008", "Cognitive behavioral therapy",               "229070002", "Psychotherapy"),
        ProcedureDef("229070002", "Psychological assessment",                   "386053000", "Evaluation procedure"),
        ProcedureDef("410604004", "Depression screening",                       "386053000", "Evaluation procedure"),
    ],
    "osteoarthritis": [
        ProcedureDef("229070002", "Physical therapy",                           "229070002", "Rehabilitation"),
        ProcedureDef("81723002",  "Joint injection",                            "387713003", "Surgical procedure",
                     "57773001",  "Joint structure"),
        ProcedureDef("312241001", "X-ray of joint",                             "363679005", "Imaging",
                     "57773001",  "Joint structure"),
    ],
    "copd": [
        ProcedureDef("23426006",  "Spirometry",                                 "386053000", "Evaluation procedure",
                     "39607008", "Lung structure"),
        ProcedureDef("229125009", "Pulmonary rehabilitation",                   "229070002", "Rehabilitation",
                     "39607008", "Lung structure"),
        ProcedureDef("182777000", "Cessation of smoking",                       "409073007", "Education"),
    ],
    "atrial_fibrillation": [
        ProcedureDef("252076005", "Electrocardiogram",                          "363679005", "Imaging",
                     "80891009", "Heart structure"),
        ProcedureDef("40701008",  "Echocardiography",                           "363679005", "Imaging",
                     "80891009", "Heart structure"),
        ProcedureDef("180995006", "Cardiac monitoring",                         "386053000", "Evaluation procedure",
                     "80891009", "Heart structure"),
    ],
    "obesity": [
        ProcedureDef("229070002", "Nutritional counseling",                     "409073007", "Education"),
        ProcedureDef("414418009", "Body composition measurement",               "386053000", "Evaluation procedure"),
        ProcedureDef("281686009", "Physical activity assessment",               "386053000", "Evaluation procedure"),
    ],
}

# Procedures appropriate for any encounter regardless of condition
GENERAL_PROCEDURES: list[ProcedureDef] = [
    ProcedureDef("371988002", "Patient history taking",     "225317008", "Routine patient examination"),
    ProcedureDef("5880005",   "Physical examination",       "225317008", "Routine patient examination"),
]

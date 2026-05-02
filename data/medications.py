"""Medication catalog keyed by condition.

Each MedicationDef holds RxNorm coding, dose, and frequency for a drug
commonly prescribed for a given condition. Generators pick 1-2 entries
per active condition to produce MedicationRequest resources.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class MedicationDef:
    rxnorm_code: str
    display: str
    dose_form: str      # e.g. "tablet", "capsule", "inhaler", "solution"
    dose_value: float
    dose_unit: str      # UCUM unit
    frequency: str      # human-readable schedule
    frequency_code: str # FHIR timing.code (BID, QD, etc.)


# condition_key → list of first-line medications
MEDICATIONS_BY_CONDITION: dict[str, list[MedicationDef]] = {
    "type2_diabetes": [
        MedicationDef("860975", "Metformin 500 MG Oral Tablet", "tablet", 500, "mg", "twice daily", "BID"),
        MedicationDef("860999", "Metformin 1000 MG Oral Tablet", "tablet", 1000, "mg", "twice daily", "BID"),
        MedicationDef("593411", "Sitagliptin 100 MG Oral Tablet", "tablet", 100, "mg", "once daily", "QD"),
        MedicationDef("310489", "Glipizide 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
        MedicationDef("1373463", "Empagliflozin 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
    ],
    "hypertension": [
        MedicationDef("29046", "Lisinopril 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("17767", "Amlodipine 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
        MedicationDef("203160", "Losartan 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("866511", "Metoprolol Succinate 50 MG Extended Release Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("153165", "Hydrochlorothiazide 25 MG Oral Tablet", "tablet", 25, "mg", "once daily", "QD"),
    ],
    "hyperlipidemia": [
        MedicationDef("83367", "Atorvastatin 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
        MedicationDef("36567", "Simvastatin 20 MG Oral Tablet", "tablet", 20, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("301542", "Rosuvastatin 20 MG Oral Tablet", "tablet", 20, "mg", "once daily", "QD"),
        MedicationDef("41493", "Pravastatin 40 MG Oral Tablet", "tablet", 40, "mg", "once daily at bedtime", "QHS"),
    ],
    "atrial_fibrillation": [
        MedicationDef("11289", "Warfarin 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
        MedicationDef("1364430", "Apixaban 5 MG Oral Tablet", "tablet", 5, "mg", "twice daily", "BID"),
        MedicationDef("1599538", "Rivaroxaban 20 MG Oral Tablet", "tablet", 20, "mg", "once daily with evening meal", "QD"),
        MedicationDef("866511", "Metoprolol Succinate 25 MG Extended Release Tablet", "tablet", 25, "mg", "once daily", "QD"),
        MedicationDef("309952", "Digoxin 0.125 MG Oral Tablet", "tablet", 0.125, "mg", "once daily", "QD"),
    ],
    "asthma": [
        MedicationDef("745752", "Albuterol 0.083 MG/ML Inhalation Solution", "inhaler", 2.5, "mg", "as needed", "PRN"),
        MedicationDef("895994", "Fluticasone 110 MCG/ACTUAT Metered Dose Inhaler", "inhaler", 110, "ug", "twice daily", "BID"),
        MedicationDef("67544", "Montelukast 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("1552001", "Budesonide 180 MCG/ACTUAT Inhalation Powder", "inhaler", 180, "ug", "twice daily", "BID"),
    ],
    "ckd": [
        MedicationDef("4603", "Furosemide 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
        MedicationDef("29046", "Lisinopril 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
        MedicationDef("309966", "Calcium Acetate 667 MG Oral Capsule", "capsule", 667, "mg", "three times daily with meals", "TID"),
        MedicationDef("204504", "Erythropoietin 4000 UNT/ML Injectable Solution", "solution", 4000, "[iU]/mL", "three times weekly", "3x/week"),
    ],
    "copd": [
        MedicationDef("704459", "Tiotropium 18 MCG Inhalation Capsule", "inhaler", 18, "ug", "once daily", "QD"),
        MedicationDef("7213", "Ipratropium 0.02 MG/ML Inhalation Solution", "inhaler", 500, "ug", "four times daily", "QID"),
        MedicationDef("895994", "Fluticasone 250 MCG/ACTUAT Metered Dose Inhaler", "inhaler", 250, "ug", "twice daily", "BID"),
        MedicationDef("2123111", "Umeclidinium 62.5 MCG/ACTUAT Inhalation Powder", "inhaler", 62.5, "ug", "once daily", "QD"),
    ],
    "depression": [
        MedicationDef("36437", "Sertraline 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("321988", "Escitalopram 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("41493", "Fluoxetine 20 MG Oral Capsule", "capsule", 20, "mg", "once daily", "QD"),
        MedicationDef("42568", "Bupropion 150 MG Extended Release Oral Tablet", "tablet", 150, "mg", "twice daily", "BID"),
    ],
    "osteoarthritis": [
        MedicationDef("161", "Acetaminophen 500 MG Oral Tablet", "tablet", 500, "mg", "every 6 hours as needed", "Q6H PRN"),
        MedicationDef("5640", "Ibuprofen 400 MG Oral Tablet", "tablet", 400, "mg", "three times daily with food", "TID"),
        MedicationDef("140587", "Celecoxib 200 MG Oral Capsule", "capsule", 200, "mg", "once daily", "QD"),
        MedicationDef("1860487", "Diclofenac 1% Topical Gel", "gel", 1, "%", "four times daily topically", "QID"),
    ],
    "obesity": [
        MedicationDef("262455", "Orlistat 120 MG Oral Capsule", "capsule", 120, "mg", "three times daily with meals", "TID"),
        MedicationDef("8152", "Phentermine 37.5 MG Oral Tablet", "tablet", 37.5, "mg", "once daily before breakfast", "QD"),
        MedicationDef("2200027", "Semaglutide 0.5 MG/0.375 ML Subcutaneous Solution", "solution", 0.5, "mg", "once weekly subcutaneous", "QWeek"),
    ],
}

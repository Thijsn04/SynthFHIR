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
        MedicationDef("2395492", "Tirzepatide 2.5 MG/0.5 ML Subcutaneous Solution", "solution", 2.5, "mg", "once weekly subcutaneous", "QWeek"),
    ],
    "anxiety_disorder": [
        MedicationDef("36437", "Sertraline 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("321988", "Escitalopram 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("2670501", "Buspirone 10 MG Oral Tablet", "tablet", 10, "mg", "twice daily", "BID"),
        MedicationDef("321988", "Duloxetine 30 MG Oral Capsule", "capsule", 30, "mg", "once daily", "QD"),
        MedicationDef("2670506", "Lorazepam 0.5 MG Oral Tablet", "tablet", 0.5, "mg", "as needed", "PRN"),
    ],
    "bipolar_disorder": [
        MedicationDef("6448", "Lithium Carbonate 300 MG Oral Capsule", "capsule", 300, "mg", "three times daily", "TID"),
        MedicationDef("647536", "Valproic Acid 250 MG Oral Capsule", "capsule", 250, "mg", "twice daily", "BID"),
        MedicationDef("28439", "Lamotrigine 100 MG Oral Tablet", "tablet", 100, "mg", "twice daily", "BID"),
        MedicationDef("115698", "Quetiapine 100 MG Oral Tablet", "tablet", 100, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("213050", "Aripiprazole 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
    ],
    "ptsd": [
        MedicationDef("36437", "Sertraline 100 MG Oral Tablet", "tablet", 100, "mg", "once daily", "QD"),
        MedicationDef("41493", "Paroxetine 20 MG Oral Tablet", "tablet", 20, "mg", "once daily", "QD"),
        MedicationDef("8124", "Prazosin 1 MG Oral Capsule", "capsule", 1, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("39786", "Venlafaxine 75 MG Extended Release Oral Capsule", "capsule", 75, "mg", "once daily", "QD"),
    ],
    "adhd": [
        MedicationDef("1091149", "Methylphenidate 10 MG Oral Tablet", "tablet", 10, "mg", "twice daily", "BID"),
        MedicationDef("1014590", "Amphetamine/Dextroamphetamine 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("75919", "Atomoxetine 40 MG Oral Capsule", "capsule", 40, "mg", "once daily", "QD"),
        MedicationDef("1091149", "Methylphenidate ER 18 MG Oral Tablet", "tablet", 18, "mg", "once daily in the morning", "QAM"),
    ],
    "schizophrenia": [
        MedicationDef("35636", "Risperidone 2 MG Oral Tablet", "tablet", 2, "mg", "twice daily", "BID"),
        MedicationDef("115698", "Olanzapine 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("213050", "Aripiprazole 15 MG Oral Tablet", "tablet", 15, "mg", "once daily", "QD"),
        MedicationDef("2389003", "Clozapine 100 MG Oral Tablet", "tablet", 100, "mg", "twice daily", "BID"),
        MedicationDef("617312", "Haloperidol 2 MG Oral Tablet", "tablet", 2, "mg", "twice daily", "BID"),
    ],
    "opioid_use_disorder": [
        MedicationDef("864706", "Methadone 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("1655060", "Buprenorphine/Naloxone 8 MG/2 MG Sublingual Film", "tablet", 8, "mg", "once daily", "QD"),
        MedicationDef("1655058", "Naltrexone 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
    ],
    "pneumonia": [
        MedicationDef("723", "Amoxicillin 500 MG Oral Capsule", "capsule", 500, "mg", "three times daily", "TID"),
        MedicationDef("308460", "Azithromycin 250 MG Oral Tablet", "tablet", 250, "mg", "once daily for 5 days", "QD"),
        MedicationDef("82122", "Levofloxacin 750 MG Oral Tablet", "tablet", 750, "mg", "once daily", "QD"),
        MedicationDef("308460", "Doxycycline 100 MG Oral Capsule", "capsule", 100, "mg", "twice daily", "BID"),
    ],
    "uti": [
        MedicationDef("631281", "Nitrofurantoin 100 MG Oral Capsule", "capsule", 100, "mg", "twice daily for 5 days", "BID"),
        MedicationDef("358801", "Trimethoprim/Sulfamethoxazole 160 MG/800 MG Oral Tablet", "tablet", 160, "mg", "twice daily for 3 days", "BID"),
        MedicationDef("309054", "Ciprofloxacin 500 MG Oral Tablet", "tablet", 500, "mg", "twice daily", "BID"),
        MedicationDef("308460", "Fosfomycin 3 GM Oral Powder Packet", "tablet", 3000, "mg", "once", "once"),
    ],
    "acute_mi": [
        MedicationDef("1191", "Aspirin 81 MG Oral Tablet", "tablet", 81, "mg", "once daily", "QD"),
        MedicationDef("83367", "Atorvastatin 80 MG Oral Tablet", "tablet", 80, "mg", "once daily", "QD"),
        MedicationDef("866511", "Metoprolol Succinate 50 MG Extended Release Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("309362", "Clopidogrel 75 MG Oral Tablet", "tablet", 75, "mg", "once daily", "QD"),
        MedicationDef("29046", "Lisinopril 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
    ],
    "ischemic_stroke": [
        MedicationDef("1191", "Aspirin 325 MG Oral Tablet", "tablet", 325, "mg", "once daily", "QD"),
        MedicationDef("309362", "Clopidogrel 75 MG Oral Tablet", "tablet", 75, "mg", "once daily", "QD"),
        MedicationDef("83367", "Atorvastatin 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
        MedicationDef("11289", "Warfarin 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
    ],
    "heart_failure": [
        MedicationDef("29046", "Lisinopril 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
        MedicationDef("200801", "Carvedilol 12.5 MG Oral Tablet", "tablet", 12.5, "mg", "twice daily", "BID"),
        MedicationDef("392464", "Spironolactone 25 MG Oral Tablet", "tablet", 25, "mg", "once daily", "QD"),
        MedicationDef("4603", "Furosemide 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
        MedicationDef("1373463", "Empagliflozin 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
    ],
    "gerd": [
        MedicationDef("7646", "Omeprazole 20 MG Oral Capsule", "capsule", 20, "mg", "once daily before breakfast", "QD"),
        MedicationDef("40790", "Pantoprazole 40 MG Oral Tablet", "tablet", 40, "mg", "once daily before breakfast", "QD"),
        MedicationDef("17128", "Famotidine 20 MG Oral Tablet", "tablet", 20, "mg", "twice daily", "BID"),
        MedicationDef("7646", "Esomeprazole 40 MG Oral Capsule", "capsule", 40, "mg", "once daily", "QD"),
    ],
    "breast_cancer": [
        MedicationDef("10324", "Tamoxifen 20 MG Oral Tablet", "tablet", 20, "mg", "once daily", "QD"),
        MedicationDef("72435", "Letrozole 2.5 MG Oral Tablet", "tablet", 2.5, "mg", "once daily", "QD"),
        MedicationDef("1657981", "Anastrozole 1 MG Oral Tablet", "tablet", 1, "mg", "once daily", "QD"),
        MedicationDef("1656700", "Trastuzumab 440 MG Injectable Solution", "solution", 440, "mg", "every 3 weeks intravenous", "Q3W"),
    ],
    "lung_cancer": [
        MedicationDef("1743330", "Erlotinib 150 MG Oral Tablet", "tablet", 150, "mg", "once daily", "QD"),
        MedicationDef("1860498", "Pembrolizumab 100 MG/4 ML Intravenous Solution", "solution", 200, "mg", "every 3 weeks intravenous", "Q3W"),
        MedicationDef("1860498", "Osimertinib 80 MG Oral Tablet", "tablet", 80, "mg", "once daily", "QD"),
    ],
    "colorectal_cancer": [
        MedicationDef("1100073", "Capecitabine 500 MG Oral Tablet", "tablet", 500, "mg", "twice daily for 14 days every 21 days", "BID"),
        MedicationDef("1860498", "Bevacizumab 25 MG/ML Intravenous Solution", "solution", 5, "mg/kg", "every 2 weeks intravenous", "Q2W"),
    ],
    "prostate_cancer": [
        MedicationDef("351556", "Bicalutamide 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("203461", "Leuprolide 3.75 MG Injectable Suspension", "solution", 3.75, "mg", "once monthly intramuscular", "QMonth"),
        MedicationDef("1860498", "Abiraterone 250 MG Oral Tablet", "tablet", 1000, "mg", "once daily", "QD"),
    ],
    "melanoma": [
        MedicationDef("1860498", "Pembrolizumab 100 MG/4 ML Intravenous Solution", "solution", 200, "mg", "every 3 weeks", "Q3W"),
        MedicationDef("1860498", "Nivolumab 10 MG/ML Intravenous Solution", "solution", 240, "mg", "every 2 weeks", "Q2W"),
        MedicationDef("1860498", "Dabrafenib 75 MG Oral Capsule", "capsule", 75, "mg", "twice daily", "BID"),
    ],
    "parkinsons": [
        MedicationDef("203122", "Levodopa/Carbidopa 25 MG/100 MG Oral Tablet", "tablet", 100, "mg", "three times daily", "TID"),
        MedicationDef("70109", "Pramipexole 0.5 MG Oral Tablet", "tablet", 0.5, "mg", "three times daily", "TID"),
        MedicationDef("1000064", "Ropinirole 1 MG Oral Tablet", "tablet", 1, "mg", "three times daily", "TID"),
        MedicationDef("866514", "Rasagiline 1 MG Oral Tablet", "tablet", 1, "mg", "once daily", "QD"),
    ],
    "alzheimers": [
        MedicationDef("41184", "Donepezil 10 MG Oral Tablet", "tablet", 10, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("139462", "Memantine 10 MG Oral Tablet", "tablet", 10, "mg", "twice daily", "BID"),
        MedicationDef("41184", "Rivastigmine 4.6 MG/24 HR Transdermal Patch", "tablet", 4.6, "mg", "once daily", "QD"),
    ],
    "epilepsy": [
        MedicationDef("28439", "Lamotrigine 100 MG Oral Tablet", "tablet", 100, "mg", "twice daily", "BID"),
        MedicationDef("854873", "Levetiracetam 500 MG Oral Tablet", "tablet", 500, "mg", "twice daily", "BID"),
        MedicationDef("647536", "Valproate Sodium 500 MG Extended Release Oral Tablet", "tablet", 500, "mg", "twice daily", "BID"),
        MedicationDef("254059", "Oxcarbazepine 300 MG Oral Tablet", "tablet", 300, "mg", "twice daily", "BID"),
    ],
    "migraine": [
        MedicationDef("1487731", "Sumatriptan 100 MG Oral Tablet", "tablet", 100, "mg", "as needed for migraine", "PRN"),
        MedicationDef("36789", "Topiramate 100 MG Oral Tablet", "tablet", 100, "mg", "twice daily", "BID"),
        MedicationDef("3498", "Amitriptyline 25 MG Oral Tablet", "tablet", 25, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("1860498", "Erenumab 70 MG/ML Subcutaneous Solution", "solution", 70, "mg", "once monthly", "QMonth"),
    ],
    "rheumatoid_arthritis": [
        MedicationDef("105585", "Methotrexate 2.5 MG Oral Tablet", "tablet", 15, "mg", "once weekly", "QWeek"),
        MedicationDef("153378", "Hydroxychloroquine 200 MG Oral Tablet", "tablet", 200, "mg", "twice daily", "BID"),
        MedicationDef("9524", "Prednisone 5 MG Oral Tablet", "tablet", 5, "mg", "once daily", "QD"),
        MedicationDef("1860498", "Adalimumab 40 MG/0.4 ML Subcutaneous Solution", "solution", 40, "mg", "every 2 weeks subcutaneous", "Q2W"),
        MedicationDef("1860498", "Etanercept 50 MG/ML Subcutaneous Solution", "solution", 50, "mg", "once weekly subcutaneous", "QWeek"),
    ],
    "lupus": [
        MedicationDef("153378", "Hydroxychloroquine 200 MG Oral Tablet", "tablet", 200, "mg", "twice daily", "BID"),
        MedicationDef("9524", "Prednisone 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
        MedicationDef("41493", "Mycophenolate Mofetil 500 MG Oral Tablet", "tablet", 500, "mg", "twice daily", "BID"),
        MedicationDef("1860498", "Belimumab 120 MG/ML Intravenous Solution", "solution", 10, "mg/kg", "monthly intravenous", "QMonth"),
    ],
    "multiple_sclerosis": [
        MedicationDef("1860498", "Interferon Beta-1a 30 MCG Intramuscular Solution", "solution", 30, "ug", "once weekly intramuscular", "QWeek"),
        MedicationDef("1860498", "Glatiramer Acetate 20 MG/ML Subcutaneous Solution", "solution", 20, "mg", "once daily subcutaneous", "QD"),
        MedicationDef("1860498", "Ocrelizumab 300 MG/10 ML Intravenous Solution", "solution", 600, "mg", "every 6 months intravenous", "Q6Month"),
        MedicationDef("1860498", "Dimethyl Fumarate 240 MG Oral Capsule", "capsule", 240, "mg", "twice daily", "BID"),
    ],
    "fibromyalgia": [
        MedicationDef("321988", "Duloxetine 60 MG Oral Capsule", "capsule", 60, "mg", "once daily", "QD"),
        MedicationDef("187832", "Pregabalin 150 MG Oral Capsule", "capsule", 150, "mg", "twice daily", "BID"),
        MedicationDef("3498", "Amitriptyline 25 MG Oral Tablet", "tablet", 25, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("39786", "Milnacipran 50 MG Oral Tablet", "tablet", 50, "mg", "twice daily", "BID"),
    ],
    "crohns_disease": [
        MedicationDef("1860498", "Mesalamine 800 MG Oral Tablet", "tablet", 800, "mg", "three times daily", "TID"),
        MedicationDef("108831", "Azathioprine 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("1860498", "Infliximab 100 MG Intravenous Solution", "solution", 5, "mg/kg", "induction then every 8 weeks", "Q8W"),
        MedicationDef("9524", "Prednisone 40 MG Oral Tablet", "tablet", 40, "mg", "once daily tapering", "QD"),
        MedicationDef("1860498", "Vedolizumab 300 MG Intravenous Solution", "solution", 300, "mg", "every 8 weeks", "Q8W"),
    ],
    "ibs": [
        MedicationDef("3498", "Dicyclomine 20 MG Oral Capsule", "capsule", 20, "mg", "four times daily", "QID"),
        MedicationDef("1860498", "Linaclotide 145 MCG Oral Capsule", "capsule", 145, "ug", "once daily before breakfast", "QD"),
        MedicationDef("321988", "Amitriptyline 10 MG Oral Tablet", "tablet", 10, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("36437", "Sertraline 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
    ],
    "hypothyroidism": [
        MedicationDef("10582", "Levothyroxine 50 MCG Oral Tablet", "tablet", 50, "ug", "once daily", "QD"),
        MedicationDef("10582", "Levothyroxine 100 MCG Oral Tablet", "tablet", 100, "ug", "once daily", "QD"),
        MedicationDef("10582", "Levothyroxine 75 MCG Oral Tablet", "tablet", 75, "ug", "once daily", "QD"),
    ],
    "hyperthyroidism": [
        MedicationDef("41493", "Methimazole 10 MG Oral Tablet", "tablet", 10, "mg", "three times daily", "TID"),
        MedicationDef("866511", "Propranolol 20 MG Oral Tablet", "tablet", 20, "mg", "three times daily", "TID"),
        MedicationDef("41493", "Propylthiouracil 50 MG Oral Tablet", "tablet", 50, "mg", "three times daily", "TID"),
    ],
    "type1_diabetes": [
        MedicationDef("274783", "Insulin Glargine 100 UNT/ML Injectable Solution", "solution", 20, "[iU]", "once daily subcutaneous", "QD"),
        MedicationDef("865098", "Insulin Aspart 100 UNT/ML Injectable Solution", "solution", 4, "[iU]", "three times daily with meals subcutaneous", "TID"),
        MedicationDef("274784", "Insulin Detemir 100 UNT/ML Injectable Solution", "solution", 10, "[iU]", "once daily subcutaneous", "QD"),
        MedicationDef("865098", "Insulin Lispro 100 UNT/ML Injectable Solution", "solution", 4, "[iU]", "three times daily with meals subcutaneous", "TID"),
    ],
    "gout": [
        MedicationDef("30212", "Allopurinol 300 MG Oral Tablet", "tablet", 300, "mg", "once daily", "QD"),
        MedicationDef("41493", "Colchicine 0.6 MG Oral Tablet", "tablet", 0.6, "mg", "twice daily", "BID"),
        MedicationDef("5640", "Indomethacin 25 MG Oral Capsule", "capsule", 25, "mg", "three times daily with food", "TID"),
        MedicationDef("41493", "Febuxostat 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
    ],
    "hiv": [
        MedicationDef("1721481", "Tenofovir/Emtricitabine 300 MG/200 MG Oral Tablet", "tablet", 1, "tablet", "once daily", "QD"),
        MedicationDef("1747691", "Dolutegravir 50 MG Oral Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("1721481", "Bictegravir/Tenofovir/Emtricitabine Oral Tablet", "tablet", 1, "tablet", "once daily", "QD"),
    ],
    "hepatitis_c": [
        MedicationDef("1860498", "Sofosbuvir/Ledipasvir 400 MG/90 MG Oral Tablet", "tablet", 1, "tablet", "once daily for 12 weeks", "QD"),
        MedicationDef("1860498", "Glecaprevir/Pibrentasvir 100 MG/40 MG Oral Tablet", "tablet", 3, "tablet", "once daily for 8-12 weeks", "QD"),
    ],
    "covid19_long": [
        MedicationDef("1191", "Aspirin 81 MG Oral Tablet", "tablet", 81, "mg", "once daily", "QD"),
        MedicationDef("187832", "Pregabalin 75 MG Oral Capsule", "capsule", 75, "mg", "twice daily", "BID"),
        MedicationDef("321988", "Duloxetine 30 MG Oral Capsule", "capsule", 30, "mg", "once daily", "QD"),
    ],
    "sleep_apnea": [
        MedicationDef("8152", "Modafinil 200 MG Oral Tablet", "tablet", 200, "mg", "once daily in the morning", "QAM"),
        MedicationDef("153165", "Acetazolamide 250 MG Oral Tablet", "tablet", 250, "mg", "twice daily", "BID"),
    ],
    "pulmonary_hypertension": [
        MedicationDef("1860498", "Sildenafil 20 MG Oral Tablet", "tablet", 20, "mg", "three times daily", "TID"),
        MedicationDef("1860498", "Bosentan 125 MG Oral Tablet", "tablet", 125, "mg", "twice daily", "BID"),
        MedicationDef("1860498", "Tadalafil 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
    ],
    "coronary_artery_disease": [
        MedicationDef("1191", "Aspirin 81 MG Oral Tablet", "tablet", 81, "mg", "once daily", "QD"),
        MedicationDef("83367", "Atorvastatin 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
        MedicationDef("866511", "Metoprolol Succinate 50 MG Extended Release Tablet", "tablet", 50, "mg", "once daily", "QD"),
        MedicationDef("314076", "Nitroglycerin 0.4 MG/ACTUAT Sublingual Spray", "inhaler", 0.4, "mg", "as needed for chest pain", "PRN"),
        MedicationDef("29046", "Lisinopril 10 MG Oral Tablet", "tablet", 10, "mg", "once daily", "QD"),
    ],
    "peripheral_artery_disease": [
        MedicationDef("1191", "Aspirin 81 MG Oral Tablet", "tablet", 81, "mg", "once daily", "QD"),
        MedicationDef("309362", "Clopidogrel 75 MG Oral Tablet", "tablet", 75, "mg", "once daily", "QD"),
        MedicationDef("83367", "Atorvastatin 40 MG Oral Tablet", "tablet", 40, "mg", "once daily", "QD"),
        MedicationDef("203461", "Cilostazol 100 MG Oral Tablet", "tablet", 100, "mg", "twice daily", "BID"),
    ],
    "anemia": [
        MedicationDef("9983", "Ferrous Sulfate 325 MG Oral Tablet", "tablet", 325, "mg", "once daily", "QD"),
        MedicationDef("4223", "Folic Acid 1 MG Oral Tablet", "tablet", 1, "mg", "once daily", "QD"),
        MedicationDef("204504", "Erythropoietin 10000 UNT/ML Injectable Solution", "solution", 10000, "[iU]", "three times weekly", "3x/week"),
    ],
    "chronic_pain": [
        MedicationDef("41493", "Gabapentin 300 MG Oral Capsule", "capsule", 300, "mg", "three times daily", "TID"),
        MedicationDef("187832", "Pregabalin 75 MG Oral Capsule", "capsule", 75, "mg", "twice daily", "BID"),
        MedicationDef("161", "Acetaminophen 500 MG Oral Tablet", "tablet", 500, "mg", "every 6 hours as needed", "Q6H PRN"),
        MedicationDef("3498", "Amitriptyline 25 MG Oral Tablet", "tablet", 25, "mg", "once daily at bedtime", "QHS"),
        MedicationDef("321988", "Duloxetine 60 MG Oral Capsule", "capsule", 60, "mg", "once daily", "QD"),
    ],
}

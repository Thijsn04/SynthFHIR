"""ServiceRequest generator.

Generates lab/imaging/referral orders linked to an encounter. Each active
condition contributes 1 condition-appropriate order. A general health
maintenance order is always included.

Each ServiceRequest includes a `produces_obs_keys` list — the observation catalog
keys that this order is expected to produce. cohort_gen.py uses this to populate
the basedOn reference on the generated Observation resources.

Output keys: id, patient_id, encounter_id, practitioner_id, status, intent,
snomed_code, display, category_code, category_display, authored_on,
priority, reason_snomed, reason_display, produces_obs_keys.
"""
import random
from datetime import date, timedelta

from generators._rng import new_uuid

# condition_key → SNOMED code (used to look up orders by condition)
_CONDITION_KEY_TO_SNOMED: dict[str, str] = {
    "type2_diabetes":        "44054006",
    "hypertension":          "38341003",
    "hyperlipidemia":        "55822004",
    "atrial_fibrillation":   "49436004",
    "asthma":                "195967001",
    "ckd":                   "709044004",
    "copd":                  "13645005",
    "depression":            "35489007",
    "osteoarthritis":        "396275006",
    "obesity":               "414916001",
    "anxiety_disorder":      "197480006",
    "bipolar_disorder":      "13746004",
    "ptsd":                  "47505003",
    "adhd":                  "406506008",
    "schizophrenia":         "58214004",
    "opioid_use_disorder":   "762176005",
    "pneumonia":             "233604007",
    "uti":                   "68566005",
    "acute_mi":              "57054005",
    "ischemic_stroke":       "422504002",
    "heart_failure":         "84114007",
    "gerd":                  "235595009",
    "breast_cancer":         "254837009",
    "lung_cancer":           "254637007",
    "colorectal_cancer":     "363406005",
    "prostate_cancer":       "399068003",
    "melanoma":              "372244006",
    "parkinsons":            "49049000",
    "alzheimers":            "26929004",
    "epilepsy":              "84757009",
    "migraine":              "37796009",
    "rheumatoid_arthritis":  "69896004",
    "lupus":                 "55464009",
    "multiple_sclerosis":    "24700007",
    "fibromyalgia":          "203082005",
    "crohns_disease":        "34000006",
    "ibs":                   "10743008",
    "hypothyroidism":        "40930008",
    "hyperthyroidism":       "34486009",
    "type1_diabetes":        "46635009",
    "gout":                  "90560007",
    "hiv":                   "86406008",
    "hepatitis_c":           "50711007",
    "covid19_long":          "1119303003",
    "sleep_apnea":           "73430006",
    "pulmonary_hypertension":"70995007",
    "coronary_artery_disease":"53741008",
    "peripheral_artery_disease":"400047006",
    "anemia":                "271737000",
    "chronic_pain":          "82423001",
}

_SNOMED_TO_KEY: dict[str, str] = {v: k for k, v in _CONDITION_KEY_TO_SNOMED.items()}

# (snomed_code, display, category_code, category_display, produces_obs_keys)
_OrderTuple = tuple[str, str, str, str, list[str]]

_ORDERS_BY_CONDITION: dict[str, list[_OrderTuple]] = {
    "type2_diabetes": [
        ("104177005", "Blood glucose level",               "108252007", "Laboratory procedure", ["blood_glucose"]),
        ("43396009",  "Hemoglobin A1c measurement",        "108252007", "Laboratory procedure", ["hba1c"]),
        ("306206005", "Referral to ophthalmology service", "3457005",   "Patient referral",     []),
        ("166712009", "Urine albumin-to-creatinine ratio", "108252007", "Laboratory procedure", ["urine_acr"]),
    ],
    "hypertension": [
        ("104177005", "Blood pressure monitoring",         "108252007", "Laboratory procedure", []),
        ("252076005", "12-lead ECG",                       "363679005", "Imaging",              []),
        ("306206005", "Referral to cardiology service",    "3457005",   "Patient referral",     []),
    ],
    "hyperlipidemia": [
        ("104567005", "Lipid panel",                       "108252007", "Laboratory procedure", ["cholesterol_total", "ldl", "hdl"]),
        ("306206005", "Referral to nutrition service",     "3457005",   "Patient referral",     []),
    ],
    "atrial_fibrillation": [
        ("252076005", "Electrocardiogram",                 "363679005", "Imaging",              []),
        ("40701008",  "Echocardiography",                  "363679005", "Imaging",              []),
        ("306206005", "Referral to cardiology service",    "3457005",   "Patient referral",     []),
    ],
    "asthma": [
        ("23426006",  "Spirometry",                        "108252007", "Laboratory procedure", ["fev1"]),
        ("306206005", "Referral to pulmonology service",   "3457005",   "Patient referral",     []),
    ],
    "ckd": [
        ("166712009", "Creatinine and eGFR measurement",  "108252007", "Laboratory procedure", ["creatinine", "egfr"]),
        ("252416005", "Renal ultrasound",                  "363679005", "Imaging",              []),
        ("306206005", "Referral to nephrology service",    "3457005",   "Patient referral",     []),
        ("166712009", "Urine albumin-to-creatinine ratio", "108252007", "Laboratory procedure", ["urine_acr"]),
    ],
    "copd": [
        ("23426006",  "Spirometry",                        "108252007", "Laboratory procedure", ["fev1"]),
        ("306206005", "Referral to pulmonology service",   "3457005",   "Patient referral",     []),
    ],
    "depression": [
        ("410604004", "Depression screening",              "108252007", "Laboratory procedure", ["phq9"]),
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral",     []),
    ],
    "osteoarthritis": [
        ("312241001", "X-ray joint",                       "363679005", "Imaging",              []),
        ("306206005", "Referral to orthopedics service",   "3457005",   "Patient referral",     []),
    ],
    "obesity": [
        ("281686009", "Physical activity assessment",      "108252007", "Laboratory procedure", []),
        ("306206005", "Referral to nutrition service",     "3457005",   "Patient referral",     []),
    ],
    "anxiety_disorder": [
        ("273830002", "Anxiety screening",                 "108252007", "Laboratory procedure", ["gad7"]),
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral",     []),
    ],
    "bipolar_disorder": [
        ("410604004", "Mood disorder screening",           "108252007", "Laboratory procedure", ["phq9"]),
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral",     []),
    ],
    "ptsd": [
        ("410604004", "PTSD screening",                    "108252007", "Laboratory procedure", ["phq9", "gad7"]),
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral",     []),
    ],
    "adhd": [
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral",     []),
    ],
    "schizophrenia": [
        ("306206005", "Referral to psychiatry service",    "3457005",   "Patient referral",     []),
    ],
    "opioid_use_disorder": [
        ("306206005", "Referral to addiction medicine",    "3457005",   "Patient referral",     []),
        ("45036005",  "Urine drug screen",                 "108252007", "Laboratory procedure", []),
    ],
    "pneumonia": [
        ("399208008", "Chest X-ray",                       "363679005", "Imaging",              []),
        ("104177005", "CBC with differential",             "108252007", "Laboratory procedure", ["hemoglobin", "platelet_count"]),
    ],
    "uti": [
        ("167217005", "Urinalysis",                        "108252007", "Laboratory procedure", []),
        ("117010004", "Urine culture",                     "108252007", "Laboratory procedure", []),
    ],
    "acute_mi": [
        ("252076005", "12-lead ECG",                       "363679005", "Imaging",              []),
        ("104177005", "Cardiac troponin measurement",      "108252007", "Laboratory procedure", []),
        ("40701008",  "Echocardiography",                  "363679005", "Imaging",              []),
    ],
    "ischemic_stroke": [
        ("241566009", "CT brain without contrast",         "363679005", "Imaging",              []),
        ("306206005", "Referral to neurology service",     "3457005",   "Patient referral",     []),
    ],
    "heart_failure": [
        ("40701008",  "Echocardiography",                  "363679005", "Imaging",              []),
        ("252076005", "12-lead ECG",                       "363679005", "Imaging",              []),
        ("104177005", "BNP measurement",                   "108252007", "Laboratory procedure", []),
    ],
    "gerd": [
        ("73761001",  "Esophagogastroduodenoscopy",        "363679005", "Imaging",              []),
        ("306206005", "Referral to gastroenterology",      "3457005",   "Patient referral",     []),
    ],
    "breast_cancer": [
        ("71651007",  "Mammography",                       "363679005", "Imaging",              []),
        ("306206005", "Referral to oncology service",      "3457005",   "Patient referral",     []),
        ("104177005", "CBC",                               "108252007", "Laboratory procedure", ["hemoglobin"]),
    ],
    "lung_cancer": [
        ("399208008", "CT chest",                          "363679005", "Imaging",              []),
        ("306206005", "Referral to oncology service",      "3457005",   "Patient referral",     []),
        ("23426006",  "Spirometry",                        "108252007", "Laboratory procedure", ["fev1"]),
    ],
    "colorectal_cancer": [
        ("73761001",  "Colonoscopy",                       "363679005", "Imaging",              []),
        ("306206005", "Referral to oncology service",      "3457005",   "Patient referral",     []),
        ("104177005", "CBC",                               "108252007", "Laboratory procedure", ["hemoglobin"]),
    ],
    "prostate_cancer": [
        ("104177005", "PSA measurement",                   "108252007", "Laboratory procedure", []),
        ("306206005", "Referral to urology service",       "3457005",   "Patient referral",     []),
    ],
    "melanoma": [
        ("240830005", "Dermatoscopy",                      "363679005", "Imaging",              []),
        ("306206005", "Referral to dermatology service",   "3457005",   "Patient referral",     []),
    ],
    "parkinsons": [
        ("306206005", "Referral to neurology service",     "3457005",   "Patient referral",     []),
        ("241566009", "MRI brain",                         "363679005", "Imaging",              []),
    ],
    "alzheimers": [
        ("306206005", "Referral to neurology service",     "3457005",   "Patient referral",     []),
        ("241566009", "MRI brain",                         "363679005", "Imaging",              []),
    ],
    "epilepsy": [
        ("54550000",  "EEG",                               "363679005", "Imaging",              []),
        ("306206005", "Referral to neurology service",     "3457005",   "Patient referral",     []),
    ],
    "migraine": [
        ("306206005", "Referral to neurology service",     "3457005",   "Patient referral",     []),
    ],
    "rheumatoid_arthritis": [
        ("312241001", "X-ray joints",                      "363679005", "Imaging",              []),
        ("306206005", "Referral to rheumatology service",  "3457005",   "Patient referral",     []),
        ("104177005", "CBC and CRP",                       "108252007", "Laboratory procedure", ["hemoglobin"]),
    ],
    "lupus": [
        ("166712009", "ANA panel",                         "108252007", "Laboratory procedure", ["creatinine"]),
        ("306206005", "Referral to rheumatology service",  "3457005",   "Patient referral",     []),
        ("104177005", "CBC",                               "108252007", "Laboratory procedure", ["hemoglobin"]),
    ],
    "multiple_sclerosis": [
        ("241566009", "MRI brain and spine",               "363679005", "Imaging",              []),
        ("306206005", "Referral to neurology service",     "3457005",   "Patient referral",     []),
    ],
    "fibromyalgia": [
        ("410604004", "Pain and depression screening",     "108252007", "Laboratory procedure", ["phq9"]),
        ("306206005", "Referral to rheumatology service",  "3457005",   "Patient referral",     []),
    ],
    "crohns_disease": [
        ("73761001",  "Colonoscopy",                       "363679005", "Imaging",              []),
        ("306206005", "Referral to gastroenterology",      "3457005",   "Patient referral",     []),
        ("104177005", "CBC and CRP",                       "108252007", "Laboratory procedure", ["hemoglobin"]),
    ],
    "ibs": [
        ("306206005", "Referral to gastroenterology",      "3457005",   "Patient referral",     []),
        ("73761001",  "Colonoscopy",                       "363679005", "Imaging",              []),
    ],
    "hypothyroidism": [
        ("104177005", "TSH measurement",                   "108252007", "Laboratory procedure", ["tsh_high"]),
        ("306206005", "Referral to endocrinology",         "3457005",   "Patient referral",     []),
    ],
    "hyperthyroidism": [
        ("104177005", "TSH measurement",                   "108252007", "Laboratory procedure", ["tsh"]),
        ("306206005", "Referral to endocrinology",         "3457005",   "Patient referral",     []),
    ],
    "type1_diabetes": [
        ("104177005", "Blood glucose level",               "108252007", "Laboratory procedure", ["blood_glucose"]),
        ("43396009",  "Hemoglobin A1c measurement",        "108252007", "Laboratory procedure", ["hba1c"]),
        ("166712009", "Urine albumin-to-creatinine ratio", "108252007", "Laboratory procedure", ["urine_acr"]),
    ],
    "gout": [
        ("166712009", "Uric acid measurement",             "108252007", "Laboratory procedure", ["creatinine"]),
        ("312241001", "X-ray joint",                       "363679005", "Imaging",              []),
    ],
    "hiv": [
        ("104177005", "HIV viral load",                    "108252007", "Laboratory procedure", []),
        ("306206005", "Referral to infectious disease",    "3457005",   "Patient referral",     []),
        ("104177005", "CBC",                               "108252007", "Laboratory procedure", ["hemoglobin"]),
    ],
    "hepatitis_c": [
        ("104177005", "Hepatitis C viral load",            "108252007", "Laboratory procedure", ["alt"]),
        ("306206005", "Referral to gastroenterology",      "3457005",   "Patient referral",     []),
    ],
    "covid19_long": [
        ("306206005", "Referral to post-COVID clinic",     "3457005",   "Patient referral",     []),
        ("23426006",  "Spirometry",                        "108252007", "Laboratory procedure", ["fev1"]),
    ],
    "sleep_apnea": [
        ("241566009", "Sleep study (polysomnography)",     "363679005", "Imaging",              []),
        ("306206005", "Referral to sleep medicine",        "3457005",   "Patient referral",     []),
    ],
    "pulmonary_hypertension": [
        ("40701008",  "Echocardiography",                  "363679005", "Imaging",              []),
        ("306206005", "Referral to pulmonology service",   "3457005",   "Patient referral",     []),
    ],
    "coronary_artery_disease": [
        ("252076005", "Stress ECG",                        "363679005", "Imaging",              []),
        ("104567005", "Lipid panel",                       "108252007", "Laboratory procedure", ["cholesterol_total", "ldl", "hdl"]),
        ("306206005", "Referral to cardiology service",    "3457005",   "Patient referral",     []),
    ],
    "peripheral_artery_disease": [
        ("241566009", "Ankle-brachial index (ABI)",        "363679005", "Imaging",              []),
        ("306206005", "Referral to vascular surgery",      "3457005",   "Patient referral",     []),
    ],
    "anemia": [
        ("104177005", "CBC with differential",             "108252007", "Laboratory procedure", ["hemoglobin", "platelet_count"]),
        ("306206005", "Referral to hematology",            "3457005",   "Patient referral",     []),
    ],
    "chronic_pain": [
        ("410604004", "Pain screening",                    "108252007", "Laboratory procedure", ["phq9"]),
        ("306206005", "Referral to pain management",       "3457005",   "Patient referral",     []),
    ],
}

_GENERAL_ORDER: _OrderTuple = (
    "310249009", "Complete blood count", "108252007", "Laboratory procedure",
    ["hemoglobin", "platelet_count"],
)
_PRIORITIES = [("routine", 0.7), ("urgent", 0.2), ("asap", 0.1)]


def generate_service_requests_for_encounter(
    patient_id: str,
    encounter_id: str,
    practitioner_id: str,
    conditions: list[dict],
    authored_on: str | None = None,
) -> list[dict]:
    """Return 1–3 ServiceRequest records for the given encounter."""
    if authored_on is None:
        days_ago = random.randint(0, 30)
        authored_on = (date.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    selected: list[_OrderTuple] = [_GENERAL_ORDER]

    for cond in conditions:
        key = cond.get("condition_key") or _SNOMED_TO_KEY.get(cond.get("snomed_code", ""))
        if not key:
            continue
        pool = _ORDERS_BY_CONDITION.get(key, [])
        if pool:
            selected.append(random.choice(pool))

    # Deduplicate by SNOMED code
    seen: set[str] = set()
    unique: list[_OrderTuple] = []
    for item in selected:
        if item[0] not in seen:
            seen.add(item[0])
            unique.append(item)

    priority = random.choices(
        [p[0] for p in _PRIORITIES],
        weights=[p[1] for p in _PRIORITIES],
        k=1,
    )[0]

    results = []
    for snomed_code, display, cat_code, cat_display, produces_obs_keys in unique:
        reason = next(
            (c for c in conditions if c.get("clinical_status") == "active"),
            None,
        )
        results.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "practitioner_id": practitioner_id,
            "status": "active",
            "intent": "order",
            "snomed_code": snomed_code,
            "display": display,
            "category_code": cat_code,
            "category_display": cat_display,
            "authored_on": authored_on,
            "priority": priority,
            "reason_snomed": reason["snomed_code"] if reason else None,
            "reason_display": reason["display"] if reason else None,
            "produces_obs_keys": produces_obs_keys,
        })

    return results


def build_sr_basedOn_map(service_requests: list[dict]) -> dict[str, str]:
    """Return a mapping obs_key → ServiceRequest.id for use by the observation generator.

    When multiple SRs produce the same obs_key, the last one wins (arbitrary but
    deterministic within a single encounter).
    """
    mapping: dict[str, str] = {}
    for sr in service_requests:
        for obs_key in sr.get("produces_obs_keys", []):
            mapping[obs_key] = sr["id"]
    return mapping

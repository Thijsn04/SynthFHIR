import random
import uuid
from datetime import date, timedelta

# (snomed_code, display, category, criticality)
_ALLERGIES = [
    ("372687004", "Penicillin",      "medication",  "high"),
    ("387406002", "Sulfonamide",     "medication",  "low"),
    ("387458008", "Aspirin",         "medication",  "low"),
    ("372665008", "NSAID",           "medication",  "low"),
    ("256349002", "Peanut",          "food",        "high"),
    ("256350002", "Tree nut",        "food",        "high"),
    ("227493005", "Cashew nut",      "food",        "high"),
    ("226760005", "Dairy product",   "food",        "low"),
    ("102263004", "Eggs",            "food",        "low"),
    ("1003755004","Latex",           "environment", "low"),
    ("288328004", "Bee venom",       "environment", "high"),
    ("256417003", "House dust mite", "environment", "low"),
]

# (snomed_code, display, default_severity)
_REACTIONS = [
    ("247472004", "Hives",       "mild"),
    ("39579001",  "Anaphylaxis", "severe"),
    ("271807003", "Skin rash",   "mild"),
    ("422587007", "Nausea",      "mild"),
    ("267036007", "Dyspnea",     "moderate"),
    ("781099009", "Angioedema",  "moderate"),
    ("64305001",  "Urticaria",   "moderate"),
]


def generate_allergies_for_patient(patient_id: str, practitioner_id: str) -> list[dict]:
    """70% of patients have no allergies; the rest have 1-3."""
    if random.random() < 0.70:
        return []

    chosen = random.sample(_ALLERGIES, k=random.randint(1, 3))
    return [_make(patient_id, practitioner_id, a) for a in chosen]


def _make(patient_id: str, practitioner_id: str, allergy: tuple) -> dict:
    code, display, category, criticality = allergy
    reaction_code, reaction_display, reaction_severity = random.choice(_REACTIONS)
    onset = date.today() - timedelta(days=random.randint(365, 7300))

    return {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "practitioner_id": practitioner_id,
        "type": "allergy",
        "substance_code": code,
        "substance_display": display,
        "category": category,
        "criticality": criticality,
        "reaction_code": reaction_code,
        "reaction_display": reaction_display,
        "reaction_severity": reaction_severity,
        "onset_date": onset.strftime("%Y-%m-%d"),
        "recorded_date": (onset + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
    }

"""FamilyMemberHistory generator.

Generates hereditary condition history for 1–3 family members of a patient.
Conditions are drawn from a catalog of heritable diseases. Relationships use
HL7 v3 RoleCode values.

Output keys: id, patient_id, relationship_code, relationship_display, name,
sex, deceased, conditions[{snomed_code, icd10_code, display}].
"""
import random

from generators._rng import fake, new_uuid

_HEREDITARY_CONDITIONS: list[tuple[str, str, str]] = [
    ("44054006",  "E11.9",   "Type 2 Diabetes Mellitus"),
    ("38341003",  "I10",     "Essential Hypertension"),
    ("55822004",  "E78.5",   "Hyperlipidemia"),
    ("22298006",  "I21.9",   "Myocardial Infarction"),
    ("64572001",  "I63.9",   "Ischemic Stroke"),
    ("363346000", "C34.90",  "Primary Malignant Neoplasm of Lung"),
    ("254837009", "C50.919", "Primary Malignant Neoplasm of Breast"),
    ("53741008",  "I25.10",  "Coronary Artery Disease"),
    ("49436004",  "I48.91",  "Atrial Fibrillation"),
    ("13645005",  "J44.1",   "COPD"),
    ("35489007",  "F32.9",   "Major Depressive Disorder"),
    ("40930008",  "E03.9",   "Hypothyroidism"),
    ("396275006", "M19.90",  "Osteoarthritis"),
]

# (HL7 v3 RoleCode, display, sex — None means random)
_RELATIONSHIPS: list[tuple[str, str, str | None]] = [
    ("FTH",  "father",               "male"),
    ("MTH",  "mother",               "female"),
    ("GFTH", "paternal grandfather", "male"),
    ("GMTH", "maternal grandmother", "female"),
    ("SIB",  "sibling",              None),
]


def generate_family_member_history(patient_id: str) -> list[dict]:
    members: list[dict] = []
    num = random.randint(1, 3)
    used: set[str] = set()

    for _ in range(num):
        options = [r for r in _RELATIONSHIPS if r[0] not in used]
        if not options:
            break
        rel_code, rel_display, rel_sex = random.choice(options)
        used.add(rel_code)

        sex: str = rel_sex or random.choice(["male", "female"])
        num_conds = random.randint(1, 2)
        cond_picks = random.sample(_HEREDITARY_CONDITIONS, min(num_conds, len(_HEREDITARY_CONDITIONS)))

        first = fake.first_name_male() if sex == "male" else fake.first_name_female()
        members.append({
            "id": new_uuid(),
            "patient_id": patient_id,
            "relationship_code": rel_code,
            "relationship_display": rel_display,
            "name": f"{first} {fake.last_name()}",
            "sex": sex,
            "deceased": random.random() < 0.30,
            "conditions": [
                {"snomed_code": sc, "icd10_code": ic, "display": disp}
                for sc, ic, disp in cond_picks
            ],
        })

    return members

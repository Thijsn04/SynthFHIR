"""R5 FamilyMemberHistory resource mapper. Spec: https://hl7.org/fhir/R5/familymemberhistory.html

R5 is structurally identical to R4 for FamilyMemberHistory; only the profile URL differs.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/FamilyMemberHistory"

_SEX_CODES: dict[str, tuple[str, str]] = {
    "male":   ("male",   "Male"),
    "female": ("female", "Female"),
}


def map_family_member_history(fmh: dict, us_core: bool = False) -> dict:
    sex = fmh.get("sex", "unknown")
    sex_code, sex_display = _SEX_CODES.get(sex, ("unknown", "Unknown"))

    resource: dict = {
        "resourceType": "FamilyMemberHistory",
        "id": fmh["id"],
        "meta": build_meta(_PROFILE),
        "status": "completed",
        "patient": ref("Patient", fmh["patient_id"]),
        "relationship": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": fmh["relationship_code"],
                    "display": fmh["relationship_display"],
                }
            ],
            "text": fmh["relationship_display"],
        },
        "sex": {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/administrative-gender",
                    "code": sex_code,
                    "display": sex_display,
                }
            ],
            "text": sex_display,
        },
        "deceasedBoolean": fmh.get("deceased", False),
        "condition": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": c["snomed_code"],
                            "display": c["display"],
                        },
                        {
                            "system": "http://hl7.org/fhir/sid/icd-10-cm",
                            "code": c["icd10_code"],
                            "display": c["display"],
                        },
                    ],
                    "text": c["display"],
                }
            }
            for c in fmh.get("conditions", [])
        ],
    }

    if fmh.get("name"):
        resource["name"] = fmh["name"]

    return resource

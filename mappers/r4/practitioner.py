"""R4 Practitioner resource mapper. Spec: https://hl7.org/fhir/R4/practitioner.html"""
from mappers._helpers import build_meta

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Practitioner"


def map_practitioner(p: dict) -> dict:
    return {
        "resourceType": "Practitioner",
        "id": p["id"],
        "meta": build_meta(_PROFILE),
        # US NPI as the primary identifier
        "identifier": [{"system": "http://hl7.org/fhir/sid/us-npi", "value": p["npi"]}],
        "active": True,
        "name": [
            {
                "use": "official",
                "family": p["last_name"],
                "given": [p["first_name"]],
                "prefix": [p["prefix"]],
            }
        ],
        "telecom": [
            {"system": "phone", "value": p["phone"], "use": "work"},
            {"system": "email", "value": p["email"], "use": "work"},
        ],
        "gender": p["gender"],
        # HL7 v2-0360 qualification code (MD, DO, NP, PA)
        "qualification": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                            "code": p["qualification_code"],
                            "display": p["qualification_display"],
                        }
                    ],
                    "text": p["qualification_display"],
                }
            }
        ],
    }

"""R5 PractitionerRole resource mapper. Spec: https://hl7.org/fhir/R5/practitionerrole.html

R5 is structurally identical to R4 for PractitionerRole; only the profile URL differs.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/PractitionerRole"


def map_practitioner_role(pr: dict) -> dict:
    return {
        "resourceType": "PractitionerRole",
        "id": pr["id"],
        "meta": build_meta(_PROFILE),
        "active": pr["active"],
        "practitioner": ref("Practitioner", pr["practitioner_id"]),
        "organization": ref("Organization", pr["organization_id"]),
        "code": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "309343006",
                        "display": pr["role_display"],
                    }
                ],
                "text": pr["role_display"],
            }
        ],
        "specialty": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": pr["specialty_code"],
                        "display": pr["specialty_display"],
                    }
                ],
                "text": pr["specialty_display"],
            }
        ],
    }

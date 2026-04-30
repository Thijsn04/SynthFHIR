"""R5 RelatedPerson resource mapper. Spec: https://hl7.org/fhir/R5/relatedperson.html

R5 difference from R4: canonical profile URL only.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/RelatedPerson"


def map_related_person(rp: dict) -> dict:
    return {
        "resourceType": "RelatedPerson",
        "id": rp["id"],
        "meta": build_meta(_PROFILE),
        "active": True,
        "patient": ref("Patient", rp["patient_id"]),
        "relationship": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": rp["relationship_code"],
                        "display": rp["relationship_display"],
                    }
                ],
                "text": rp["relationship_display"],
            }
        ],
        "name": [
            {
                "use": "official",
                "family": rp["last_name"],
                "given": [rp["first_name"]],
            }
        ],
        "telecom": [
            {"system": "phone", "value": rp["phone"]},
            {"system": "email", "value": rp["email"]},
        ],
        "gender": rp["gender"],
        "birthDate": rp["birth_date"],
        "address": [
            {
                "use": "home",
                "line": [rp["address_line"]],
                "city": rp["city"],
                "state": rp["state"],
                "postalCode": rp["postal_code"],
                "country": rp["country"],
            }
        ],
    }

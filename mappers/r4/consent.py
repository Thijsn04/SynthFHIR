"""R4 Consent resource mapper. Spec: https://hl7.org/fhir/R4/consent.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Consent"


def map_consent(consent: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Consent",
        "id": consent["id"],
        "meta": build_meta(_PROFILE),
        "status": consent["status"],
        "scope": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/consentscope",
                    "code": consent["scope_code"],
                    "display": consent["scope_display"],
                }
            ],
            "text": consent["scope_display"],
        },
        "category": [
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": consent["category_code"],
                        "display": consent["category_display"],
                    }
                ],
                "text": consent["category_display"],
            }
        ],
        "patient": ref("Patient", consent["patient_id"]),
        "dateTime": consent["datetime"],
        "organization": [ref("Organization", consent["organization_id"])],
        "policyRule": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "OPTIN",
                    "display": "opt-in",
                }
            ]
        },
        "provision": {
            "type": consent["provision_type"],
        },
    }

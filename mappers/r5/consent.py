"""R5 Consent resource mapper. Spec: https://hl7.org/fhir/R5/consent.html

R5 structural differences from R4:
  1. Consent.policyRule (R4) replaced by Consent.regulatoryBasis (array, R5).
  2. Consent.organization (R4) replaced by Consent.manager (R5).
  3. Consent.dateTime renamed to Consent.date (R5).
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Consent"


def map_consent(consent: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Consent",
        "id": consent["id"],
        "meta": build_meta(_PROFILE),
        "status": consent["status"],
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
        "subject": ref("Patient", consent["patient_id"]),
        # R5: dateTime → date
        "date": consent["datetime"][:10],
        # R5: organization → manager
        "manager": [ref("Organization", consent["organization_id"])],
        # R5: policyRule → regulatoryBasis (array of CodeableConcept)
        "regulatoryBasis": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "OPTIN",
                        "display": "opt-in",
                    }
                ]
            }
        ],
        "decision": consent["provision_type"],
    }

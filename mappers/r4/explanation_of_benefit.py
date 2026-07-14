"""R4 ExplanationOfBenefit mapper. Spec: https://hl7.org/fhir/R4/explanationofbenefit.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/ExplanationOfBenefit"
_CLAIM_TYPE = "http://terminology.hl7.org/CodeSystem/claim-type"
_ADJUDICATION = "http://terminology.hl7.org/CodeSystem/adjudication"
_CPT = "http://www.ama-assn.org/go/cpt"
_CURRENCY = "urn:iso:std:iso:4217"


def _money(value: float) -> dict:
    return {"value": value, "currency": "USD", "system": _CURRENCY, "code": "USD"}


def _adjudication(code: str, display: str, value: float) -> dict:
    return {
        "category": {"coding": [{"system": _ADJUDICATION, "code": code, "display": display}]},
        "amount": _money(value),
    }


def map_explanation_of_benefit(eob: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "ExplanationOfBenefit",
        "id": eob["id"],
        "meta": build_meta(_PROFILE),
        "status": "active",
        "type": {"coding": [{"system": _CLAIM_TYPE, "code": "professional", "display": "Professional"}]},
        "use": "claim",
        "patient": ref("Patient", eob["patient_id"]),
        "created": eob["created"],
        "insurer": ref("Organization", eob["organization_id"]),
        "provider": ref("Organization", eob["organization_id"]),
        "claim": ref("Claim", eob["claim_id"]),
        "outcome": "complete",
        "insurance": [{"focal": True, "coverage": ref("Coverage", eob["coverage_id"])}],
        "item": [
            {
                "sequence": 1,
                "productOrService": {
                    "coding": [{"system": _CPT, "code": eob["item_code"], "display": eob["item_display"]}],
                    "text": eob["item_display"],
                },
                "servicedDate": eob["created"],
                "net": _money(eob["amount"]),
                "adjudication": [_adjudication("benefit", "Benefit Amount", eob["paid"])],
            }
        ],
        "total": [
            _adjudication("submitted", "Submitted Amount", eob["amount"]),
            _adjudication("benefit", "Benefit Amount", eob["paid"]),
        ],
        "payment": {"amount": _money(eob["paid"])},
    }

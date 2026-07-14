"""R5 Claim resource mapper. Spec: https://hl7.org/fhir/R5/claim.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Claim"
_CLAIM_TYPE = "http://terminology.hl7.org/CodeSystem/claim-type"
_PRIORITY = "http://terminology.hl7.org/CodeSystem/processpriority"
_CPT = "http://www.ama-assn.org/go/cpt"


def _money(value: float) -> dict:
    return {"value": value, "currency": "USD"}


def map_claim(claim: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Claim",
        "id": claim["id"],
        "meta": build_meta(_PROFILE),
        "status": "active",
        "type": {"coding": [{"system": _CLAIM_TYPE, "code": "professional", "display": "Professional"}]},
        "use": "claim",
        "patient": ref("Patient", claim["patient_id"]),
        "created": claim["created"],
        "provider": ref("Organization", claim["organization_id"]),
        "priority": {"coding": [{"system": _PRIORITY, "code": "normal", "display": "Normal"}]},
        "insurance": [
            {"sequence": 1, "focal": True, "coverage": ref("Coverage", claim["coverage_id"])}
        ],
        "item": [
            {
                "sequence": 1,
                "productOrService": {
                    "coding": [{"system": _CPT, "code": claim["item_code"], "display": claim["item_display"]}],
                    "text": claim["item_display"],
                },
                "servicedDate": claim["created"],
                "net": _money(claim["amount"]),
            }
        ],
    }

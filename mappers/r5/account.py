"""R5 Account resource mapper. Spec: https://hl7.org/fhir/R5/account.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Account"


def map_account(account: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Account",
        "id": account["id"],
        "meta": build_meta(_PROFILE),
        "status": account["status"],
        "type": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "PBILLACCT",
                    "display": "patient billing account",
                }
            ]
        },
        "name": account["name"],
        "subject": [ref("Patient", account["patient_id"])],
        "owner": ref("Organization", account["organization_id"]),
    }

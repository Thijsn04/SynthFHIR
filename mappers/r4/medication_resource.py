"""R4 Medication resource mapper. Spec: https://hl7.org/fhir/R4/medication.html"""
from mappers._helpers import build_meta

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Medication"
_US_CORE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medication"
_RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"


def map_medication_resource(med: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Medication",
        "id": med["id"],
        "meta": build_meta(_US_CORE if us_core else _PROFILE),
        "status": "active",
        "code": {
            "coding": [
                {"system": _RXNORM, "code": med["rxnorm_code"], "display": med["display"]}
            ],
            "text": med["display"],
        },
    }

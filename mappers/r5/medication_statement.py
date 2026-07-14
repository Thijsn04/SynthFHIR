"""R5 MedicationStatement mapper. Spec: https://hl7.org/fhir/R5/medicationstatement.html

R5 differences: status codes are recorded | entered-in-error | draft, medication
is a CodeableReference, and the visit link is `encounter` rather than `context`.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/MedicationStatement"
_RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"


def map_medication_statement(stmt: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "MedicationStatement",
        "id": stmt["id"],
        "meta": build_meta(_PROFILE),
        "status": "recorded",
        "medication": {
            "concept": {
                "coding": [
                    {"system": _RXNORM, "code": stmt["rxnorm_code"], "display": stmt["display"]}
                ],
                "text": stmt["display"],
            }
        },
        "subject": ref("Patient", stmt["patient_id"]),
        "derivedFrom": [ref("MedicationRequest", stmt["medication_request_id"])],
    }
    if stmt.get("effective_start"):
        resource["effectiveDateTime"] = stmt["effective_start"]
    if stmt.get("encounter_id"):
        resource["encounter"] = ref("Encounter", stmt["encounter_id"])
    return resource

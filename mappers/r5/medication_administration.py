"""R5 MedicationAdministration mapper. Spec: https://hl7.org/fhir/R5/medicationadministration.html

R5 differences: medication is a CodeableReference, the visit link is `encounter`
rather than `context`, and the timing element is `occurence[x]` rather than
`effective[x]`.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/MedicationAdministration"
_RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"


def map_medication_administration(admin: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "MedicationAdministration",
        "id": admin["id"],
        "meta": build_meta(_PROFILE),
        "status": "completed",
        "medication": {
            "concept": {
                "coding": [
                    {"system": _RXNORM, "code": admin["rxnorm_code"], "display": admin["display"]}
                ],
                "text": admin["display"],
            }
        },
        "subject": ref("Patient", admin["patient_id"]),
        "occurenceDateTime": admin["effective_datetime"],
        "request": ref("MedicationRequest", admin["medication_request_id"]),
    }
    if admin.get("encounter_id"):
        resource["encounter"] = ref("Encounter", admin["encounter_id"])
    if admin.get("practitioner_id"):
        resource["performer"] = [{"actor": ref("Practitioner", admin["practitioner_id"])}]
    if admin.get("dose_value") is not None:
        resource["dosage"] = {
            "dose": {
                "value": admin["dose_value"],
                "unit": admin.get("dose_unit", ""),
                "system": "http://unitsofmeasure.org",
                "code": admin.get("dose_unit", "1"),
            }
        }
    return resource

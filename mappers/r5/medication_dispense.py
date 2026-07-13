"""R5 MedicationDispense resource mapper. Spec: https://hl7.org/fhir/R5/medicationdispense.html

R5 difference from R4: medication is a CodeableReference rather than a choice of
medicationCodeableConcept or medicationReference.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/MedicationDispense"
_RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"


def map_medication_dispense(dispense: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "MedicationDispense",
        "id": dispense["id"],
        "meta": build_meta(_PROFILE),
        "status": "completed",
        "medication": {
            "concept": {
                "coding": [
                    {"system": _RXNORM, "code": dispense["rxnorm_code"], "display": dispense["display"]}
                ],
                "text": dispense["display"],
            }
        },
        "subject": ref("Patient", dispense["patient_id"]),
        "authorizingPrescription": [ref("MedicationRequest", dispense["medication_request_id"])],
        "type": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "RFP",
                    "display": "Refill - Part Fill",
                }
            ]
        },
        "quantity": {
            "value": dispense["quantity"],
            "unit": "dose",
            "system": "http://unitsofmeasure.org",
            "code": "{dose}",
        },
        "daysSupply": {
            "value": dispense["days_supply"],
            "unit": "days",
            "system": "http://unitsofmeasure.org",
            "code": "d",
        },
        "whenHandedOver": dispense["when_handed_over"],
    }
    if dispense.get("practitioner_id"):
        resource["performer"] = [{"actor": ref("Practitioner", dispense["practitioner_id"])}]
    return resource

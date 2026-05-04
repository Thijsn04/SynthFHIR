"""R4 MedicationRequest resource mapper. Spec: https://hl7.org/fhir/R4/medicationrequest.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/MedicationRequest"


def map_medication(med: dict) -> dict:
    return {
        "resourceType": "MedicationRequest",
        "id": med["id"],
        "meta": build_meta(_PROFILE),
        "status": med["status"],
        "intent": med["intent"],
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": med["rxnorm_code"],
                    "display": med["display"],
                }
            ],
            "text": med["display"],
        },
        "subject": ref("Patient", med["patient_id"]),
        "encounter": ref("Encounter", med["encounter_id"]),
        "authoredOn": med["authored_on"],
        "requester": ref("Practitioner", med["practitioner_id"]),
        "dosageInstruction": [
            {
                "text": f"{med['dose_value']} {med['dose_unit']} {med['frequency']}",
                "timing": {
                    "code": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-GTSAbbreviation",
                                "code": med["frequency_code"],
                                "display": med["frequency"],
                            }
                        ],
                        "text": med["frequency"],
                    }
                },
                "doseAndRate": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/dose-rate-type",
                                    "code": "ordered",
                                    "display": "Ordered",
                                }
                            ]
                        },
                        "doseQuantity": {
                            "value": med["dose_value"],
                            "unit": med["dose_unit"],
                            "system": "http://unitsofmeasure.org",
                            "code": med["dose_unit"],
                        },
                    }
                ],
            }
        ],
        "dispenseRequest": {
            "numberOfRepeatsAllowed": med["num_refills"],
            "quantity": {
                "value": med["dispense_quantity"],
                "unit": "day",
                "system": "http://unitsofmeasure.org",
                "code": med["dispense_quantity_unit"],
            },
            "expectedSupplyDuration": {
                "value": med["dispense_supply_days"],
                "unit": "days",
                "system": "http://unitsofmeasure.org",
                "code": "d",
            },
        },
    }

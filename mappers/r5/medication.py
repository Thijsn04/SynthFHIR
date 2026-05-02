"""R5 MedicationRequest resource mapper. Spec: https://hl7.org/fhir/R5/medicationrequest.html

R5 differences from R4:
  1. Profile URL uses 5.0 path segment.
  2. requester renamed to informationSource in some profiles; kept as requester here
     since R5 still supports it for the ordering provider role.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/MedicationRequest"


def map_medication(med: dict) -> dict:
    return {
        "resourceType": "MedicationRequest",
        "id": med["id"],
        "meta": build_meta(_PROFILE),
        "status": med["status"],
        "intent": med["intent"],
        "medication": {
            "concept": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": med["rxnorm_code"],
                        "display": med["display"],
                    }
                ],
                "text": med["display"],
            }
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
    }

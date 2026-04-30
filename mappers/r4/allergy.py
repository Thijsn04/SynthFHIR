"""R4 AllergyIntolerance resource mapper. Spec: https://hl7.org/fhir/R4/allergyintolerance.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/AllergyIntolerance"


def map_allergy(allergy: dict) -> dict:
    return {
        "resourceType": "AllergyIntolerance",
        "id": allergy["id"],
        "meta": build_meta(_PROFILE),
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": "active",
                    "display": "Active",
                }
            ]
        },
        "verificationStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                    "code": "confirmed",
                    "display": "Confirmed",
                }
            ]
        },
        # R4: 'type' is a primitive string enum ("allergy" | "intolerance")
        "type": allergy["type"],
        "category": [allergy["category"]],
        "criticality": allergy["criticality"],
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": allergy["substance_code"],
                    "display": allergy["substance_display"],
                }
            ],
            "text": allergy["substance_display"],
        },
        "patient": ref("Patient", allergy["patient_id"]),
        "onsetDateTime": allergy["onset_date"],
        "recordedDate": allergy["recorded_date"],
        "recorder": ref("Practitioner", allergy["practitioner_id"]),
        "reaction": [
            {
                # R4: manifestation is a list of CodeableConcept
                "manifestation": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": allergy["reaction_code"],
                                "display": allergy["reaction_display"],
                            }
                        ],
                        "text": allergy["reaction_display"],
                    }
                ],
                "severity": allergy["reaction_severity"],
            }
        ],
    }

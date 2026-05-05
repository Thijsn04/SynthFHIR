"""R5 AllergyIntolerance resource mapper. Spec: https://hl7.org/fhir/R5/allergyintolerance.html

R5 structural differences from R4:
  1. 'type' changed from a primitive string enum to a CodeableConcept.
  2. 'reaction.manifestation' is now wrapped: [{concept: {coding: [...]}}]
     instead of the R4 form [{coding: [...]}].
  3. 'recorder' and 'asserter' are replaced by a 'participant' array, each
     entry carrying a provenance-participant-type function code.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/AllergyIntolerance"


def map_allergy(allergy: dict, us_core: bool = False) -> dict:
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
        # R5: 'type' is now a CodeableConcept (was a string in R4)
        "type": {
            "coding": [
                {
                    "system": "http://hl7.org/fhir/allergy-intolerance-type",
                    "code": allergy["type"],
                    "display": allergy["type"].title(),
                }
            ]
        },
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
        # R5: recorder/asserter replaced by participant[] with function codes
        "participant": [
            {
                "function": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                            "code": "author",
                            "display": "Author",
                        }
                    ]
                },
                "actor": ref("Practitioner", allergy["practitioner_id"]),
            }
        ],
        "reaction": [
            {
                # R5: each manifestation is wrapped in a 'concept' key
                "manifestation": [
                    {
                        "concept": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": allergy["reaction_code"],
                                    "display": allergy["reaction_display"],
                                }
                            ],
                            "text": allergy["reaction_display"],
                        }
                    }
                ],
                "severity": allergy["reaction_severity"],
            }
        ],
    }

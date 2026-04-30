"""R4 Observation resource mapper. Spec: https://hl7.org/fhir/R4/observation.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Observation"


def map_observation(obs: dict) -> dict:
    resource: dict = {
        "resourceType": "Observation",
        "id": obs["id"],
        "meta": build_meta(_PROFILE),
        "status": obs["status"],
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": obs["category_code"],
                        "display": obs["category_display"],
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": obs["loinc_code"],
                    "display": obs["display"],
                }
            ],
            "text": obs["display"],
        },
        "subject": ref("Patient", obs["patient_id"]),
        "encounter": ref("Encounter", obs["encounter_id"]),
        "effectiveDateTime": obs["effective_datetime"],
        "performer": [ref("Practitioner", obs["practitioner_id"])],
        # valueQuantity uses UCUM units for the machine-readable code
        "valueQuantity": {
            "value": obs["value"],
            "unit": obs["unit"],
            "system": "http://unitsofmeasure.org",
            "code": obs["ucum_code"],
        },
    }

    if obs.get("interpretation_code"):
        resource["interpretation"] = [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        "code": obs["interpretation_code"],
                        "display": obs["interpretation_display"],
                    }
                ]
            }
        ]

    return resource

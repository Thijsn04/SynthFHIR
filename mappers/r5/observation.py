"""R5 Observation resource mapper. Spec: https://hl7.org/fhir/R5/observation.html

R5 difference from R4: canonical profile URL only.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Observation"


def map_observation(obs: dict, us_core: bool = False) -> dict:
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
    }

    if obs.get("components"):
        resource["component"] = [_map_component(c) for c in obs["components"]]
    elif obs.get("value_type") == "integer":
        resource["valueInteger"] = int(obs["value"])
    else:
        resource["valueQuantity"] = {
            "value": obs["value"],
            "unit": obs["unit"],
            "system": "http://unitsofmeasure.org",
            "code": obs["ucum_code"],
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

    if obs.get("based_on_service_request_id"):
        resource["basedOn"] = [ref("ServiceRequest", obs["based_on_service_request_id"])]

    if obs.get("ref_range_low") is not None:
        ref_range: dict = {
            "low": {
                "value": obs["ref_range_low"],
                "unit": obs["ref_range_unit"],
                "system": "http://unitsofmeasure.org",
                "code": obs["ref_range_ucum"],
            },
            "high": {
                "value": obs["ref_range_high"],
                "unit": obs["ref_range_unit"],
                "system": "http://unitsofmeasure.org",
                "code": obs["ref_range_ucum"],
            },
        }
        resource["referenceRange"] = [ref_range]

    return resource


def _map_component(comp: dict) -> dict:
    c: dict = {
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": comp["loinc_code"],
                    "display": comp["display"],
                }
            ],
            "text": comp["display"],
        },
        "valueQuantity": {
            "value": comp["value"],
            "unit": comp["unit"],
            "system": "http://unitsofmeasure.org",
            "code": comp["ucum_code"],
        },
    }
    if comp.get("interpretation_code"):
        c["interpretation"] = [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        "code": comp["interpretation_code"],
                        "display": comp["interpretation_display"],
                    }
                ]
            }
        ]
    return c

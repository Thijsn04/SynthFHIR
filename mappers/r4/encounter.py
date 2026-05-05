"""R4 Encounter resource mapper. Spec: https://hl7.org/fhir/R4/encounter.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Encounter"


def map_encounter(enc: dict) -> dict:
    resource: dict = {
        "resourceType": "Encounter",
        "id": enc["id"],
        "meta": build_meta(_PROFILE),
        "status": enc["status"],
        # R4: Encounter.class is a single Coding (not a CodeableConcept array)
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": enc["class_code"],
            "display": enc["class_display"],
        },
        "type": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": enc["type_code"],
                        "display": enc["type_display"],
                    }
                ],
                "text": enc["type_display"],
            }
        ],
        "subject": ref("Patient", enc["patient_id"]),
        "participant": [
            {"individual": ref("Practitioner", enc["practitioner_id"])}
        ],
        "period": {
            "start": enc["start_datetime"],
            "end": enc["end_datetime"],
        },
        "serviceProvider": ref("Organization", enc["organization_id"]),
    }

    if enc.get("reason_codes"):
        resource["reasonCode"] = [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": rc["snomed_code"],
                        "display": rc["display"],
                    }
                ],
                "text": rc["display"],
            }
            for rc in enc["reason_codes"]
        ]

    if enc.get("location_id"):
        resource["location"] = [
            {"location": ref("Location", enc["location_id"]), "status": "completed"}
        ]

    return resource

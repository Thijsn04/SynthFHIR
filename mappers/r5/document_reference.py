"""R5 DocumentReference resource mapper. Spec: https://hl7.org/fhir/R5/documentreference.html

R5 differences from R4: context is a flat list of references (the encounter moves
there and the separate context.period is dropped).
"""
import base64

from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/DocumentReference"
_US_CORE_CATEGORY = "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category"


def map_document_reference(doc: dict, us_core: bool = False) -> dict:
    data = base64.b64encode(doc["note_text"].encode("utf-8")).decode("ascii")

    return {
        "resourceType": "DocumentReference",
        "id": doc["id"],
        "meta": build_meta(_PROFILE),
        "status": "current",
        "docStatus": "final",
        "type": {
            "coding": [
                {"system": "http://loinc.org", "code": doc["type_code"], "display": doc["type_display"]}
            ],
            "text": doc["type_display"],
        },
        "category": [
            {
                "coding": [
                    {"system": _US_CORE_CATEGORY, "code": "clinical-note", "display": "Clinical Note"}
                ]
            }
        ],
        "subject": ref("Patient", doc["patient_id"]),
        "date": doc["date"],
        "author": [ref("Practitioner", doc["practitioner_id"])],
        "custodian": ref("Organization", doc["organization_id"]),
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "data": data,
                    "title": doc["type_display"],
                }
            }
        ],
        "context": [ref("Encounter", doc["encounter_id"])],
    }

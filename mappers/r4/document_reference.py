"""R4 DocumentReference resource mapper. Spec: https://hl7.org/fhir/R4/documentreference.html"""
import base64

from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/DocumentReference"
_US_CORE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-documentreference"
_US_CORE_CATEGORY = "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category"


def map_document_reference(doc: dict, us_core: bool = False) -> dict:
    profile = _US_CORE if us_core else _PROFILE
    data = base64.b64encode(doc["note_text"].encode("utf-8")).decode("ascii")

    return {
        "resourceType": "DocumentReference",
        "id": doc["id"],
        "meta": build_meta(profile),
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
                },
                "format": {
                    "system": "http://ihe.net/fhir/ValueSet/IHE.FormatCode.codesystem",
                    "code": "urn:ihe:iti:xds:2017:mimeTypeSufficient",
                    "display": "mimeType Sufficient",
                },
            }
        ],
        "context": {
            "encounter": [ref("Encounter", doc["encounter_id"])],
            "period": {"start": doc["date"]},
        },
    }

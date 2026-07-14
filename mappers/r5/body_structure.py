"""R5 BodyStructure mapper. Spec: https://hl7.org/fhir/R5/bodystructure.html

R5 replaces the flat location/morphology with includedStructure, a backbone
element whose `structure` (a CodeableConcept) is required.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/BodyStructure"
_SNOMED = "http://snomed.info/sct"


def map_body_structure(bs: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "BodyStructure",
        "id": bs["id"],
        "meta": build_meta(_PROFILE),
        "active": True,
        "includedStructure": [
            {
                "structure": {
                    "coding": [
                        {"system": _SNOMED, "code": bs["structure_code"], "display": bs["structure_display"]}
                    ],
                    "text": bs["structure_display"],
                },
                "laterality": {
                    "coding": [
                        {"system": _SNOMED, "code": bs["laterality_code"], "display": bs["laterality_display"]}
                    ]
                },
            }
        ],
        "patient": ref("Patient", bs["patient_id"]),
    }

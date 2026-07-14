"""R5 ImagingStudy resource mapper. Spec: https://hl7.org/fhir/R5/imagingstudy.html

R5 differences: modality and series.modality are CodeableConcept (not Coding),
and series.bodySite is a CodeableReference.
"""
import uuid

from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/ImagingStudy"
_DCM = "http://dicom.nema.org/resources/ontology/DCM"
_SNOMED = "http://snomed.info/sct"
_SOP_SYSTEM = "urn:ietf:rfc:3986"
_SOP_CLASS = "urn:oid:1.2.840.10008.5.1.4.1.1.7"


def _uid(resource_id: str, offset: int = 0) -> str:
    return f"2.25.{uuid.UUID(resource_id).int + offset}"


def _modality(study: dict) -> dict:
    return {
        "coding": [
            {"system": _DCM, "code": study["modality_code"], "display": study["modality_display"]}
        ]
    }


def map_imaging_study(study: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "ImagingStudy",
        "id": study["id"],
        "meta": build_meta(_PROFILE),
        "status": "available",
        "subject": ref("Patient", study["patient_id"]),
        "modality": [_modality(study)],
        "numberOfSeries": 1,
        "numberOfInstances": 1,
        "description": study["description"],
        "series": [
            {
                "uid": _uid(study["id"]),
                "number": 1,
                "modality": _modality(study),
                "numberOfInstances": 1,
                "bodySite": {
                    "concept": {
                        "coding": [
                            {"system": _SNOMED, "code": study["bodysite_code"], "display": study["bodysite_display"]}
                        ]
                    }
                },
                "instance": [
                    {"uid": _uid(study["id"], 1), "sopClass": {"system": _SOP_SYSTEM, "code": _SOP_CLASS}, "number": 1}
                ],
            }
        ],
    }
    if study.get("started"):
        resource["started"] = study["started"]
    if study.get("encounter_id"):
        resource["encounter"] = ref("Encounter", study["encounter_id"])
    return resource

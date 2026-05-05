"""R5 DiagnosticReport resource mapper. Spec: https://hl7.org/fhir/R5/diagnosticreport.html

R5 differences from R4:
  1. Profile URL uses 5.0 path segment.
  2. subject reference remains; encounter reference is unchanged.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/DiagnosticReport"


def map_diagnostic_report(report: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "DiagnosticReport",
        "id": report["id"],
        "meta": build_meta(_PROFILE),
        "status": report["status"],
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": report["category_code"],
                        "display": report["category_display"],
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": report["loinc_code"],
                    "display": report["display"],
                }
            ],
            "text": report["display"],
        },
        "subject": ref("Patient", report["patient_id"]),
        "encounter": ref("Encounter", report["encounter_id"]),
        "effectiveDateTime": report["effective_datetime"],
        "issued": report["issued"],
        "performer": [ref("Practitioner", report["practitioner_id"])],
        "result": [ref("Observation", obs_id) for obs_id in report["observation_ids"]],
    }

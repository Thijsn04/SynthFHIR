"""R4 DiagnosticReport resource mapper. Spec: https://hl7.org/fhir/R4/diagnosticreport.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/DiagnosticReport"

# US Core DiagnosticReport (Lab) requires "LAB" category slice from v2-0074
_LAB_CATEGORY = {
    "coding": [
        {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
            "code": "LAB",
            "display": "Laboratory",
        }
    ]
}


def map_diagnostic_report(report: dict, us_core: bool = False) -> dict:
    profile = US_CORE_PROFILES["DiagnosticReport-lab"] if us_core else _PROFILE

    # Build category: always include the report's own category;
    # when us_core=True and not already LAB, prepend the required LAB slice.
    base_category = {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": report["category_code"],
                "display": report["category_display"],
            }
        ]
    }
    if us_core and report.get("category_code", "").upper() != "LAB":
        categories = [_LAB_CATEGORY, base_category]
    else:
        categories = [base_category]

    return {
        "resourceType": "DiagnosticReport",
        "id": report["id"],
        "meta": build_meta(profile),
        "status": report["status"],
        "category": categories,
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

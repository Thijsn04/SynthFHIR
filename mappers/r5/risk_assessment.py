"""R5 RiskAssessment mapper. Spec: https://hl7.org/fhir/R5/riskassessment.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/RiskAssessment"
_SNOMED = "http://snomed.info/sct"


def map_risk_assessment(risk: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "RiskAssessment",
        "id": risk["id"],
        "meta": build_meta(_PROFILE),
        "status": "final",
        "subject": ref("Patient", risk["patient_id"]),
        "occurrenceDateTime": risk["effective_datetime"],
        "prediction": [
            {
                "outcome": {
                    "coding": [
                        {"system": _SNOMED, "code": risk["outcome_code"], "display": risk["outcome_display"]}
                    ],
                    "text": risk["outcome_display"],
                },
                "probabilityDecimal": risk["probability"],
            }
        ],
    }
    if risk.get("encounter_id"):
        resource["encounter"] = ref("Encounter", risk["encounter_id"])
    return resource

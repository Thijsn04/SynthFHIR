"""R4 QuestionnaireResponse mapper. Spec: https://hl7.org/fhir/R4/questionnaireresponse.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/QuestionnaireResponse"


def map_questionnaire_response(qr: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "QuestionnaireResponse",
        "id": qr["id"],
        "meta": build_meta(_PROFILE),
        "questionnaire": qr["questionnaire"],
        "status": "completed",
        "subject": ref("Patient", qr["patient_id"]),
        "authored": qr["authored"],
        "item": [
            {
                "linkId": qr["link_id"],
                "text": qr["question_text"],
                "answer": [{"valueInteger": qr["score"]}],
            }
        ],
    }
    if qr.get("encounter_id"):
        resource["encounter"] = ref("Encounter", qr["encounter_id"])
    return resource

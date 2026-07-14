"""R5 NutritionOrder resource mapper. Spec: https://hl7.org/fhir/R5/nutritionorder.html

R5 difference: the patient link is `subject` rather than R4's `patient`.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/NutritionOrder"
_SNOMED = "http://snomed.info/sct"


def map_nutrition_order(order: dict, us_core: bool = False) -> dict:
    resource = {
        "resourceType": "NutritionOrder",
        "id": order["id"],
        "meta": build_meta(_PROFILE),
        "status": "active",
        "intent": "order",
        "subject": ref("Patient", order["patient_id"]),
        "dateTime": order["datetime"],
        "oralDiet": {
            "type": [
                {
                    "coding": [{"system": _SNOMED, "code": order["diet_code"], "display": order["diet_display"]}],
                    "text": order["diet_display"],
                }
            ]
        },
    }
    if order.get("encounter_id"):
        resource["encounter"] = ref("Encounter", order["encounter_id"])
    return resource

"""R5 Slot resource mapper. Spec: https://hl7.org/fhir/R5/slot.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Slot"


def map_slot(slot: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Slot",
        "id": slot["id"],
        "meta": build_meta(_PROFILE),
        "schedule": ref("Schedule", slot["schedule_id"]),
        "status": slot["status"],
        "start": slot["start"],
        "end": slot["end"],
    }

"""R4 Schedule resource mapper. Spec: https://hl7.org/fhir/R4/schedule.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Schedule"


def map_schedule(sched: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Schedule",
        "id": sched["id"],
        "meta": build_meta(_PROFILE),
        "active": True,
        "actor": [ref("Practitioner", sched["practitioner_id"])],
        "planningHorizon": {"start": sched["horizon_start"], "end": sched["horizon_end"]},
    }

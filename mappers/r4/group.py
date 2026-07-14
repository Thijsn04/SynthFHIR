"""R4 Group resource mapper. Spec: https://hl7.org/fhir/R4/group.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Group"


def map_group(group: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Group",
        "id": group["id"],
        "meta": build_meta(_PROFILE),
        "type": "person",
        "actual": True,
        "name": "Synthetic patient cohort",
        "quantity": group["quantity"],
        "member": [{"entity": ref("Patient", pid)} for pid in group["member_ids"]],
    }

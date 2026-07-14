"""R5 Group resource mapper. Spec: https://hl7.org/fhir/R5/group.html

R5 difference: the boolean `actual` is replaced by the `membership` code
(enumerated | definitional), and `type` "person" becomes "Patient"-style still
uses the group-type value set.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Group"


def map_group(group: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Group",
        "id": group["id"],
        "meta": build_meta(_PROFILE),
        "type": "person",
        "membership": "enumerated",
        "name": "Synthetic patient cohort",
        "quantity": group["quantity"],
        "member": [{"entity": ref("Patient", pid)} for pid in group["member_ids"]],
    }

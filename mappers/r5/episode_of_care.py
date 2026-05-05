"""R5 EpisodeOfCare resource mapper. Spec: https://hl7.org/fhir/R5/episodeofcare.html

R5 changes: diagnosis.condition is now a CodeableReference, not a plain
Reference — it wraps the Reference inside a .reference field.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/EpisodeOfCare"


def map_episode_of_care(eoc: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "EpisodeOfCare",
        "id": eoc["id"],
        "meta": build_meta(_PROFILE),
        "status": eoc["status"],
        "type": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": eoc["type_code"],
                        "display": eoc["type_display"],
                    }
                ],
                "text": eoc["type_display"],
            }
        ],
        "patient": ref("Patient", eoc["patient_id"]),
        "managingOrganization": ref("Organization", eoc["organization_id"]),
    }

    if eoc.get("period_start"):
        resource["period"] = {"start": eoc["period_start"]}
        if eoc.get("period_end"):
            resource["period"]["end"] = eoc["period_end"]

    if eoc.get("condition_ids"):
        resource["diagnosis"] = [
            # R5: CodeableReference wraps the Reference inside .reference
            {"condition": {"reference": ref("Condition", cid)}, "rank": idx + 1}
            for idx, cid in enumerate(eoc["condition_ids"])
        ]

    return resource

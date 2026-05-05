"""R4 CareTeam resource mapper. Spec: https://hl7.org/fhir/R4/careteam.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/CareTeam"


def map_care_team(ct: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "CareTeam",
        "id": ct["id"],
        "meta": build_meta(US_CORE_PROFILES["CareTeam"] if us_core else _PROFILE),
        "status": ct["status"],
        "name": ct["name"],
        "subject": ref("Patient", ct["patient_id"]),
        "participant": [
            {
                "role": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "309343006",
                                "display": "Physician",
                            }
                        ]
                    }
                ],
                "member": ref("Practitioner", pid),
            }
            for pid in ct["practitioner_ids"]
        ],
    }

    if ct.get("condition_ids"):
        resource["reasonReference"] = [
            ref("Condition", cid) for cid in ct["condition_ids"]
        ]

    return resource

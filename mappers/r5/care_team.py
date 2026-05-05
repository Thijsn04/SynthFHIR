"""R5 CareTeam resource mapper. Spec: https://hl7.org/fhir/R5/careteam.html

R5 structural differences from R4:
  1. CareTeam.reasonReference (R4) replaced by CareTeam.reason[].reference (R5).
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/CareTeam"


def map_care_team(ct: dict) -> dict:
    resource: dict = {
        "resourceType": "CareTeam",
        "id": ct["id"],
        "meta": build_meta(_PROFILE),
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

    # R5: reasonReference → reason[].reference
    if ct.get("condition_ids"):
        resource["reason"] = [
            {"reference": ref("Condition", cid)}
            for cid in ct["condition_ids"]
        ]

    return resource

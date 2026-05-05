"""R5 Provenance resource mapper. Spec: https://hl7.org/fhir/R5/provenance.html

R5 is structurally identical to R4 for Provenance; only the profile URL differs.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Provenance"


def map_provenance(prov: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Provenance",
        "id": prov["id"],
        "meta": build_meta(_PROFILE),
        "target": [{"reference": f"urn:uuid:{tid}"} for tid in prov["target_ids"]],
        "recorded": prov["recorded"],
        "agent": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                            "code": "author",
                            "display": "Author",
                        }
                    ]
                },
                "who": ref("Practitioner", prov["practitioner_id"]),
                "onBehalfOf": ref("Organization", prov["organization_id"]),
            }
        ],
        "activity": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-DataOperation",
                    "code": prov["activity_code"],
                    "display": prov["activity_display"],
                }
            ]
        },
    }

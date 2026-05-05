"""R4 Location resource mapper. Spec: https://hl7.org/fhir/R4/location.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Location"


def map_location(loc: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Location",
        "id": loc["id"],
        "meta": build_meta(US_CORE_PROFILES["Location"] if us_core else _PROFILE),
        "status": loc["status"],
        "name": loc["name"],
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": loc["type_code"],
                        "display": loc["type_display"],
                    }
                ],
                "text": loc["type_display"],
            }
        ],
        "telecom": [{"system": "phone", "value": loc["phone"], "use": "work"}],
        "address": {
            "use": "work",
            "line": [loc["address_line"]],
            "city": loc["city"],
            "state": loc["state"],
            "postalCode": loc["postal_code"],
            "country": loc["country"],
        },
        "managingOrganization": ref("Organization", loc["organization_id"]),
    }

"""R4 Organization resource mapper. Spec: https://hl7.org/fhir/R4/organization.html"""
from mappers._helpers import US_CORE_PROFILES, build_meta

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Organization"


def map_organization(org: dict, us_core: bool = False) -> dict:
    resource: dict = {
        "resourceType": "Organization",
        "id": org["id"],
        "meta": build_meta(US_CORE_PROFILES["Organization"] if us_core else _PROFILE),
        "active": True,
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                        "code": org["type_code"],
                        "display": org["type_display"],
                    }
                ]
            }
        ],
        "name": org["name"],
        "telecom": [
            {"system": "phone", "value": org["phone"], "use": "work"},
            {"system": "email", "value": org["email"], "use": "work"},
        ],
        "address": [
            {
                "use": "work",
                "type": "postal",
                "line": [org["address_line"]],
                "city": org["city"],
                "state": org["state"],
                "postalCode": org["postal_code"],
                "country": org["country"],
            }
        ],
    }

    # US Core Organization requires an NPI identifier
    if us_core and org.get("npi"):
        resource["identifier"] = [
            {
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": org["npi"],
            }
        ]

    return resource

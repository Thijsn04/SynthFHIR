"""R4 PractitionerRole resource mapper. Spec: https://hl7.org/fhir/R4/practitionerrole.html

US Core PractitionerRole requires specialty from NUCC provider taxonomy
(http://nucc.org/provider-taxonomy) in addition to or instead of SNOMED.
"""
from mappers._helpers import US_CORE_PROFILES, build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/PractitionerRole"

# SNOMED specialty code → NUCC provider taxonomy code mapping
_SNOMED_TO_NUCC: dict[str, tuple[str, str]] = {
    "419772000": ("207Q00000X", "Family Medicine"),
    "419192003": ("207R00000X", "Internal Medicine"),
    "408443003": ("208D00000X", "General Practice"),
    "394814009": ("208D00000X", "General Practice"),
    "408467006": ("207RC0000X", "Cardiovascular Disease"),
    "394591006": ("2084N0400X", "Neurology"),
    "394583002": ("207N00000X", "Dermatology"),
    "394585009": ("207V00000X", "Obstetrics & Gynecology"),
    "394801008": ("207X00000X", "Orthopaedic Surgery"),
    "394592004": ("207RX0202X", "Medical Oncology"),
    "394602003": ("208100000X", "Physical Medicine & Rehabilitation"),
    "394609007": ("208600000X", "Surgery"),
    "394807007": ("2084P0800X", "Psychiatry"),
    "418112009": ("207RP1001X", "Pulmonary Disease"),
    "394589003": ("207RN0300X", "Nephrology"),
    "394805004": ("208M00000X", "Hospitalist"),
}


def map_practitioner_role(pr: dict, us_core: bool = False) -> dict:
    specialty_coding: list[dict] = [
        {
            "system": "http://snomed.info/sct",
            "code": pr["specialty_code"],
            "display": pr["specialty_display"],
        }
    ]

    # US Core PractitionerRole: add NUCC taxonomy code alongside SNOMED
    if us_core:
        nucc = _SNOMED_TO_NUCC.get(pr["specialty_code"])
        if nucc:
            specialty_coding.append(
                {
                    "system": "http://nucc.org/provider-taxonomy",
                    "code": nucc[0],
                    "display": nucc[1],
                }
            )

    return {
        "resourceType": "PractitionerRole",
        "id": pr["id"],
        "meta": build_meta(US_CORE_PROFILES["PractitionerRole"] if us_core else _PROFILE),
        "active": pr["active"],
        "practitioner": ref("Practitioner", pr["practitioner_id"]),
        "organization": ref("Organization", pr["organization_id"]),
        "code": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "309343006",
                        "display": pr["role_display"],
                    }
                ],
                "text": pr["role_display"],
            }
        ],
        "specialty": [
            {
                "coding": specialty_coding,
                "text": pr["specialty_display"],
            }
        ],
    }

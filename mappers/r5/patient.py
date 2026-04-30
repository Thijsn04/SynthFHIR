"""R5 Patient resource mapper. Spec: https://hl7.org/fhir/R5/patient.html

R5 differences from R4:
  1. Canonical profile URL uses the R5 version path segment.
  2. A human-readable 'text' narrative is strongly recommended.
  3. The individual-genderIdentity extension is formally standardised in R5;
     SNOMED CT codes for male/female, HL7 NullFlavor for other/unknown.
"""
from mappers._helpers import (
    build_address,
    build_communication,
    build_marital_status,
    build_meta,
    build_mrn_identifier,
    build_patient_name,
    build_patient_telecom,
)

_PROFILE = "http://hl7.org/fhir/5.0/StructureDefinition/Patient"

# Maps administrative-gender to the R5 genderIdentity value set.
# SNOMED CT: 446151000124109 = male, 446141000124107 = female
# HL7 NullFlavor: OTH = other, UNK = unknown
_GENDER_IDENTITY: dict[str, tuple[str, str, str]] = {
    "male":    ("http://snomed.info/sct",                                 "446151000124109", "Identifies as male gender"),
    "female":  ("http://snomed.info/sct",                                 "446141000124107", "Identifies as female gender"),
    "other":   ("http://terminology.hl7.org/CodeSystem/v3-NullFlavor",    "OTH",             "Other"),
    "unknown": ("http://terminology.hl7.org/CodeSystem/v3-NullFlavor",    "UNK",             "Unknown"),
}


def map_patient(patient: dict) -> dict:
    first, last = patient["first_name"], patient["last_name"]

    resource: dict = {
        "resourceType": "Patient",
        "id": patient["id"],
        "meta": build_meta(_PROFILE),
        # R5 strongly recommends a human-readable XHTML narrative
        "text": {
            "status": "generated",
            "div": (
                f'<div xmlns="http://www.w3.org/1999/xhtml">'
                f"<p><b>{first} {last}</b></p>"
                f'<p>DOB: {patient["birth_date"]} | Gender: {patient["gender"]}</p>'
                f"</div>"
            ),
        },
        # R5 standard genderIdentity extension (complex extension with sub-extension)
        "extension": [_build_gender_identity_ext(patient["gender"])],
        "identifier": [build_mrn_identifier(patient)],
        "active": True,
        "name": [build_patient_name(patient)],
        "telecom": build_patient_telecom(patient),
        "gender": patient["gender"],
        "birthDate": patient["birth_date"],
        "address": [build_address(patient)],
        "maritalStatus": build_marital_status(patient),
        "communication": [build_communication(patient)],
    }
    if patient.get("deceased"):
        resource["deceasedBoolean"] = True
    return resource


def _build_gender_identity_ext(gender: str) -> dict:
    """Builds the R5 individual-genderIdentity complex extension.

    The outer url names the extension; the inner 'value' sub-extension holds
    the CodeableConcept with the actual gender identity code.
    """
    system, code, display = _GENDER_IDENTITY.get(
        gender,
        ("http://terminology.hl7.org/CodeSystem/v3-NullFlavor", "UNK", "Unknown"),
    )
    return {
        "url": "http://hl7.org/fhir/StructureDefinition/individual-genderIdentity",
        "extension": [
            {
                "url": "value",
                "valueCodeableConcept": {
                    "coding": [{"system": system, "code": code, "display": display}],
                    "text": display,
                },
            }
        ],
    }

"""Shared FHIR building-block helpers used by both the R4 and R5 mappers."""
from datetime import UTC, datetime


def utcnow() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def ref(resource_type: str, resource_id: str) -> dict:
    """Builds a FHIR Reference using urn:uuid form to match Bundle fullUrls."""
    return {"reference": f"urn:uuid:{resource_id}"}


def bundle_ref(resource_id: str) -> dict:
    """Alias of ref() for clarity at call sites that know they're inside a Bundle."""
    return {"reference": f"urn:uuid:{resource_id}"}


def build_meta(profile_url: str) -> dict:
    return {
        "versionId": "1",
        "lastUpdated": utcnow(),
        "profile": [profile_url],
    }


def build_patient_name(patient: dict) -> dict:
    """HumanName — family + given array + optional prefix/suffix."""
    entry: dict = {
        "use": "official",
        "family": patient["last_name"],
        "given": [patient["first_name"], patient["middle_name"]],
    }
    if patient.get("prefix"):
        entry["prefix"] = [patient["prefix"]]
    if patient.get("suffix"):
        entry["suffix"] = [patient["suffix"]]
    return entry


def build_patient_telecom(patient: dict) -> list[dict]:
    return [
        {"system": "phone", "value": patient["phone_home"],   "use": "home"},
        {"system": "phone", "value": patient["phone_mobile"],  "use": "mobile"},
        {"system": "email", "value": patient["email"]},
    ]


def build_address(d: dict, use: str = "home") -> dict:
    """Address datatype. 'line' is an array to support multi-line addresses."""
    return {
        "use": use,
        "type": "postal",
        "line": [d["address_line"]],
        "city": d["city"],
        "state": d["state"],
        "postalCode": d["postal_code"],
        "country": d["country"],
    }


def build_marital_status(patient: dict) -> dict:
    """CodeableConcept from the HL7 v3 MaritalStatus code system."""
    return {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                "code": patient["marital_code"],
                "display": patient["marital_display"],
            }
        ],
        "text": patient["marital_display"],
    }


def build_communication(patient: dict) -> dict:
    """Patient.communication element with a BCP-47 language code."""
    return {
        "language": {
            "coding": [
                {
                    "system": "urn:ietf:bcp:47",
                    "code": patient["language_code"],
                    "display": patient["language_display"],
                }
            ],
            "text": patient["language_display"],
        },
        "preferred": True,
    }


def build_mrn_identifier(patient: dict) -> dict:
    """Identifier using HL7 v2 table 0203 type 'MR' (Medical Record Number)."""
    return {
        "use": "usual",
        "type": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "MR",
                    "display": "Medical Record Number",
                }
            ]
        },
        "system": "urn:synthfhir:mrn",
        "value": patient["mrn"],
    }


# ---------------------------------------------------------------------------
# US Core extension builders
# ---------------------------------------------------------------------------

def build_us_core_race(patient: dict) -> dict:
    """US Core Race extension (OMB race categories)."""
    return {
        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
        "extension": [
            {
                "url": "ombCategory",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": patient["race_code"],
                    "display": patient["race_display"],
                },
            },
            {
                "url": "text",
                "valueString": patient["race_display"],
            },
        ],
    }


def build_us_core_ethnicity(patient: dict) -> dict:
    """US Core Ethnicity extension (OMB ethnicity categories)."""
    return {
        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
        "extension": [
            {
                "url": "ombCategory",
                "valueCoding": {
                    "system": "urn:oid:2.16.840.1.113883.6.238",
                    "code": patient["ethnicity_code"],
                    "display": patient["ethnicity_display"],
                },
            },
            {
                "url": "text",
                "valueString": patient["ethnicity_display"],
            },
        ],
    }


def build_us_core_birth_sex(patient: dict) -> dict:
    """US Core Birth Sex extension."""
    return {
        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
        "valueCode": patient.get("birth_sex", "UNK"),
    }

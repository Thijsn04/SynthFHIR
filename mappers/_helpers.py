"""Shared FHIR building-block helpers used by both the R4 and R5 mappers."""
from datetime import datetime, timezone


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ref(resource_type: str, resource_id: str) -> dict:
    """Builds a FHIR Reference from a resource type and bare ID."""
    return {"reference": f"{resource_type}/{resource_id}"}


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
        # 'given' is ordered: [firstName, middleName]
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
        # Email has no 'use' code in the FHIR ContactPoint value set
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
                    # BCP-47 tags: "en", "es", "fr", etc.
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

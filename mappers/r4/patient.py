"""R4 Patient resource mapper. Spec: https://hl7.org/fhir/R4/patient.html"""
from mappers._helpers import (
    build_address,
    build_communication,
    build_marital_status,
    build_meta,
    build_mrn_identifier,
    build_patient_name,
    build_patient_telecom,
    build_us_core_birth_sex,
    build_us_core_ethnicity,
    build_us_core_race,
)

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Patient"
_US_CORE_PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"


def map_patient(patient: dict, us_core: bool = False) -> dict:
    profile = _US_CORE_PROFILE if us_core else _PROFILE
    resource: dict = {
        "resourceType": "Patient",
        "id": patient["id"],
        "meta": build_meta(profile),
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

    if us_core and patient.get("race_code"):
        resource["extension"] = [
            build_us_core_race(patient),
            build_us_core_ethnicity(patient),
            build_us_core_birth_sex(patient),
        ]

    if patient.get("deceased"):
        resource["deceasedBoolean"] = True

    return resource

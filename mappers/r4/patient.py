"""R4 Patient resource mapper. Spec: https://hl7.org/fhir/R4/patient.html"""
from mappers._helpers import (
    build_address,
    build_communication,
    build_marital_status,
    build_meta,
    build_mrn_identifier,
    build_patient_name,
    build_patient_telecom,
)

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Patient"


def map_patient(patient: dict) -> dict:
    resource: dict = {
        "resourceType": "Patient",
        "id": patient["id"],
        "meta": build_meta(_PROFILE),
        "identifier": [build_mrn_identifier(patient)],
        "active": True,
        "name": [build_patient_name(patient)],
        "telecom": build_patient_telecom(patient),
        # FHIR administrative-gender: male | female | other | unknown
        "gender": patient["gender"],
        "birthDate": patient["birth_date"],
        "address": [build_address(patient)],
        "maritalStatus": build_marital_status(patient),
        "communication": [build_communication(patient)],
    }
    # deceasedBoolean is omitted entirely for living patients
    if patient.get("deceased"):
        resource["deceasedBoolean"] = True
    return resource

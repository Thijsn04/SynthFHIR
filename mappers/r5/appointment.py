"""R5 Appointment resource mapper. Spec: https://hl7.org/fhir/R5/appointment.html

R5 renames participant.actor → participant.actor (unchanged) but adds
subject as a direct top-level field and drops reasonCode → reason.
"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Appointment"


def map_appointment(appt: dict, us_core: bool = False) -> dict:
    participants: list[dict] = [
        {"actor": ref("Patient", appt["patient_id"]), "status": "accepted"},
        {"actor": ref("Practitioner", appt["practitioner_id"]), "status": "accepted"},
    ]
    if appt.get("location_id"):
        participants.append({"actor": ref("Location", appt["location_id"]), "status": "accepted"})

    resource: dict = {
        "resourceType": "Appointment",
        "id": appt["id"],
        "meta": build_meta(_PROFILE),
        "status": appt["status"],
        "subject": ref("Patient", appt["patient_id"]),
        "serviceType": [
            {
                "concept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": appt["service_type_code"],
                            "display": appt["service_type_display"],
                        }
                    ],
                    "text": appt["service_type_display"],
                }
            }
        ],
        "appointmentType": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
                    "code": appt["appointment_type_code"],
                    "display": appt["appointment_type_display"],
                }
            ]
        },
        "start": appt["start"],
        "end": appt["end"],
        "participant": participants,
    }

    if appt.get("reason_snomed"):
        resource["reason"] = [
            {
                "concept": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": appt["reason_snomed"],
                            "display": appt["reason_display"],
                        }
                    ],
                    "text": appt["reason_display"],
                }
            }
        ]

    return resource

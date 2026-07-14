"""Communication generator.

A completed communication to the patient, such as an appointment reminder or a
results notification.

Output keys: id, patient_id, encounter_id, sender_id, category_code,
category_display, payload, sent.
"""
import random

from generators._rng import new_uuid

_MESSAGES = [
    ("reminder", "Reminder", "Appointment reminder sent to patient."),
    ("notification", "Notification", "Lab results are available in the patient portal."),
    ("instruction", "Instruction", "Medication adherence instructions provided."),
]
_COMMUNICATION_PROBABILITY = 0.5


def generate_communication_for_patient(
    patient_id: str, encounter_id: str, sender_id: str, sent: str
) -> list[dict]:
    """Generate zero or one Communication to a patient."""
    if random.random() > _COMMUNICATION_PROBABILITY:
        return []
    cat_code, cat_display, payload = random.choice(_MESSAGES)
    return [
        {
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "sender_id": sender_id,
            "category_code": cat_code,
            "category_display": cat_display,
            "payload": payload,
            "sent": sent,
        }
    ]

"""Task generator.

A workflow Task per patient, representing a fulfilled care action such as a
referral or follow-up arrangement.

Output keys: id, patient_id, encounter_id, requester_id, code, display,
authored_on, status.
"""
import random

from generators._rng import new_uuid

_TASKS = [
    ("fulfill", "Fulfill referral to specialist"),
    ("approve", "Approve prior authorization"),
    ("fulfill", "Schedule follow-up appointment"),
    ("fulfill", "Arrange home health services"),
]
_TASK_PROBABILITY = 0.5


def generate_task_for_patient(
    patient_id: str, encounter_id: str, requester_id: str, authored_on: str
) -> list[dict]:
    """Generate zero or one workflow Task for a patient."""
    if random.random() > _TASK_PROBABILITY:
        return []
    code, display = random.choice(_TASKS)
    return [
        {
            "id": new_uuid(),
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "requester_id": requester_id,
            "code": code,
            "display": display,
            "authored_on": authored_on,
            "status": "completed",
        }
    ]

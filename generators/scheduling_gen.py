"""Schedule and Slot generators.

A Schedule per practitioner and a handful of bookable Slots per schedule, giving
a minimal scheduling surface alongside the Appointment resources.

Schedule keys: id, practitioner_id, horizon_start, horizon_end.
Slot keys: id, schedule_id, status, start, end.
"""
import random
from datetime import datetime, timedelta

from generators._rng import new_uuid

_SLOTS_PER_SCHEDULE = 4
_SLOT_MINUTES = 30


def generate_schedules_and_slots(practitioners: list[dict]) -> tuple[list[dict], list[dict]]:
    """One Schedule per practitioner with several bookable Slots each."""
    schedules: list[dict] = []
    slots: list[dict] = []
    base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    for prac in practitioners:
        schedule = {
            "id": new_uuid(),
            "practitioner_id": prac["id"],
            "horizon_start": base.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "horizon_end": (base + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        schedules.append(schedule)

        for i in range(_SLOTS_PER_SCHEDULE):
            start = base + timedelta(minutes=i * _SLOT_MINUTES)
            end = start + timedelta(minutes=_SLOT_MINUTES)
            slots.append(
                {
                    "id": new_uuid(),
                    "schedule_id": schedule["id"],
                    "status": random.choice(["free", "free", "busy"]),
                    "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
    return schedules, slots

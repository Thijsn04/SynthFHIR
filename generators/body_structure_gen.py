"""BodyStructure generator.

Anatomical structures relevant to a patient's musculoskeletal conditions, useful
for anchoring procedures and imaging.

Output keys: id, patient_id, structure_code, structure_display, laterality.
"""
import random

from generators._rng import new_uuid

_STRUCTURE_RULES = {
    "osteoarthritis": ("72696002", "Knee joint structure", 0.6),
    "gout": ("67169006", "First metatarsophalangeal joint structure", 0.5),
    "rheumatoid_arthritis": ("85562004", "Hand joint structure", 0.5),
    "peripheral_artery_disease": ("113257007", "Structure of lower limb artery", 0.4),
}
_LATERALITY = [("7771000", "Left"), ("24028007", "Right")]


def generate_body_structures_for_patient(patient_id: str, condition_keys: set[str]) -> list[dict]:
    """Generate anatomical BodyStructures implied by a patient's conditions."""
    results: list[dict] = []
    for key in condition_keys:
        rule = _STRUCTURE_RULES.get(key)
        if not rule:
            continue
        code, display, prob = rule
        if random.random() > prob:
            continue
        lat_code, lat_display = random.choice(_LATERALITY)
        results.append(
            {
                "id": new_uuid(),
                "patient_id": patient_id,
                "structure_code": code,
                "structure_display": display,
                "laterality_code": lat_code,
                "laterality_display": lat_display,
            }
        )
    return results

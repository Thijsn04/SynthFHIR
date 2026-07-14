"""ImagingStudy generator.

Radiology studies performed at a share of encounters. Each study carries a DICOM
modality, a body site, and one series with one instance, which is enough to model
the imaging graph without fabricating pixel data.

Output keys: id, patient_id, encounter_id, started, modality_code, modality_display,
bodysite_code, bodysite_display, description.
"""
import random

from generators._rng import new_uuid

_IMAGING_STUDY_PROBABILITY = 0.2

# (modality code, modality display, bodysite SNOMED, bodysite display, description)
_STUDIES = [
    ("CR", "Computed Radiography", "51185008", "Thoracic structure", "Chest X-ray"),
    ("CT", "Computed Tomography", "12738006", "Brain structure", "CT head"),
    ("MR", "Magnetic Resonance", "421060004", "Vertebral column", "MRI spine"),
    ("US", "Ultrasound", "818983003", "Abdomen", "Abdominal ultrasound"),
    ("XA", "X-ray Angiography", "80891009", "Heart structure", "Coronary angiography"),
    ("MG", "Mammography", "76752008", "Breast structure", "Mammogram"),
]


def generate_imaging_studies_for_encounters(encounters: list[dict]) -> list[dict]:
    """Generate imaging studies for a share of encounters."""
    results: list[dict] = []
    for enc in encounters:
        if random.random() > _IMAGING_STUDY_PROBABILITY:
            continue
        mod_code, mod_display, site_code, site_display, description = random.choice(_STUDIES)
        results.append(
            {
                "id": new_uuid(),
                "patient_id": enc["patient_id"],
                "encounter_id": enc["id"],
                "started": enc.get("start_datetime", ""),
                "modality_code": mod_code,
                "modality_display": mod_display,
                "bodysite_code": site_code,
                "bodysite_display": site_display,
                "description": description,
            }
        )
    return results

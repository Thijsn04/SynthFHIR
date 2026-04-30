from typing import Literal

from fastapi import APIRouter, Query

from generators.patient_gen import generate_patients
from mappers.r4_mapper import map_to_r4
from mappers.r5_mapper import map_to_r5

router = APIRouter(tags=["Patient"])


@router.get(
    "/generate/patient",
    summary="Generate synthetic FHIR Patient resources",
    response_description="A list of synthetic FHIR Patient resources",
)
def generate_patient(
    count: int = Query(
        default=1,
        ge=1,
        le=100,
        description="Number of patients to generate (1–100)",
    ),
    version: Literal["R4", "R5"] = Query(
        default="R4",
        description="FHIR version: R4 or R5",
    ),
):
    """
    Generate one or more synthetic FHIR Patient resources.

    - **count**: How many patients to generate (1–100).
    - **version**: Which FHIR version to use — `R4` (default) or `R5`.

    All data is generated locally via Faker — no external services are called.
    """
    raw_patients = generate_patients(count)
    mapper = map_to_r4 if version == "R4" else map_to_r5
    return [mapper(p) for p in raw_patients]

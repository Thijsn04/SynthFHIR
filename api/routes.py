import random
from typing import Annotated, Literal

from faker import Faker
from fastapi import APIRouter, Query

from data.conditions import CONDITIONS
from data.observations import OBSERVATIONS
from generators.cohort_gen import generate_cohort
from generators.patient_gen import generate_patients
from mappers.r4 import allergy as r4_allergy
from mappers.r4 import bundle as r4_bundle
from mappers.r4 import condition as r4_condition
from mappers.r4 import encounter as r4_encounter
from mappers.r4 import observation as r4_observation
from mappers.r4 import organization as r4_organization
from mappers.r4 import patient as r4_patient
from mappers.r4 import practitioner as r4_practitioner
from mappers.r4 import related_person as r4_related_person
from mappers.r5 import allergy as r5_allergy
from mappers.r5 import bundle as r5_bundle
from mappers.r5 import condition as r5_condition
from mappers.r5 import encounter as r5_encounter
from mappers.r5 import observation as r5_observation
from mappers.r5 import organization as r5_organization
from mappers.r5 import patient as r5_patient
from mappers.r5 import practitioner as r5_practitioner
from mappers.r5 import related_person as r5_related_person

router = APIRouter()

# ---------------------------------------------------------------------------
# Mapper dispatch tables — index by FHIR version string
# ---------------------------------------------------------------------------
_PATIENT_MAPPER    = {"R4": r4_patient.map_patient,           "R5": r5_patient.map_patient}
_PRAC_MAPPER       = {"R4": r4_practitioner.map_practitioner,  "R5": r5_practitioner.map_practitioner}
_ORG_MAPPER        = {"R4": r4_organization.map_organization,  "R5": r5_organization.map_organization}
_RP_MAPPER         = {"R4": r4_related_person.map_related_person, "R5": r5_related_person.map_related_person}
_COND_MAPPER       = {"R4": r4_condition.map_condition,        "R5": r5_condition.map_condition}
_ALLERGY_MAPPER    = {"R4": r4_allergy.map_allergy,            "R5": r5_allergy.map_allergy}
_ENC_MAPPER        = {"R4": r4_encounter.map_encounter,        "R5": r5_encounter.map_encounter}
_OBS_MAPPER        = {"R4": r4_observation.map_observation,    "R5": r5_observation.map_observation}
_BUNDLE_BUILDER    = {"R4": r4_bundle.build_bundle,            "R5": r5_bundle.build_bundle}


def _map_and_bundle(raw: dict, version: str) -> dict:
    """Maps every raw resource in the cohort dict and wraps the result in a Bundle."""
    v = version
    resources: list[dict] = []
    resources += [_ORG_MAPPER[v](o)   for o in raw["organizations"]]
    resources += [_PRAC_MAPPER[v](p)  for p in raw["practitioners"]]
    resources += [_PATIENT_MAPPER[v](p) for p in raw["patients"]]
    resources += [_COND_MAPPER[v](c)  for c in raw["conditions"]]
    resources += [_ALLERGY_MAPPER[v](a) for a in raw["allergies"]]
    resources += [_RP_MAPPER[v](r)    for r in raw["related_persons"]]
    resources += [_ENC_MAPPER[v](e)   for e in raw["encounters"]]
    resources += [_OBS_MAPPER[v](o)   for o in raw["observations"]]
    return _BUNDLE_BUILDER[v](resources)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/generate/cohort",
    tags=["Generate"],
    summary="Generate a fully relational synthetic clinical cohort",
    response_description="A FHIR Bundle containing patients, practitioners, organizations, "
                         "conditions, allergies, encounters, observations, and related persons.",
)
def generate_cohort_endpoint(
    count: Annotated[int, Query(ge=1, le=1000, description="Number of patients")] = 10,
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
    age_min: Annotated[int, Query(ge=0, le=119, description="Minimum patient age")] = 0,
    age_max: Annotated[int, Query(ge=1, le=120, description="Maximum patient age")] = 80,
    condition: Annotated[
        str | None,
        Query(description="Optional condition filter — partial name or key, e.g. 'diabetes', 'hypertension'"),
    ] = None,
    seed: Annotated[int | None, Query(description="RNG seed for reproducible output")] = None,
    num_practitioners: Annotated[int, Query(ge=1, le=50, description="Practitioners to generate")] = 3,
    num_organizations: Annotated[int, Query(ge=1, le=10, description="Organizations to generate")] = 1,
):
    """
    Generate a complete, interconnected synthetic clinical dataset.

    Every patient is linked to practitioners, an organization, conditions,
    allergies, family members (RelatedPerson), clinic visits (Encounter),
    and condition-appropriate lab/vital results (Observation).

    Use **seed** to get reproducible datasets across runs — useful for CI
    pipelines and regression testing.
    """
    raw = generate_cohort(
        count=count,
        age_min=age_min,
        age_max=age_max,
        condition_filter=condition,
        seed=seed,
        num_practitioners=num_practitioners,
        num_organizations=num_organizations,
    )
    return _map_and_bundle(raw, version)


@router.get(
    "/generate/patient",
    tags=["Generate"],
    summary="Generate one or more standalone Patient resources",
    response_description="A FHIR Bundle containing only Patient resources.",
)
def generate_patient_endpoint(
    count: Annotated[int, Query(ge=1, le=100, description="Number of patients (1–100)")] = 1,
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
    age_min: Annotated[int, Query(ge=0, le=119)] = 0,
    age_max: Annotated[int, Query(ge=1, le=120)] = 100,
    seed: Annotated[int | None, Query(description="RNG seed for reproducible output")] = None,
):
    """
    Generate lightweight Patient resources with no linked clinical data.
    For a full relational dataset use **/generate/cohort** instead.
    """
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    raw_patients = generate_patients(count, age_min=age_min, age_max=age_max)
    mapped = [_PATIENT_MAPPER[version](p) for p in raw_patients]
    return _BUNDLE_BUILDER[version](mapped)


@router.get(
    "/conditions",
    tags=["Catalog"],
    summary="List all available condition keys and display names",
)
def list_conditions():
    """Returns the full catalog of condition keys accepted by the `condition` query parameter."""
    return [
        {
            "key": c.key,
            "display": c.display,
            "snomed_code": c.snomed_code,
            "icd10_code": c.icd10_code,
            "linked_observations": list(c.linked_obs_types),
        }
        for c in CONDITIONS
    ]


@router.get(
    "/observations",
    tags=["Catalog"],
    summary="List all supported observation types",
)
def list_observations():
    """Returns the full catalog of observation types that can be generated."""
    return [
        {
            "key": obs.key,
            "loinc_code": obs.loinc_code,
            "display": obs.display,
            "category": obs.category_code,
            "unit": obs.unit,
        }
        for obs in OBSERVATIONS.values()
    ]

"""SynthFHIR public Python API.

A small, stable surface for using SynthFHIR as a library:

    import synthfhir

    bundle = synthfhir.generate_cohort_bundle(count=10, version="R4", seed=42)
    report = synthfhir.validate_bundle(bundle)
    assert report.valid

    ndjson = synthfhir.generate_cohort_ndjson(count=100)

Everything here is deterministic when a `seed` is supplied. The heavy lifting
lives in the `generators`, `mappers`, and `validation` packages; this module is
a thin, documented facade over them so downstream code has one import to learn.
"""
from __future__ import annotations

from data.conditions import CONDITIONS, ConditionDef
from data.observations import OBSERVATIONS
from generators._rng import generation_scope, seed_all
from generators.cohort_gen import generate_cohort as generate_raw_cohort
from mappers.pipeline import build_bundle_from_cohort, iter_ndjson, map_cohort
from validation import ValidationReport, validate_bundle

__version__ = "0.5.0"

__all__ = [
    "__version__",
    "CONDITIONS",
    "ConditionDef",
    "OBSERVATIONS",
    "seed_all",
    "generate_raw_cohort",
    "generate_cohort_bundle",
    "generate_cohort_ndjson",
    "map_cohort",
    "validate_bundle",
    "ValidationReport",
]


def generate_cohort_bundle(
    count: int = 10,
    *,
    version: str = "R4",
    age_min: int = 0,
    age_max: int = 80,
    condition: str | None = None,
    years: int = 2,
    num_practitioners: int = 3,
    num_organizations: int = 1,
    profile: str = "base",
    bundle_type: str = "collection",
    seed: int | None = None,
) -> dict:
    """Generate a full relational cohort and return it as a FHIR Bundle dict.

    Args:
        count: Number of patients.
        version: FHIR version, "R4" or "R5".
        age_min, age_max: Inclusive patient age bounds.
        condition: Optional condition key or partial name every patient receives.
        years: Years of clinical history per patient.
        num_practitioners, num_organizations: Size of the shared care network.
        profile: "base" or "us-core" (adds race, ethnicity, and birth-sex).
        bundle_type: "collection" or "transaction".
        seed: Seed for reproducible output.

    Returns:
        A FHIR Bundle as a plain dict, ready to serialize with json.dumps.
    """
    # Hold one generation scope across both generation and bundling so the
    # bundle id draw stays inside the seeded, serialized section.
    with generation_scope(seed):
        raw = generate_raw_cohort(
            count=count,
            age_min=age_min,
            age_max=age_max,
            condition_filter=condition,
            seed=None,
            num_practitioners=num_practitioners,
            num_organizations=num_organizations,
            years=years,
        )
        return build_bundle_from_cohort(
            raw, version, bundle_type=bundle_type, us_core=profile == "us-core"
        )


def generate_cohort_ndjson(
    count: int = 10,
    *,
    version: str = "R4",
    age_min: int = 0,
    age_max: int = 80,
    condition: str | None = None,
    years: int = 2,
    num_practitioners: int = 3,
    num_organizations: int = 1,
    profile: str = "base",
    seed: int | None = None,
) -> str:
    """Generate a cohort and return it as an NDJSON string (one resource per line)."""
    with generation_scope(seed):
        raw = generate_raw_cohort(
            count=count,
            age_min=age_min,
            age_max=age_max,
            condition_filter=condition,
            seed=None,
            num_practitioners=num_practitioners,
            num_organizations=num_organizations,
            years=years,
        )
        return "".join(iter_ndjson(raw, version, us_core=profile == "us-core"))

import asyncio
from typing import Annotated, Literal

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from data.conditions import CONDITIONS, VALID_CONDITION_KEYS, find_condition
from data.observations import OBSERVATIONS
from generators._rng import generation_scope
from generators.cohort_gen import generate_cohort
from generators.patient_gen import generate_patients
from mappers.pipeline import (
    BUNDLE_BUILDER,
    ORG_MAPPER,
    PATIENT_MAPPER,
    PRAC_MAPPER,
    build_bundle_from_cohort,
    iter_ndjson,
)

router = APIRouter()


def _validate_condition(condition: str | None) -> None:
    """Raise HTTP 422 if condition filter matches no known condition."""
    if condition is not None and find_condition(condition) is None:
        valid = sorted(VALID_CONDITION_KEYS)
        raise HTTPException(
            status_code=422,
            detail={
                "msg": f"Unknown condition '{condition}'. Valid keys: {valid}",
                "valid_keys": valid,
            },
        )


def _validate_age_range(age_min: int, age_max: int) -> None:
    if age_min >= age_max:
        raise HTTPException(
            status_code=422,
            detail=f"age_min ({age_min}) must be less than age_max ({age_max})",
        )


class CohortSpec(BaseModel):
    """Generation spec for POST /generate/cohort.

    Mirrors the cohort query parameters so complex requests can be expressed as
    a single JSON document instead of a long query string.
    """

    count: int = Field(10, ge=1, le=1000, description="Number of patients")
    version: Literal["R4", "R5"] = "R4"
    age_min: int = Field(0, ge=0, le=119)
    age_max: int = Field(80, ge=1, le=120)
    condition: str | None = Field(None, description="Condition key or partial name")
    seed: int | None = Field(None, description="Seed for reproducible output")
    num_practitioners: int = Field(3, ge=1, le=50)
    num_organizations: int = Field(1, ge=1, le=10)
    years: int = Field(2, ge=1, le=20)
    bundle_type: Literal["collection", "transaction"] = "collection"
    format: Literal["bundle", "ndjson"] = "bundle"
    profile: Literal["base", "us-core"] = "base"


async def _run_cohort(spec: CohortSpec):
    """Shared cohort generation used by both the GET and POST endpoints."""
    _validate_age_range(spec.age_min, spec.age_max)
    _validate_condition(spec.condition)

    us_core = spec.profile == "us-core"

    def _produce():
        # Generation and bundling share one scope so seeded output is
        # reproducible and concurrent requests cannot corrupt each other's RNG.
        with generation_scope(spec.seed):
            raw = generate_cohort(
                count=spec.count,
                age_min=spec.age_min,
                age_max=spec.age_max,
                condition_filter=spec.condition,
                seed=None,
                num_practitioners=spec.num_practitioners,
                num_organizations=spec.num_organizations,
                years=spec.years,
            )
            if spec.format == "ndjson":
                # NDJSON mapping draws no randomness, so it can stream after the
                # scope is released; the raw cohort is already deterministic.
                return raw, None
            bundle = build_bundle_from_cohort(
                raw, spec.version, bundle_type=spec.bundle_type, us_core=us_core
            )
            return None, bundle

    raw, bundle = await asyncio.to_thread(_produce)

    if spec.format == "ndjson":
        return StreamingResponse(
            iter_ndjson(raw, spec.version, us_core=us_core),
            media_type="application/fhir+ndjson",
            headers={"Content-Disposition": "attachment; filename=cohort.ndjson"},
        )

    return bundle


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/generate/cohort",
    tags=["Generate"],
    summary="Generate a fully relational synthetic clinical cohort",
    response_description=(
        "A FHIR Bundle (or NDJSON stream) containing patients, practitioners, "
        "organizations, conditions, allergies, immunizations, encounters, "
        "observations, diagnostic reports, medications, and related persons."
    ),
)
async def generate_cohort_endpoint(
    count: Annotated[int, Query(ge=1, le=1000, description="Number of patients")] = 10,
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
    age_min: Annotated[int, Query(ge=0, le=119, description="Minimum patient age")] = 0,
    age_max: Annotated[int, Query(ge=1, le=120, description="Maximum patient age")] = 80,
    condition: Annotated[
        str | None,
        Query(description="Condition filter - partial name or key, e.g. 'diabetes', 'hypertension'"),
    ] = None,
    seed: Annotated[int | None, Query(description="RNG seed for fully reproducible output")] = None,
    num_practitioners: Annotated[int, Query(ge=1, le=50)] = 3,
    num_organizations: Annotated[int, Query(ge=1, le=10)] = 1,
    years: Annotated[
        int,
        Query(ge=1, le=20, description="Years of clinical history to generate per patient (1-20)"),
    ] = 2,
    bundle_type: Annotated[
        Literal["collection", "transaction"],
        Query(description="FHIR Bundle type. Use 'transaction' for direct server ingestion."),
    ] = "collection",
    format: Annotated[
        Literal["bundle", "ndjson"],
        Query(description="Response format. 'ndjson' streams one resource per line."),
    ] = "bundle",
    profile: Annotated[
        Literal["base", "us-core"],
        Query(description="Profile set. 'us-core' adds race, ethnicity, and birth-sex extensions."),
    ] = "base",
):
    """
    Generate a complete, interconnected synthetic clinical dataset.

    Every patient is linked to practitioners, an organization, conditions,
    allergies, immunizations, family members (RelatedPerson), clinic visits
    (Encounter), condition-appropriate lab/vital results (Observation) grouped
    under DiagnosticReport resources, and MedicationRequests for active
    conditions.

    Use **seed** to get fully reproducible datasets across runs - useful for
    CI pipelines and regression testing.
    """
    return await _run_cohort(
        CohortSpec(
            count=count,
            version=version,
            age_min=age_min,
            age_max=age_max,
            condition=condition,
            seed=seed,
            num_practitioners=num_practitioners,
            num_organizations=num_organizations,
            years=years,
            bundle_type=bundle_type,
            format=format,
            profile=profile,
        )
    )


@router.post(
    "/generate/cohort",
    tags=["Generate"],
    summary="Generate a cohort from a JSON generation spec",
    response_description="A FHIR Bundle (or NDJSON stream) for the given spec.",
)
async def generate_cohort_post_endpoint(spec: CohortSpec):
    """Generate a cohort from a JSON body instead of query parameters.

    Accepts the same options as the GET endpoint as a single JSON document,
    which is more convenient for complex or scripted requests.
    """
    return await _run_cohort(spec)


@router.get(
    "/generate/patient",
    tags=["Generate"],
    summary="Generate one or more standalone Patient resources",
    response_description="A FHIR Bundle containing only Patient resources.",
)
async def generate_patient_endpoint(
    count: Annotated[int, Query(ge=1, le=100, description="Number of patients (1-100)")] = 1,
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
    age_min: Annotated[int, Query(ge=0, le=119)] = 0,
    age_max: Annotated[int, Query(ge=1, le=120)] = 100,
    seed: Annotated[int | None, Query(description="RNG seed for reproducible output")] = None,
    bundle_type: Annotated[Literal["collection", "transaction"], Query()] = "collection",
    profile: Annotated[Literal["base", "us-core"], Query()] = "base",
):
    """Generate lightweight Patient resources with no linked clinical data.
    For a full relational dataset use **/generate/cohort** instead.
    """
    _validate_age_range(age_min, age_max)

    us_core = profile == "us-core"

    def _build() -> list[dict]:
        with generation_scope(seed):
            return generate_patients(count, age_min, age_max)

    raw_patients = await asyncio.to_thread(_build)
    mapped = [PATIENT_MAPPER[version](p, us_core=us_core) for p in raw_patients]
    return BUNDLE_BUILDER[version](mapped, bundle_type=bundle_type)


@router.get(
    "/generate/practitioner",
    tags=["Generate"],
    summary="Generate one or more standalone Practitioner resources",
)
async def generate_practitioner_endpoint(
    count: Annotated[int, Query(ge=1, le=100, description="Number of practitioners (1-100)")] = 1,
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
    seed: Annotated[int | None, Query(description="RNG seed for reproducible output")] = None,
    bundle_type: Annotated[Literal["collection", "transaction"], Query()] = "collection",
):
    """Generate Practitioner resources not linked to any organization or patient."""
    from generators._rng import new_uuid
    from generators.practitioner_gen import generate_practitioner

    def _build() -> list[dict]:
        with generation_scope(seed):
            dummy_org_id = new_uuid()
            return [generate_practitioner(dummy_org_id) for _ in range(count)]

    raw = await asyncio.to_thread(_build)
    mapped = [PRAC_MAPPER[version](p) for p in raw]
    return BUNDLE_BUILDER[version](mapped, bundle_type=bundle_type)


@router.get(
    "/generate/organization",
    tags=["Generate"],
    summary="Generate one or more standalone Organization resources",
)
async def generate_organization_endpoint(
    count: Annotated[int, Query(ge=1, le=50, description="Number of organizations (1-50)")] = 1,
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
    seed: Annotated[int | None, Query(description="RNG seed for reproducible output")] = None,
    bundle_type: Annotated[Literal["collection", "transaction"], Query()] = "collection",
):
    """Generate Organization resources representing healthcare facilities."""
    from generators.organization_gen import generate_organization

    def _build() -> list[dict]:
        with generation_scope(seed):
            return [generate_organization() for _ in range(count)]

    raw = await asyncio.to_thread(_build)
    mapped = [ORG_MAPPER[version](o) for o in raw]
    return BUNDLE_BUILDER[version](mapped, bundle_type=bundle_type)


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
            "typical_age_min": c.typical_age_min,
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
            "normal_range": {"low": obs.normal_range[0], "high": obs.normal_range[1]},
            "abnormal_range": {"low": obs.abnormal_range[0], "high": obs.abnormal_range[1]},
        }
        for obs in OBSERVATIONS.values()
    ]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@router.post(
    "/validate",
    tags=["Validation"],
    summary="Validate a FHIR Bundle for structure and referential integrity",
    response_description="A validation report with errors and warnings.",
)
def validate_bundle_endpoint(
    bundle: Annotated[dict, Body(description="A FHIR Bundle JSON document to validate")],
):
    """Validate a FHIR Bundle.

    Checks bundle shape, resource types, id and fullUrl uniqueness, base-FHIR
    mandatory elements, transaction request entries, and that every internal
    reference resolves to a resource inside the bundle. Returns a structured
    report; the bundle is never stored.
    """
    from validation import validate_bundle

    return validate_bundle(bundle).to_dict()


# ---------------------------------------------------------------------------
# FHIR Metadata / CapabilityStatement
# ---------------------------------------------------------------------------

_RESOURCE_TYPES = [
    "Patient", "Practitioner", "PractitionerRole", "Organization", "Location",
    "RelatedPerson", "Condition", "AllergyIntolerance", "Immunization", "Coverage",
    "Encounter", "Appointment", "EpisodeOfCare", "Observation", "DiagnosticReport",
    "MedicationRequest", "Procedure", "ServiceRequest", "CareTeam", "CarePlan",
    "Goal", "List", "FamilyMemberHistory", "Consent", "Provenance",
]

_US_CORE_BASE = "http://hl7.org/fhir/us/core/StructureDefinition"


@router.get(
    "/metadata",
    tags=["Conformance"],
    summary="FHIR CapabilityStatement - describes what this server supports",
)
def capability_statement(
    version: Annotated[Literal["R4", "R5"], Query(description="FHIR version")] = "R4",
):
    """Returns a CapabilityStatement resource listing supported resource types,
    FHIR version, and US Core profile URLs.  Follows the FHIR REST conformance
    pattern: ``GET /metadata``.
    """
    from mappers._helpers import utcnow

    fhir_version = "4.0.1" if version == "R4" else "5.0.0"

    rest_resources = []
    for rt in _RESOURCE_TYPES:
        entry: dict = {
            "type": rt,
            "interaction": [
                {"code": "read"},
                {"code": "search-type"},
            ],
        }
        # Attach US Core profile for R4 resources that have one
        if version == "R4":
            profile_map = {
                "Patient":              f"{_US_CORE_BASE}/us-core-patient",
                "AllergyIntolerance":   f"{_US_CORE_BASE}/us-core-allergyintolerance",
                "CarePlan":             f"{_US_CORE_BASE}/us-core-careplan",
                "CareTeam":             f"{_US_CORE_BASE}/us-core-careteam",
                "Condition":            f"{_US_CORE_BASE}/us-core-condition-problems-health-concerns",
                "DiagnosticReport":     f"{_US_CORE_BASE}/us-core-diagnosticreport-lab",
                "Encounter":            f"{_US_CORE_BASE}/us-core-encounter",
                "Goal":                 f"{_US_CORE_BASE}/us-core-goal",
                "Immunization":         f"{_US_CORE_BASE}/us-core-immunization",
                "Location":             f"{_US_CORE_BASE}/us-core-location",
                "MedicationRequest":    f"{_US_CORE_BASE}/us-core-medicationrequest",
                "Observation":          f"{_US_CORE_BASE}/us-core-observation-lab",
                "Organization":         f"{_US_CORE_BASE}/us-core-organization",
                "Practitioner":         f"{_US_CORE_BASE}/us-core-practitioner",
                "PractitionerRole":     f"{_US_CORE_BASE}/us-core-practitionerrole",
                "Procedure":            f"{_US_CORE_BASE}/us-core-procedure",
            }
            if rt in profile_map:
                entry["supportedProfile"] = [profile_map[rt]]
        rest_resources.append(entry)

    return {
        "resourceType": "CapabilityStatement",
        "id": "synthfhir-capability",
        "status": "active",
        "date": utcnow()[:10],
        "publisher": "SynthFHIR",
        "kind": "instance",
        "software": {
            "name": "SynthFHIR",
            "version": "0.2.0",
        },
        "fhirVersion": fhir_version,
        "format": ["application/fhir+json"],
        "rest": [
            {
                "mode": "server",
                "resource": rest_resources,
            }
        ],
    }

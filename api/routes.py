import asyncio
import json
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from data.conditions import CONDITIONS, VALID_CONDITION_KEYS, find_condition
from data.observations import OBSERVATIONS
from generators._rng import seed_all
from generators.cohort_gen import generate_cohort
from generators.patient_gen import generate_patients
from mappers.r4 import allergy as r4_allergy
from mappers.r4 import bundle as r4_bundle
from mappers.r4 import care_plan as r4_care_plan
from mappers.r4 import care_team as r4_care_team
from mappers.r4 import condition as r4_condition
from mappers.r4 import consent as r4_consent
from mappers.r4 import coverage as r4_coverage
from mappers.r4 import diagnostic_report as r4_diagnostic_report
from mappers.r4 import encounter as r4_encounter
from mappers.r4 import family_member_history as r4_family_member_history
from mappers.r4 import goal as r4_goal
from mappers.r4 import immunization as r4_immunization
from mappers.r4 import list as r4_list
from mappers.r4 import location as r4_location
from mappers.r4 import medication as r4_medication
from mappers.r4 import observation as r4_observation
from mappers.r4 import organization as r4_organization
from mappers.r4 import patient as r4_patient
from mappers.r4 import practitioner as r4_practitioner
from mappers.r4 import practitioner_role as r4_practitioner_role
from mappers.r4 import procedure as r4_procedure
from mappers.r4 import provenance as r4_provenance
from mappers.r4 import related_person as r4_related_person
from mappers.r4 import appointment as r4_appointment
from mappers.r4 import episode_of_care as r4_episode_of_care
from mappers.r4 import service_request as r4_service_request
from mappers.r5 import allergy as r5_allergy
from mappers.r5 import appointment as r5_appointment
from mappers.r5 import episode_of_care as r5_episode_of_care
from mappers.r5 import bundle as r5_bundle
from mappers.r5 import care_plan as r5_care_plan
from mappers.r5 import care_team as r5_care_team
from mappers.r5 import condition as r5_condition
from mappers.r5 import consent as r5_consent
from mappers.r5 import coverage as r5_coverage
from mappers.r5 import diagnostic_report as r5_diagnostic_report
from mappers.r5 import encounter as r5_encounter
from mappers.r5 import family_member_history as r5_family_member_history
from mappers.r5 import goal as r5_goal
from mappers.r5 import immunization as r5_immunization
from mappers.r5 import list as r5_list
from mappers.r5 import location as r5_location
from mappers.r5 import medication as r5_medication
from mappers.r5 import observation as r5_observation
from mappers.r5 import organization as r5_organization
from mappers.r5 import patient as r5_patient
from mappers.r5 import practitioner as r5_practitioner
from mappers.r5 import practitioner_role as r5_practitioner_role
from mappers.r5 import procedure as r5_procedure
from mappers.r5 import provenance as r5_provenance
from mappers.r5 import related_person as r5_related_person
from mappers.r5 import service_request as r5_service_request

router = APIRouter()

# ---------------------------------------------------------------------------
# Mapper dispatch tables — indexed by FHIR version string
# ---------------------------------------------------------------------------
_PATIENT_MAPPER    = {"R4": r4_patient.map_patient,                          "R5": r5_patient.map_patient}
_PRAC_MAPPER       = {"R4": r4_practitioner.map_practitioner,                "R5": r5_practitioner.map_practitioner}
_ORG_MAPPER        = {"R4": r4_organization.map_organization,                "R5": r5_organization.map_organization}
_LOC_MAPPER        = {"R4": r4_location.map_location,                        "R5": r5_location.map_location}
_PR_MAPPER         = {"R4": r4_practitioner_role.map_practitioner_role,      "R5": r5_practitioner_role.map_practitioner_role}
_RP_MAPPER         = {"R4": r4_related_person.map_related_person,            "R5": r5_related_person.map_related_person}
_COND_MAPPER       = {"R4": r4_condition.map_condition,                      "R5": r5_condition.map_condition}
_ALLERGY_MAPPER    = {"R4": r4_allergy.map_allergy,                          "R5": r5_allergy.map_allergy}
_ENC_MAPPER        = {"R4": r4_encounter.map_encounter,                      "R5": r5_encounter.map_encounter}
_OBS_MAPPER        = {"R4": r4_observation.map_observation,                  "R5": r5_observation.map_observation}
_MED_MAPPER        = {"R4": r4_medication.map_medication,                    "R5": r5_medication.map_medication}
_IMM_MAPPER        = {"R4": r4_immunization.map_immunization,                "R5": r5_immunization.map_immunization}
_DR_MAPPER         = {"R4": r4_diagnostic_report.map_diagnostic_report,      "R5": r5_diagnostic_report.map_diagnostic_report}
_PROC_MAPPER       = {"R4": r4_procedure.map_procedure,                      "R5": r5_procedure.map_procedure}
_SR_MAPPER         = {"R4": r4_service_request.map_service_request,          "R5": r5_service_request.map_service_request}
_COV_MAPPER        = {"R4": r4_coverage.map_coverage,                        "R5": r5_coverage.map_coverage}
_FMH_MAPPER        = {"R4": r4_family_member_history.map_family_member_history, "R5": r5_family_member_history.map_family_member_history}
_CONSENT_MAPPER    = {"R4": r4_consent.map_consent,                          "R5": r5_consent.map_consent}
_CARE_TEAM_MAPPER  = {"R4": r4_care_team.map_care_team,                      "R5": r5_care_team.map_care_team}
_CARE_PLAN_MAPPER  = {"R4": r4_care_plan.map_care_plan,                      "R5": r5_care_plan.map_care_plan}
_GOAL_MAPPER       = {"R4": r4_goal.map_goal,                                "R5": r5_goal.map_goal}
_LIST_MAPPER       = {"R4": r4_list.map_list,                                "R5": r5_list.map_list}
_PROV_MAPPER       = {"R4": r4_provenance.map_provenance,                    "R5": r5_provenance.map_provenance}
_APPT_MAPPER       = {"R4": r4_appointment.map_appointment,                  "R5": r5_appointment.map_appointment}
_EOC_MAPPER        = {"R4": r4_episode_of_care.map_episode_of_care,          "R5": r5_episode_of_care.map_episode_of_care}
_BUNDLE_BUILDER    = {"R4": r4_bundle.build_bundle,                          "R5": r5_bundle.build_bundle}


def _map_and_bundle(raw: dict, version: str, bundle_type: str, us_core: bool) -> dict:
    """Maps every raw resource in the cohort dict and wraps the result in a Bundle."""
    v = version
    uc = {"us_core": us_core}
    resources: list[dict] = []

    resources += [_ORG_MAPPER[v](o,   **uc)   for o   in raw["organizations"]]
    resources += [_LOC_MAPPER[v](loc, **uc)   for loc in raw.get("locations", [])]
    resources += [_PRAC_MAPPER[v](p,  **uc)   for p   in raw["practitioners"]]
    resources += [_PR_MAPPER[v](pr,   **uc)   for pr  in raw.get("practitioner_roles", [])]
    resources += [_PATIENT_MAPPER[v](p, **uc) for p   in raw["patients"]]
    resources += [_COV_MAPPER[v](c,   **uc)   for c   in raw.get("coverages", [])]
    resources += [_COND_MAPPER[v](c,  **uc)   for c   in raw["conditions"]]
    resources += [_ALLERGY_MAPPER[v](a, **uc) for a   in raw["allergies"]]
    resources += [_IMM_MAPPER[v](i,   **uc)   for i   in raw.get("immunizations", [])]
    resources += [_RP_MAPPER[v](r,    **uc)   for r   in raw["related_persons"]]
    resources += [_FMH_MAPPER[v](f,   **uc)   for f   in raw.get("family_member_histories", [])]
    resources += [_CONSENT_MAPPER[v](c, **uc) for c   in raw.get("consents", [])]
    resources += [_CARE_TEAM_MAPPER[v](ct, **uc) for ct in raw.get("care_teams", [])]
    resources += [_CARE_PLAN_MAPPER[v](cp, **uc) for cp in raw.get("care_plans", [])]
    resources += [_GOAL_MAPPER[v](g,  **uc)   for g   in raw.get("goals", [])]
    resources += [_ENC_MAPPER[v](e,   **uc)   for e   in raw["encounters"]]
    resources += [_APPT_MAPPER[v](a,  **uc)   for a   in raw.get("appointments", [])]
    resources += [_EOC_MAPPER[v](eoc, **uc)   for eoc in raw.get("episodes_of_care", [])]
    resources += [_OBS_MAPPER[v](o,   **uc)   for o   in raw["observations"]]
    resources += [_DR_MAPPER[v](d,    **uc)   for d   in raw.get("diagnostic_reports", [])]
    resources += [_MED_MAPPER[v](m,   **uc)   for m   in raw.get("medications", [])]
    resources += [_PROC_MAPPER[v](p,  **uc)   for p   in raw.get("procedures", [])]
    resources += [_SR_MAPPER[v](s,    **uc)   for s   in raw.get("service_requests", [])]
    resources += [_LIST_MAPPER[v](lst, **uc)  for lst in raw.get("lists", [])]
    resources += [_PROV_MAPPER[v](p,  **uc)   for p   in raw.get("provenances", [])]

    return _BUNDLE_BUILDER[v](resources, bundle_type=bundle_type)


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


def _ndjson_stream(raw: dict, version: str, us_core: bool):
    """Generator that yields one FHIR resource JSON per line (NDJSON)."""
    v = version
    uc = {"us_core": us_core}
    mappers = [
        (_ORG_MAPPER[v],         raw["organizations"],                   uc),
        (_LOC_MAPPER[v],         raw.get("locations", []),               uc),
        (_PRAC_MAPPER[v],        raw["practitioners"],                   uc),
        (_PR_MAPPER[v],          raw.get("practitioner_roles", []),      uc),
        (_PATIENT_MAPPER[v],     raw["patients"],                        uc),
        (_COV_MAPPER[v],         raw.get("coverages", []),               uc),
        (_COND_MAPPER[v],        raw["conditions"],                      uc),
        (_ALLERGY_MAPPER[v],     raw["allergies"],                       uc),
        (_IMM_MAPPER[v],         raw.get("immunizations", []),           uc),
        (_RP_MAPPER[v],          raw["related_persons"],                 uc),
        (_FMH_MAPPER[v],         raw.get("family_member_histories", []), uc),
        (_CONSENT_MAPPER[v],     raw.get("consents", []),                uc),
        (_CARE_TEAM_MAPPER[v],   raw.get("care_teams", []),              uc),
        (_CARE_PLAN_MAPPER[v],   raw.get("care_plans", []),              uc),
        (_GOAL_MAPPER[v],        raw.get("goals", []),                   uc),
        (_ENC_MAPPER[v],         raw["encounters"],                      uc),
        (_APPT_MAPPER[v],        raw.get("appointments", []),            uc),
        (_EOC_MAPPER[v],         raw.get("episodes_of_care", []),        uc),
        (_OBS_MAPPER[v],         raw["observations"],                    uc),
        (_DR_MAPPER[v],          raw.get("diagnostic_reports", []),      uc),
        (_MED_MAPPER[v],         raw.get("medications", []),             uc),
        (_PROC_MAPPER[v],        raw.get("procedures", []),              uc),
        (_SR_MAPPER[v],          raw.get("service_requests", []),        uc),
        (_LIST_MAPPER[v],        raw.get("lists", []),                   uc),
        (_PROV_MAPPER[v],        raw.get("provenances", []),             uc),
    ]
    for mapper_fn, items, kwargs in mappers:
        for item in items:
            yield json.dumps(mapper_fn(item, **kwargs), separators=(",", ":")) + "\n"


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
        Query(description="Condition filter — partial name or key, e.g. 'diabetes', 'hypertension'"),
    ] = None,
    seed: Annotated[int | None, Query(description="RNG seed for fully reproducible output")] = None,
    num_practitioners: Annotated[int, Query(ge=1, le=50)] = 3,
    num_organizations: Annotated[int, Query(ge=1, le=10)] = 1,
    years: Annotated[
        int,
        Query(ge=1, le=20, description="Years of clinical history to generate per patient (1–20)"),
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

    Use **seed** to get fully reproducible datasets across runs — useful for
    CI pipelines and regression testing.
    """
    _validate_age_range(age_min, age_max)
    _validate_condition(condition)

    us_core = profile == "us-core"

    raw = await asyncio.to_thread(
        generate_cohort,
        count=count,
        age_min=age_min,
        age_max=age_max,
        condition_filter=condition,
        seed=seed,
        num_practitioners=num_practitioners,
        num_organizations=num_organizations,
        years=years,
    )

    if format == "ndjson":
        return StreamingResponse(
            _ndjson_stream(raw, version, us_core),
            media_type="application/fhir+ndjson",
            headers={"Content-Disposition": "attachment; filename=cohort.ndjson"},
        )

    return _map_and_bundle(raw, version, bundle_type, us_core)


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

    if seed is not None:
        seed_all(seed)

    us_core = profile == "us-core"
    raw_patients = await asyncio.to_thread(generate_patients, count, age_min, age_max)
    mapped = [_PATIENT_MAPPER[version](p, us_core=us_core) for p in raw_patients]
    return _BUNDLE_BUILDER[version](mapped, bundle_type=bundle_type)


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

    if seed is not None:
        seed_all(seed)

    dummy_org_id = new_uuid()
    raw = await asyncio.to_thread(
        lambda: [generate_practitioner(dummy_org_id) for _ in range(count)]
    )
    mapped = [_PRAC_MAPPER[version](p) for p in raw]
    return _BUNDLE_BUILDER[version](mapped, bundle_type=bundle_type)


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

    if seed is not None:
        seed_all(seed)

    raw = await asyncio.to_thread(lambda: [generate_organization() for _ in range(count)])
    mapped = [_ORG_MAPPER[version](o) for o in raw]
    return _BUNDLE_BUILDER[version](mapped, bundle_type=bundle_type)


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
    summary="FHIR CapabilityStatement — describes what this server supports",
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

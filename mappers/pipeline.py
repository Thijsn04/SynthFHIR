"""Mapping pipeline: turn a raw generator cohort into FHIR output.

This module owns the version dispatch tables and the resource ordering so that
every entry point (the REST API, the CLI, and the Python library) produces
identical bundles. Nothing here knows about HTTP.
"""
from __future__ import annotations

import json
from collections.abc import Iterator

from mappers.r4 import allergy as r4_allergy
from mappers.r4 import appointment as r4_appointment
from mappers.r4 import bundle as r4_bundle
from mappers.r4 import care_plan as r4_care_plan
from mappers.r4 import care_team as r4_care_team
from mappers.r4 import condition as r4_condition
from mappers.r4 import consent as r4_consent
from mappers.r4 import coverage as r4_coverage
from mappers.r4 import diagnostic_report as r4_diagnostic_report
from mappers.r4 import document_reference as r4_document_reference
from mappers.r4 import encounter as r4_encounter
from mappers.r4 import episode_of_care as r4_episode_of_care
from mappers.r4 import family_member_history as r4_family_member_history
from mappers.r4 import goal as r4_goal
from mappers.r4 import immunization as r4_immunization
from mappers.r4 import list as r4_list
from mappers.r4 import location as r4_location
from mappers.r4 import medication as r4_medication
from mappers.r4 import medication_administration as r4_medication_administration
from mappers.r4 import medication_dispense as r4_medication_dispense
from mappers.r4 import medication_resource as r4_medication_resource
from mappers.r4 import medication_statement as r4_medication_statement
from mappers.r4 import observation as r4_observation
from mappers.r4 import organization as r4_organization
from mappers.r4 import patient as r4_patient
from mappers.r4 import practitioner as r4_practitioner
from mappers.r4 import practitioner_role as r4_practitioner_role
from mappers.r4 import procedure as r4_procedure
from mappers.r4 import provenance as r4_provenance
from mappers.r4 import related_person as r4_related_person
from mappers.r4 import service_request as r4_service_request
from mappers.r5 import allergy as r5_allergy
from mappers.r5 import appointment as r5_appointment
from mappers.r5 import bundle as r5_bundle
from mappers.r5 import care_plan as r5_care_plan
from mappers.r5 import care_team as r5_care_team
from mappers.r5 import condition as r5_condition
from mappers.r5 import consent as r5_consent
from mappers.r5 import coverage as r5_coverage
from mappers.r5 import diagnostic_report as r5_diagnostic_report
from mappers.r5 import document_reference as r5_document_reference
from mappers.r5 import encounter as r5_encounter
from mappers.r5 import episode_of_care as r5_episode_of_care
from mappers.r5 import family_member_history as r5_family_member_history
from mappers.r5 import goal as r5_goal
from mappers.r5 import immunization as r5_immunization
from mappers.r5 import list as r5_list
from mappers.r5 import location as r5_location
from mappers.r5 import medication as r5_medication
from mappers.r5 import medication_administration as r5_medication_administration
from mappers.r5 import medication_dispense as r5_medication_dispense
from mappers.r5 import medication_resource as r5_medication_resource
from mappers.r5 import medication_statement as r5_medication_statement
from mappers.r5 import observation as r5_observation
from mappers.r5 import organization as r5_organization
from mappers.r5 import patient as r5_patient
from mappers.r5 import practitioner as r5_practitioner
from mappers.r5 import practitioner_role as r5_practitioner_role
from mappers.r5 import procedure as r5_procedure
from mappers.r5 import provenance as r5_provenance
from mappers.r5 import related_person as r5_related_person
from mappers.r5 import service_request as r5_service_request

# ---------------------------------------------------------------------------
# Version dispatch tables, indexed by FHIR version string ("R4" or "R5").
# ---------------------------------------------------------------------------
PATIENT_MAPPER = {"R4": r4_patient.map_patient, "R5": r5_patient.map_patient}
PRAC_MAPPER = {"R4": r4_practitioner.map_practitioner, "R5": r5_practitioner.map_practitioner}
ORG_MAPPER = {"R4": r4_organization.map_organization, "R5": r5_organization.map_organization}
LOC_MAPPER = {"R4": r4_location.map_location, "R5": r5_location.map_location}
PR_MAPPER = {"R4": r4_practitioner_role.map_practitioner_role, "R5": r5_practitioner_role.map_practitioner_role}
RP_MAPPER = {"R4": r4_related_person.map_related_person, "R5": r5_related_person.map_related_person}
COND_MAPPER = {"R4": r4_condition.map_condition, "R5": r5_condition.map_condition}
ALLERGY_MAPPER = {"R4": r4_allergy.map_allergy, "R5": r5_allergy.map_allergy}
ENC_MAPPER = {"R4": r4_encounter.map_encounter, "R5": r5_encounter.map_encounter}
OBS_MAPPER = {"R4": r4_observation.map_observation, "R5": r5_observation.map_observation}
MED_MAPPER = {"R4": r4_medication.map_medication, "R5": r5_medication.map_medication}
IMM_MAPPER = {"R4": r4_immunization.map_immunization, "R5": r5_immunization.map_immunization}
DR_MAPPER = {"R4": r4_diagnostic_report.map_diagnostic_report, "R5": r5_diagnostic_report.map_diagnostic_report}
DOC_REF_MAPPER = {"R4": r4_document_reference.map_document_reference, "R5": r5_document_reference.map_document_reference}
MED_DISP_MAPPER = {"R4": r4_medication_dispense.map_medication_dispense, "R5": r5_medication_dispense.map_medication_dispense}
MEDICATION_MAPPER = {"R4": r4_medication_resource.map_medication_resource, "R5": r5_medication_resource.map_medication_resource}
MED_STMT_MAPPER = {"R4": r4_medication_statement.map_medication_statement, "R5": r5_medication_statement.map_medication_statement}
MED_ADMIN_MAPPER = {"R4": r4_medication_administration.map_medication_administration, "R5": r5_medication_administration.map_medication_administration}
PROC_MAPPER = {"R4": r4_procedure.map_procedure, "R5": r5_procedure.map_procedure}
SR_MAPPER = {"R4": r4_service_request.map_service_request, "R5": r5_service_request.map_service_request}
COV_MAPPER = {"R4": r4_coverage.map_coverage, "R5": r5_coverage.map_coverage}
FMH_MAPPER = {"R4": r4_family_member_history.map_family_member_history, "R5": r5_family_member_history.map_family_member_history}
CONSENT_MAPPER = {"R4": r4_consent.map_consent, "R5": r5_consent.map_consent}
CARE_TEAM_MAPPER = {"R4": r4_care_team.map_care_team, "R5": r5_care_team.map_care_team}
CARE_PLAN_MAPPER = {"R4": r4_care_plan.map_care_plan, "R5": r5_care_plan.map_care_plan}
GOAL_MAPPER = {"R4": r4_goal.map_goal, "R5": r5_goal.map_goal}
LIST_MAPPER = {"R4": r4_list.map_list, "R5": r5_list.map_list}
PROV_MAPPER = {"R4": r4_provenance.map_provenance, "R5": r5_provenance.map_provenance}
APPT_MAPPER = {"R4": r4_appointment.map_appointment, "R5": r5_appointment.map_appointment}
EOC_MAPPER = {"R4": r4_episode_of_care.map_episode_of_care, "R5": r5_episode_of_care.map_episode_of_care}
BUNDLE_BUILDER = {"R4": r4_bundle.build_bundle, "R5": r5_bundle.build_bundle}

# Resource emission order: infrastructure first, then people, then clinical
# data, so that references always point at resources that appear earlier.
# Each tuple is (dispatch table, cohort key).
_ORDER: list[tuple[dict, str]] = [
    (ORG_MAPPER, "organizations"),
    (LOC_MAPPER, "locations"),
    (PRAC_MAPPER, "practitioners"),
    (PR_MAPPER, "practitioner_roles"),
    (PATIENT_MAPPER, "patients"),
    (COV_MAPPER, "coverages"),
    (COND_MAPPER, "conditions"),
    (ALLERGY_MAPPER, "allergies"),
    (IMM_MAPPER, "immunizations"),
    (RP_MAPPER, "related_persons"),
    (FMH_MAPPER, "family_member_histories"),
    (CONSENT_MAPPER, "consents"),
    (CARE_TEAM_MAPPER, "care_teams"),
    (CARE_PLAN_MAPPER, "care_plans"),
    (GOAL_MAPPER, "goals"),
    (ENC_MAPPER, "encounters"),
    (APPT_MAPPER, "appointments"),
    (EOC_MAPPER, "episodes_of_care"),
    (OBS_MAPPER, "observations"),
    (DR_MAPPER, "diagnostic_reports"),
    (DOC_REF_MAPPER, "document_references"),
    (MEDICATION_MAPPER, "medication_catalog"),
    (MED_MAPPER, "medications"),
    (MED_DISP_MAPPER, "medication_dispenses"),
    (MED_STMT_MAPPER, "medication_statements"),
    (MED_ADMIN_MAPPER, "medication_administrations"),
    (PROC_MAPPER, "procedures"),
    (SR_MAPPER, "service_requests"),
    (LIST_MAPPER, "lists"),
    (PROV_MAPPER, "provenances"),
]

# Cohort keys that older generator versions may omit are read with .get([]).
_REQUIRED_KEYS = {"organizations", "practitioners", "patients", "conditions", "allergies",
                  "related_persons", "encounters", "observations"}


def map_cohort(raw: dict, version: str, *, us_core: bool = False) -> list[dict]:
    """Map every raw resource in a cohort to FHIR dicts, in reference-safe order."""
    uc = {"us_core": us_core}
    resources: list[dict] = []
    for table, key in _ORDER:
        items = raw[key] if key in _REQUIRED_KEYS else raw.get(key, [])
        resources += [table[version](item, **uc) for item in items]
    return resources


def build_bundle_from_cohort(
    raw: dict,
    version: str,
    *,
    bundle_type: str = "collection",
    us_core: bool = False,
) -> dict:
    """Map a cohort and wrap the resources in a FHIR Bundle."""
    resources = map_cohort(raw, version, us_core=us_core)
    return BUNDLE_BUILDER[version](resources, bundle_type=bundle_type)


def iter_ndjson(raw: dict, version: str, *, us_core: bool = False) -> Iterator[str]:
    """Yield one compact JSON line per mapped resource (NDJSON)."""
    uc = {"us_core": us_core}
    for table, key in _ORDER:
        items = raw[key] if key in _REQUIRED_KEYS else raw.get(key, [])
        for item in items:
            yield json.dumps(table[version](item, **uc), separators=(",", ":")) + "\n"

"""Cohort orchestrator — dependency-ordered generation of a full relational dataset.

Generation order:
  Organization → Location (per org) → Practitioner → PractitionerRole →
  Patient →
    Condition → (obs baseline update) → Allergy → Immunization → Coverage →
    RelatedPerson → FamilyMemberHistory → Consent →
    CareTeam → CarePlan → Goal →
      [per encounter]:
        Encounter (with location) → ServiceRequest → Observation →
        DiagnosticReport → Procedure →
    MedicationRequest → List → Provenance

Temporal consistency guarantee: every encounter is scheduled after the patient's
earliest condition was recorded, so no visit can precede its diagnosis.

Phase 1 additions:
- Comorbidity graph replaces random 40% in condition_gen.
- update_obs_baseline_for_conditions called after conditions are resolved so
  the patient's personal BP/HR/O2 midpoints reflect their active diagnoses.
- ServiceRequests are generated before Observations so obs can carry basedOn refs.

Phase 2 additions:
- Location: per organization; linked to encounters.
- PractitionerRole: per practitioner; links practitioner to organization.
- CareTeam, CarePlan, Goal: per patient; linked to conditions.
- List: per patient; aggregates conditions, medications, and allergies.
- FamilyMemberHistory: per patient; hereditary conditions.
- Consent: per patient; HIPAA + optional research consent.
- Provenance: per patient; audit trail covering conditions, encounters, meds.
"""
import random
from datetime import date, datetime

from generators._rng import seed_all
from generators.allergy_gen import generate_allergies_for_patient
from generators.care_plan_gen import generate_care_plan
from generators.care_team_gen import generate_care_team
from generators.condition_gen import generate_conditions_for_patient
from generators.consent_gen import generate_consents_for_patient
from generators.coverage_gen import generate_coverage_for_patient
from generators.diagnostic_report_gen import generate_diagnostic_reports_for_encounter
from generators.encounter_gen import generate_encounter
from generators.family_member_history_gen import generate_family_member_history
from generators.goal_gen import generate_goals_for_patient
from generators.immunization_gen import generate_immunizations_for_patient
from generators.list_gen import generate_lists_for_patient
from generators.location_gen import generate_locations_for_organization
from generators.medication_gen import generate_medications_for_patient
from generators.observation_gen import (
    generate_observations_for_encounter,
    update_obs_baseline_for_conditions,
)
from generators.organization_gen import generate_organization
from generators.patient_gen import generate_patient
from generators.practitioner_gen import generate_practitioner
from generators.practitioner_role_gen import generate_practitioner_role
from generators.procedure_gen import generate_procedures_for_encounter
from generators.provenance_gen import generate_provenance
from generators.related_person_gen import generate_related_persons
from generators.service_request_gen import (
    build_sr_basedOn_map,
    generate_service_requests_for_encounter,
)

_MAX_ENCOUNTERS_PER_PATIENT = 5


def generate_cohort(
    count: int = 10,
    age_min: int = 0,
    age_max: int = 100,
    condition_filter: str | None = None,
    seed: int | None = None,
    num_practitioners: int = 3,
    num_organizations: int = 1,
) -> dict:
    """Returns a dict of raw lists keyed by resource type, ready for mapping.

    Raises ValueError if condition_filter matches no known condition.
    """
    if seed is not None:
        seed_all(seed)

    # Step 1 — infrastructure
    organizations = [generate_organization() for _ in range(num_organizations)]
    org_ids = [o["id"] for o in organizations]

    # Locations — 2 per organization, sharing the org's address
    locations: list[dict] = []
    location_ids_by_org: dict[str, list[str]] = {}
    for org in organizations:
        org_locs = generate_locations_for_organization(org, count=2)
        locations.extend(org_locs)
        location_ids_by_org[org["id"]] = [loc["id"] for loc in org_locs]

    practitioners = [
        generate_practitioner(organization_id=random.choice(org_ids))
        for _ in range(num_practitioners)
    ]
    prac_ids = [p["id"] for p in practitioners]

    # PractitionerRoles — one per practitioner linked to their organization
    practitioner_roles = [
        generate_practitioner_role(prac, prac["organization_id"])
        for prac in practitioners
    ]

    patients: list[dict] = []
    conditions: list[dict] = []
    allergies: list[dict] = []
    immunizations: list[dict] = []
    related_persons: list[dict] = []
    family_member_histories: list[dict] = []
    consents: list[dict] = []
    care_teams: list[dict] = []
    care_plans: list[dict] = []
    goals: list[dict] = []
    encounters: list[dict] = []
    observations: list[dict] = []
    diagnostic_reports: list[dict] = []
    medications: list[dict] = []
    procedures: list[dict] = []
    service_requests: list[dict] = []
    coverages: list[dict] = []
    lists: list[dict] = []
    provenances: list[dict] = []

    for _ in range(count):
        patient = generate_patient(age_min=age_min, age_max=age_max)
        patients.append(patient)
        patient_age = patient["age"]

        prac_id = random.choice(prac_ids)
        org_id = random.choice(org_ids)

        # Conditions — primary filter + comorbidity graph (raises on bad filter)
        pt_conditions = generate_conditions_for_patient(
            patient_id=patient["id"],
            practitioner_id=prac_id,
            patient_age=patient_age,
            condition_filter=condition_filter,
        )
        conditions.extend(pt_conditions)

        # Update the patient's obs_baseline so BP/HR/O2 reflect active conditions.
        obs_baseline = patient.get("obs_baseline")
        if obs_baseline is not None:
            update_obs_baseline_for_conditions(obs_baseline, pt_conditions)

        # Temporal bound: encounters must happen after the earliest condition was recorded
        earliest_recorded_days_ago = _days_ago_from(
            min(c["recorded_date"] for c in pt_conditions)
        )
        enc_window = min(730, max(30, earliest_recorded_days_ago - 1))

        # Allergies — probabilistic
        pt_allergies = generate_allergies_for_patient(patient["id"], prac_id)
        allergies.extend(pt_allergies)

        # Immunizations — age-appropriate coverage
        immunizations.extend(
            generate_immunizations_for_patient(patient["id"], prac_id, patient_age)
        )

        # Insurance coverage — one per patient
        coverages.append(generate_coverage_for_patient(patient["id"], patient_age))

        # Family / emergency contacts — age + marital status aware
        related_persons.extend(generate_related_persons(patient))

        # FamilyMemberHistory — 1–3 relatives with hereditary conditions
        family_member_histories.extend(generate_family_member_history(patient["id"]))

        # Consent — HIPAA + optional research
        consents.extend(generate_consents_for_patient(patient["id"], org_id))

        # CareTeam — practitioners managing this patient's conditions
        care_team = generate_care_team(patient["id"], [prac_id], pt_conditions)
        care_teams.append(care_team)

        # CarePlan — links patient, care team, and conditions
        care_plan = generate_care_plan(patient["id"], care_team["id"], pt_conditions)
        care_plans.append(care_plan)

        # Goals — one per condition linked to the care plan
        pt_goals = generate_goals_for_patient(patient["id"], care_plan["id"], pt_conditions)
        goals.extend(pt_goals)

        # Encounters spread evenly across the post-diagnosis window
        num_enc = min(max(1, len(pt_conditions) * 2), _MAX_ENCOUNTERS_PER_PATIENT)
        window_per_enc = enc_window // num_enc

        # Pick location IDs for this org
        org_loc_ids = location_ids_by_org.get(org_id, [])

        first_enc_written = False
        pt_encounters: list[dict] = []
        for enc_idx in range(num_enc):
            loc_id = random.choice(org_loc_ids) if org_loc_ids else None
            enc = generate_encounter(
                patient_id=patient["id"],
                practitioner_id=prac_id,
                organization_id=org_id,
                patient_age=patient_age,
                days_ago_min=max(1, enc_idx * window_per_enc),
                days_ago_max=(enc_idx + 1) * window_per_enc,
                conditions=pt_conditions,
                location_id=loc_id,
            )
            encounters.append(enc)
            pt_encounters.append(enc)

            # Link all conditions to the first encounter (diagnosis visit)
            if not first_enc_written:
                for cond in pt_conditions:
                    cond["encounter_id"] = enc["id"]
                first_enc_written = True

            # ServiceRequests first — observation generator needs the SR ids for basedOn
            enc_srs = generate_service_requests_for_encounter(
                patient_id=patient["id"],
                encounter_id=enc["id"],
                practitioner_id=prac_id,
                conditions=pt_conditions,
                authored_on=enc["start_datetime"][:10],
            )
            service_requests.extend(enc_srs)

            sr_basedOn = build_sr_basedOn_map(enc_srs)

            enc_obs = generate_observations_for_encounter(
                patient_id=patient["id"],
                encounter_id=enc["id"],
                practitioner_id=prac_id,
                effective_datetime=enc["start_datetime"],
                conditions=pt_conditions,
                obs_baseline=obs_baseline,
                height_cm=patient.get("height_cm"),
                sr_basedOn=sr_basedOn,
            )
            observations.extend(enc_obs)

            diagnostic_reports.extend(
                generate_diagnostic_reports_for_encounter(
                    patient_id=patient["id"],
                    encounter_id=enc["id"],
                    practitioner_id=prac_id,
                    effective_datetime=enc["start_datetime"],
                    observations=enc_obs,
                )
            )

            procedures.extend(
                generate_procedures_for_encounter(
                    patient_id=patient["id"],
                    encounter_id=enc["id"],
                    practitioner_id=prac_id,
                    performed_datetime=enc["start_datetime"],
                    conditions=pt_conditions,
                )
            )

        # MedicationRequests — one set per patient (linked to first encounter)
        first_enc_id = pt_encounters[0]["id"] if pt_encounters else ""
        pt_meds = generate_medications_for_patient(
            patient_id=patient["id"],
            practitioner_id=prac_id,
            encounter_id=first_enc_id,
            conditions=pt_conditions,
        )
        medications.extend(pt_meds)

        # Lists — aggregate conditions, medications, allergies
        lists.extend(
            generate_lists_for_patient(
                patient_id=patient["id"],
                conditions=pt_conditions,
                medications=pt_meds,
                allergies=pt_allergies,
            )
        )

        # Provenance — audit trail for this patient's clinical data
        prov_targets = (
            [patient["id"]]
            + [c["id"] for c in pt_conditions]
            + [e["id"] for e in pt_encounters]
            + [m["id"] for m in pt_meds]
        )
        recorded = pt_encounters[0]["start_datetime"] if pt_encounters else _utcnow()
        provenances.append(
            generate_provenance(
                target_ids=prov_targets,
                practitioner_id=prac_id,
                organization_id=org_id,
                recorded=recorded,
            )
        )

    return {
        "organizations": organizations,
        "locations": locations,
        "practitioners": practitioners,
        "practitioner_roles": practitioner_roles,
        "patients": patients,
        "coverages": coverages,
        "conditions": conditions,
        "allergies": allergies,
        "immunizations": immunizations,
        "related_persons": related_persons,
        "family_member_histories": family_member_histories,
        "consents": consents,
        "care_teams": care_teams,
        "care_plans": care_plans,
        "goals": goals,
        "encounters": encounters,
        "observations": observations,
        "diagnostic_reports": diagnostic_reports,
        "medications": medications,
        "procedures": procedures,
        "service_requests": service_requests,
        "lists": lists,
        "provenances": provenances,
    }


def _days_ago_from(date_str: str) -> int:
    """Convert a YYYY-MM-DD string to number of days before today."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except ValueError:
        return 365


def _utcnow() -> str:
    from datetime import UTC
    from datetime import datetime as dt
    return dt.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

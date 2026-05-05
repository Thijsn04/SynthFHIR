"""Cohort orchestrator — dependency-ordered generation of a full relational dataset.

Generation order:
  Organization → Practitioner → Patient →
    Condition → (obs baseline update) → Allergy → Immunization → RelatedPerson →
      [per encounter]:
        Encounter → ServiceRequest → Observation → DiagnosticReport → Procedure →
      MedicationRequest

Temporal consistency guarantee: every encounter is scheduled after the patient's
earliest condition was recorded, so no visit can precede its diagnosis.

Phase 1 additions:
- Comorbidity graph replaces random 40% in condition_gen.
- update_obs_baseline_for_conditions called after conditions are resolved so
  the patient's personal BP/HR/O2 midpoints reflect their active diagnoses.
- ServiceRequests are generated before Observations so obs can carry basedOn refs.
"""
import random
from datetime import date, datetime

from generators._rng import seed_all
from generators.allergy_gen import generate_allergies_for_patient
from generators.condition_gen import generate_conditions_for_patient
from generators.coverage_gen import generate_coverage_for_patient
from generators.diagnostic_report_gen import generate_diagnostic_reports_for_encounter
from generators.encounter_gen import generate_encounter
from generators.immunization_gen import generate_immunizations_for_patient
from generators.medication_gen import generate_medications_for_patient
from generators.observation_gen import (
    generate_observations_for_encounter,
    update_obs_baseline_for_conditions,
)
from generators.organization_gen import generate_organization
from generators.patient_gen import generate_patient
from generators.practitioner_gen import generate_practitioner
from generators.procedure_gen import generate_procedures_for_encounter
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

    practitioners = [
        generate_practitioner(organization_id=random.choice(org_ids))
        for _ in range(num_practitioners)
    ]
    prac_ids = [p["id"] for p in practitioners]

    patients: list[dict] = []
    conditions: list[dict] = []
    allergies: list[dict] = []
    immunizations: list[dict] = []
    related_persons: list[dict] = []
    encounters: list[dict] = []
    observations: list[dict] = []
    diagnostic_reports: list[dict] = []
    medications: list[dict] = []
    procedures: list[dict] = []
    service_requests: list[dict] = []
    coverages: list[dict] = []

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
        # This must happen before any encounters are generated.
        obs_baseline = patient.get("obs_baseline")
        if obs_baseline is not None:
            update_obs_baseline_for_conditions(obs_baseline, pt_conditions)

        # Temporal bound: encounters must happen after the earliest condition was recorded
        earliest_recorded_days_ago = _days_ago_from(
            min(c["recorded_date"] for c in pt_conditions)
        )
        enc_window = min(730, max(30, earliest_recorded_days_ago - 1))

        # Allergies — probabilistic
        allergies.extend(generate_allergies_for_patient(patient["id"], prac_id))

        # Immunizations — age-appropriate coverage
        immunizations.extend(
            generate_immunizations_for_patient(patient["id"], prac_id, patient_age)
        )

        # Insurance coverage — one per patient
        coverages.append(generate_coverage_for_patient(patient["id"], patient_age))

        # Family / emergency contacts — age + marital status aware
        related_persons.extend(generate_related_persons(patient))

        # Encounters spread evenly across the post-diagnosis window
        num_enc = min(max(1, len(pt_conditions) * 2), _MAX_ENCOUNTERS_PER_PATIENT)
        window_per_enc = enc_window // num_enc

        first_enc_written = False
        for enc_idx in range(num_enc):
            enc = generate_encounter(
                patient_id=patient["id"],
                practitioner_id=prac_id,
                organization_id=org_id,
                patient_age=patient_age,
                days_ago_min=max(1, enc_idx * window_per_enc),
                days_ago_max=(enc_idx + 1) * window_per_enc,
                conditions=pt_conditions,
            )
            encounters.append(enc)

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

            # Build obs_key → SR.id map for basedOn references
            sr_basedOn = build_sr_basedOn_map(enc_srs)

            # Observations — longitudinally consistent vitals + condition labs
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

            # DiagnosticReport — groups lab observations for this encounter
            diagnostic_reports.extend(
                generate_diagnostic_reports_for_encounter(
                    patient_id=patient["id"],
                    encounter_id=enc["id"],
                    practitioner_id=prac_id,
                    effective_datetime=enc["start_datetime"],
                    observations=enc_obs,
                )
            )

            # Procedures — general exam + condition-specific procedures
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
        first_enc_id = encounters[-num_enc]["id"] if encounters else ""
        medications.extend(
            generate_medications_for_patient(
                patient_id=patient["id"],
                practitioner_id=prac_id,
                encounter_id=first_enc_id,
                conditions=pt_conditions,
            )
        )

    return {
        "organizations": organizations,
        "practitioners": practitioners,
        "patients": patients,
        "coverages": coverages,
        "conditions": conditions,
        "allergies": allergies,
        "immunizations": immunizations,
        "related_persons": related_persons,
        "encounters": encounters,
        "observations": observations,
        "diagnostic_reports": diagnostic_reports,
        "medications": medications,
        "procedures": procedures,
        "service_requests": service_requests,
    }


def _days_ago_from(date_str: str) -> int:
    """Convert a YYYY-MM-DD string to number of days before today."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except ValueError:
        return 365

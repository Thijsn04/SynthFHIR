"""Cohort orchestrator — dependency-ordered generation of a full relational dataset.

Generation order:
  Organization → Practitioner → Patient →
    Condition → Allergy → RelatedPerson →
      Encounter → Observation
"""
import random

from faker import Faker

from generators.allergy_gen import generate_allergies_for_patient
from generators.condition_gen import generate_conditions_for_patient
from generators.encounter_gen import generate_encounter
from generators.observation_gen import generate_observations_for_encounter
from generators.organization_gen import generate_organization
from generators.patient_gen import generate_patient
from generators.practitioner_gen import generate_practitioner
from generators.related_person_gen import generate_related_persons

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
    """Returns a dict of raw lists keyed by resource type, ready for mapping."""
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    # Step 1 — infrastructure
    organizations = [generate_organization() for _ in range(num_organizations)]
    org_ids = [o["id"] for o in organizations]

    practitioners = [
        generate_practitioner(organization_id=random.choice(org_ids))
        for _ in range(num_practitioners)
    ]
    prac_ids = [p["id"] for p in practitioners]

    patients, conditions, allergies, related_persons, encounters, observations = (
        [], [], [], [], [], []
    )

    for _ in range(count):
        patient = generate_patient(age_min=age_min, age_max=age_max)
        patients.append(patient)

        prac_id = random.choice(prac_ids)
        org_id = random.choice(org_ids)

        # Conditions — primary filter + possible comorbidity
        pt_conditions = generate_conditions_for_patient(
            patient_id=patient["id"],
            practitioner_id=prac_id,
            condition_filter=condition_filter,
        )
        conditions.extend(pt_conditions)

        # Allergies — probabilistic
        allergies.extend(generate_allergies_for_patient(patient["id"], prac_id))

        # Family / emergency contacts — age + marital status aware
        related_persons.extend(generate_related_persons(patient))

        # Encounters — more conditions → more visits, capped at _MAX_ENCOUNTERS_PER_PATIENT
        num_enc = min(max(1, len(pt_conditions) * 2), _MAX_ENCOUNTERS_PER_PATIENT)
        window = 730 // num_enc  # spread visits evenly across 2-year window

        for enc_idx in range(num_enc):
            enc = generate_encounter(
                patient_id=patient["id"],
                practitioner_id=prac_id,
                organization_id=org_id,
                days_ago_min=max(1, enc_idx * window),
                days_ago_max=(enc_idx + 1) * window,
            )
            encounters.append(enc)

            # Observations — condition-aware vitals + labs
            observations.extend(
                generate_observations_for_encounter(
                    patient_id=patient["id"],
                    encounter_id=enc["id"],
                    practitioner_id=prac_id,
                    effective_datetime=enc["start_datetime"],
                    conditions=pt_conditions,
                )
            )

    return {
        "organizations": organizations,
        "practitioners": practitioners,
        "patients": patients,
        "conditions": conditions,
        "allergies": allergies,
        "related_persons": related_persons,
        "encounters": encounters,
        "observations": observations,
    }

"""Unit tests for FHIR R4 and R5 mapper modules.

Run with:  pytest tests/test_mappers.py -v
"""
import pytest

from generators._rng import seed_all
from generators.cohort_gen import generate_cohort


def _raw(seed: int = 42, count: int = 2) -> dict:
    return generate_cohort(count=count, seed=seed)


# ---------------------------------------------------------------------------
# R4 mappers
# ---------------------------------------------------------------------------

class TestR4PatientMapper:
    def setup_method(self):
        seed_all(0)
        self.raw = _raw()
        from mappers.r4.patient import map_patient
        self.resource = map_patient(self.raw["patients"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Patient"

    def test_id_matches(self):
        assert self.resource["id"] == self.raw["patients"][0]["id"]

    def test_profile_base(self):
        assert "hl7.org/fhir/StructureDefinition/Patient" in self.resource["meta"]["profile"][0]

    def test_us_core_profile(self):
        from mappers.r4.patient import map_patient
        r = map_patient(self.raw["patients"][0], us_core=True)
        assert "us-core-patient" in r["meta"]["profile"][0]
        ext_urls = [e["url"] for e in r.get("extension", [])]
        assert any("us-core-race" in u for u in ext_urls)
        assert any("us-core-ethnicity" in u for u in ext_urls)
        assert any("us-core-birthsex" in u for u in ext_urls)

    def test_references_use_urn_uuid(self):
        # Patients have no outbound references to check in this mapper
        pass

    def test_telecom_e164(self):
        for tc in self.resource["telecom"]:
            if tc.get("system") == "phone":
                assert tc["value"].startswith("+1"), f"Phone not E.164: {tc['value']}"


class TestR4ConditionMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.condition import map_condition
        self.resource = map_condition(raw["conditions"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Condition"

    def test_subject_reference_urn(self):
        assert self.resource["subject"]["reference"].startswith("urn:uuid:")

    def test_dual_coding(self):
        codings = self.resource["code"]["coding"]
        systems = {c["system"] for c in codings}
        assert "http://snomed.info/sct" in systems
        assert "http://hl7.org/fhir/sid/icd-10-cm" in systems


class TestR4ObservationMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.observation import map_observation
        # Use a non-BP-panel, non-survey observation so valueQuantity is present
        non_panel = next(
            o for o in raw["observations"]
            if o["loinc_code"] != "85354-9" and o.get("category_code") != "survey"
        )
        self.resource = map_observation(non_panel)
        # Also map the BP panel for component tests
        bp_panel_raw = next(o for o in raw["observations"] if o["loinc_code"] == "85354-9")
        self.bp_panel = map_observation(bp_panel_raw)

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Observation"

    def test_value_quantity_present(self):
        assert "valueQuantity" in self.resource
        assert "value" in self.resource["valueQuantity"]

    def test_bp_panel_has_component(self):
        assert "component" in self.bp_panel
        assert len(self.bp_panel["component"]) == 2
        codes = {c["code"]["coding"][0]["code"] for c in self.bp_panel["component"]}
        assert "8480-6" in codes  # systolic
        assert "8462-4" in codes  # diastolic

    def test_reference_range_present(self):
        assert "referenceRange" in self.resource
        rr = self.resource["referenceRange"][0]
        assert "low" in rr and "high" in rr

    def test_loinc_coding(self):
        codings = self.resource["code"]["coding"]
        assert any(c["system"] == "http://loinc.org" for c in codings)

    def test_references_urn_uuid(self):
        assert self.resource["subject"]["reference"].startswith("urn:uuid:")
        assert self.resource["encounter"]["reference"].startswith("urn:uuid:")


class TestR4MedicationMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=5)
        from mappers.r4.medication import map_medication
        meds = raw.get("medications", [])
        self.resource = map_medication(meds[0]) if meds else None

    def test_resource_type(self):
        if self.resource is None:
            pytest.skip("No medications generated")
        assert self.resource["resourceType"] == "MedicationRequest"

    def test_rxnorm_coding(self):
        if self.resource is None:
            pytest.skip("No medications generated")
        codings = self.resource["medicationCodeableConcept"]["coding"]
        assert any("rxnorm" in c["system"] for c in codings)

    def test_dosage_present(self):
        if self.resource is None:
            pytest.skip("No medications generated")
        assert "dosageInstruction" in self.resource
        assert len(self.resource["dosageInstruction"]) >= 1


class TestR4ImmunizationMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=5)
        from mappers.r4.immunization import map_immunization
        imms = raw.get("immunizations", [])
        self.resource = map_immunization(imms[0]) if imms else None

    def test_resource_type(self):
        if self.resource is None:
            pytest.skip("No immunizations generated")
        assert self.resource["resourceType"] == "Immunization"

    def test_cvx_coding(self):
        if self.resource is None:
            pytest.skip("No immunizations generated")
        assert self.resource["vaccineCode"]["coding"][0]["system"] == "http://hl7.org/fhir/sid/cvx"


class TestR4DiagnosticReportMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=5)
        from mappers.r4.diagnostic_report import map_diagnostic_report
        reports = raw.get("diagnostic_reports", [])
        self.resource = map_diagnostic_report(reports[0]) if reports else None

    def test_resource_type(self):
        if self.resource is None:
            pytest.skip("No diagnostic reports generated")
        assert self.resource["resourceType"] == "DiagnosticReport"

    def test_result_references_urn(self):
        if self.resource is None:
            pytest.skip("No diagnostic reports generated")
        for r in self.resource["result"]:
            assert r["reference"].startswith("urn:uuid:")


class TestR4BundleBuilder:
    def setup_method(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.bundle import build_bundle
        from mappers.r4.patient import map_patient
        self.resources = [map_patient(p) for p in raw["patients"]]
        self.bundle = build_bundle(self.resources)

    def test_bundle_type(self):
        assert self.bundle["resourceType"] == "Bundle"
        assert self.bundle["type"] == "collection"

    def test_total_matches_entries(self):
        assert self.bundle["total"] == len(self.bundle["entry"])

    def test_fulluris_urn_uuid(self):
        for entry in self.bundle["entry"]:
            assert entry["fullUrl"].startswith("urn:uuid:")

    def test_transaction_bundle_has_request(self):
        from mappers.r4.bundle import build_bundle
        b = build_bundle(self.resources, bundle_type="transaction")
        for entry in b["entry"]:
            assert "request" in entry
            assert entry["request"]["method"] == "POST"


# ---------------------------------------------------------------------------
# R5 mappers — spot checks on R5-specific structural differences
# ---------------------------------------------------------------------------

class TestR5EncounterMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw()
        from mappers.r5.encounter import map_encounter
        self.resource = map_encounter(raw["encounters"][0])

    def test_class_is_array(self):
        assert isinstance(self.resource["class"], list)

    def test_actual_period(self):
        assert "actualPeriod" in self.resource

    def test_completed_status(self):
        # "finished" (R4) maps to "completed" (R5)
        if self.resource["status"] in ("completed", "in-progress", "cancelled"):
            pass  # valid R5 status
        else:
            pytest.fail(f"Unexpected R5 encounter status: {self.resource['status']}")


class TestR5PatientGenderIdentity:
    def test_gender_identity_extension_present(self):
        seed_all(0)
        raw = _raw()
        from mappers.r5.patient import map_patient
        r = map_patient(raw["patients"][0])
        urls = [e["url"] for e in r.get("extension", [])]
        assert any("genderIdentity" in u for u in urls)


class TestR5ConditionParticipant:
    def test_participant_instead_of_recorder(self):
        seed_all(0)
        raw = _raw()
        from mappers.r5.condition import map_condition
        r = map_condition(raw["conditions"][0])
        assert "participant" in r
        assert "recorder" not in r


# ---------------------------------------------------------------------------
# Phase 2 R4 mapper tests
# ---------------------------------------------------------------------------

class TestR4LocationMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=2)
        from mappers.r4.location import map_location
        self.resource = map_location(raw["locations"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Location"

    def test_managing_org_urn(self):
        assert self.resource["managingOrganization"]["reference"].startswith("urn:uuid:")

    def test_type_present(self):
        assert "type" in self.resource
        assert self.resource["type"][0]["coding"][0]["system"]


class TestR4PractitionerRoleMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=2)
        from mappers.r4.practitioner_role import map_practitioner_role
        self.resource = map_practitioner_role(raw["practitioner_roles"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "PractitionerRole"

    def test_references_urn(self):
        assert self.resource["practitioner"]["reference"].startswith("urn:uuid:")
        assert self.resource["organization"]["reference"].startswith("urn:uuid:")

    def test_specialty_snomed(self):
        codings = self.resource["specialty"][0]["coding"]
        assert any(c["system"] == "http://snomed.info/sct" for c in codings)


class TestR4CareTeamMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.care_team import map_care_team
        self.resource = map_care_team(raw["care_teams"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "CareTeam"

    def test_subject_urn(self):
        assert self.resource["subject"]["reference"].startswith("urn:uuid:")

    def test_participant_members_urn(self):
        for p in self.resource["participant"]:
            assert p["member"]["reference"].startswith("urn:uuid:")


class TestR4CarePlanMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.care_plan import map_care_plan
        self.resource = map_care_plan(raw["care_plans"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "CarePlan"

    def test_subject_urn(self):
        assert self.resource["subject"]["reference"].startswith("urn:uuid:")

    def test_care_team_urn(self):
        assert self.resource["careTeam"][0]["reference"].startswith("urn:uuid:")

    def test_period_present(self):
        assert "period" in self.resource
        assert "start" in self.resource["period"]
        assert "end" in self.resource["period"]


class TestR4GoalMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.goal import map_goal
        goals = raw.get("goals", [])
        self.resource = map_goal(goals[0]) if goals else None

    def test_resource_type(self):
        if self.resource is None:
            pytest.skip("No goals generated")
        assert self.resource["resourceType"] == "Goal"

    def test_subject_urn(self):
        if self.resource is None:
            pytest.skip("No goals generated")
        assert self.resource["subject"]["reference"].startswith("urn:uuid:")

    def test_lifecycle_status(self):
        if self.resource is None:
            pytest.skip("No goals generated")
        assert self.resource["lifecycleStatus"] in (
            "proposed", "active", "completed", "on-hold", "cancelled",
            "entered-in-error", "rejected",
        )


class TestR4ListMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.list import map_list
        lists = raw.get("lists", [])
        self.resource = map_list(lists[0]) if lists else None

    def test_resource_type(self):
        if self.resource is None:
            pytest.skip("No lists generated")
        assert self.resource["resourceType"] == "List"

    def test_subject_urn(self):
        if self.resource is None:
            pytest.skip("No lists generated")
        assert self.resource["subject"]["reference"].startswith("urn:uuid:")

    def test_entries_present(self):
        if self.resource is None:
            pytest.skip("No lists generated")
        assert len(self.resource["entry"]) >= 1
        for e in self.resource["entry"]:
            assert e["item"]["reference"].startswith("urn:uuid:")


class TestR4FamilyMemberHistoryMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.family_member_history import map_family_member_history
        self.resource = map_family_member_history(raw["family_member_histories"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "FamilyMemberHistory"

    def test_patient_urn(self):
        assert self.resource["patient"]["reference"].startswith("urn:uuid:")

    def test_dual_coding_in_conditions(self):
        for cond in self.resource["condition"]:
            systems = {c["system"] for c in cond["code"]["coding"]}
            assert "http://snomed.info/sct" in systems
            assert "http://hl7.org/fhir/sid/icd-10-cm" in systems


class TestR4ConsentMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.consent import map_consent
        self.resource = map_consent(raw["consents"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Consent"

    def test_patient_urn(self):
        assert self.resource["patient"]["reference"].startswith("urn:uuid:")

    def test_provision_present(self):
        assert "provision" in self.resource
        assert self.resource["provision"]["type"] in ("permit", "deny")


class TestR4ProvenanceMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=2)
        from mappers.r4.provenance import map_provenance
        self.resource = map_provenance(raw["provenances"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Provenance"

    def test_target_references(self):
        assert len(self.resource["target"]) >= 1
        for t in self.resource["target"]:
            assert t["reference"].startswith("urn:uuid:")

    def test_agent_who_urn(self):
        assert self.resource["agent"][0]["who"]["reference"].startswith("urn:uuid:")


# ---------------------------------------------------------------------------
# Phase 2 R5 mapper spot checks
# ---------------------------------------------------------------------------

class TestR5CareTeamReason:
    def test_r5_uses_reason_not_reason_reference(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r5.care_team import map_care_team
        ct = raw["care_teams"][0]
        r = map_care_team(ct)
        if ct.get("condition_ids"):
            assert "reason" in r
            assert "reasonReference" not in r


class TestR5ConsentStructure:
    def test_r5_uses_regulatory_basis_not_policy_rule(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r5.consent import map_consent
        r = map_consent(raw["consents"][0])
        assert "regulatoryBasis" in r
        assert "policyRule" not in r
        assert "manager" in r
        assert "organization" not in r


class TestR5CarePlanActivities:
    def test_r5_uses_planned_activity_detail(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r5.care_plan import map_care_plan
        cp = raw["care_plans"][0]
        r = map_care_plan(cp)
        if r.get("activity"):
            for act in r["activity"]:
                assert "plannedActivityDetail" in act
                assert "detail" not in act


# ---------------------------------------------------------------------------
# Phase 3 — US Core conformance tests
# ---------------------------------------------------------------------------

_US_CORE_BASE = "http://hl7.org/fhir/us/core/StructureDefinition"


class TestUSCoreCondition:
    def setup_method(self):
        seed_all(0)
        self.raw = _raw(count=5)

    def test_problem_list_profile(self):
        from mappers.r4.condition import map_condition
        cond = next(
            c for c in self.raw["conditions"]
            if c["category_code"] == "problem-list-item"
        )
        r = map_condition(cond, us_core=True)
        assert "us-core-condition-problems-health-concerns" in r["meta"]["profile"][0]

    def test_encounter_diagnosis_profile(self):
        from mappers.r4.condition import map_condition
        cond = next(
            (c for c in self.raw["conditions"] if c["category_code"] == "encounter-diagnosis"),
            None,
        )
        if cond is None:
            pytest.skip("No encounter-diagnosis condition generated with this seed")
        r = map_condition(cond, us_core=True)
        assert "us-core-condition-encounter-diagnosis" in r["meta"]["profile"][0]

    def test_base_profile_unchanged(self):
        from mappers.r4.condition import map_condition
        r = map_condition(self.raw["conditions"][0], us_core=False)
        assert r["meta"]["profile"][0] == "http://hl7.org/fhir/StructureDefinition/Condition"


class TestUSCoreAllergy:
    def test_us_core_profile(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.allergy import map_allergy
        r = map_allergy(raw["allergies"][0], us_core=True)
        assert f"{_US_CORE_BASE}/us-core-allergyintolerance" == r["meta"]["profile"][0]


class TestUSCoreEncounter:
    def setup_method(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.encounter import map_encounter
        self.resource = map_encounter(raw["encounters"][0], us_core=True)

    def test_us_core_profile(self):
        assert f"{_US_CORE_BASE}/us-core-encounter" == self.resource["meta"]["profile"][0]

    def test_identifier_present(self):
        assert "identifier" in self.resource
        assert len(self.resource["identifier"]) >= 1
        assert self.resource["identifier"][0]["value"]


class TestUSCoreObservation:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=5)
        from mappers.r4.observation import map_observation
        self.lab_obs = next(
            (o for o in raw["observations"] if o.get("category_code") == "laboratory"), None
        )
        self.vital_obs = next(
            (o for o in raw["observations"] if o.get("category_code") == "vital-signs"), None
        )

    def test_lab_us_core_profile(self):
        if self.lab_obs is None:
            pytest.skip("No laboratory observation generated")
        from mappers.r4.observation import map_observation
        r = map_observation(self.lab_obs, us_core=True)
        assert f"{_US_CORE_BASE}/us-core-observation-lab" == r["meta"]["profile"][0]

    def test_vitals_us_core_profile(self):
        if self.vital_obs is None:
            pytest.skip("No vital-signs observation generated")
        from mappers.r4.observation import map_observation
        r = map_observation(self.vital_obs, us_core=True)
        assert f"{_US_CORE_BASE}/us-core-vital-signs" == r["meta"]["profile"][0]


class TestUSCoreDiagnosticReport:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=5)
        from mappers.r4.diagnostic_report import map_diagnostic_report
        reports = raw.get("diagnostic_reports", [])
        self.resource = map_diagnostic_report(reports[0], us_core=True) if reports else None

    def test_us_core_profile(self):
        if self.resource is None:
            pytest.skip("No diagnostic reports generated")
        assert f"{_US_CORE_BASE}/us-core-diagnosticreport-lab" == self.resource["meta"]["profile"][0]

    def test_lab_category_present(self):
        if self.resource is None:
            pytest.skip("No diagnostic reports generated")
        all_codes = [
            coding["code"]
            for cat in self.resource["category"]
            for coding in cat["coding"]
        ]
        assert "LAB" in all_codes


class TestUSCoreMedicationRequest:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=5)
        from mappers.r4.medication import map_medication
        meds = raw.get("medications", [])
        self.resource = map_medication(meds[0], us_core=True) if meds else None

    def test_us_core_profile(self):
        if self.resource is None:
            pytest.skip("No medications generated")
        assert f"{_US_CORE_BASE}/us-core-medicationrequest" == self.resource["meta"]["profile"][0]

    def test_reported_boolean_present(self):
        if self.resource is None:
            pytest.skip("No medications generated")
        assert "reportedBoolean" in self.resource
        assert self.resource["reportedBoolean"] is False


class TestUSCorePractitionerRole:
    def setup_method(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.practitioner_role import map_practitioner_role
        self.resource = map_practitioner_role(raw["practitioner_roles"][0], us_core=True)

    def test_us_core_profile(self):
        assert f"{_US_CORE_BASE}/us-core-practitionerrole" == self.resource["meta"]["profile"][0]

    def test_nucc_specialty_added(self):
        codings = self.resource["specialty"][0]["coding"]
        systems = {c["system"] for c in codings}
        assert "http://nucc.org/provider-taxonomy" in systems


class TestUSCoreCarePlan:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r4.care_plan import map_care_plan
        self.resource = map_care_plan(raw["care_plans"][0], us_core=True)

    def test_us_core_profile(self):
        assert f"{_US_CORE_BASE}/us-core-careplan" == self.resource["meta"]["profile"][0]

    def test_category_assess_plan(self):
        cats = self.resource["category"]
        codes = [c["code"] for cat in cats for c in cat["coding"]]
        assert "assess-plan" in codes

    def test_narrative_text_present(self):
        assert "text" in self.resource
        assert self.resource["text"]["status"] == "generated"
        assert "<div" in self.resource["text"]["div"]


class TestUSCoreOrganization:
    def test_us_core_profile_and_npi(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.organization import map_organization
        r = map_organization(raw["organizations"][0], us_core=True)
        assert f"{_US_CORE_BASE}/us-core-organization" == r["meta"]["profile"][0]
        assert "identifier" in r
        assert any(
            i["system"] == "http://hl7.org/fhir/sid/us-npi"
            for i in r["identifier"]
        )


class TestUSCorePractitioner:
    def test_us_core_profile_and_npi(self):
        seed_all(0)
        raw = _raw()
        from mappers.r4.practitioner import map_practitioner
        r = map_practitioner(raw["practitioners"][0], us_core=True)
        assert f"{_US_CORE_BASE}/us-core-practitioner" == r["meta"]["profile"][0]
        assert any(
            i["system"] == "http://hl7.org/fhir/sid/us-npi"
            for i in r["identifier"]
        )


# ---------------------------------------------------------------------------
# Phase 4 mappers — Appointment and EpisodeOfCare
# ---------------------------------------------------------------------------

class TestR4AppointmentMapper:
    def setup_method(self):
        seed_all(0)
        self.raw = _raw(count=3)
        from mappers.r4.appointment import map_appointment
        self.appt = self.raw["appointments"][0]
        self.resource = map_appointment(self.appt)

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Appointment"

    def test_required_fields(self):
        assert "status" in self.resource
        assert "participant" in self.resource
        assert len(self.resource["participant"]) >= 2

    def test_status_fulfilled(self):
        assert self.resource["status"] == "fulfilled"

    def test_patient_participant(self):
        # References use urn:uuid: format — check by matching patient_id
        patient_id = self.appt["patient_id"]
        actor_refs = [p["actor"]["reference"] for p in self.resource["participant"]]
        assert any(patient_id in r for r in actor_refs)

    def test_practitioner_participant(self):
        prac_id = self.appt["practitioner_id"]
        actor_refs = [p["actor"]["reference"] for p in self.resource["participant"]]
        assert any(prac_id in r for r in actor_refs)

    def test_service_type_present(self):
        assert "serviceType" in self.resource
        assert self.resource["serviceType"][0]["coding"][0]["system"] == "http://snomed.info/sct"

    def test_start_before_end(self):
        from datetime import datetime
        start = datetime.strptime(self.resource["start"], "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime(self.resource["end"], "%Y-%m-%dT%H:%M:%SZ")
        assert start < end

    def test_us_core_param_accepted(self):
        from mappers.r4.appointment import map_appointment
        r = map_appointment(self.appt, us_core=True)
        assert r["resourceType"] == "Appointment"


class TestR5AppointmentMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r5.appointment import map_appointment
        self.resource = map_appointment(raw["appointments"][0])

    def test_resource_type(self):
        assert self.resource["resourceType"] == "Appointment"

    def test_r5_subject_field(self):
        assert "subject" in self.resource
        # References use urn:uuid: format
        assert "urn:uuid:" in self.resource["subject"]["reference"]

    def test_r5_service_type_uses_concept(self):
        svc = self.resource["serviceType"][0]
        assert "concept" in svc
        assert "coding" in svc["concept"]


class TestR4EpisodeOfCareMapper:
    def setup_method(self):
        seed_all(0)
        self.raw = _raw(count=3)
        from mappers.r4.episode_of_care import map_episode_of_care
        self.eoc = self.raw["episodes_of_care"][0]
        self.resource = map_episode_of_care(self.eoc)

    def test_resource_type(self):
        assert self.resource["resourceType"] == "EpisodeOfCare"

    def test_required_fields(self):
        assert "status" in self.resource
        assert "patient" in self.resource

    def test_patient_reference(self):
        # References use urn:uuid: format — check by ID
        assert self.eoc["patient_id"] in self.resource["patient"]["reference"]

    def test_managing_organization(self):
        assert self.eoc["organization_id"] in self.resource["managingOrganization"]["reference"]

    def test_period_present(self):
        assert "period" in self.resource
        assert "start" in self.resource["period"]

    def test_diagnosis_links_conditions(self):
        if self.eoc.get("condition_ids"):
            assert "diagnosis" in self.resource
            for diag in self.resource["diagnosis"]:
                assert "urn:uuid:" in diag["condition"]["reference"]

    def test_us_core_param_accepted(self):
        from mappers.r4.episode_of_care import map_episode_of_care
        r = map_episode_of_care(self.eoc, us_core=True)
        assert r["resourceType"] == "EpisodeOfCare"


class TestR5EpisodeOfCareMapper:
    def setup_method(self):
        seed_all(0)
        raw = _raw(count=3)
        from mappers.r5.episode_of_care import map_episode_of_care
        self.eoc = raw["episodes_of_care"][0]
        self.resource = map_episode_of_care(self.eoc)

    def test_resource_type(self):
        assert self.resource["resourceType"] == "EpisodeOfCare"

    def test_r5_diagnosis_uses_codeable_reference(self):
        if self.eoc.get("condition_ids"):
            assert "diagnosis" in self.resource
            diag = self.resource["diagnosis"][0]
            # R5: CodeableReference wraps Reference inside .reference
            assert "reference" in diag["condition"]
            assert "urn:uuid:" in diag["condition"]["reference"]["reference"]

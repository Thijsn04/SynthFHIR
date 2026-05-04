"""Unit tests for all generator modules.

Run with:  pytest tests/test_generators.py -v
"""
import pytest

from generators._rng import seed_all
from generators.cohort_gen import generate_cohort
from generators.condition_gen import generate_conditions_for_patient
from generators.diagnostic_report_gen import generate_diagnostic_reports_for_encounter
from generators.immunization_gen import generate_immunizations_for_patient
from generators.medication_gen import generate_medications_for_patient
from generators.observation_gen import generate_observations_for_encounter
from generators.organization_gen import generate_organization
from generators.patient_gen import generate_patient, generate_patients

# ---------------------------------------------------------------------------
# _rng — seeding reproducibility
# ---------------------------------------------------------------------------

class TestRng:
    def test_seed_produces_same_uuid(self):
        seed_all(42)
        from generators._rng import new_uuid
        id1 = new_uuid()

        seed_all(42)
        id2 = new_uuid()

        assert id1 == id2

    def test_different_seeds_produce_different_uuids(self):
        from generators._rng import new_uuid
        seed_all(1)
        id1 = new_uuid()
        seed_all(2)
        id2 = new_uuid()
        assert id1 != id2

    def test_e164_format(self):
        from generators._rng import e164_phone
        seed_all(0)
        phone = e164_phone()
        assert phone.startswith("+1")
        assert len(phone) == 12
        assert phone[2:].isdigit()


# ---------------------------------------------------------------------------
# Patient generator
# ---------------------------------------------------------------------------

class TestPatientGenerator:
    def setup_method(self):
        seed_all(0)

    def test_required_keys(self):
        p = generate_patient()
        for key in ("id", "mrn", "first_name", "last_name", "gender", "birth_date",
                    "age", "phone_home", "phone_mobile", "email", "address_line",
                    "city", "state", "postal_code", "country", "language_code",
                    "race_code", "ethnicity_code", "birth_sex", "height_cm", "obs_baseline"):
            assert key in p, f"Missing key: {key}"

    def test_age_range_respected(self):
        patients = generate_patients(20, age_min=30, age_max=50)
        for p in patients:
            assert 30 <= p["age"] <= 51, f"Age {p['age']} outside expected range"

    def test_minors_never_married(self):
        seed_all(999)
        for _ in range(50):
            p = generate_patient(age_min=0, age_max=17)
            if p["age"] < 18:
                assert p["marital_code"] == "S", f"Minor has marital_code={p['marital_code']}"

    def test_phone_e164(self):
        p = generate_patient()
        assert p["phone_home"].startswith("+1")
        assert p["phone_mobile"].startswith("+1")

    def test_gender_values(self):
        valid = {"male", "female", "other", "unknown"}
        patients = generate_patients(20)
        for p in patients:
            assert p["gender"] in valid

    def test_obs_baseline_keys(self):
        p = generate_patient()
        for key in ("systolic_bp", "diastolic_bp", "heart_rate", "body_temperature", "height_cm"):
            assert key in p["obs_baseline"]

    def test_height_in_realistic_range(self):
        patients = generate_patients(50)
        for p in patients:
            assert 140 <= p["height_cm"] <= 210


# ---------------------------------------------------------------------------
# Organization generator
# ---------------------------------------------------------------------------

class TestOrganizationGenerator:
    def setup_method(self):
        seed_all(0)

    def test_required_keys(self):
        org = generate_organization()
        for key in ("id", "name", "type_code", "type_display", "phone", "email",
                    "address_line", "city", "state", "postal_code", "country"):
            assert key in org

    def test_phone_e164(self):
        org = generate_organization()
        assert org["phone"].startswith("+1")

    def test_country_us(self):
        assert generate_organization()["country"] == "US"


# ---------------------------------------------------------------------------
# Condition generator
# ---------------------------------------------------------------------------

class TestConditionGenerator:
    def setup_method(self):
        seed_all(0)

    def test_required_keys(self):
        conds = generate_conditions_for_patient("pid", "pracid", patient_age=40)
        assert len(conds) >= 1
        for c in conds:
            for key in ("id", "patient_id", "snomed_code", "icd10_code", "display",
                        "clinical_status", "onset_date", "recorded_date", "linked_obs_types"):
                assert key in c

    def test_onset_before_recorded(self):
        from datetime import date
        seed_all(1)
        for _ in range(20):
            conds = generate_conditions_for_patient("pid", "pracid", patient_age=50)
            for c in conds:
                onset = date.fromisoformat(c["onset_date"])
                recorded = date.fromisoformat(c["recorded_date"])
                assert onset <= recorded, f"Onset {onset} after recorded {recorded}"

    def test_age_filter_applied(self):
        """Conditions with typical_age_min > patient_age should not appear."""
        from data.conditions import CONDITIONS_BY_KEY
        afib = CONDITIONS_BY_KEY["atrial_fibrillation"]  # typical_age_min=50
        for _ in range(30):
            seed_all(_)
            conds = generate_conditions_for_patient("pid", "pracid", patient_age=10)
            condition_keys = [c["snomed_code"] for c in conds]
            assert afib.snomed_code not in condition_keys, (
                "Atrial fibrillation assigned to 10-year-old"
            )

    def test_invalid_condition_raises(self):
        with pytest.raises(ValueError, match="Unknown condition"):
            generate_conditions_for_patient("pid", "pracid", patient_age=40,
                                            condition_filter="nonsense_xyz")

    def test_valid_condition_filter(self):
        conds = generate_conditions_for_patient("pid", "pracid", patient_age=40,
                                                condition_filter="diabetes")
        snomed_codes = [c["snomed_code"] for c in conds]
        assert "44054006" in snomed_codes  # Type 2 Diabetes SNOMED


# ---------------------------------------------------------------------------
# Observation generator
# ---------------------------------------------------------------------------

class TestObservationGenerator:
    def setup_method(self):
        seed_all(0)

    def _make_condition(self, snomed_code: str, status: str = "active") -> dict:
        return {
            "snomed_code": snomed_code,
            "clinical_status": status,
            "linked_obs_types": ["systolic_bp", "diastolic_bp"],
        }

    def test_baseline_vitals_always_present(self):
        obs = generate_observations_for_encounter("p", "e", "pr", "2024-01-01T10:00:00Z", [])
        loinc_codes = {o["loinc_code"] for o in obs}
        # BP is now a panel (85354-9) with systolic/diastolic as components
        assert "85354-9" in loinc_codes   # blood pressure panel
        assert "8867-4" in loinc_codes    # heart_rate
        assert "8310-5" in loinc_codes    # body_temperature
        assert "9279-1" in loinc_codes    # respiratory_rate
        assert "8302-2" in loinc_codes    # height

    def test_bp_panel_has_components(self):
        obs = generate_observations_for_encounter("p", "e", "pr", "2024-01-01T10:00:00Z", [])
        bp_panel = next(o for o in obs if o["loinc_code"] == "85354-9")
        component_codes = {c["loinc_code"] for c in bp_panel["components"]}
        assert "8480-6" in component_codes  # systolic
        assert "8462-4" in component_codes  # diastolic

    def test_bmi_derived_not_independent(self):
        baseline = {"systolic_bp": 110, "diastolic_bp": 70, "heart_rate": 72,
                    "respiratory_rate": 14, "body_temperature": 36.7, "oxygen_saturation": 98}
        height_cm = 175.0
        obs = generate_observations_for_encounter(
            "p", "e", "pr", "2024-01-01T10:00:00Z", [],
            obs_baseline=baseline, height_cm=height_cm
        )
        weight_obs = next((o for o in obs if o["loinc_code"] == "29463-7"), None)
        bmi_obs = next((o for o in obs if o["loinc_code"] == "39156-5"), None)

        if weight_obs and bmi_obs:
            expected_bmi = round(weight_obs["value"] / ((height_cm / 100) ** 2), 1)
            assert bmi_obs["value"] == expected_bmi

    def test_abnormal_values_for_active_conditions(self):
        cond = {"clinical_status": "active", "linked_obs_types": ["blood_glucose"]}
        seed_all(5)
        values = []
        for _ in range(20):
            obs_list = generate_observations_for_encounter("p", "e", "pr", "2024-01-01T10:00:00Z",
                                                           [cond])
            glucose = next((o for o in obs_list if o["loinc_code"] == "2345-7"), None)
            if glucose:
                values.append(glucose["value"])
        # With active diabetes, most glucose readings should be above the normal threshold (99)
        assert sum(v > 99 for v in values) > len(values) * 0.7


# ---------------------------------------------------------------------------
# Cohort generator (integration)
# ---------------------------------------------------------------------------

class TestCohortGenerator:
    def test_basic_cohort(self):
        seed_all(42)
        raw = generate_cohort(count=3, seed=None)  # already seeded
        assert len(raw["patients"]) == 3
        assert len(raw["organizations"]) >= 1
        assert len(raw["practitioners"]) >= 1
        assert len(raw["encounters"]) >= 3
        assert len(raw["observations"]) >= 3

    def test_seed_reproducibility(self):
        raw1 = generate_cohort(count=2, seed=100)
        raw2 = generate_cohort(count=2, seed=100)
        # Patient IDs and names should be identical
        assert raw1["patients"][0]["id"] == raw2["patients"][0]["id"]
        assert raw1["patients"][0]["first_name"] == raw2["patients"][0]["first_name"]

    def test_new_resource_types_present(self):
        raw = generate_cohort(count=5, seed=7)
        assert "immunizations" in raw
        assert "diagnostic_reports" in raw
        assert "medications" in raw

    def test_encounter_after_condition_onset(self):
        from datetime import datetime
        raw = generate_cohort(count=5, seed=42)
        cond_recorded_dates = {
            c["patient_id"]: c["recorded_date"] for c in raw["conditions"]
        }
        for enc in raw["encounters"]:
            pid = enc["patient_id"]
            if pid not in cond_recorded_dates:
                continue
            recorded = datetime.strptime(cond_recorded_dates[pid], "%Y-%m-%d")
            enc_start = datetime.strptime(enc["start_datetime"], "%Y-%m-%dT%H:%M:%SZ")
            assert enc_start >= recorded, (
                f"Encounter {enc['start_datetime']} is before condition recorded {cond_recorded_dates[pid]}"
            )

    def test_invalid_condition_filter_raises(self):
        with pytest.raises(ValueError):
            generate_cohort(count=1, condition_filter="not_a_real_condition")

    def test_age_appropriate_conditions(self):
        """Children should not get conditions with high typical_age_min."""
        from data.conditions import CONDITIONS_BY_KEY
        afib_snomed = CONDITIONS_BY_KEY["atrial_fibrillation"].snomed_code
        raw = generate_cohort(count=30, age_min=0, age_max=15, seed=123)
        for cond in raw["conditions"]:
            assert cond["snomed_code"] != afib_snomed, (
                "Atrial fibrillation assigned to child"
            )


# ---------------------------------------------------------------------------
# Medication generator
# ---------------------------------------------------------------------------

class TestMedicationGenerator:
    def test_active_conditions_get_meds(self):
        conds = [
            {"snomed_code": "44054006", "clinical_status": "active",
             "linked_obs_types": [], "display": "Diabetes"}
        ]
        meds = generate_medications_for_patient("pid", "pracid", "encid", conds)
        assert len(meds) >= 1
        for m in meds:
            assert m["rxnorm_code"]
            assert m["patient_id"] == "pid"

    def test_resolved_conditions_have_stopped_status(self):
        conds = [
            {"snomed_code": "44054006", "clinical_status": "resolved",
             "linked_obs_types": [], "display": "Diabetes"}
        ]
        meds = generate_medications_for_patient("pid", "pracid", "encid", conds)
        # resolved → stopped (or no meds at all if filter is strict)
        for m in meds:
            assert m["status"] in ("stopped", "active")


# ---------------------------------------------------------------------------
# Immunization generator
# ---------------------------------------------------------------------------

class TestImmunizationGenerator:
    def test_age_filter(self):
        seed_all(0)
        imms = generate_immunizations_for_patient("pid", "pracid", patient_age=70)
        cvx_codes = {i["cvx_code"] for i in imms}
        # HPV (CVX 62) is only for age 9-45 — should not appear for 70-year-old
        assert "62" not in cvx_codes

    def test_required_keys(self):
        seed_all(1)
        imms = generate_immunizations_for_patient("pid", "pracid", patient_age=30)
        for imm in imms:
            for key in ("id", "patient_id", "practitioner_id", "cvx_code",
                        "display", "status", "occurrence_date", "lot_number"):
                assert key in imm


# ---------------------------------------------------------------------------
# DiagnosticReport generator
# ---------------------------------------------------------------------------

class TestDiagnosticReportGenerator:
    def test_groups_lab_observations(self):
        obs = [
            {"id": "o1", "category_code": "laboratory"},
            {"id": "o2", "category_code": "vital-signs"},
            {"id": "o3", "category_code": "laboratory"},
        ]
        reports = generate_diagnostic_reports_for_encounter("p", "e", "pr", "2024-01-01T10:00:00Z", obs)
        assert len(reports) == 1
        assert set(reports[0]["observation_ids"]) == {"o1", "o3"}

    def test_no_report_when_no_lab_obs(self):
        obs = [{"id": "o1", "category_code": "vital-signs"}]
        reports = generate_diagnostic_reports_for_encounter("p", "e", "pr", "2024-01-01T10:00:00Z", obs)
        assert reports == []

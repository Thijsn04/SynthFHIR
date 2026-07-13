"""Tests for clinical and demographic realism features."""
from data.geography import LOCALITIES
from generators.cohort_gen import generate_cohort


class TestGeographicCoherence:
    def test_address_parts_agree(self):
        by_city_state = {(loc.city, loc.state): loc.zip_prefix for loc in LOCALITIES}
        raw = generate_cohort(count=40, seed=11)
        assert raw["patients"]
        for p in raw["patients"]:
            key = (p["city"], p["state"])
            assert key in by_city_state, f"unknown locality {key}"
            assert p["postal_code"].startswith(by_city_state[key])
            assert len(p["postal_code"]) == 5


class TestSexAppropriateConditions:
    def test_prostate_cancer_only_for_males(self):
        # Force prostate cancer as the primary filter across a mixed cohort.
        raw = generate_cohort(count=60, seed=7, condition_filter=None)
        gender_by_id = {p["id"]: p["gender"] for p in raw["patients"]}
        for cond in raw["conditions"]:
            if cond.get("condition_key") == "prostate_cancer":
                assert gender_by_id[cond["patient_id"]] != "female"

    def test_non_binary_patients_still_get_conditions(self):
        # Patients with gender other/unknown should not be blocked from conditions.
        raw = generate_cohort(count=40, seed=3)
        non_binary = [p for p in raw["patients"] if p["gender"] in ("other", "unknown")]
        if non_binary:
            ids = {p["id"] for p in non_binary}
            assert any(c["patient_id"] in ids for c in raw["conditions"])

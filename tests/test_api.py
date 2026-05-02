"""Integration tests for the FastAPI endpoints.

Run with:  pytest tests/test_api.py -v
Requires:  pip install httpx
"""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# /api/generate/cohort
# ---------------------------------------------------------------------------

class TestCohortEndpoint:
    def test_returns_bundle(self):
        r = client.get("/api/generate/cohort", params={"count": 2, "seed": 1})
        assert r.status_code == 200
        body = r.json()
        assert body["resourceType"] == "Bundle"

    def test_entry_count_scales_with_patient_count(self):
        r1 = client.get("/api/generate/cohort", params={"count": 1, "seed": 5})
        r2 = client.get("/api/generate/cohort", params={"count": 3, "seed": 5})
        assert r2.json()["total"] > r1.json()["total"]

    def test_seed_reproducibility(self):
        r1 = client.get("/api/generate/cohort", params={"count": 2, "seed": 42})
        r2 = client.get("/api/generate/cohort", params={"count": 2, "seed": 42})
        assert r1.json() == r2.json()

    def test_r5_version(self):
        r = client.get("/api/generate/cohort", params={"count": 1, "seed": 1, "version": "R5"})
        assert r.status_code == 200
        body = r.json()
        assert body["resourceType"] == "Bundle"
        patient_entries = [e for e in body["entry"] if e["resource"]["resourceType"] == "Patient"]
        assert len(patient_entries) >= 1

    def test_invalid_condition_returns_422(self):
        r = client.get("/api/generate/cohort", params={"count": 1, "condition": "xyz_not_real"})
        assert r.status_code == 422

    def test_valid_condition_filter(self):
        r = client.get("/api/generate/cohort",
                       params={"count": 3, "seed": 1, "condition": "diabetes"})
        assert r.status_code == 200
        body = r.json()
        condition_entries = [
            e for e in body["entry"]
            if e["resource"]["resourceType"] == "Condition"
        ]
        snomed_codes = {
            coding["code"]
            for e in condition_entries
            for coding in e["resource"]["code"]["coding"]
            if coding.get("system") == "http://snomed.info/sct"
        }
        assert "44054006" in snomed_codes  # Type 2 Diabetes

    def test_age_min_gte_age_max_returns_422(self):
        r = client.get("/api/generate/cohort", params={"age_min": 80, "age_max": 20})
        assert r.status_code == 422

    def test_transaction_bundle_type(self):
        r = client.get("/api/generate/cohort",
                       params={"count": 1, "seed": 1, "bundle_type": "transaction"})
        assert r.status_code == 200
        body = r.json()
        assert body["type"] == "transaction"
        for entry in body["entry"]:
            assert "request" in entry
            assert entry["request"]["method"] == "POST"

    def test_ndjson_format(self):
        r = client.get("/api/generate/cohort",
                       params={"count": 1, "seed": 1, "format": "ndjson"})
        assert r.status_code == 200
        assert "ndjson" in r.headers["content-type"]
        lines = [ln for ln in r.text.strip().splitlines() if ln.strip()]
        assert len(lines) >= 1
        import json
        for line in lines:
            obj = json.loads(line)
            assert "resourceType" in obj

    def test_us_core_profile(self):
        r = client.get("/api/generate/cohort",
                       params={"count": 1, "seed": 1, "profile": "us-core"})
        assert r.status_code == 200
        body = r.json()
        patient_entries = [e["resource"] for e in body["entry"]
                           if e["resource"]["resourceType"] == "Patient"]
        assert len(patient_entries) >= 1
        p = patient_entries[0]
        assert "us-core-patient" in p["meta"]["profile"][0]
        ext_urls = [e["url"] for e in p.get("extension", [])]
        assert any("us-core-race" in u for u in ext_urls)

    def test_new_resource_types_in_bundle(self):
        r = client.get("/api/generate/cohort", params={"count": 10, "seed": 7})
        body = r.json()
        resource_types = {e["resource"]["resourceType"] for e in body["entry"]}
        assert "Immunization" in resource_types
        assert "MedicationRequest" in resource_types
        assert "DiagnosticReport" in resource_types

    def test_bundle_references_are_urn_uuid(self):
        r = client.get("/api/generate/cohort", params={"count": 1, "seed": 1})
        body = r.json()
        full_urls = {e["fullUrl"] for e in body["entry"]}
        for entry in body["entry"]:
            resource = entry["resource"]
            _check_references(resource, full_urls)


def _check_references(resource: dict, full_urls: set, path: str = "") -> None:
    """Walk a resource dict and assert every 'reference' value is in full_urls."""
    if isinstance(resource, dict):
        for k, v in resource.items():
            if k == "reference" and isinstance(v, str):
                assert v in full_urls, (
                    f"Reference '{v}' at path '{path}.{k}' not found in bundle fullUrls"
                )
            else:
                _check_references(v, full_urls, f"{path}.{k}")
    elif isinstance(resource, list):
        for i, item in enumerate(resource):
            _check_references(item, full_urls, f"{path}[{i}]")


# ---------------------------------------------------------------------------
# /api/generate/patient
# ---------------------------------------------------------------------------

class TestPatientEndpoint:
    def test_returns_bundle(self):
        r = client.get("/api/generate/patient", params={"count": 3, "seed": 1})
        assert r.status_code == 200
        body = r.json()
        assert body["resourceType"] == "Bundle"
        patient_entries = [e for e in body["entry"] if e["resource"]["resourceType"] == "Patient"]
        assert len(patient_entries) == 3

    def test_age_range_validation(self):
        r = client.get("/api/generate/patient", params={"age_min": 50, "age_max": 10})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# /api/generate/practitioner
# ---------------------------------------------------------------------------

class TestPractitionerEndpoint:
    def test_returns_bundle(self):
        r = client.get("/api/generate/practitioner", params={"count": 2, "seed": 1})
        assert r.status_code == 200
        body = r.json()
        prac_entries = [e for e in body["entry"] if e["resource"]["resourceType"] == "Practitioner"]
        assert len(prac_entries) == 2


# ---------------------------------------------------------------------------
# /api/generate/organization
# ---------------------------------------------------------------------------

class TestOrganizationEndpoint:
    def test_returns_bundle(self):
        r = client.get("/api/generate/organization", params={"count": 2, "seed": 1})
        assert r.status_code == 200
        body = r.json()
        org_entries = [e for e in body["entry"] if e["resource"]["resourceType"] == "Organization"]
        assert len(org_entries) == 2


# ---------------------------------------------------------------------------
# /api/conditions and /api/observations
# ---------------------------------------------------------------------------

class TestCatalogEndpoints:
    def test_conditions_catalog(self):
        r = client.get("/api/conditions")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 10
        keys = {item["key"] for item in data}
        assert "type2_diabetes" in keys
        assert "depression" in keys

    def test_conditions_include_typical_age_min(self):
        r = client.get("/api/conditions")
        data = r.json()
        for item in data:
            assert "typical_age_min" in item

    def test_observations_catalog(self):
        r = client.get("/api/observations")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 15  # we added several new observations
        loinc_codes = {item["loinc_code"] for item in data}
        assert "8302-2" in loinc_codes    # height
        assert "44261-6" in loinc_codes   # PHQ-9
        assert "70274-6" in loinc_codes   # GAD-7
        assert "9279-1"  in loinc_codes   # respiratory_rate

    def test_observations_include_ranges(self):
        r = client.get("/api/observations")
        data = r.json()
        for item in data:
            assert "normal_range" in item
            assert "abnormal_range" in item

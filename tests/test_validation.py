"""Tests for the dependency-free bundle validator."""
import synthfhir
from validation import validate_bundle


def _bundle(*resources, bundle_type="collection"):
    return {
        "resourceType": "Bundle",
        "type": bundle_type,
        "entry": [
            {"fullUrl": f"urn:uuid:{r.get('id', i)}", "resource": r}
            for i, r in enumerate(resources)
        ],
    }


class TestStructuralChecks:
    def test_non_bundle_rejected(self):
        report = validate_bundle({"resourceType": "Patient"})
        assert not report.valid
        assert any("Bundle" in e.message for e in report.errors)

    def test_missing_resource_type_is_error(self):
        report = validate_bundle(_bundle({"id": "a"}))
        assert not report.valid
        assert any("resourceType" in e.message for e in report.errors)

    def test_missing_required_element_is_error(self):
        # Observation requires status and code.
        report = validate_bundle(_bundle({"resourceType": "Observation", "id": "o1"}))
        messages = {e.message for e in report.errors}
        assert "Missing required element 'status'." in messages
        assert "Missing required element 'code'." in messages

    def test_duplicate_full_url_is_error(self):
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {"fullUrl": "urn:uuid:dup", "resource": {"resourceType": "Patient", "id": "dup"}},
                {"fullUrl": "urn:uuid:dup", "resource": {"resourceType": "Patient", "id": "dup"}},
            ],
        }
        report = validate_bundle(bundle)
        assert any("Duplicate" in e.message for e in report.errors)

    def test_transaction_requires_request(self):
        bundle = _bundle({"resourceType": "Patient", "id": "p1"}, bundle_type="transaction")
        report = validate_bundle(bundle)
        assert any("request" in e.message for e in report.errors)


class TestReferenceResolution:
    def test_unresolved_internal_reference_is_error(self):
        obs = {
            "resourceType": "Observation",
            "id": "o1",
            "status": "final",
            "code": {"text": "x"},
            "subject": {"reference": "urn:uuid:ghost"},
        }
        report = validate_bundle(_bundle(obs))
        assert any("Unresolved reference" in e.message for e in report.errors)

    def test_external_reference_is_ignored(self):
        obs = {
            "resourceType": "Observation",
            "id": "o1",
            "status": "final",
            "code": {"coding": [{"system": "http://loinc.org", "code": "1234-5"}]},
            "subject": {"reference": "https://example.org/Patient/1"},
        }
        report = validate_bundle(_bundle(obs))
        assert report.valid


class TestGeneratedCohorts:
    def test_generated_r4_bundle_is_clean(self):
        bundle = synthfhir.generate_cohort_bundle(count=5, seed=1)
        report = validate_bundle(bundle)
        assert report.valid, report.to_dict()["errors"]

    def test_generated_r5_us_core_bundle_is_clean(self):
        bundle = synthfhir.generate_cohort_bundle(count=5, seed=2, version="R5", profile="us-core")
        report = validate_bundle(bundle)
        assert report.valid, report.to_dict()["errors"]

    def test_transaction_bundle_is_clean(self):
        bundle = synthfhir.generate_cohort_bundle(count=3, seed=3, bundle_type="transaction")
        report = validate_bundle(bundle)
        assert report.valid, report.to_dict()["errors"]

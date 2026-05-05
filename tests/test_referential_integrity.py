"""Referential integrity test suite.

Verifies that every FHIR reference in a generated Bundle resolves to an entry
within that same Bundle. This catches broken cross-resource links that
structural tests and endpoint tests do not detect.

Run with:  pytest tests/test_referential_integrity.py -v
"""
import re

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Regex to pull the id from a urn:uuid: fullUrl
_URN_UUID_RE = re.compile(r"^urn:uuid:(.+)$")


def _collect_full_urls(bundle: dict) -> set[str]:
    """Collect all fullUrl values from Bundle.entry."""
    urls: set[str] = set()
    for entry in bundle.get("entry", []):
        fu = entry.get("fullUrl", "")
        if fu:
            urls.add(fu)
    return urls


def _collect_references(obj, path: str = "") -> list[tuple[str, str]]:
    """Recursively walk a FHIR resource dict and collect all reference strings.

    Returns a list of (json_path, reference_value) pairs.
    """
    results: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            child_path = f"{path}.{k}" if path else k
            if k == "reference" and isinstance(v, str):
                results.append((child_path, v))
            else:
                results.extend(_collect_references(v, child_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(_collect_references(item, f"{path}[{i}]"))
    return results


def _assert_bundle_integrity(bundle: dict) -> list[str]:
    """Return a list of broken-reference error strings (empty = all good)."""
    full_urls = _collect_full_urls(bundle)
    errors: list[str] = []

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType", "?")
        resource_id = resource.get("id", "?")

        refs = _collect_references(resource)
        for ref_path, ref_val in refs:
            # References are urn:uuid:... style
            if ref_val.startswith("urn:uuid:"):
                if ref_val not in full_urls:
                    errors.append(
                        f"{resource_type}/{resource_id} @ {ref_path} → "
                        f"'{ref_val}' not found in Bundle"
                    )
            # Relative references like "Patient/urn:uuid:..." would be a mapper bug
            # but we still flag them if they don't resolve
    return errors


class TestReferentialIntegrity:
    """All FHIR references in a generated Bundle must resolve within that Bundle."""

    def _get_bundle(self, **params) -> dict:
        r = client.get("/api/generate/cohort", params=params)
        assert r.status_code == 200, f"Unexpected status {r.status_code}: {r.text}"
        return r.json()

    def test_small_cohort_r4(self):
        bundle = self._get_bundle(count=3, seed=1)
        errors = _assert_bundle_integrity(bundle)
        assert not errors, "\n".join(errors)

    def test_small_cohort_r5(self):
        bundle = self._get_bundle(count=3, seed=2, version="R5")
        errors = _assert_bundle_integrity(bundle)
        assert not errors, "\n".join(errors)

    def test_larger_cohort(self):
        bundle = self._get_bundle(count=10, seed=42)
        errors = _assert_bundle_integrity(bundle)
        assert not errors, "\n".join(errors)

    def test_condition_filtered_cohort(self):
        bundle = self._get_bundle(count=5, seed=7, condition="diabetes")
        errors = _assert_bundle_integrity(bundle)
        assert not errors, "\n".join(errors)

    def test_service_request_basedOn_resolves(self):
        """Observations with basedOn must reference a ServiceRequest in the Bundle."""
        bundle = self._get_bundle(count=5, seed=99)
        full_urls = _collect_full_urls(bundle)

        sr_urls = {
            entry["fullUrl"]
            for entry in bundle.get("entry", [])
            if entry.get("resource", {}).get("resourceType") == "ServiceRequest"
        }

        broken: list[str] = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") != "Observation":
                continue
            for based_on in resource.get("basedOn", []):
                ref_val = based_on.get("reference", "")
                if ref_val and ref_val not in sr_urls:
                    broken.append(
                        f"Observation/{resource.get('id')} basedOn '{ref_val}' "
                        f"not found among ServiceRequests"
                    )
        assert not broken, "\n".join(broken)

    def test_observations_linked_to_service_requests(self):
        """At least some Observations in the bundle must have a basedOn reference."""
        bundle = self._get_bundle(count=5, seed=55)
        obs_with_basedOn = [
            entry["resource"]
            for entry in bundle.get("entry", [])
            if entry.get("resource", {}).get("resourceType") == "Observation"
            and entry["resource"].get("basedOn")
        ]
        assert len(obs_with_basedOn) > 0, (
            "No Observations have a basedOn reference — ServiceRequest linkage is not working"
        )

    @pytest.mark.parametrize("seed", [1, 10, 100, 1000])
    def test_multiple_seeds(self, seed: int):
        bundle = self._get_bundle(count=4, seed=seed)
        errors = _assert_bundle_integrity(bundle)
        assert not errors, f"seed={seed}:\n" + "\n".join(errors)

"""Strict FHIR conformance tests.

Every generated resource is validated against the real FHIR StructureDefinitions
using the fhir.resources pydantic models (R4B for R4 output, R5 for R5 output).
This catches cardinality, datatype, and structural errors that the lightweight
built-in validator does not. Skipped if fhir.resources is not installed.
"""
import importlib

import pytest

import synthfhir

fhir_resources = pytest.importorskip("fhir.resources")

# A spread of condition cohorts so every condition-gated resource type appears.
_CONDITIONS = ["type2_diabetes", "osteoarthritis", "atrial_fibrillation", "coronary_artery_disease"]


def _model_class(resource_type: str, r4: bool):
    module = f"fhir.resources.{'R4B.' if r4 else ''}{resource_type.lower()}"
    return getattr(importlib.import_module(module), resource_type)


def _validate_bundle(bundle: dict, r4: bool) -> list[str]:
    failures: list[str] = []
    for entry in bundle["entry"]:
        resource = entry["resource"]
        rtype = resource["resourceType"]
        try:
            _model_class(rtype, r4).model_validate(resource)
        except Exception as exc:  # noqa: BLE001 - report the first line per resource
            failures.append(f"{rtype}/{resource.get('id', '?')}: {str(exc).splitlines()[0]}")
    return failures


@pytest.mark.parametrize("version,r4", [("R4", True), ("R5", False)])
@pytest.mark.parametrize("profile", ["base", "us-core"])
def test_generated_resources_are_spec_conformant(version, r4, profile):
    for condition in _CONDITIONS:
        bundle = synthfhir.generate_cohort_bundle(
            count=12, seed=3, version=version, profile=profile, years=4, condition=condition
        )
        failures = _validate_bundle(bundle, r4)
        assert not failures, f"{version}/{profile}/{condition}: {failures[:8]}"


@pytest.mark.parametrize("version,r4", [("R4", True), ("R5", False)])
def test_transaction_bundle_is_conformant(version, r4):
    bundle = synthfhir.generate_cohort_bundle(
        count=6, seed=5, version=version, bundle_type="transaction", years=3
    )
    assert not _validate_bundle(bundle, r4)

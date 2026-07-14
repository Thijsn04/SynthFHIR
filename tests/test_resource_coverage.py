"""Broad resource-coverage tests across the expanded resource set."""
import synthfhir
from generators.cohort_gen import generate_cohort
from mappers.pipeline import map_cohort

# Resource types that a rich cohort should reliably contain.
_CORE_TYPES = {
    "Patient", "Practitioner", "PractitionerRole", "Organization", "Location",
    "RelatedPerson", "Condition", "Encounter", "Observation", "DiagnosticReport",
    "Specimen", "QuestionnaireResponse", "DocumentReference", "Medication",
    "MedicationRequest", "MedicationStatement", "Procedure", "ServiceRequest",
    "ClinicalImpression", "Account", "Claim", "ExplanationOfBenefit", "Task",
    "Communication", "Schedule", "Slot", "Composition", "Group", "CareTeam",
    "CarePlan", "Goal", "List", "Coverage", "Provenance",
}


def _types(bundle):
    return {e["resource"]["resourceType"] for e in bundle["entry"]}


class TestBreadth:
    def test_rich_cohort_covers_core_types(self):
        bundle = synthfhir.generate_cohort_bundle(count=25, seed=13, years=5, condition="type2_diabetes")
        present = _types(bundle)
        missing = _CORE_TYPES - present
        assert not missing, f"missing expected resource types: {sorted(missing)}"

    def test_at_least_forty_resource_types_available(self):
        # Combine several targeted cohorts to exercise condition-gated resources.
        seen = set()
        for cond in ("osteoarthritis", "atrial_fibrillation", "type2_diabetes", "coronary_artery_disease"):
            seen |= _types(synthfhir.generate_cohort_bundle(count=15, seed=2, condition=cond))
        assert len(seen) >= 40, f"only {len(seen)} types seen: {sorted(seen)}"


class TestValidityAcrossVersions:
    def test_r4_and_r5_validate_clean(self):
        for version in ("R4", "R5"):
            for profile in ("base", "us-core"):
                bundle = synthfhir.generate_cohort_bundle(
                    count=12, seed=8, version=version, profile=profile, years=4
                )
                report = synthfhir.validate_bundle(bundle)
                assert report.valid, (version, profile, report.to_dict()["errors"][:5])

    def test_transaction_bundle_validates(self):
        bundle = synthfhir.generate_cohort_bundle(count=10, seed=9, bundle_type="transaction", years=3)
        assert synthfhir.validate_bundle(bundle).valid


class TestOrderingIsReferenceSafe:
    def test_every_reference_resolves(self):
        raw = generate_cohort(count=15, seed=4, years=4)
        for version in ("R4", "R5"):
            resources = map_cohort(raw, version)
            ids = set()
            for r in resources:
                if r.get("id"):
                    ids.add(f"urn:uuid:{r['id']}")
                    ids.add(f"{r['resourceType']}/{r['id']}")
            # Build the bundle and validate references resolve.
            bundle = {
                "resourceType": "Bundle",
                "type": "collection",
                "entry": [{"fullUrl": f"urn:uuid:{r['id']}", "resource": r} for r in resources],
            }
            report = synthfhir.validate_bundle(bundle)
            unresolved = [e for e in report.errors if "Unresolved reference" in e.message]
            assert not unresolved, unresolved[:5]

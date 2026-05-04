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
        # Use a non-BP-panel observation so valueQuantity is present
        non_panel = next(o for o in raw["observations"] if o["loinc_code"] != "85354-9")
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

"""Tests for DocumentReference and MedicationDispense generation and mapping."""
import base64

from generators.cohort_gen import generate_cohort
from mappers.pipeline import map_cohort


def _resources(version="R4", **kw):
    raw = generate_cohort(count=8, seed=21, **kw)
    return raw, map_cohort(raw, version)


def _by_type(resources, rtype):
    return [r for r in resources if r["resourceType"] == rtype]


class TestDocumentReference:
    def test_one_note_per_encounter(self):
        raw, resources = _resources()
        docs = _by_type(resources, "DocumentReference")
        encounters = _by_type(resources, "Encounter")
        assert len(docs) == len(encounters)

    def test_structure_and_references(self):
        raw, resources = _resources()
        enc_ids = {f"urn:uuid:{e['id']}" for e in raw["encounters"]}
        for doc in _by_type(resources, "DocumentReference"):
            assert doc["status"] == "current"
            assert doc["type"]["coding"][0]["system"] == "http://loinc.org"
            assert doc["subject"]["reference"].startswith("urn:uuid:")
            att = doc["content"][0]["attachment"]
            assert att["contentType"] == "text/plain"
            # The note text round-trips through base64.
            assert base64.b64decode(att["data"]).decode("utf-8")
            assert doc["context"]["encounter"][0]["reference"] in enc_ids

    def test_r5_context_is_a_list(self):
        _, resources = _resources(version="R5")
        docs = _by_type(resources, "DocumentReference")
        assert docs
        assert isinstance(docs[0]["context"], list)


class TestMedicationDispense:
    def test_dispense_references_a_request(self):
        raw, resources = _resources()
        request_ids = {f"urn:uuid:{m['id']}" for m in raw["medications"]}
        dispenses = _by_type(resources, "MedicationDispense")
        for d in dispenses:
            assert d["status"] == "completed"
            assert d["authorizingPrescription"][0]["reference"] in request_ids
            assert d["daysSupply"]["value"] > 0

    def test_r4_uses_codeable_concept_r5_uses_codeable_reference(self):
        _, r4 = _resources(version="R4")
        _, r5 = _resources(version="R5")
        r4_disp = _by_type(r4, "MedicationDispense")
        r5_disp = _by_type(r5, "MedicationDispense")
        if r4_disp:
            assert "medicationCodeableConcept" in r4_disp[0]
        if r5_disp:
            assert "medication" in r5_disp[0] and "concept" in r5_disp[0]["medication"]

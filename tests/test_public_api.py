"""Tests for the Python library facade, the CLI, and concurrent-seed determinism."""
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

import cli
import synthfhir
from main import app

client = TestClient(app)


# Keys whose values are the record-keeping instant (conventionally "now" in
# FHIR), not seeded clinical content. Clinical datetimes such as
# effectiveDateTime, period.start/end, and recordedDate are intentionally kept.
_RECORD_TIME_KEYS = {
    "lastUpdated", "timestamp", "issued", "authoredOn",
    "created", "recorded", "dateTime", "date",
}


def _scrub(node):
    if isinstance(node, dict):
        return {k: _scrub(v) for k, v in node.items() if k not in _RECORD_TIME_KEYS}
    if isinstance(node, list):
        return [_scrub(v) for v in node]
    return node


def _normalize(bundle: dict) -> str:
    """Serialize a bundle's clinical content, dropping generation-time metadata.

    Seeding makes RNG-derived clinical content (ids, names, values, references,
    clinical datetimes) reproducible. Record-keeping instants and the Bundle id
    reflect when generation ran and are not seeded, so they are removed here.
    """
    clone = json.loads(json.dumps(bundle))
    clone.pop("id", None)
    return json.dumps(_scrub(clone))


class TestLibrary:
    def test_bundle_is_deterministic_with_seed(self):
        a = synthfhir.generate_cohort_bundle(count=4, seed=42)
        b = synthfhir.generate_cohort_bundle(count=4, seed=42)
        assert _normalize(a) == _normalize(b)

    def test_ndjson_lines_match_entry_count(self):
        text = synthfhir.generate_cohort_ndjson(count=3, seed=1)
        lines = [ln for ln in text.splitlines() if ln.strip()]
        bundle = synthfhir.generate_cohort_bundle(count=3, seed=1)
        assert len(lines) == len(bundle["entry"])

    def test_generated_bundle_validates(self):
        bundle = synthfhir.generate_cohort_bundle(count=5, seed=7, profile="us-core")
        assert synthfhir.validate_bundle(bundle).valid

    def test_seed_is_byte_reproducible(self):
        # With a seed the record-keeping clock is frozen, so output is identical
        # down to the timestamps, not just the clinical content.
        a = synthfhir.generate_cohort_bundle(count=4, seed=2024)
        b = synthfhir.generate_cohort_bundle(count=4, seed=2024)
        assert json.dumps(a) == json.dumps(b)


class TestConcurrencyDeterminism:
    def test_concurrent_seeded_runs_are_identical(self):
        # Without serialized RNG state these would interleave and differ.
        def run():
            return _normalize(synthfhir.generate_cohort_bundle(count=3, seed=555))

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: run(), range(16)))

        assert len(set(results)) == 1


class TestPostEndpoint:
    def test_post_spec_returns_bundle(self):
        r = client.post("/api/generate/cohort", json={"count": 2, "seed": 1, "version": "R5"})
        assert r.status_code == 200
        assert r.json()["resourceType"] == "Bundle"

    def test_post_matches_get_for_same_seed(self):
        get = client.get("/api/generate/cohort?count=2&seed=99").json()
        post = client.post("/api/generate/cohort", json={"count": 2, "seed": 99}).json()
        assert _normalize(get) == _normalize(post)

    def test_post_invalid_age_range_is_422(self):
        r = client.post("/api/generate/cohort", json={"age_min": 50, "age_max": 40})
        assert r.status_code == 422

    def test_validate_endpoint_flags_bad_bundle(self):
        bad = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": {"resourceType": "Observation", "id": "x"}}],
        }
        report = client.post("/api/validate", json=bad).json()
        assert report["valid"] is False
        assert report["error_count"] >= 1


class TestCli:
    def test_generate_writes_valid_bundle(self, tmp_path, capsys):
        out = tmp_path / "cohort.json"
        rc = cli.main(["generate", "--count", "2", "--seed", "5", "-o", str(out)])
        assert rc == 0
        bundle = json.loads(out.read_text())
        assert synthfhir.validate_bundle(bundle).valid

    def test_validate_command_returns_nonzero_on_invalid(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps({"resourceType": "Patient"}))
        assert cli.main(["validate", str(bad)]) == 1

    def test_conditions_json_output(self, capsys):
        rc = cli.main(["conditions", "--json"])
        out = capsys.readouterr().out
        assert rc == 0
        assert any(c["key"] == "hypertension" for c in json.loads(out))

    def test_generate_ndjson_to_stdout(self, capsys):
        rc = cli.main(["generate", "--count", "1", "--seed", "1", "--format", "ndjson"])
        out = capsys.readouterr().out
        assert rc == 0
        first = json.loads(out.splitlines()[0])
        assert "resourceType" in first


@pytest.mark.parametrize("command", [["--version"], ["conditions"], ["observations"]])
def test_cli_smoke(command, capsys):
    try:
        cli.main(command)
    except SystemExit as exc:  # --version raises SystemExit(0)
        assert exc.code == 0

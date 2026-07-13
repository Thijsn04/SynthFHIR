# Getting started

## Requirements

- Python 3.11 or newer
- pip

No database, no message broker, and no network access are required. SynthFHIR
runs as a single process.

## Install

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/Thijsn04/SynthFHIR.git
cd SynthFHIR
pip install -e .
```

For development, install the extra tooling (pytest, ruff, mypy):

```bash
pip install -e ".[dev]"
```

## Run the server

```bash
uvicorn main:app --reload
```

or use the CLI:

```bash
synthfhir serve --port 8000
```

Then open:

- Web console: http://localhost:8000/
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Your first cohort

Generate five patients who all have diabetes, as an R4 Bundle:

```bash
curl "http://localhost:8000/api/generate/cohort?count=5&condition=diabetes&version=R4"
```

Reproducible output. The same seed always returns the same dataset:

```bash
curl "http://localhost:8000/api/generate/cohort?count=10&seed=42"
```

Stream a large cohort as NDJSON, one resource per line:

```bash
curl "http://localhost:8000/api/generate/cohort?count=500&format=ndjson" -o cohort.ndjson
```

From the command line, without starting a server:

```bash
synthfhir generate --count 10 --condition hypertension --seed 42 -o cohort.json
synthfhir validate cohort.json
```

From Python:

```python
import synthfhir

bundle = synthfhir.generate_cohort_bundle(count=10, seed=42)
report = synthfhir.validate_bundle(bundle)
assert report.valid
```

## What you get

A single cohort call returns a FHIR Bundle whose resources reference each other
by `urn:uuid:` identifiers that match the Bundle `fullUrl` entries. Patients are
linked to practitioners, organizations, conditions, encounters, observations,
medications, and more. See [FHIR resources](resources.md) for the full list.

## Next steps

- Explore the [web console](web-console.md).
- Read the [REST API reference](rest-api.md).
- Learn what a [seed guarantees](reproducibility.md).
- Add your own conditions and observations in [Catalogs](catalogs.md).

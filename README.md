<div align="center">

# 🧬 SynthFHIR

**A free, locally hosted synthetic FHIR patient-data generator**

Generate fully relational clinical datasets across **27 FHIR resource types**, conformant to R4/R5 and US Core, all linked by ID. A REST API, a CLI, a Python library, and a clean web console. No external APIs, no paid services, runs entirely on your machine.

[![CI](https://github.com/Thijsn04/SynthFHIR/actions/workflows/ci.yml/badge.svg)](https://github.com/Thijsn04/SynthFHIR/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![HL7 FHIR](https://img.shields.io/badge/HL7-FHIR%20R4%2FR5-e6007e.svg)](https://hl7.org/fhir/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Quick start

```bash
pip install -e .
uvicorn main:app --reload
```

Then open:

- Web console: http://localhost:8000/
- API docs (Swagger UI): http://localhost:8000/docs

```bash
# Generate 5 diabetes patients as an R4 Bundle
curl "http://localhost:8000/api/generate/cohort?count=5&condition=diabetes"

# Reproducible output: the same seed always returns the same data
curl "http://localhost:8000/api/generate/cohort?count=10&seed=42"

# Stream a large cohort as NDJSON
curl "http://localhost:8000/api/generate/cohort?count=500&format=ndjson" -o cohort.ndjson
```

## Four ways to use it

**Web console.** A clean browser UI at `/` to configure, generate, preview, and
download datasets. See [docs/web-console.md](docs/web-console.md).

**REST API.** Generate cohorts and standalone resources, validate bundles, and
read a CapabilityStatement. Full reference in [docs/rest-api.md](docs/rest-api.md).

**Command line.**

```bash
synthfhir generate --count 20 --condition hypertension --seed 42 -o cohort.json
synthfhir validate cohort.json
```

See [docs/cli.md](docs/cli.md).

**Python library.**

```python
import synthfhir

bundle = synthfhir.generate_cohort_bundle(count=10, seed=42)
assert synthfhir.validate_bundle(bundle).valid
```

See [docs/python-library.md](docs/python-library.md).

## What gets generated

A single cohort call returns a FHIR Bundle whose resources reference each other
by `urn:uuid:` ids matching the Bundle `fullUrl` entries: Patient,
Practitioner, PractitionerRole, Organization, Location, RelatedPerson,
Condition, AllergyIntolerance, Immunization, Coverage, Encounter, Appointment,
EpisodeOfCare, Observation, DiagnosticReport, DocumentReference,
MedicationRequest, MedicationDispense, Procedure, ServiceRequest, CareTeam,
CarePlan, Goal, List, FamilyMemberHistory, Consent, and Provenance.

Real terminology throughout: SNOMED CT and ICD-10 on conditions, LOINC and UCUM
on observations, RxNorm on medications, CVX on immunizations. Clinically
coherent: encounters never precede diagnosis, vitals stay consistent per patient,
BMI is derived from height and weight, and long timelines drift labs and escalate
therapy. See [docs/resources.md](docs/resources.md).

## Highlights

- FHIR R4 and R5, with US Core profiles and extensions via `profile=us-core`.
- Bundle or NDJSON output; collection or transaction bundles.
- Byte-reproducible output from a `seed`, safe under concurrency. See
  [docs/reproducibility.md](docs/reproducibility.md).
- A built-in bundle validator for structure and referential integrity. See
  [docs/validation.md](docs/validation.md).
- 50 conditions and 26 observation types, extendable with a single edit. See
  [docs/catalogs.md](docs/catalogs.md).

## Documentation

Full documentation lives in [docs/](docs/README.md):

| Guide | What it covers |
|---|---|
| [Getting started](docs/getting-started.md) | Install, run, first cohort |
| [Web console](docs/web-console.md) | The browser UI |
| [REST API](docs/rest-api.md) | Every endpoint and parameter |
| [CLI](docs/cli.md) | The `synthfhir` command |
| [Python library](docs/python-library.md) | Use it from your own code |
| [Architecture](docs/architecture.md) | How the layers fit together |
| [FHIR resources](docs/resources.md) | The 27 resource types and codings |
| [Catalogs](docs/catalogs.md) | Conditions, observations, and extending them |
| [Reproducibility](docs/reproducibility.md) | What a seed guarantees |
| [Validation](docs/validation.md) | The bundle validator |
| [Configuration](docs/configuration.md) | Environment variables and API key |
| [Deployment](docs/deployment.md) | Docker and production notes |
| [Roadmap](docs/roadmap.md) | Planned resource types and realism work |
| [FAQ](docs/faq.md) | Common questions |

## Docker

```bash
docker compose up --build
# or
docker build -t synthfhir . && docker run --rm -p 8000:8000 synthfhir
```

## Development

```bash
pip install -e ".[dev]"
make check     # ruff + tests
```

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md).

## A note on the data

Every record is fabricated and does not describe real people. SynthFHIR is for
development, testing, demos, and education. It is not for clinical use.

## License

MIT. Free to use in any project, commercial or otherwise.

---

<div align="center">
<sub>Built by <a href="https://github.com/Thijsn04">Thijs Nannings</a> · Medical Informatics @ UvA · <a href="https://lythos.nl">Lythos</a></sub>
</div>

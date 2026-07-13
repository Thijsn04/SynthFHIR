# SynthFHIR - Codebase Guide

Local generator of synthetic, relational FHIR patient data. No external APIs.
Ships a REST API, a CLI, a Python library, and a static web console.

Full docs live in `docs/`. This file is the quick orientation for working in the
codebase.

## Dev setup

```bash
pip install -e ".[dev]"
uvicorn main:app --reload   # web console at /, API docs at /docs
pytest tests/ -v
ruff check .
make check                  # ruff + tests
```

## Architecture

```
data/*.py  ->  generators/*_gen.py  ->  mappers/pipeline.py (r4/ or r5/)  ->  FHIR Bundle / NDJSON
```

- **`data/`** - Typed catalog dataclasses (conditions, observations, medications, immunizations, procedures). Add new code sets here.
- **`generators/`** - Produce version-agnostic plain Python dicts. `cohort_gen.py` orchestrates the pipeline in dependency order. `_rng.py` owns all randomness; `generation_scope(seed)` serializes a generation and, when seeded, seeds the RNG and freezes the clock.
- **`mappers/r4/` and `mappers/r5/`** - Convert generator dicts to FHIR resource dicts. Shared helpers live in `mappers/_helpers.py`. `mappers/pipeline.py` owns the version dispatch tables and resource ordering, shared by the API, CLI, and library.
- **`validation/`** - Dependency-free bundle validator (structure, id and reference integrity, mandatory elements).
- **`clock.py`** - Generation clock; record-keeping timestamps freeze to a deterministic instant when seeded.
- **Interfaces** - `api/routes.py` and `main.py` (REST API plus the web console mount at `/`), `cli.py` (the `synthfhir` command), `synthfhir.py` (the public library facade), `web/` (the static console).

## Key invariants

- Generators know nothing about FHIR; mappers know nothing about the API.
- All FHIR IDs are `urn:uuid:` URIs from `_rng.new_uuid()` so they match Bundle `fullUrl` entries.
- All datetimes are UTC. Clinical datetimes come from the seeded RNG; record-keeping timestamps use the generation clock.
- Seeded output is byte-reproducible within a day and safe under concurrency (see `docs/reproducibility.md`). Keep the concurrency and byte-reproducibility tests green.
- No em dashes anywhere in the repository.
- `ruff check .` must be clean before committing; mypy is soft (CI `continue-on-error`).

## Adding a new resource type

1. Generator in `generators/` returning a plain dict.
2. Catalog data in `data/` if needed (follow existing `*Def` dataclass pattern).
3. Mappers in `mappers/r4/` and `mappers/r5/`.
4. Wire into `generators/cohort_gen.py` - call generator, include in return dict.
5. Add the mappers to the dispatch tables and `_ORDER` in `mappers/pipeline.py`. The API, CLI, and library then pick it up automatically.

## Test layout

```
tests/test_generators.py            # generator output shape and field correctness
tests/test_mappers.py               # FHIR resource structure, required fields, coding
tests/test_api.py                   # HTTP endpoints, status codes, bundle structure
tests/test_validation.py            # the bundle validator
tests/test_public_api.py            # library, CLI, POST endpoint, concurrency determinism
tests/test_referential_integrity.py # cross-resource reference resolution
tests/test_realism.py               # geographic coherence, sex-appropriate conditions
tests/test_new_resources.py         # DocumentReference and MedicationDispense
tests/test_config.py                # optional API key and configuration
```

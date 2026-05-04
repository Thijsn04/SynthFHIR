# SynthFHIR — Codebase Guide

FastAPI service that generates synthetic FHIR patient data locally. No external APIs.

## Dev setup

```bash
pip install -e ".[dev]"
uvicorn main:app --reload   # http://localhost:8000/docs
pytest tests/ -v
ruff check .
```

## Architecture

```
data/*.py  →  generators/*_gen.py  →  mappers/r4/ or r5/  →  FHIR Bundle / NDJSON
```

- **`data/`** — Typed catalog dataclasses (conditions, observations, medications, immunizations, procedures). Add new code sets here.
- **`generators/`** — Produce version-agnostic plain Python dicts. `cohort_gen.py` orchestrates the full pipeline in dependency order. `_rng.py` owns all randomness — call `seed_all(n)` for reproducibility.
- **`mappers/r4/` and `mappers/r5/`** — Convert generator dicts to FHIR-conformant resource dicts. Shared helpers (ref, build_meta, build_address, …) live in `mappers/_helpers.py`.
- **`api/routes.py`** — Endpoints, query-param validation, mapper dispatch tables, Bundle/NDJSON output.

## Key invariants

- Generators know nothing about FHIR; mappers know nothing about the API.
- All FHIR IDs are `urn:uuid:` URIs from `_rng.new_uuid()` so they match Bundle `fullUrl` entries.
- All datetimes are UTC-aware (`.isoformat()` emits `+00:00`).
- `ruff check .` must be clean before committing; mypy is soft (CI `continue-on-error`).

## Adding a new resource type

1. Generator in `generators/` returning a plain dict.
2. Catalog data in `data/` if needed (follow existing `*Def` dataclass pattern).
3. Mappers in `mappers/r4/` and `mappers/r5/`.
4. Wire into `generators/cohort_gen.py` — call generator, include in return dict.
5. Wire into `api/routes.py` — add to dispatch table, `_map_and_bundle`, `_ndjson_stream`.

## Test layout

```
tests/test_generators.py   # generator output shape and field correctness
tests/test_mappers.py      # FHIR resource structure, required fields, coding
tests/test_api.py          # HTTP endpoints, status codes, bundle structure
```

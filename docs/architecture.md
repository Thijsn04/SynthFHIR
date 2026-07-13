# Architecture

SynthFHIR is organized as a set of layers, each with a single responsibility.
Data flows in one direction:

```
data/*.py  ->  generators/*_gen.py  ->  mappers/r4 or r5  ->  FHIR Bundle / NDJSON
```

## Layers

### `data/`

Typed catalog dataclasses: conditions, observations, medications, immunizations,
and procedures. These are the fixed clinical code sets. Adding a new condition or
lab is an edit here. See [Catalogs](catalogs.md).

### `generators/`

Produce version-agnostic plain Python dicts. Generators know nothing about FHIR.
`cohort_gen.py` orchestrates the full pipeline in dependency order:
organizations and locations, then practitioners, then patients and their
clinical data, then encounters and everything anchored to a visit.

`_rng.py` owns all randomness. Every generator draws from the shared, seedable
RNG through it, and `generation_scope()` serializes a generation so seeded
output stays reproducible under concurrency. See [Reproducibility](reproducibility.md).

### `mappers/`

Convert generator dicts into FHIR-conformant resource dicts. There is one mapper
per resource type per version under `mappers/r4/` and `mappers/r5/`. Shared FHIR
building blocks (references, meta, address, name, US Core extensions) live in
`mappers/_helpers.py`. Mappers know nothing about the API.

`mappers/pipeline.py` owns the version dispatch tables and the resource emission
order. It is the single mapping path shared by the REST API, the CLI, and the
Python library, which guarantees they all produce identical bundles.

### `validation/`

A dependency-free bundle validator: structure, id and reference integrity, and
base-FHIR mandatory elements. See [Validation](validation.md).

### Interfaces

- `api/routes.py` and `main.py`: the FastAPI application, endpoints, and the
  static web console mount.
- `cli.py`: the `synthfhir` command.
- `synthfhir.py`: the public Python library facade.

## Key invariants

- Generators know nothing about FHIR; mappers know nothing about the API.
- All FHIR ids are `urn:uuid:` URIs from `_rng.new_uuid()`, so they match the
  Bundle `fullUrl` entries and inter-resource references resolve within a bundle.
- All datetimes are UTC. Clinical datetimes are drawn from the seeded RNG.
  Record-keeping timestamps use a generation clock that is frozen when a seed is
  given (see [Reproducibility](reproducibility.md)).
- `ruff check .` must be clean before committing. mypy is advisory in CI.

## Request lifecycle for a cohort

1. The endpoint validates the age range and the condition filter.
2. Generation runs in a worker thread inside `generation_scope(seed)`, which
   serializes RNG state and, when seeded, freezes the clock.
3. For a bundle, mapping and bundling happen inside the same scope so the whole
   output is deterministic. For NDJSON, the deterministic raw cohort is streamed
   through the mappers, which draw no randomness.

## Adding a new resource type

1. Write a generator in `generators/` returning a plain dict.
2. Add catalog data in `data/` if needed.
3. Write mappers in `mappers/r4/` and `mappers/r5/`.
4. Wire the generator into `generators/cohort_gen.py`.
5. Add the mappers to the dispatch tables and emission order in
   `mappers/pipeline.py`.

The API, CLI, and library pick up the new resource type automatically because
they all go through the pipeline.

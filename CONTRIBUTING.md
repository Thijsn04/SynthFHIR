# Contributing to SynthFHIR

Thanks for your interest in improving SynthFHIR. This project generates
synthetic FHIR data locally, and contributions of all sizes are welcome:
bug reports, new code sets, new resource types, documentation, and tests.

## Ground rules

- Be respectful. See the [Code of Conduct](CODE_OF_CONDUCT.md).
- Keep the layering intact: generators know nothing about FHIR, mappers know
  nothing about the API. See [Architecture](docs/architecture.md).
- Do not use em dashes anywhere in the repository. Use a colon, a period, or a
  hyphen instead.
- `ruff check .` must be clean and the test suite must pass before you open a
  pull request.

## Development setup

```bash
git clone https://github.com/Thijsn04/SynthFHIR.git
cd SynthFHIR
pip install -e ".[dev]"
```

Common tasks are wrapped in the Makefile:

```bash
make serve       # run the API with reload
make test        # run the test suite
make lint        # run ruff
make check       # lint and test
make format      # auto-fix lint issues
```

## Making a change

1. Create a branch from `main`.
2. Make your change with tests.
3. Run `make check`.
4. If you drive a runtime change, exercise it end to end, for example:
   ```bash
   synthfhir generate --count 5 --seed 1 | synthfhir validate -
   ```
5. Open a pull request that fills in the template and explains the change.

## Adding clinical content

Adding a condition or an observation is usually a single edit in `data/`. See
[Catalogs](docs/catalogs.md). The catalog tests check that every observation key
referenced by a condition exists, so run the tests after your edit.

## Adding a resource type

Adding a whole new resource type touches four places: a generator, optional
catalog data, R4 and R5 mappers, and the wiring in `generators/cohort_gen.py`
and `mappers/pipeline.py`. See the step-by-step list in
[Architecture](docs/architecture.md).

## Tests

The suite is organized by layer:

```
tests/test_generators.py            generator output shape and field correctness
tests/test_mappers.py               FHIR resource structure and coding
tests/test_api.py                   HTTP endpoints and bundle structure
tests/test_validation.py            the bundle validator
tests/test_public_api.py            library, CLI, POST endpoint, determinism
tests/test_referential_integrity.py cross-resource reference resolution
```

New behavior should come with a test. Reproducibility-sensitive changes should
keep the concurrency and byte-reproducibility tests green.

## Style

- Python 3.11+ with type hints.
- Follow the conventions of the surrounding code.
- Keep comments purposeful and match the density of nearby code.
- Docstrings on public functions and modules.

## Reporting bugs

Open an issue with the steps to reproduce. If the bug is about generated data,
include the exact request and a `seed` so the output is reproducible.

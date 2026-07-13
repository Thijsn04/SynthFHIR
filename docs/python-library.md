# Python library

SynthFHIR exposes a small, stable public API through the top-level `synthfhir`
module. It is a thin facade over the `generators`, `mappers`, and `validation`
packages, so downstream code has one import to learn.

```python
import synthfhir
```

## Generate a bundle

```python
bundle = synthfhir.generate_cohort_bundle(
    count=10,
    version="R4",
    age_min=0,
    age_max=80,
    condition="type2_diabetes",
    years=3,
    num_practitioners=3,
    num_organizations=1,
    profile="us-core",
    bundle_type="collection",
    seed=42,
)
```

The return value is a plain `dict` ready to serialize with `json.dumps`.

## Generate NDJSON

```python
ndjson = synthfhir.generate_cohort_ndjson(count=100, seed=1)
with open("cohort.ndjson", "w") as fh:
    fh.write(ndjson)
```

## Validate

```python
report = synthfhir.validate_bundle(bundle)
if not report.valid:
    for issue in report.errors:
        print(issue.path, issue.message)
```

`validate_bundle` returns a `ValidationReport` with `valid`, `resource_count`,
`errors`, `warnings`, and `to_dict()`. See [Validation](validation.md).

## Work with the raw cohort

If you want the version-agnostic data before mapping, for example to write your
own exporter:

```python
raw = synthfhir.generate_raw_cohort(count=5, seed=1)
patients = raw["patients"]          # list of plain dicts
conditions = raw["conditions"]
```

You can then map the raw cohort yourself:

```python
from mappers.pipeline import map_cohort, build_bundle_from_cohort

resources = map_cohort(raw, "R5", us_core=True)     # ordered list of resources
bundle = build_bundle_from_cohort(raw, "R5", bundle_type="transaction")
```

## Catalogs

```python
for c in synthfhir.CONDITIONS:
    print(c.key, c.display, c.snomed_code, c.icd10_code)

for key, obs in synthfhir.OBSERVATIONS.items():
    print(key, obs.loinc_code, obs.unit)
```

## Reproducibility

Passing `seed` makes the output byte-reproducible for that seed within a given
day. See [Reproducibility](reproducibility.md) for the exact guarantee and the
concurrency model. If you call the lower-level `seed_all`, note that all
public generation functions already manage seeding for you.

## Public API surface

| Name | Description |
|---|---|
| `generate_cohort_bundle(...)` | Full cohort as a FHIR Bundle dict |
| `generate_cohort_ndjson(...)` | Full cohort as an NDJSON string |
| `generate_raw_cohort(...)` | Version-agnostic cohort dict |
| `validate_bundle(bundle)` | Validate a bundle, returns `ValidationReport` |
| `CONDITIONS` | The condition catalog |
| `OBSERVATIONS` | The observation catalog |
| `__version__` | Package version string |

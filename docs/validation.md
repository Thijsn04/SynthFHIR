# Validation

SynthFHIR includes a fast, dependency-free validator for FHIR Bundles. It is not
a full StructureDefinition engine. It catches the mistakes that matter most for
synthetic data and runs in milliseconds, so it is safe to call on every bundle
and in CI.

## Using it

From the API:

```bash
curl -X POST "http://localhost:8000/api/validate" \
     -H "Content-Type: application/json" \
     --data-binary @cohort.json
```

From the CLI (exit code 0 when valid, 1 when not):

```bash
synthfhir validate cohort.json
synthfhir validate cohort.json --json
```

From Python:

```python
from validation import validate_bundle

report = validate_bundle(bundle)
print(report.valid, report.resource_count)
for issue in report.errors:
    print(issue.path, issue.message)
```

## What it checks

Errors (make a bundle invalid):

- The top-level resource is a `Bundle` with an `entry` array.
- Every entry carries a `resource` with a `resourceType`.
- `fullUrl` values are unique across the bundle.
- Transaction bundles carry `entry.request.method` and `entry.request.url`.
- Each resource has the base-FHIR mandatory elements for its type (for example,
  `Observation` requires `status` and `code`).
- Every internal reference (`urn:uuid:...` or `ResourceType/id`) resolves to a
  resource in the bundle. External `http(s)` references and contained `#`
  references are ignored.

Warnings (do not fail the bundle):

- A resource has no `id`.
- The bundle has no `type`.

## The report

`validate_bundle` returns a `ValidationReport`:

| Field | Description |
|---|---|
| `valid` | True when there are no errors |
| `resource_count` | Number of resources in the bundle |
| `errors` | List of `Issue(severity, path, message)` |
| `warnings` | List of `Issue(severity, path, message)` |
| `to_dict()` | JSON-serializable summary |

## Scope and limits

The built-in validator does not check value sets, cardinality beyond the curated
mandatory set, profile slicing, or terminology bindings. It is a fast,
dependency-free guardrail, not a certification.

## Strict conformance testing

For real conformance, the test suite validates every generated resource against
the actual FHIR StructureDefinitions using the
[fhir.resources](https://pypi.org/project/fhir.resources/) models (R4B for R4
output, R5 for R5 output). This catches cardinality, datatype, and structural
errors that the lightweight validator does not.

```bash
pip install -e ".[dev]"
pytest tests/test_conformance.py -v
```

The suite validates base and US Core cohorts, both FHIR versions, and
transaction bundles, and runs in CI, so a change that breaks spec conformance
fails the build. Every one of the 48 resource types passes strict validation in
both R4 and R5.

For certification against a specific Implementation Guide (US Core slicing,
value-set bindings, invariants), run the output through the official HL7 FHIR
validator as well.

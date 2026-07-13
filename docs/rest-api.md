# REST API reference

Base URL when running locally: `http://localhost:8000`

All generation endpoints live under the `/api` prefix. Interactive
documentation is available at `/docs` (Swagger UI) and `/redoc`, and the
machine-readable OpenAPI schema is at `/openapi.json`.

## Conventions

- Media types: FHIR JSON is returned as `application/json`; NDJSON streams as
  `application/fhir+ndjson`.
- References: every resource id is a UUID, and references use the
  `urn:uuid:<id>` form so they resolve against the Bundle `fullUrl` entries.
- Errors: invalid input returns HTTP 422 with a JSON `detail` field.

## System endpoints

### `GET /health`

Liveness probe. Returns `{"status": "ok", "service": "synthfhir", "version": ...}`.

### `GET /api`

A machine-readable index of the primary endpoints.

## Generate

### `GET /api/generate/cohort`

Generate a complete, interconnected clinical cohort.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1 to 1000) | 10 | Number of patients |
| `version` | `R4` or `R5` | `R4` | FHIR version |
| `age_min` | int (0 to 119) | 0 | Minimum patient age |
| `age_max` | int (1 to 120) | 80 | Maximum patient age |
| `condition` | string | none | Condition key or partial name every patient receives |
| `seed` | int | none | Seed for reproducible output |
| `num_practitioners` | int (1 to 50) | 3 | Practitioner pool size |
| `num_organizations` | int (1 to 10) | 1 | Organization pool size |
| `years` | int (1 to 20) | 2 | Years of clinical history per patient |
| `bundle_type` | `collection` or `transaction` | `collection` | `transaction` adds `entry.request` for server ingestion |
| `format` | `bundle` or `ndjson` | `bundle` | `ndjson` streams one resource per line |
| `profile` | `base` or `us-core` | `base` | `us-core` adds race, ethnicity, and birth-sex extensions |

Example:

```bash
curl "http://localhost:8000/api/generate/cohort?count=5&condition=copd&years=5&profile=us-core"
```

### `POST /api/generate/cohort`

The same generation as the GET endpoint, driven by a JSON body. This is more
convenient for complex or scripted requests. The body fields match the query
parameters.

```bash
curl -X POST "http://localhost:8000/api/generate/cohort" \
  -H "Content-Type: application/json" \
  -d '{"count": 20, "condition": "ckd", "years": 6, "seed": 7, "profile": "us-core"}'
```

### `GET /api/generate/patient`

Generate standalone Patient resources with no linked clinical data.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1 to 100) | 1 | Number of patients |
| `version` | `R4` or `R5` | `R4` | FHIR version |
| `age_min` | int (0 to 119) | 0 | Minimum age |
| `age_max` | int (1 to 120) | 100 | Maximum age |
| `seed` | int | none | Seed |
| `bundle_type` | `collection` or `transaction` | `collection` | Bundle type |
| `profile` | `base` or `us-core` | `base` | US Core extensions |

### `GET /api/generate/practitioner`

Generate standalone Practitioner resources.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1 to 100) | 1 | Number of practitioners |
| `version` | `R4` or `R5` | `R4` | FHIR version |
| `seed` | int | none | Seed |
| `bundle_type` | `collection` or `transaction` | `collection` | Bundle type |

### `GET /api/generate/organization`

Generate standalone Organization resources.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1 to 50) | 1 | Number of organizations |
| `version` | `R4` or `R5` | `R4` | FHIR version |
| `seed` | int | none | Seed |
| `bundle_type` | `collection` or `transaction` | `collection` | Bundle type |

## Validation

### `POST /api/validate`

Validate a FHIR Bundle. The request body is the Bundle JSON. The response is a
report with `valid`, `resource_count`, `error_count`, `warning_count`,
`errors`, and `warnings`. The bundle is never stored. See
[Validation](validation.md) for the checks performed.

```bash
curl "http://localhost:8000/api/generate/cohort?count=3&seed=1" \
  | curl -s -X POST "http://localhost:8000/api/validate" \
         -H "Content-Type: application/json" --data-binary @-
```

## Catalog

### `GET /api/conditions`

Returns every available condition key with its SNOMED and ICD-10 codes, typical
minimum age, and linked observation types.

### `GET /api/observations`

Returns every supported observation type with LOINC code, UCUM unit, category,
and normal and abnormal ranges.

## Conformance

### `GET /api/metadata`

Returns a FHIR CapabilityStatement describing the supported resource types, the
FHIR version, and the US Core profile URLs. Follows the FHIR REST conformance
pattern. Accepts a `version` query parameter (`R4` or `R5`).

## Interactive documentation

Swagger UI at `/docs` lets you call every endpoint from the browser and shows
the request and response schemas generated from the code.

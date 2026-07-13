# Changelog

All notable changes to this project are documented here. The format is based on
Keep a Changelog, and this project adheres to semantic versioning.

## [0.3.0]

### Added

- A production web console served by the API at `/`: configure, generate,
  preview, inspect, and download datasets. Light and dark themes, responsive,
  and accessible. Replaces the previous single-file test UI.
- A dependency-free FHIR Bundle validator (structure, id and reference
  integrity, base-FHIR mandatory elements), exposed as `POST /api/validate`, a
  `synthfhir validate` command, and `synthfhir.validate_bundle`.
- A `synthfhir` command-line tool: `generate`, `validate`, `conditions`,
  `observations`, and `serve`.
- A Python library facade (`synthfhir` module) with `generate_cohort_bundle`,
  `generate_cohort_ndjson`, and `generate_raw_cohort`.
- `POST /api/generate/cohort` accepting a JSON generation spec.
- `GET /health` liveness endpoint and a machine-readable `GET /api` index.
- Packaging: console entry point, full project metadata, Docker image with a
  non-root user and healthcheck, `docker-compose.yml`, and a `Makefile`.
- Comprehensive documentation under `docs/`, plus contributing, code of
  conduct, and security policy files.

### Changed

- Mapper version dispatch and resource ordering moved into
  `mappers/pipeline.py`, shared by the API, CLI, and library.
- The version is 0.3.0 across the app, library, and CapabilityStatement.

### Fixed

- Seeded output is now reproducible under concurrent generation. All generation
  runs inside a serialized scope, and cohort bundling happens inside the same
  scope so the bundle id draw cannot corrupt another request's sequence.
- Encounter datetimes are anchored to the date, so the time of day comes from
  the seeded RNG rather than the wall clock.
- Record-keeping timestamps are frozen to a deterministic instant when a seed is
  given, making seeded output byte-reproducible.
- Removed all em dashes from the repository.

## [0.2.0]

- Expanded resource coverage to 25 FHIR resource types across R4 and R5, US Core
  profiles, NDJSON streaming, transaction bundles, and a comorbidity-aware
  clinical timeline.

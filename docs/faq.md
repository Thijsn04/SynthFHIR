# FAQ

## Is the data real?

No. Every record is fabricated by rules and random draws. It does not describe
real people and must not be used clinically.

## Which FHIR versions are supported?

R4 (4.0.1) and R5 (5.0.0). Choose with the `version` parameter.

## Does it need an internet connection?

No. SynthFHIR runs entirely locally and contacts no external services.

## How do I get the same data twice?

Pass a `seed`. The output is byte-reproducible for that seed within a day. See
[Reproducibility](reproducibility.md).

## How do I load the output into a FHIR server?

Generate a transaction bundle and POST it:

```bash
curl "http://localhost:8000/api/generate/cohort?count=10&bundle_type=transaction" \
  | curl -X POST "http://your-fhir-server/fhir" \
         -H "Content-Type: application/fhir+json" --data-binary @-
```

Transaction bundles include `entry.request` so a FHIR server can ingest them
atomically, and references use `urn:uuid:` so they resolve during ingestion.

## How do I generate very large datasets?

Use `format=ndjson` so the response streams one resource per line instead of
buffering a single large document. The CLI writes NDJSON straight to a file:

```bash
synthfhir generate --count 1000 --format ndjson -o cohort.ndjson
```

## Is the output US Core conformant?

Add `profile=us-core` to attach US Core profiles and the Patient race,
ethnicity, and birth-sex extensions. The built-in validator checks structure and
references; for strict US Core conformance run the output through the official
HL7 validator. See [Validation](validation.md).

## Can I add my own conditions or labs?

Yes, and it takes one edit. See [Catalogs](catalogs.md).

## How do I use it from another language?

Call the REST API. Any HTTP client works, and the OpenAPI schema at
`/openapi.json` lets you generate a typed client.

## What is the difference between the cohort and patient endpoints?

`/api/generate/cohort` produces a full relational dataset. The
`/api/generate/patient`, `/practitioner`, and `/organization` endpoints produce
standalone resources with no linked clinical data, which is useful when you only
need one resource type.

## How is randomness handled across concurrent requests?

Generation is serialized per process so concurrent seeded requests cannot
corrupt each other's random sequence. See [Reproducibility](reproducibility.md).

## Where do I report a bug or request a feature?

Open an issue on GitHub. See the [contributing guide](../CONTRIBUTING.md).

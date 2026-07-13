# Reproducibility

SynthFHIR is built to produce the same data given the same inputs. This matters
for CI pipelines, regression tests, demos, and bug reports.

## The guarantee

When you pass a `seed`, the output is byte-for-byte identical across runs on the
same day, including record-keeping timestamps. Without a seed, output is random
on every call.

```python
import json, synthfhir

a = synthfhir.generate_cohort_bundle(count=10, seed=42)
b = synthfhir.generate_cohort_bundle(count=10, seed=42)
assert json.dumps(a) == json.dumps(b)
```

The same holds through the REST API and the CLI:

```bash
curl "http://localhost:8000/api/generate/cohort?count=10&seed=42" > a.json
curl "http://localhost:8000/api/generate/cohort?count=10&seed=42" > b.json
diff a.json b.json    # no output
```

## Why "within a day"

Clinical dates are generated relative to the current date (for example, an
encounter three months ago). That reference date advances at midnight UTC, so a
seeded run today and the same seeded run tomorrow differ by one day in their
dates. Everything else, including the sequence of random draws, is identical.

Record-keeping timestamps (`meta.lastUpdated`, `Bundle.timestamp`, and FHIR
recording instants) are frozen to the current date at midnight UTC when a seed
is given, so they do not introduce sub-second differences. Without a seed, these
reflect the real wall-clock time.

## How it works

All randomness flows through `generators/_rng.py`. UUIDs are derived from the
seeded random stream rather than the system UUID generator, so ids are
reproducible too.

A generation runs inside `generation_scope(seed)`, which:

1. Acquires a process-wide lock so concurrent generations cannot interleave
   their RNG draws.
2. Seeds the random and Faker generators.
3. Freezes the generation clock to a deterministic instant.

Because the mapping and bundling for a cohort happen inside the same scope, even
the Bundle id (which is drawn from the seeded stream) is reproducible.

## Concurrency

The global random state is shared across the process. Two concurrent seeded
requests would corrupt each other's sequence if they ran at the same time, so
`generation_scope()` serializes generation with a lock. Generation is CPU bound
and already serialized by the GIL, so the throughput cost is negligible while
determinism is guaranteed. This behavior is covered by a concurrency test that
runs many seeded generations in parallel and asserts they are identical.

## What is not seeded

- Two runs on different days differ in their clinical dates by the day offset.
- Unseeded runs are intentionally random.

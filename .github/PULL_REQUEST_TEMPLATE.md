## What does this PR do?

<!-- One-sentence summary. -->

## Type of change

- [ ] Bug fix
- [ ] New resource type
- [ ] New condition / observation / catalog entry
- [ ] API parameter or output format
- [ ] Refactor / test / docs

## Checklist

- [ ] `ruff check .` passes
- [ ] `pytest tests/ -v` passes (all 82+ tests green)
- [ ] New generator returns a plain dict (no FHIR knowledge)
- [ ] New mapper handles both R4 and R5 if resource type is version-sensitive
- [ ] FHIR codes are real (SNOMED, LOINC, RxNorm, CVX, ICD-10 as appropriate)
- [ ] UTC-aware datetimes (`datetime.now(UTC)`, not `datetime.utcnow()`)

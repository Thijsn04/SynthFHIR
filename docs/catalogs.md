# Catalogs

The clinical code sets live in `data/` as typed dataclasses. They are the fixed
vocabulary the generators draw from. This page explains each catalog and how to
extend it. Adding to a catalog needs no changes elsewhere.

## Conditions

`data/conditions.py` holds 50 conditions spanning chronic disease, mental
health, acute and episodic illness, cancer, neurological, autoimmune, GI,
endocrine, infectious, respiratory, and cardiovascular categories.

Each `ConditionDef` maps a query-friendly key to codes and to the observation
types that are clinically ordered for it:

```python
ConditionDef(
    key="hypothyroidism",
    display="Hypothyroidism",
    snomed_code="40930008",
    icd10_code="E03.9",
    linked_obs_types=("tsh", "body_weight"),   # observation keys
    typical_age_min=30,
)
```

`typical_age_min` prevents implausible diagnoses (for example atrial
fibrillation in a small child). The `condition` query parameter accepts the
exact key or a partial case-insensitive match against the key or display name,
so `diabetes` matches `type2_diabetes`.

List them all:

```bash
curl http://localhost:8000/api/conditions
synthfhir conditions
```

## Observations

`data/observations.py` holds 26 observation types across three categories:
vital signs, laboratory, and survey. Each `ObservationDef` carries a LOINC code,
a UCUM unit, normal and abnormal ranges, thresholds, and decimal precision.

```python
ObservationDef(
    key="tsh",
    loinc_code="3016-3",
    display="Thyrotropin [Units/volume] in Serum or Plasma",
    category_code="laboratory",
    category_display="Laboratory",
    unit="mIU/L",
    ucum_code="m[IU]/L",
    normal_range=(0.4, 4.0),
    abnormal_range=(4.5, 20.0),
    low_threshold=0.4,
    high_threshold=4.0,
    decimal_places=2,
)
```

The `normal_range` also populates `referenceRange` in the mapped resource, and
an interpretation flag is emitted only when a value falls outside it.

List them all:

```bash
curl http://localhost:8000/api/observations
synthfhir observations
```

## Medications, immunizations, procedures

- `data/medications.py`: RxNorm-coded medications keyed by the condition they
  treat, with dosage details.
- `data/immunizations.py`: CVX-coded vaccines with age eligibility and
  prevalence weighting.
- `data/procedures.py`: SNOMED-coded procedures keyed by condition.

## Extending a catalog

### Add a condition

Add a `ConditionDef` to the `CONDITIONS` list in `data/conditions.py`. It is
immediately available via `?condition=<key>` and appears in
`GET /api/conditions`. If it references observation keys that do not exist yet,
add those too.

### Add an observation

Add an `ObservationDef` in `data/observations.py`. It is generated automatically
for any encounter where the patient has an active condition that lists the key
in `linked_obs_types`.

### Verify your change

```bash
ruff check .
pytest tests/ -v
synthfhir generate --count 5 --condition <your_key> --seed 1 | synthfhir validate -
```

The catalog tests assert that every observation key referenced by a condition
exists, so a typo is caught immediately.

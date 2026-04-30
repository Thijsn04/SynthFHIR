# SynthFHIR

A free, open-source, locally-hosted synthetic FHIR patient data generator. Produces fully relational clinical datasets with realistic, interconnected records: patients, practitioners, organizations, conditions, allergies, encounters, observations, and family members, all perfectly linked by ID.

Built with [Faker](https://faker.readthedocs.io/). No external APIs. No paid services. Runs entirely on your machine.

Supports **FHIR R4** and **FHIR R5**.

---

## Quick start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

```bash
# Generate 5 diabetes patients as an R4 Bundle
curl "http://localhost:8000/api/generate/cohort?count=5&condition=diabetes&version=R4"

# Reproducible output: same seed always returns the same data
curl "http://localhost:8000/api/generate/cohort?count=10&seed=42"

# List all available condition keys
curl "http://localhost:8000/api/conditions"
```

Interactive docs (Swagger UI): `http://localhost:8000/docs`
Test UI: open `test_ui.html` in a browser.

---

## What gets generated

A single `/api/generate/cohort` call returns a FHIR Bundle containing:

| Resource | Notes |
|---|---|
| `Patient` | Demographics, MRN, contact info, language preference |
| `Practitioner` | NPI, SNOMED specialty, HL7 qualification |
| `Organization` | Facility name, type, contact details |
| `Condition` | SNOMED + ICD-10 codes, clinical status, 40% comorbidity chance |
| `AllergyIntolerance` | SNOMED substance + reaction codes, 30% of patients affected |
| `RelatedPerson` | Parents for minors, spouses for married adults, emergency contacts |
| `Encounter` | Distributed across a 2-year window, linked to practitioner + org |
| `Observation` | Baseline vitals every encounter; condition-linked labs with abnormal values for active conditions |

All resources reference each other by FHIR ID. A Patient's encounters point back to the Patient, the Practitioner, and the Organization.

---

## API reference

### Generate

#### `GET /api/generate/cohort`

Generates a complete, interconnected clinical cohort.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1–1000) | 10 | Number of patients |
| `version` | `R4` \| `R5` | `R4` | FHIR version |
| `age_min` | int (0–119) | 0 | Minimum patient age |
| `age_max` | int (1–120) | 80 | Maximum patient age |
| `condition` | string | optional | Filter by condition key or partial name (e.g. `diabetes`, `hypertension`) |
| `seed` | int | optional | RNG seed for reproducible output |
| `num_practitioners` | int (1–50) | 3 | Number of practitioners |
| `num_organizations` | int (1–10) | 1 | Number of organizations |

#### `GET /api/generate/patient`

Generates lightweight Patient resources with no linked clinical data.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1–100) | 1 | Number of patients |
| `version` | `R4` \| `R5` | `R4` | FHIR version |
| `age_min` | int (0–119) | 0 | Minimum age |
| `age_max` | int (1–120) | 100 | Maximum age |
| `seed` | int | optional | RNG seed for reproducible output |

### Catalog

#### `GET /api/conditions`
Returns all available condition keys with SNOMED and ICD-10 codes and their linked observation types.

#### `GET /api/observations`
Returns all supported observation types with LOINC codes, UCUM units, and normal/abnormal ranges.

---

## Built-in condition keys

| Key | Display |
|---|---|
| `type2_diabetes` | Type 2 Diabetes Mellitus |
| `hypertension` | Essential Hypertension |
| `asthma` | Asthma |
| `ckd` | Chronic Kidney Disease |
| `hyperlipidemia` | Hyperlipidemia |
| `depression` | Major Depressive Disorder |
| `osteoarthritis` | Osteoarthritis |
| `copd` | Chronic Obstructive Pulmonary Disease |
| `atrial_fibrillation` | Atrial Fibrillation |
| `obesity` | Obesity |

The `condition` query parameter accepts either the key exactly or a partial case-insensitive match against the key or display name (`"diabetes"` matches `type2_diabetes`).

---

## Project structure

```
SynthFHIR/
├── main.py                      # FastAPI app, CORS middleware
├── api/
│   └── routes.py                # All endpoints + mapper dispatch tables
├── generators/                  # Raw data producers (version-agnostic dicts)
│   ├── cohort_gen.py            # Orchestrates the full dependency-ordered pipeline
│   ├── patient_gen.py
│   ├── practitioner_gen.py
│   ├── organization_gen.py
│   ├── condition_gen.py
│   ├── allergy_gen.py
│   ├── encounter_gen.py
│   ├── observation_gen.py
│   └── related_person_gen.py
├── mappers/
│   ├── _helpers.py              # Shared FHIR building-block functions
│   ├── r4/                      # FHIR R4 resource + Bundle mappers
│   └── r5/                      # FHIR R5 resource + Bundle mappers
├── data/
│   ├── conditions.py            # Condition catalog (SNOMED + ICD-10 + linked obs)
│   └── observations.py          # Observation catalog (LOINC + UCUM + value ranges)
└── test_ui.html                 # Browser-based test interface
```

The data flow is:
```
data/conditions.py  ──►  generators/*_gen.py  ──►  mappers/r4/ or r5/  ──►  FHIR Bundle
data/observations.py ──►
```

Generators produce plain Python dicts. Mappers convert those dicts into FHIR-conformant resource dicts. Nothing between the two layers knows about FHIR.

---

## Extending SynthFHIR

### Add a new condition

Edit [data/conditions.py](data/conditions.py). Add a new `ConditionDef` to the `CONDITIONS` list:

```python
ConditionDef(
    key="hypothyroidism",
    display="Hypothyroidism",
    snomed_code="40930008",
    icd10_code="E03.9",
    linked_obs_types=("tsh", "body_weight"),   # observation keys from data/observations.py
    typical_age_min=30,
),
```

That's it. The condition is immediately available via `?condition=hypothyroidism` and will show up in `GET /api/conditions`. If you reference observation keys that don't exist yet, add those too (see below).

### Add a new observation type

Edit [data/observations.py](data/observations.py). Add a new `ObservationDef` inside the `OBSERVATIONS` dict comprehension:

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
),
```

The observation will be generated automatically for any encounter where the patient has an active condition that lists this key in `linked_obs_types`.

### Add a new resource type

Adding a completely new resource type (e.g. `MedicationRequest`) requires four steps:

1. **Create a generator**: add `generators/medication_gen.py` following the pattern of any existing generator. Return a plain dict with all the raw fields you need.

2. **Add catalog data if needed**: if the resource has a fixed set of codes, add a dataclass catalog in `data/` following the `ConditionDef` / `ObservationDef` pattern.

3. **Create mappers**: add `mappers/r4/medication.py` and `mappers/r5/medication.py`. Import helpers from `mappers/_helpers.py` for shared FHIR primitives (references, addresses, meta, etc.).

4. **Wire it into the pipeline**:
   - In `generators/cohort_gen.py`: call your generator inside the patient loop and collect results.
   - In `api/routes.py`: import both mappers, add them to the dispatch tables (`_MED_MAPPER`), and map them inside `_map_and_bundle`.

---

## Requirements

- Python 3.9+
- See [requirements.txt](requirements.txt) — FastAPI, Uvicorn, Faker, Pydantic v2

---

## License

MIT. Free to use in any project, commercial or otherwise.

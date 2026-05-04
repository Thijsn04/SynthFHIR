# SynthFHIR

[![CI](https://github.com/Thijsn04/SynthFHIR/actions/workflows/ci.yml/badge.svg)](https://github.com/Thijsn04/SynthFHIR/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A free, open-source, locally-hosted synthetic FHIR patient data generator. Produces fully relational clinical datasets with realistic, interconnected records across **15 resource types**, all linked by ID and conformant to FHIR R4/R5 and US Core profiles.

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

# Stream as NDJSON (one resource per line)
curl "http://localhost:8000/api/generate/cohort?count=100&format=ndjson"

# US Core profile (adds race, ethnicity, birth sex extensions)
curl "http://localhost:8000/api/generate/cohort?count=5&profile=us-core"

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
| `Patient` | Demographics, MRN, contact info, language preference; US Core race/ethnicity/birth-sex extensions via `?profile=us-core` |
| `Practitioner` | NPI, SNOMED specialty, HL7 qualification |
| `Organization` | Facility name, type, contact details |
| `Coverage` | Insurance record per patient (Medicare 65+, Medicaid 15%, commercial otherwise); payer, subscriber ID, plan name, period |
| `Condition` | SNOMED + ICD-10 dual coding, clinical/verification status, 40% comorbidity chance, links back to diagnosing Encounter |
| `AllergyIntolerance` | SNOMED substance + reaction codes, type, category, criticality; 30% of patients affected |
| `Immunization` | CVX-coded, age-eligible vaccines with prevalence weighting; performer and lot number |
| `RelatedPerson` | Parents for minors, spouses for married adults, emergency contacts |
| `Encounter` | Distributed across a 2-year post-diagnosis window; `reasonCode` from active conditions; type, class, period with start + end |
| `Observation` | Baseline vitals every encounter (BP panel, HR, RR, temp, O2 sat, height, weight, BMI); condition-linked labs with abnormal values; `referenceRange` on all results; survey scores as `valueInteger` |
| `DiagnosticReport` | Groups lab Observations per encounter; issued date; performer |
| `MedicationRequest` | RxNorm coded; dosage instructions; `dispenseRequest` with quantity, supply days, and refills |
| `Procedure` | SNOMED-coded; physical exam every encounter plus condition-specific procedures (spirometry, ECG, joint injection, etc.); performer and body site |
| `ServiceRequest` | Lab orders, imaging, referrals per encounter; priority; `reasonCode` from active conditions |

All resources reference each other by FHIR `urn:uuid:` IDs that match the Bundle `fullUrl` entries.

### Blood pressure

Blood pressure is generated as a **panel Observation** (LOINC `85354-9`) with systolic and diastolic as `component` entries — matching the US Core Blood Pressure Profile — rather than two separate Observations.

---

## FHIR compliance highlights

- Dual SNOMED CT + ICD-10-CM coding on `Condition`
- LOINC codes on all `Observation` resources; UCUM units throughout
- CVX codes on `Immunization`
- RxNorm codes on `MedicationRequest`
- `referenceRange` on all lab and vital Observations (derived from catalog normal ranges)
- Interpretation flags (`H`/`L`) only emitted when a value is outside the reference range
- US Core Blood Pressure Profile (`component`-based panel)
- `valueInteger` for survey scores (PHQ-9, GAD-7) — not `valueQuantity`
- Pulse oximetry uses LOINC `59408-5` (not the arterial blood gas code)
- US Core extensions for race, ethnicity, and birth sex via `?profile=us-core`
- Transaction bundles with `entry.request` via `?bundle_type=transaction`
- NDJSON streaming via `?format=ndjson`
- `Encounter.reasonCode` linked to active conditions
- `Condition.encounter` reference to the diagnosing visit
- `MedicationRequest.dispenseRequest` with refills and supply duration
- Temporal consistency: encounters always after condition onset; BMI always derived from weight + height

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
| `condition` | string | — | Filter by condition key or partial name (e.g. `diabetes`, `hypertension`) |
| `seed` | int | — | RNG seed for fully reproducible output |
| `num_practitioners` | int (1–50) | 3 | Number of practitioners in the pool |
| `num_organizations` | int (1–10) | 1 | Number of organizations in the pool |
| `bundle_type` | `collection` \| `transaction` | `collection` | `transaction` adds `entry.request` for direct server ingestion |
| `format` | `bundle` \| `ndjson` | `bundle` | `ndjson` streams one resource per line |
| `profile` | `base` \| `us-core` | `base` | `us-core` adds race, ethnicity, and birth-sex extensions to Patient |

#### `GET /api/generate/patient`

Generates lightweight Patient resources with no linked clinical data.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1–100) | 1 | Number of patients |
| `version` | `R4` \| `R5` | `R4` | FHIR version |
| `age_min` | int (0–119) | 0 | Minimum age |
| `age_max` | int (1–120) | 100 | Maximum age |
| `seed` | int | — | RNG seed |
| `bundle_type` | `collection` \| `transaction` | `collection` | Bundle type |
| `profile` | `base` \| `us-core` | `base` | US Core extensions |

#### `GET /api/generate/practitioner`

Generates standalone Practitioner resources.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1–100) | 1 | Number of practitioners |
| `version` | `R4` \| `R5` | `R4` | FHIR version |
| `seed` | int | — | RNG seed |
| `bundle_type` | `collection` \| `transaction` | `collection` | Bundle type |

#### `GET /api/generate/organization`

Generates standalone Organization resources.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `count` | int (1–50) | 1 | Number of organizations |
| `version` | `R4` \| `R5` | `R4` | FHIR version |
| `seed` | int | — | RNG seed |
| `bundle_type` | `collection` \| `transaction` | `collection` | Bundle type |

### Catalog

#### `GET /api/conditions`
Returns all available condition keys with SNOMED and ICD-10 codes and their linked observation types.

#### `GET /api/observations`
Returns all supported observation types with LOINC codes, UCUM units, and normal/abnormal ranges.

---

## Built-in condition keys

| Key | Display | Typical age min |
|---|---|---|
| `type2_diabetes` | Type 2 Diabetes Mellitus | 30 |
| `hypertension` | Essential Hypertension | 25 |
| `asthma` | Asthma | 5 |
| `ckd` | Chronic Kidney Disease | 40 |
| `hyperlipidemia` | Hyperlipidemia | 30 |
| `depression` | Major Depressive Disorder | 15 |
| `osteoarthritis` | Osteoarthritis | 45 |
| `copd` | Chronic Obstructive Pulmonary Disease | 40 |
| `atrial_fibrillation` | Atrial Fibrillation | 50 |
| `obesity` | Obesity | 18 |

The `condition` query parameter accepts the exact key or a partial case-insensitive match against the key or display name (`"diabetes"` matches `type2_diabetes`). Returns HTTP 422 with a list of valid keys on an unknown value.

---

## Project structure

```
SynthFHIR/
├── main.py                        # FastAPI app, CORS middleware
├── api/
│   └── routes.py                  # All endpoints + mapper dispatch tables
├── generators/                    # Raw data producers (version-agnostic dicts)
│   ├── cohort_gen.py              # Orchestrates the full dependency-ordered pipeline
│   ├── patient_gen.py
│   ├── practitioner_gen.py
│   ├── organization_gen.py
│   ├── condition_gen.py
│   ├── allergy_gen.py
│   ├── immunization_gen.py
│   ├── encounter_gen.py
│   ├── observation_gen.py
│   ├── diagnostic_report_gen.py
│   ├── medication_gen.py
│   ├── procedure_gen.py
│   ├── service_request_gen.py
│   ├── coverage_gen.py
│   ├── related_person_gen.py
│   └── _rng.py                    # Centralized RNG + seeding; reproducible UUIDs
├── mappers/
│   ├── _helpers.py                # Shared FHIR building-block functions
│   ├── r4/                        # FHIR R4 resource + Bundle mappers
│   │   ├── patient.py, practitioner.py, organization.py
│   │   ├── condition.py, allergy.py, immunization.py
│   │   ├── encounter.py, observation.py, diagnostic_report.py
│   │   ├── medication.py, procedure.py, service_request.py
│   │   ├── coverage.py, related_person.py, bundle.py
│   └── r5/                        # FHIR R5 resource + Bundle mappers (same set)
├── data/
│   ├── conditions.py              # Condition catalog (SNOMED + ICD-10 + linked obs)
│   ├── observations.py            # Observation catalog (LOINC + UCUM + value ranges)
│   ├── medications.py             # Medication catalog (RxNorm, by condition)
│   ├── immunizations.py           # Immunization catalog (CVX, age-eligible)
│   └── procedures.py              # Procedure catalog (SNOMED, by condition)
├── tests/
│   ├── test_generators.py
│   ├── test_mappers.py
│   └── test_api.py
└── test_ui.html                   # Browser-based test interface
```

The data flow is:
```
data/*.py  ──►  generators/*_gen.py  ──►  mappers/r4/ or r5/  ──►  FHIR Bundle / NDJSON
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

That's it. The condition is immediately available via `?condition=hypothyroidism` and will appear in `GET /api/conditions`. If you reference observation keys that don't exist yet, add those too (see below).

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

The observation will be generated automatically for any encounter where the patient has an active condition that lists this key in `linked_obs_types`. The `normal_range` is also used to populate `referenceRange` in the mapped FHIR resource.

### Add a new resource type

Adding a completely new resource type requires four steps:

1. **Create a generator** in `generators/` returning a plain dict with all raw fields needed.

2. **Add catalog data if needed** — fixed code sets go in `data/` following the `ConditionDef` / `MedicationDef` / `ProcedureDef` pattern.

3. **Create mappers** in `mappers/r4/` and `mappers/r5/`. Use helpers from `mappers/_helpers.py` for shared FHIR primitives (`ref()`, `build_meta()`, `build_address()`, etc.).

4. **Wire into the pipeline**:
   - `generators/cohort_gen.py`: import and call your generator; add results to the return dict.
   - `api/routes.py`: import both mappers, add to the dispatch table, and include in `_map_and_bundle` and `_ndjson_stream`.

---

## Requirements

- Python 3.11+
- See [requirements.txt](requirements.txt) — FastAPI, Uvicorn, Faker, Pydantic v2

---

## License

MIT. Free to use in any project, commercial or otherwise.

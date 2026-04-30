# SynthFHIR

A free, open-source, locally-hosted synthetic FHIR patient data generator. Produces fully relational clinical datasets with realistic, interconnected records — patients, practitioners, organizations, conditions, allergies, encounters, observations, and family members — all perfectly linked by ID. Built with [Faker](https://faker.readthedocs.io/); no external APIs or paid services required.

Supports both **FHIR R4** and **FHIR R5**.

## Features

- Generates complete FHIR Bundles with referential integrity across all resource types
- Condition-aware observations (e.g. diabetes patients get glucose labs)
- Reproducible output via optional RNG seed
- Condition and age filtering
- Built-in test UI (`test_ui.html`)
- Interactive Swagger docs at `/docs`

## Requirements

- Python 3.9+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload
```

The API is then available at `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Test UI: open `test_ui.html` in a browser

## API Endpoints

### Generate

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/generate/cohort` | Full relational cohort (patients + all linked resources) |
| GET | `/api/generate/patient` | Standalone Patient resources only |

#### `/api/generate/cohort` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int (1–1000) | 10 | Number of patients |
| `version` | "R4" \| "R5" | "R4" | FHIR version |
| `age_min` | int (0–119) | 0 | Minimum patient age |
| `age_max` | int (1–120) | 80 | Maximum patient age |
| `condition` | string | — | Filter by condition key (e.g. `diabetes`, `hypertension`) |
| `seed` | int | — | RNG seed for reproducible output |
| `num_practitioners` | int (1–50) | 3 | Number of practitioners |
| `num_organizations` | int (1–10) | 1 | Number of organizations |

#### `/api/generate/patient` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int (1–100) | 1 | Number of patients |
| `version` | "R4" \| "R5" | "R4" | FHIR version |
| `age_min` | int (0–119) | 0 | Minimum age |
| `age_max` | int (1–120) | 100 | Maximum age |
| `seed` | int | — | RNG seed for reproducible output |

### Catalog

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/conditions` | All available condition keys with SNOMED and ICD-10 codes |
| GET | `/api/observations` | All supported observation types with LOINC codes and units |

## Project Structure

```
SynthFHIR/
├── main.py                  # FastAPI app entry point
├── api/
│   └── routes.py            # API route definitions
├── generators/
│   ├── cohort_gen.py        # Orchestrates full relational dataset generation
│   ├── patient_gen.py
│   ├── practitioner_gen.py
│   ├── organization_gen.py
│   ├── condition_gen.py
│   ├── allergy_gen.py
│   ├── encounter_gen.py
│   ├── observation_gen.py
│   └── related_person_gen.py
├── mappers/
│   ├── r4/                  # FHIR R4 resource mappers
│   └── r5/                  # FHIR R5 resource mappers
├── data/
│   ├── conditions.py        # Condition catalog (SNOMED + ICD-10 codes)
│   └── observations.py      # Observation definitions (LOINC codes, ranges)
└── test_ui.html             # Browser-based test interface
```

## License

MIT

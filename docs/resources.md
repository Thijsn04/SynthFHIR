# FHIR resources

A cohort is a connected graph of 25 resource types across R4 and R5. Every
resource references others by `urn:uuid:` id. This page lists what is generated
and the terminology each resource carries.

## Coding systems used

| System | Used on |
|---|---|
| SNOMED CT | Condition, Procedure, AllergyIntolerance, Practitioner specialty |
| ICD-10-CM | Condition (dual coded with SNOMED) |
| LOINC | Observation, DiagnosticReport |
| UCUM | Observation units |
| RxNorm | MedicationRequest |
| CVX | Immunization |
| NPI | Practitioner, Organization identifiers |
| OMB race and ethnicity | US Core Patient extensions |

## Resource types

### People and organizations

- **Patient**: demographics, MRN, contact details, marital status, language.
  With `profile=us-core`, adds race, ethnicity, and birth-sex extensions.
- **Practitioner**: NPI identifier, SNOMED specialty, HL7 qualification.
- **PractitionerRole**: links a practitioner to an organization.
- **Organization**: a healthcare facility with type and contact details.
- **Location**: a physical place within an organization, linked to encounters.
- **RelatedPerson**: parents for minors, spouses for married adults, and
  emergency contacts.

### Clinical status

- **Condition**: dual SNOMED and ICD-10 coding, clinical and verification
  status, a link to the diagnosing encounter, and plausible comorbidities.
- **AllergyIntolerance**: SNOMED substance and reaction, type, category, and
  criticality.
- **Immunization**: CVX-coded, age-eligible vaccines with performer and lot.
- **FamilyMemberHistory**: relatives with hereditary conditions.

### Visits and coordination

- **Encounter**: clinic visits spread across the patient history window, with
  reasons drawn from active conditions and a class, type, and period.
- **Appointment**: scheduled shortly before its encounter.
- **EpisodeOfCare**: groups a patient's encounters.
- **CareTeam**: the practitioners managing a patient's conditions.
- **CarePlan**: links patient, care team, and conditions.
- **Goal**: a target per condition, linked to the care plan.
- **ServiceRequest**: lab orders, imaging, and referrals per encounter.

### Results and treatment

- **Observation**: vitals every encounter (blood pressure as a component panel,
  heart rate, respiratory rate, temperature, oxygen saturation, height, weight,
  BMI) and condition-linked labs, each with a `referenceRange` and an
  interpretation flag only when the value is out of range. Survey scores such as
  PHQ-9 and GAD-7 are emitted as `valueInteger`.
- **DiagnosticReport**: groups the lab observations of an encounter.
- **MedicationRequest**: RxNorm coded, with dosage instructions and a
  `dispenseRequest` carrying quantity, supply days, and refills.
- **Procedure**: SNOMED coded, a physical exam every encounter plus
  condition-specific procedures, with performer and body site.

### Records and administration

- **Coverage**: one insurance record per patient (Medicare for 65 and older,
  Medicaid for a share, commercial otherwise) with payer, subscriber id, and
  plan.
- **Consent**: HIPAA consent plus optional research consent.
- **List**: aggregates a patient's conditions, medications, and allergies.
- **Provenance**: an audit trail across a patient's conditions, encounters, and
  medications.

## Clinical realism highlights

- Every encounter happens after the earliest condition was recorded, so no visit
  precedes its diagnosis.
- Per-patient vital baselines keep values consistent across encounters, and BMI
  is always derived from the generated height and weight.
- Long timelines drift key labs (for example HbA1c or eGFR) and can add a
  second-line medication mid-timeline, reflecting treatment escalation.
- Blood pressure follows the US Core Blood Pressure Profile as a single panel
  observation with systolic and diastolic components.

## Profiles

With `profile=us-core`, resources carry the relevant US Core `meta.profile` and
the Patient gains race, ethnicity, and birth-sex extensions. The
`GET /api/metadata` CapabilityStatement lists the US Core profile URLs the
server advertises.

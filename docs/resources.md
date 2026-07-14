# FHIR resources

A cohort is a connected graph of up to 48 resource types across R4 and R5. Every
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
- **Specimen**: the sample a lab report was run on (blood, urine, and others).
- **ImagingStudy**: radiology studies at a share of encounters, with a DICOM
  modality, body site, and one series and instance.
- **QuestionnaireResponse**: each survey Observation (PHQ-9, GAD-7) as a
  structured response carrying the total score.
- **DocumentReference**: a clinical note per encounter (LOINC-typed, US Core
  clinical-note category) with the note text as a base64 attachment.
- **Composition**: a per-patient summary document with a problem-list section.
- **Procedure**: SNOMED coded, a physical exam every encounter plus
  condition-specific procedures, with performer and body site.

### Medications

- **Medication**: a cohort-wide catalog of the distinct drugs prescribed.
- **MedicationRequest**: RxNorm coded, with dosage instructions and a
  `dispenseRequest` carrying quantity, supply days, and refills.
- **MedicationDispense**: the pharmacy fill for most prescriptions, linked to its
  authorizing MedicationRequest with quantity, days supply, and handover date.
- **MedicationStatement**: a record that the patient is taking a medication.
- **MedicationAdministration**: a dose administered during care.

### Devices, safety, and assessment

- **Device**: implantable devices (cardiac devices, stents, joint prostheses)
  with a UDI, modeled after US Core Implantable Device.
- **BodyStructure**: anatomical sites for musculoskeletal conditions.
- **Flag**: clinical alerts such as anticoagulation or controlled-substance
  monitoring.
- **RiskAssessment**: a cardiovascular risk prediction scaled by risk factors.
- **ClinicalImpression**: a per-encounter assessment referencing active problems.

### Financial

- **Account**: a billing account per patient.
- **Claim**: a professional claim per encounter with a CPT-style service line.
- **ExplanationOfBenefit**: payer adjudication per claim (submitted, benefit, and
  patient responsibility).

### Workflow and scheduling

- **Task**: fulfilled workflow actions such as referrals and follow-ups.
- **NutritionOrder**: diet orders for diet-relevant conditions.
- **Communication**: patient messages such as reminders and notifications.
- **Schedule** and **Slot**: a bookable scheduling surface per practitioner.
- **Group**: a cohort-level enumeration of all patients.

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

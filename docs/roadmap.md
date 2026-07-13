# Roadmap: expanding resource coverage

SynthFHIR currently generates 27 FHIR resource types. FHIR defines roughly 150,
so there is room to grow. This page records which resource types are worth adding
next and why, so contributors can pick them up. Priorities are driven by two
questions: does US Core require it, and does it appear often in real datasets.

Each addition follows the same four-step pattern (generator, optional catalog
data, R4 and R5 mappers, pipeline wiring). See [Architecture](architecture.md).

## Recently added

- **DocumentReference**: a clinical note per encounter. US Core mandatory.
- **MedicationDispense**: pharmacy fills for prescriptions. US Core v6.

## High priority

These close US Core gaps and appear in almost every real dataset.

| Resource | Why | Notes |
|---|---|---|
| **Specimen** | Referenced by lab Observations and DiagnosticReports | Blood, urine, swab; link from existing lab results |
| **Medication** | US Core lets MedicationRequest reference a Medication resource | Promote the inline RxNorm coding to a standalone resource |
| **MedicationStatement** | Patient-reported medication use, distinct from prescriptions | Reuse the medication catalog |
| **Device** and **Implantable Device** | US Core Implantable Device profile | Pacemakers, stents, joint prostheses; link to Procedure |
| **QuestionnaireResponse** | Model PHQ-9 and GAD-7 as structured responses | Pairs with the survey Observations already generated |
| **ImagingStudy** | Radiology results | Link to the imaging ServiceRequests already generated |

## Medium priority

Common in claims, scheduling, and workflow data.

| Resource | Why |
|---|---|
| **Claim**, **ClaimResponse**, **ExplanationOfBenefit** | Payer and CARIN Blue Button style datasets; pair with the existing Coverage |
| **Schedule** and **Slot** | Complete the scheduling story around Appointment |
| **Task** | Workflow and referrals management |
| **Flag** | Patient alerts (allergy, fall risk) |
| **NutritionOrder** | Diet orders during encounters |
| **Communication** | Messages between patients and providers |
| **RiskAssessment** | Predicted risk scores tied to conditions |

## Lower priority or specialized

| Resource | Why |
|---|---|
| **BodyStructure** | Anatomical detail for procedures and imaging |
| **Media** | Photos and scanned documents |
| **MolecularSequence** | Genomics use cases |
| **Group** | Cohort membership as a first-class resource |
| **Composition** plus a document Bundle | Produce a FHIR Document (for example an IPS-style summary) |
| **Basic** | Escape hatch for concepts without a dedicated resource |

## Cross-cutting realism work

Beyond new resource types, these deepen the realism of what already exists:

- **Age and sex calibrated prevalence**: weight condition assignment by real
  epidemiology (partly in place through the comorbidity graph and sex
  restrictions; extend with prevalence tables).
- **Disease progression modules**: Synthea-style state machines so conditions
  evolve over the timeline (for example diabetes to nephropathy).
- **Geographic realism**: expand `data/geography.py`, and tie clinical dates to
  the locality timezone.
- **Provider panels and networks**: model realistic practitioner specialties and
  referral patterns.
- **Mortality modeling**: cause-of-death consistent with the patient's conditions.

## How to propose an addition

Open an issue describing the resource, the profile it should follow, and the
references it needs. If you want to implement it, follow the four-step pattern in
[Architecture](architecture.md) and add mapper tests plus a validation entry.

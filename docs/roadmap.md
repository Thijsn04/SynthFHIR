# Roadmap: expanding resource coverage

SynthFHIR currently generates 27 FHIR resource types. FHIR defines roughly 150,
so there is room to grow. This page records which resource types are worth adding
next and why, so contributors can pick them up. Priorities are driven by two
questions: does US Core require it, and does it appear often in real datasets.

Each addition follows the same four-step pattern (generator, optional catalog
data, R4 and R5 mappers, pipeline wiring). See [Architecture](architecture.md).

## Recently added (48 resource types total)

Across several releases SynthFHIR grew from 27 to 48 resource types: Specimen,
ImagingStudy, QuestionnaireResponse, DocumentReference, Composition, Medication,
MedicationDispense, MedicationStatement, MedicationAdministration, Device,
BodyStructure, Flag, RiskAssessment, ClinicalImpression, Account, Claim,
ExplanationOfBenefit, Task, NutritionOrder, Communication, Schedule, Slot, and
Group, each in R4 and R5.

## Candidate additions

Clinically relevant resource types not yet generated, in rough priority order:

| Resource | Why |
|---|---|
| **ClaimResponse** | Complete the claim/adjudication pair alongside ExplanationOfBenefit |
| **CommunicationRequest** | The order that precedes a Communication |
| **DeviceRequest** and **DeviceUsage** | Ordering and use of the devices already modeled |
| **AppointmentResponse** | Responses to the Appointments already generated |
| **ImmunizationRecommendation** | Forecast alongside the Immunizations |
| **VisionPrescription** | Optometry orders |
| **SupplyRequest** and **SupplyDelivery** | Durable medical equipment |
| **AdverseEvent** | Safety events tied to medications or procedures |
| **Media** | Photos and scanned documents (folded into DocumentReference in R5) |
| **MolecularSequence** | Genomics use cases |
| **ChargeItem** and **Invoice** | Finer-grained billing |

## Out of scope

FHIR also defines many infrastructure and conformance resources that are not
patient data and are intentionally not generated: CapabilityStatement (the
server does emit its own at `/api/metadata`), StructureDefinition, ValueSet,
CodeSystem, ConceptMap, SearchParameter, OperationDefinition, Subscription,
MessageHeader, Parameters, Binary, and similar. A synthetic patient-data
generator populates clinical and administrative resources, not the terminology
and conformance layer.

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

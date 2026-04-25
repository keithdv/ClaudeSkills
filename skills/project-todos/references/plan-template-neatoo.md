# Plan Template — Neatoo / zTreatment Domain Model Section

Append this block to the plan-template's "Domain Model Behavioral Design" section when the active project uses Neatoo. The base template stays framework-agnostic; these tables are specific to how Neatoo expects behavioral logic to be designed.

The premise: the domain model is the ViewModel for UI pages. Every behavioral property the UI needs is designed here. Razor pages bind to these properties and do not implement business logic.

## Computed Properties

| Property | Type | Computes | Triggered By |
|----------|------|----------|-------------|
| [e.g., FullName] | [string] | [FirstName + " " + LastName] | [FirstName, LastName] |

## Visibility / Conditional Flags

| Property | Condition | Depends On |
|----------|-----------|------------|
| [e.g., ShowDeclineReason] | [CareStatus == ConsultationDeclined] | [CareStatus] |

## Reactive Rules

| Rule | Trigger | Affected Property | Behavior |
|------|---------|-------------------|----------|
| [e.g., Auto-set consultation date] | [CareStatus -> Consultation] | [ConsultationDate] | [Set to today if null] |

## Classification Properties

| Property | Type | Logic |
|----------|------|-------|
| [e.g., IsPatient] | [bool] | [CareStatus >= InitialCare] |

## Validation Rules

| Rule | Trigger Properties | Error Message |
|------|-------------------|---------------|
| [e.g., DeclineReason required] | [CareStatus, DeclineReason] | [Decline reason is required when consultation is declined] |

# Plan Template — Neatoo Domain Model Section

Optional appendix to the iterative-todo `plan-template.md`. Append this block to a plan's **Framework & Architectural Alignment** or a dedicated *Domain Model Behavioral Design* section when the active project uses Neatoo and the plan touches domain-model behavior.

The base plan-template stays framework-agnostic; these tables are specific to how Neatoo expects behavioral logic to be designed.

The premise: the domain model is the ViewModel for UI pages. Every behavioral property the UI needs is designed here. Razor pages bind to these properties and do not implement business logic.

**Important.** These tables are intent-bearing — they describe *what* needs to be true. Keep entries terse: a property name, what it computes, what triggers it. Do **not** turn these tables into implementation transcription (no `partial` declarations, no AddValidation/AddAction call signatures, no method bodies). If a row drifts into code shape, compress it back to intent.

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

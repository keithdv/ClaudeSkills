# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft
**Last Updated:** YYYY-MM-DD

<!-- Valid status values (do not render in plan):
Draft | Vetoed | Approved | In Progress | Awaiting Review |
Grade A | Grade B | Grade C | Documented | Complete
-->

---

## Overview

[Brief description of what this plan addresses. User + orchestrator write this in Step 1.]

---

## Current Behavior Map

[How does the affected code work TODAY? Document specific paths, assumptions, invariants before designing the change. This is the anchor for "don't break what works." Enhancement contradictions with current behavior are caught here, not at review.]

- **[Flow / feature]**: [file:method] — [what it does today]
- **Assumption:** [any implicit assumption the current code relies on]
- **Invariant:** [any property/state guarantee the current design depends on]

---

## Out of Scope / Invariants

[Behaviors that must NOT change. Specific callers, integrations, UI flows, data shapes. Graded at review time under Scope Discipline.]

- [Specific behavior that must continue to work — e.g., "The PatientService.SearchAsync pagination contract (returns up to 50 results)"]
- [Specific integration — e.g., "The reports controller's /api/reports/patient endpoint signature"]
- [Specific data shape — e.g., "The Consultation.TreatmentPlan serialization does not add or remove fields"]

---

## Fallacy

<!-- ONLY for Bug-Exposes-Fallacy todos. Remove this section for Enhancement or Bug todos. -->

- **What we believed:** [The assumption that turned out to be wrong]
- **What is actually true:** [The corrected understanding]
- **Downstream consequences:** [What else in the codebase assumed the fallacy; what else needs rethinking]

---

## Approach

[High-level strategy. How will we solve this?]

---

## Design

[Detailed design — architecture, file structure, data flow, aggregate boundaries.]

---

## Business Rules (Testable Assertions)

[All business rules as numbered, crisp, unambiguous WHEN/THEN assertions. Every design decision and test scenario traces back to these. Mark NEW for rules not traced to an existing documented requirement.]

1. WHEN [conditions], THEN [property/method] RETURNS [expected value] — Source: [requirement reference or NEW]
2. WHEN [conditions], THEN [observable behavior]. Expected: [value] — Source: [requirement reference or NEW]
3. ...

### Test Scenarios

[For each business rule above, at least one concrete scenario with inputs and expected result.]

| # | Scenario | Inputs / State | Rule(s) | Expected Result |
|---|----------|---------------|---------|-----------------|
| 1 | [Descriptive name] | [Concrete values] | Rule 1 | [Expected value with brief explanation] |
| 2 | [Descriptive name] | [Concrete values] | Rule 2 | [Expected value with brief explanation] |

---

## Domain Model Behavioral Design

[The domain model is the ViewModel for UI pages. Every behavioral property the UI needs is designed here. Razor pages bind to these properties and do not implement business logic.]

### Computed Properties

| Property | Type | Computes | Triggered By |
|----------|------|----------|-------------|
| [e.g., FullName] | [string] | [FirstName + " " + LastName] | [FirstName, LastName] |

### Visibility / Conditional Flags

| Property | Condition | Depends On |
|----------|-----------|------------|
| [e.g., ShowDeclineReason] | [CareStatus == ConsultationDeclined] | [CareStatus] |

### Reactive Rules

| Rule | Trigger | Affected Property | Behavior |
|------|---------|-------------------|----------|
| [e.g., Auto-set consultation date] | [CareStatus -> Consultation] | [ConsultationDate] | [Set to today if null] |

### Classification Properties

| Property | Type | Logic |
|----------|------|-------|
| [e.g., IsPatient] | [bool] | [CareStatus >= InitialCare] |

### Validation Rules

| Rule | Trigger Properties | Error Message |
|------|-------------------|---------------|
| [e.g., DeclineReason required] | [CareStatus, DeclineReason] | [Decline reason is required when consultation is declined] |

---

## Design Decisions

[Timestamped "chose A over B because C" entries. Grows during Step 1 design and during Step 3 implementation as decisions get made. Append — do not rewrite history. The graded review checks that the implementation honored each decision.]

### YYYY-MM-DD
- **Decision:** [What was decided]
- **Alternative considered:** [What was rejected]
- **Reason:** [Why]

---

## Skills

[Orchestrator identifies these during Step 1. Every skill needed during implementation — domain, framework, component. At Step 3, the orchestrator loads these into a fresh context alongside the plan. Not listed = not available.]

- `path/to/skill/SKILL.md` — [why this skill is needed]

---

## Implementation Steps

[Ordered steps. Written in Step 1.]

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Deferred Scope

[Things noticed during planning or implementation that are explicitly not being done. Captured so they aren't lost. Grows during Step 3 — append as things come up.]

- [Item — e.g., "Also refactor PaymentHistoryPage to use the new calculation"] — [When noticed] — [Why deferred]

---

## Dependencies

[Prerequisites, tools, external factors.]

---

## Risks / Considerations

[Trade-offs, known issues, things to watch out for.]

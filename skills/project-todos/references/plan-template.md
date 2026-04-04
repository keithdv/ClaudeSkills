# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft
**Last Updated:** YYYY-MM-DD

<!-- Valid status values (do not render in plan):
Draft | Under Review (Architect) | Concerns Raised (Architect) | Ready for Implementation |
In Progress | Awaiting Code Review | Code Review Concerns | Awaiting Verification | Sent Back |
Requirements Documented | Documentation Complete | Complete
-->

---

## Overview

[Brief description of what this plan addresses. Written by user + orchestrator in Step 1.]

---

## Business Rules (Testable Assertions)

[Orchestrator writes this section during Step 1 with the user. ALL business rules from the design as numbered, crisp, unambiguous assertions. These are the source of truth for the entire plan. Every design decision, implementation step, and test scenario must trace back to one or more assertions here.]

[Format each rule using WHEN/THEN to eliminate ambiguity about what the expected value applies to.]

[For rules that trace to an existing documented requirement, include the reference. For new rules, mark as NEW.]

1. WHEN [conditions], THEN [property/method] RETURNS [expected value] — Source: [requirement reference or NEW]
2. WHEN [conditions], THEN [observable behavior]. Expected: [value] — Source: [requirement reference or NEW]
3. ...

### Test Scenarios

[Orchestrator writes this section during Step 1 with the user. For each business rule above, at least one concrete scenario showing inputs and expected result. These scenarios become acceptance tests.]

| # | Scenario | Inputs / State | Rule(s) | Expected Result |
|---|----------|---------------|---------|-----------------|
| 1 | [Descriptive name] | [Concrete values] | Rule 1 | [Expected value — with brief explanation] |
| 2 | [Descriptive name] | [Concrete values] | Rule 2 | [Expected value — with brief explanation] |
| 3 | ... | ... | ... | ... |

---

## Approach

[How will we solve this? High-level strategy. Written by user + orchestrator in Step 1.]

---

## Domain Model Behavioral Design

[Orchestrator writes this section during Step 1 with the user. The domain model is the ViewModel for Blazor pages. Every behavioral property the UI needs must be designed here — Razor pages bind to these properties and NEVER implement business logic themselves.]

### Computed Properties

[Values derived from other properties. The domain framework skill documents implementation patterns.]

| Property | Type | Computes | Triggered By |
|----------|------|----------|-------------|
| [e.g., FullName] | [string] | [FirstName + " " + LastName] | [FirstName, LastName] |

### Visibility / Conditional Flags

[Booleans that control what the UI shows or hides. Razor binds to these — never writes its own @if conditions on business state.]

| Property | Condition | Depends On |
|----------|-----------|------------|
| [e.g., ShowDeclineReason] | [CareStatus == ConsultationDeclined] | [CareStatus] |

### Reactive Rules

[When property A changes, update property B — within an entity or across parent-child boundaries in the aggregate graph.]

| Rule | Trigger | Affected Property | Behavior |
|------|---------|-------------------|----------|
| [e.g., Auto-set consultation date] | [CareStatus -> Consultation] | [ConsultationDate] | [Set to today if null] |

### Classification Properties

[Properties that classify or categorize for display purposes.]

| Property | Type | Logic |
|----------|------|-------|
| [e.g., IsPatient] | [bool] | [CareStatus >= InitialCare] |

### Validation Rules

[Business constraints enforced in the domain model.]

| Rule | Trigger Properties | Error Message |
|------|-------------------|---------------|
| [e.g., DeclineReason required] | [CareStatus, DeclineReason] | [Decline reason is required when consultation is declined] |

---

## Design

[Detailed design - architecture, file structure, data flow, etc. Written by user + orchestrator in Step 1.]

---

## Implementation Steps

[Ordered steps for the developer. Written by user + orchestrator in Step 1.]

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Acceptance Criteria

[Written by user + orchestrator in Step 1.]

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Dependencies

[Any prerequisites, tools, or external factors. Written by user + orchestrator in Step 1.]

---

## Risks / Considerations

[Things to watch out for, trade-offs, known issues. Written by user + orchestrator in Step 1.]

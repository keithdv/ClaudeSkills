# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft
**Last Updated:** YYYY-MM-DD

<!-- Valid status values (do not render in plan):
Draft | Under Review (Architect) | Concerns Raised (Architect) | Under Review (Developer) |
Concerns Raised | Ready for Implementation | In Progress | Awaiting Verification | Sent Back |
Requirements Documented | Documentation Complete | Complete
-->

---

## Overview

[Brief description of what this plan addresses. Written by user + orchestrator in Step 1.]

---

## Business Requirements Context

[Architect populates this section from the todo's Requirements Review during plan review (Step 3). The reviewer's findings in the todo are the source; the architect incorporates them here so the plan is self-contained.]

**Source:** [Link to todo's Requirements Review section]

### Relevant Existing Requirements

[Every project organizes requirements differently. List requirements from whatever sources the project uses — documentation, tests, legacy code, etc. Use whichever sections below apply and remove the rest.]

#### Business Rules

- [Rule reference/location]: [Summary] — Relevance: [How it relates to this todo]

#### User Stories

- [Story ID/location]: [Summary] — Relevance: [How it relates]

#### Workflows

- [Workflow reference/location]: [Summary] — Relevance: [How it relates]

#### Data Definitions

- [Definition reference/location]: [Summary] — Relevance: [How it relates]

#### Existing Tests

[Tests that pass today and define expected behavior for the affected area]

- [Test location]: [What behavior it verifies] — Relevance: [How the proposed change affects it]

### Gaps

[Areas where the todo's scope has no existing documented requirements — the architect must establish new rules for these areas]

### Contradictions

[Any conflicts between the todo's proposed approach and existing documented requirements. If VETOED, each contradiction must be listed here with specific requirement references.]

### Recommendations for Architect

[Guidance for the architect based on existing requirements — key constraints to respect, patterns to follow]

---

## Business Rules (Testable Assertions)

[Architect fills this section during plan review (Step 3). Extracts ALL business rules from the user's design as numbered, crisp, unambiguous assertions. These are the source of truth for the entire plan. Every design decision, implementation step, and test scenario must trace back to one or more assertions here.]

[Format each rule using WHEN/THEN to eliminate ambiguity about what the expected value applies to.]

[For rules that trace to an existing documented requirement (from the Business Requirements Context section), include the reference. For new rules covering gaps, mark them as NEW.]

[**If the architect struggles to write clear assertions from the user's design, this is an architectural smell — the design may not be concrete enough. Return to the user for clarification.**]

1. WHEN [conditions], THEN [property/method] RETURNS [expected value] — Source: [requirement reference or NEW]
2. WHEN [conditions], THEN [observable behavior]. Expected: [value] — Source: [requirement reference or NEW]
3. ...

### Test Scenarios

[Architect fills this section during plan review (Step 3). For each business rule above, provide at least one concrete scenario showing inputs and expected result. These scenarios become acceptance tests.]

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

[Architect fills this section during plan review (Step 3). The domain model is the ViewModel for Blazor pages. Every behavioral property the UI needs must be designed here — Razor pages bind to these properties and NEVER implement business logic themselves. If this section is empty, the architect must justify why no behavioral properties are needed.]

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

## Agent Phasing

[Architect fills this section during plan review (Step 3). Identifies which implementation phases benefit from fresh agents. Each phase is a unit of work that can be handed to an agent with clear inputs and expected outputs.]

| Phase | Agent Type | Fresh Agent? | Rationale | Dependencies |
|-------|-----------|-------------|-----------|--------------|
| [Phase 1 name] | [developer/UI/specialized] | [Yes/No] | [Why fresh or continuing] | [Prior phases needed] |
| [Phase 2 name] | [developer/UI/specialized] | [Yes/No] | [Why fresh or continuing] | [Prior phases needed] |

**Parallelizable phases:** [List phases that can run concurrently, if any]

**Notes:** [Any special coordination needed between phases]

---

## Dependencies

[Any prerequisites, tools, or external factors. Written by user + orchestrator in Step 1.]

---

## Risks / Considerations

[Things to watch out for, trade-offs, known issues. Written by user + orchestrator in Step 1.]

# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft
**Last Updated:** YYYY-MM-DD

<!-- Valid status values (do not render in plan):
Draft | Approved | In Progress | Awaiting Review | Reviewed | Documented | Complete |
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

## Domain Model Behavioral Design (optional, framework-specific)

[Optional section. Use it when the project's domain model framework expects behavioral design (computed properties, visibility flags, reactive rules, validation rules) to be specified up front so the UI binds to them rather than re-implementing logic.

For Neatoo / zTreatment-style projects, append the tables in `references/plan-template-neatoo.md` here. For other projects, use the format their domain framework expects, or omit this section entirely if it doesn't apply.]

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

## Companion Plans

[Other plans (in this todo) or sibling todos covering work outside this plan's scope. Grows during Step 3 — append as the orchestrator notices work that belongs elsewhere.

**Every entry MUST link to a real plan or todo file.** When the orchestrator notices work outside this plan's scope, the question is *which plan/todo does it belong to?* — either a stub plan that already exists in this todo, a new plan in this todo, or a sibling todo. The orchestrator creates the file (status `Draft`) and links it here. See "Multi-Plan Todos — Decompose Up Front, Don't Defer" in the project-todos SKILL.

A Companion Plans entry without a real file link is treated by plan-reviewer and code-reviewer as a silent drop — CONCERNS at plan review, automatic C in Scope Discipline at graded review.

Required entry formats:]

- Plan (this todo): `docs/plans/{plan-name}.md` — [one-line summary of what this plan covers]
- Sibling todo: `docs/todos/{todo-name}.md` — [one-line summary of why it's its own todo]

---

## Plan Amendments

[Append-only. Used ONLY when, during or after Step 3, a major issue surfaces and the user explicitly chooses option 1 ("Tweak plan + implementation") from the three options presented in Step 3 (see "The Plan Is Sacred Once Implementation Begins" in the project-todos SKILL).

The plan body above (Overview, Approach, Design, Business Rules, Implementation Steps, etc.) is **frozen** once Step 3 begins. Do NOT edit it in place. Instead, every authorized change gets recorded here as a dated entry with a back-pointer to the section it modifies. The original text stays intact so the audit trail between intent and reality is preserved — that gap is exactly what the graded review needs to see.

The other two options (revert + restart, or ship + spawn new plan/todo) do NOT use this section: revert + restart spawns a new todo/plan, and ship + spawn adds an entry to Companion Plans.

Required entry format:]

### YYYY-MM-DD — [Short title]

- **Section affected:** [e.g., "Approach", "Design — Visit aggregate", "Business Rule BR-3"]
- **Original text said:** [one-line summary of what the plan committed to]
- **What changed:** [what the implementation actually does instead]
- **Why:** [the issue that surfaced]
- **User decision:** Approved tweak on YYYY-MM-DD. (Acknowledges revert + restart and ship + follow-up were the other options.)

---

## Dependencies

[Prerequisites, tools, external factors.]

---

## Risks / Considerations

[Trade-offs, known issues, things to watch out for.]

# Agent Migration Guide: v2.x to v3.0

**Skill version:** 3.0.0
**Breaking change from 2.x:** Yes — the architect role shifts from plan creator to plan reviewer; the clarification loop routing changes.

## What Changed in v3.0

The core workflow change: **the user now creates both the todo AND the plan** in conversation with the orchestrator. The architect shifts from autonomous designer to reviewer/enhancer.

| Before (v2) | After (v3) |
|-------------|------------|
| Orchestrator creates todo, architect creates plan | User + orchestrator create todo AND plan together |
| Architect is the designer (creates plan, writes assertions, designs domain model) | Architect is a reviewer who validates and enhances the user's plan |
| Orchestrator "discovers but never analyzes" | Orchestrator is the user's full design partner (analysis allowed) |
| Architect comprehension check step (Step 2) | Eliminated — user IS the designer |
| Clarification loop: user chooses who answers developer concerns | Architect tries technical answers, escalates design changes to user |
| 10 steps | 9 steps (comprehension check removed, old steps renumbered) |

### Step Renumbering

| v2 Step | v3 Step | Description |
|---------|---------|-------------|
| Step 1: Create Todo | Step 1: Create Todo AND Draft Plan (user + orchestrator) |
| Step 2: Architect Comprehension Check | **Removed** |
| Step 3: Business Requirements Review | Step 2: Business Requirements Review |
| Step 4: Architect Plan Creation & Design | Step 3: Architect Review (reviewer, not creator) |
| Step 5: Developer Review | Step 4: Developer Review |
| Step 6: Clarification Loop | Step 5: Clarification Loop (new escalation rules) |
| Step 7: Implementation | Step 6: Implementation |
| Step 8: Verification | Step 7: Verification |
| Step 9: Documentation | Step 8: Documentation |
| Step 10: Completion | Step 9: Completion |

### Plan Status Changes

| v2 Status | v3 Status | Notes |
|-----------|-----------|-------|
| `Draft (Architect)` | **Removed** — architect no longer creates plans |
| — | `Draft` | New initial status when user creates the plan |
| — | `Under Review (Architect)` | New status for architect review step |
| — | `Concerns Raised (Architect)` | Architect found issues in user's plan |
| `Under Review (Developer)` | `Under Review (Developer)` | Unchanged |
| `Concerns Raised` | `Concerns Raised` | Unchanged (developer concerns) |
| All others | Same | Unchanged |

---

## Architect Agent Migration

The architect agent needs the most significant changes. The primary workflow mode shifts from "Feature Design" (creating plans) to "Plan Review" (reviewing and enhancing the user's plans).

### New: Plan Review Mode

Add a new mode (or replace the existing Feature Design mode) for the architect's primary workflow role:

```markdown
## Mode: Plan Review (Primary Workflow Mode)

When invoked after the user has created a plan, the architect reviews and enhances it.

### What the Architect Fills In

The user's plan will have these sections populated: Overview, Approach, Design, Implementation Steps, Acceptance Criteria, Dependencies, Risks.

The architect fills in these sections during review:
1. **Business Requirements Context** — from the todo's Requirements Review
2. **Business Rules (Testable Assertions)** — extracted from the user's design
3. **Test Scenarios** — concrete scenarios for each business rule
4. **Domain Model Behavioral Design** — computed properties, visibility flags, reactive rules, validation
5. **Agent Phasing** — which implementation phases benefit from fresh agents

### Validation Responsibilities

1. Deep codebase dive — examine affected aggregates, existing patterns, related tests
2. Validate aggregate boundaries, repository patterns, framework constraints
3. Check for affected tests the user didn't account for
4. Verify the approach is feasible

### Architectural Smell: Struggling with Assertions

If the architect cannot write clear, unambiguous WHEN/THEN assertions from the user's design, this is a signal that the design isn't concrete enough. **Report this to the orchestrator** rather than inventing assertions that don't clearly follow from the design.

### Verdicts

- **Approved** — Design is sound, all sections filled. Set plan status to `Under Review (Developer)`.
- **Concerns** — Issues found. Return to orchestrator for user. Set plan status to `Concerns Raised (Architect)`.
- **Rejected** — Fundamental problems. Return to orchestrator for user. Set plan status to `Concerns Raised (Architect)`.
```

### New: Clarification Loop Behavior

Add escalation rules for when the architect is asked to address developer concerns:

```markdown
## Clarification Loop Escalation Rules

When the orchestrator relays developer concerns:

**Handle directly (technical implementation details):**
- Correct Include patterns, factory method attributes, test setup patterns
- Framework-specific guidance (Neatoo rule mechanisms, EF Core configuration)
- Test tier selection and test strategy details
- Implementation ordering and phasing adjustments

**STOP and escalate to user (design changes):**
- Changes to aggregate boundaries
- Adding or removing domain model properties
- Changing the approach or strategy
- Scope changes (adding or removing implementation steps)
- Anything that changes what the user decided to build

**When in doubt, escalate.** It is always safer to ask the user than to make a design decision autonomously.
```

### Checklist for Architect Agent

- [ ] Add "Plan Review" mode as the primary workflow mode (or rename Feature Design)
- [ ] Clarify that the architect REVIEWS the user's plan, does not CREATE it
- [ ] Add "architect fills these sections" list (Business Rules, Test Scenarios, Domain Model Behavioral Design, Agent Phasing, Business Requirements Context)
- [ ] Add "architectural smell" guidance — struggling to write assertions = design needs more work
- [ ] Add clarification loop escalation rules (technical = handle, design = escalate)
- [ ] Update step references: old Step 4 -> new Step 3, old Step 8 -> new Step 7, etc.
- [ ] Remove references to "creating the plan file" — the plan already exists when the architect gets it
- [ ] Update Workflow Integration section to describe receiving user's plan instead of creating one
- [ ] Feature Design, Bug Investigation, Brainstorming, Post-Implementation Verification modes remain (renumber if needed)
- [ ] Post-Implementation Verification (Mode 4) is unchanged

### What to Search For

Grep the architect agent file for these strings to find sections that need updating:

```
"create the plan"          -> architect no longer creates plans
"creates the plan"         -> same
"Step 4"                   -> renumber to Step 3
"Step 8"                   -> renumber to Step 7
"comprehension check"      -> removed step
"Draft (Architect)"        -> removed status
"Feature Design"           -> may need to become Plan Review or add Plan Review alongside
"Plan Creation"            -> no longer applicable
```

---

## Developer Agent Migration

The developer agent changes are smaller — mainly the clarification loop behavior.

### Updated: Clarification Loop

In v2, the developer's concerns went to the user, who chose whether to answer themselves or send to architect. In v3, concerns go to the architect first, who handles technical details and escalates design questions to the user.

**The developer does not need to know about this routing change.** The developer still raises concerns the same way. The orchestrator handles the routing.

However, update any documentation in the developer agent that references the old flow:

```markdown
### OLD (v2):
"If concerns: Ask user: 'I have concerns about this plan. Would you like to clarify
these yourself, or should I send them back to the architect?'"

### NEW (v3):
"If concerns: Return concerns to the orchestrator. The orchestrator will route them
to the architect for technical resolution and to the user for design decisions."
```

### Checklist for Developer Agent

- [ ] Update clarification loop description — concerns go to orchestrator, not directly to user
- [ ] Remove "ask user who should answer" language — orchestrator routes automatically
- [ ] Update step references: old Step 5 -> new Step 4, old Step 6 -> new Step 5, old Step 7 -> new Step 6, etc.
- [ ] Remove references to "architect comprehension check" (removed step)
- [ ] Update plan status references: remove `Draft (Architect)`, add `Under Review (Architect)`, `Concerns Raised (Architect)`

### What to Search For

```
"Step 5"                   -> renumber to Step 4
"Step 6"                   -> renumber to Step 5
"Step 7"                   -> renumber to Step 6
"comprehension check"      -> removed step
"Draft (Architect)"        -> removed status
"Would you like to clarify" -> old clarification loop prompt
"send them back to the architect" -> old routing language
```

---

## Business Requirements Reviewer Agent Migration

Minimal changes — the reviewer's role is the same, just invoked at a different step number.

### Checklist

- [ ] Update step references: old Step 3 -> new Step 2, old Step 8 -> new Step 7
- [ ] The reviewer now reviews the todo AND the draft plan (in v2 it only saw the todo before the plan existed). Update instructions to mention reading the plan file if provided.

### What to Search For

```
"Step 3"          -> renumber to Step 2
"Step 8"          -> renumber to Step 7
```

---

## Business Requirements Documenter Agent Migration

Minimal changes — step renumbering only.

### Checklist

- [ ] Update step references: old Step 9 -> new Step 8

### What to Search For

```
"Step 9"          -> renumber to Step 8
```

---

## Todo Template Changes

The **Clarifications** section has been removed from the todo template. It was used for the architect comprehension check (v2 Step 2), which no longer exists.

The **Requirements Review** section remains but now references Step 2 instead of Step 3.

---

## Plan Template Changes

### New Status Values

- `Draft` — initial status when user creates the plan (replaces `Draft (Architect)`)
- `Under Review (Architect)` — new status for architect review
- `Concerns Raised (Architect)` — new status for architect concerns

### Section Ownership

Sections are now explicitly labeled with who fills them:

| Section | Filled By | When |
|---------|-----------|------|
| Overview, Approach, Design, Implementation Steps, Acceptance Criteria, Dependencies, Risks | User + orchestrator | Step 1 |
| Business Requirements Context | Architect | Step 3 (from todo's Requirements Review) |
| Business Rules (Testable Assertions) | Architect | Step 3 |
| Test Scenarios | Architect | Step 3 |
| Domain Model Behavioral Design | Architect | Step 3 |
| Agent Phasing | Architect | Step 3 |

---

## Reference Files Migration

The following reference files in the skill also need updates when migrating to v3:

### documentation-step-guide.md

- [ ] Update step numbers: Step 9 -> Step 8, Step 10 -> Step 9
- [ ] Replace references to "plan's Documentation section" with memory file references
- [ ] Align invocation instructions with SKILL.md Step 8

**Note:** This file was fully rewritten as part of v3.0. If you have a project-specific copy, update it to match the skill's version.

---

## Compatibility

### Existing Plans (v2)

Plans created under v2 that have `Draft (Architect)` status are in-progress architect work. Complete them under v2 rules, then switch to v3 for new work.

### New Plans (v3)

All new plans follow the v3 workflow. The user creates the plan, the architect reviews it.

### Mixed Agent Versions

If some project agents are updated to v3 but others are still v2, the workflow will have friction. Update all agents in a project at once when migrating.

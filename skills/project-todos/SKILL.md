---
name: project-todos
version: 6.1.0
description: This skill should be used when the user asks to "create a todo", "add a plan", "plan this work", "track this work", "document this task", "complete a todo", "verify the implementation", "start the implementation", "update docs for this feature", "what's the next step", "what's the plan status", "resume the todo", "what's blocked", "pick up where we left off", "design this feature", "check business requirements", "review requirements", "review against requirements", "check for requirement conflicts", "review the plan", "review plan against codebase", "plan review", "grade the work", "code review", or mentions managing project todos, plans, and multi-agent workflows. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration through the full design-review-implement-grade-document lifecycle.
---

# Project Todos, Plans, and Agent Workflow

Manage significant project work using structured markdown files. The orchestrator designs and implements in conversation with the user; three agents handle review, grading, and documentation.

## Core Principle: Conversation Designs and Implements, Agents Review

**Design and implementation are conversational.** The orchestrator works through them with the user in real time — analyzing code together, making design calls, writing code, course-correcting on the fly. Agents are poor at design because they can't have a back-and-forth.

**Review is independent.** Agents review without the bias of the design conversation. They trace plan assertions through real code, grade the work, and flag what the orchestrator and user missed.

**Everything durable lives in the todo and plan files.** No agent memory, no hidden state. Agents return findings in their response; the orchestrator writes summaries to the todo or plan. If a finding isn't captured there, it's gone.

### What the Orchestrator Does

- Authors all plan and todo content
- Analyzes the codebase with the user during design
- Implements code changes in conversation with the user
- Invokes agents for review, grading, and documentation
- Writes agent findings (summaries) into the todo or plan
- Sets plan/todo status based on agent verdicts
- Decides which steps to skip (with user confirmation)

### What Agents Do

- Review, grade, verify, and document
- Return findings in their response text
- Never write to plan or todo files
- Never set status
- Never communicate with other agents

## When to Use This Workflow

Create a todo when:
- The user explicitly asks for one
- Work is significant, spans sessions, or requires design before implementation
- The change affects business rules, multiple aggregates, or user-facing behavior

Skip for trivial fixes, simple refactors, or work tracked elsewhere.

## Directory Structure

```
docs/
├── todos/
│   ├── {todo-name}.md              # Active
│   └── completed/
│       └── {todo-name}.md
└── plans/
    ├── {plan-name}.md              # Active
    └── completed/
        └── {plan-name}.md
```

All paths are relative to the project root.

## The Four Agents

### 1. `business-requirements-reviewer` — Step 2 (plan vs. documented rules)

Reads the draft plan, searches the project's business requirements docs, identifies contradictions, implicit dependencies, and gaps. Verdict: **APPROVED** or **VETOED**.

### 2. `plan-reviewer` — Step 2.5 (plan vs. codebase, optional but recommended)

Reads the draft plan and does a codebase deep-dive. Catches design gaps, missed call sites, infeasible approaches, domain-logic-in-UI smells, framework-correctness risks, and invariant violations before implementation. Complementary to `business-requirements-reviewer`: that agent checks plan-vs-docs; this agent checks plan-vs-code. Verdict: **APPROVED**, **CONCERNS**, or **REJECTED**.

### 3. `code-reviewer` — Step 4 (graded review)

Reads the plan and actual code, runs fresh builds and tests, grades seven categories A/B/C, produces "to reach A" suggestions. See `references/rubric.md` for the rubric.

### 4. `business-requirements-documenter` — Step 5 (post-impl docs, optional)

Updates the project's business requirements documentation to reflect what was implemented. Skipped when no requirements changed (internal refactor, bug fix with no behavior change).

### Optional specialist agents

Domain and framework experts (e.g., `ef-postgres-query-expert`, `grails-legacy-expert`, `blazor-ui`, `dosing-analyst`, `treatment-architect`, `dosing-architect`) are research helpers during Step 1 or deep-dive reviewers the orchestrator calls situationally when Step 2.5 or a rubric category needs a specialist opinion. They do not own workflow steps.

## Prerequisites

Before starting:

1. **Check `.claude/agents/` and `~/.claude/agents/`** for project-specific versions of the three workflow agents. Project-specific takes priority.
2. **Check the project's CLAUDE.md** for business requirements locations. If unclear, stop and ask the user.
3. **Identify skills** needed during implementation. These go in the plan's Skills section.

## Todo Types

Every todo has one of these types. Declared in the todo's header.

- **Enhancement** — Adding or changing behavior to support new requirements.
- **Bug** — Restoring correct behavior that was lost or never worked.
- **Bug-Exposes-Fallacy** — A bug that reveals a false assumption in the existing design. The plan **must** include a Fallacy section (see plan template) stating what was believed, what is actually true, and the downstream consequences. The design flows from the corrected assumption, not the symptom.

## Skipping Steps

Every step except Step 1 and Step 6 can be skipped. Skips are conversational: the user requests a skip, the orchestrator confirms what's being skipped and why it matters, the skip is recorded in the todo's **Skipped Steps** list with a reason.

Common skip patterns:

- **Step 2 (Requirements Review)** — Skip if the project has no documented requirements yet, or the change is purely mechanical with no business rule impact. Ask first.
- **Step 2.5 (Plan Review)** — Opt-in, not default. Recommended for Enhancement and Bug-Exposes-Fallacy todos, plans that touch multiple aggregates or introduce new patterns, or any plan where the orchestrator isn't confident all affected code has been accounted for. Skip for trivial one-file changes or bug fixes with a tight blast radius.
- **Step 5 (Documentation)** — Skip for internal refactors, bug fixes restoring documented behavior, or test-only changes.

Step 2 is the default for changes that touch business behavior. Step 2.5 is the default for Enhancement and Bug-Exposes-Fallacy todos — propose running it unless the plan is obviously small.

## Step 1: Create Todo and Draft Plan

The user is the designer. The orchestrator is the design partner.

### Part A: Create the Todo

1. Capture the problem and desired outcome in the user's words.
2. Analyze the codebase together — search, trace patterns, identify affected aggregates, check prior completed todos for related context.
3. Create the todo file in `docs/todos/` using `references/todo-template.md`.
4. Set Type, Status "In Progress", Priority, and today's date.

### Part B: Draft the Plan

Collaborate with the user to fill every plan section:

- **Overview** — What the plan addresses.
- **Current Behavior Map** — How the affected code works today. Specific paths, assumptions, invariants. This is the anchor for "don't break what works." Enhancements that contradict current behavior are caught here, not during review.
- **Out of Scope / Invariants** — Behaviors that must NOT change. Specific callers, integrations, UI flows, data shapes. Becomes the basis for the Scope Discipline rubric category.
- **Fallacy** (Bug-Exposes-Fallacy only) — What was believed. What is actually true. Downstream consequences.
- **Approach** — High-level strategy.
- **Design** — Detailed design (architecture, file structure, data flow).
- **Business Rules (Testable Assertions)** — Numbered WHEN/THEN assertions. Trace each to an existing requirement or mark NEW.
- **Test Scenarios** — Concrete scenarios for each rule with inputs and expected results.
- **Domain Model Behavioral Design** — Computed properties, visibility flags, reactive rules, validation rules.
- **Design Decisions** — Timestamped "chose A over B because C" entries. Grows during implementation as decisions get made.
- **Skills** — Every skill needed at Step 3 with its path and why. Not listed → not loaded at implementation.
- **Implementation Steps** — Ordered steps.
- **Acceptance Criteria** — What "done" looks like.
- **Deferred Scope** — Noticed during planning/implementation but explicitly not doing. Grows during implementation.
- **Dependencies** and **Risks**.

Link the plan and todo (update both files). Set plan status to **Draft**.

## Step 2: Business Requirements Review

**Purpose:** Catch contradictions between the draft plan and existing documented requirements before implementation. The most expensive bugs come from chasing a design that conflicts with a rule nobody remembered.

Invoke **business-requirements-reviewer** with:
- The todo file path and plan file path
- The project's requirements locations (from CLAUDE.md)
- Instruction: "Review this todo and plan against the project's existing business requirements. Return your verdict (APPROVED or VETOED) with specific findings."

The reviewer searches requirements docs and the legacy codebase (if applicable), identifies relevant rules, gaps, implicit dependencies, and contradictions, then reports.

**When the reviewer reports back:**

The orchestrator writes a summary to the todo's **Requirements Review** section (verdict, date, one-paragraph summary, key findings).

**If VETOED:** Present contradictions to the user. The user decides direction (modify plan, update requirements, override). Update the plan, re-invoke the reviewer. Repeat until APPROVED.

**If APPROVED:** Set plan status to **Requirements Approved** and propose Step 2.5 unless the plan is trivially small.

## Step 2.5: Plan Review (Optional, Recommended for Enhancements)

**Purpose:** Catch gaps between the draft plan and the actual codebase before implementation. The business-requirements-reviewer validates plan-vs-docs; this step validates plan-vs-code.

**When to run:**
- **Default yes** for Enhancement and Bug-Exposes-Fallacy todos
- **Default yes** for any plan that touches multiple aggregates, introduces new patterns, or renames/refactors widely-referenced types
- **Default no** for one-file bug fixes with an obvious blast radius

The common Step 3 failure mode is discovering, mid-implementation, that the plan missed 5+ call sites, a save path, or a UI binding. Step 2.5 exists to catch those before the orchestrator commits to the design.

Invoke **plan-reviewer** with:
- The todo file path and plan file path
- Instruction: "Review this plan against the codebase. Verify feasibility, find missed call sites, check domain-logic placement, flag framework-correctness risks. Return APPROVED, CONCERNS, or REJECTED with specific findings."

The reviewer reads the plan and CLAUDE.md, does a codebase deep-dive on affected aggregates/services/UI/tests, and reports.

**When the reviewer reports back:**

The orchestrator writes a summary to the todo's **Plan Review** section (verdict, date, files examined count, gaps, domain-logic concerns, framework risks, invariant violations, recommendations).

**If REJECTED:** Present fundamental issues to the user. The Approach needs rework, not tweaks. Rewrite affected plan sections, then re-invoke.

**If CONCERNS:** Present gaps to the user. Orchestrator and user update the plan to address each concern. Re-invoke the reviewer. Repeat until APPROVED (or the user explicitly accepts a concern as out-of-scope).

**If APPROVED:** Set plan status to **Approved**.

**If Skipped:** Skip is recorded in the todo's Skipped Steps list. Set plan status directly to **Approved** from **Requirements Approved**.

## Step 3: Implementation

**Start in a fresh context.** The planning conversation has been distilled into the plan. The back-and-forth is noise at this point.

Recommend the user start a new session. If continuing in the same session, treat the plan as the sole source of truth.

### What to Load

1. The plan file (all sections)
2. The todo file
3. Every skill listed in the plan's Skills section
4. The project's CLAUDE.md

### Implementation

Work through Implementation Steps in order, in conversation with the user. Run tests at natural checkpoints.

**During implementation, update the plan in these places:**
- **Design Decisions** — Append any new "chose A because B" decisions with timestamps.
- **Deferred Scope** — Append anything noticed but not doing.

**If out-of-scope tests fail**, stop. Present to the user: "Test X in area Y started failing, outside the current task. (1) fix root cause, (2) add to bug list, (3) investigate further?"

**Do NOT update docs markdown, skill markdown, release notes, or user-facing documentation.** Those are Step 5. Implementation scope is source code only. XML code comments on modified code are fine.

When done, run all builds and tests. Set plan status to **Awaiting Review**.

## Step 4: Graded Code Review

**Purpose:** Independent grading of the implementation against the plan. Produces a letter grade and concrete suggestions to reach A.

Invoke **code-reviewer** with:
- The plan file path and todo file path
- Summary of what was implemented (files changed)
- Instruction: "Grade this implementation against the plan using the rubric in `references/rubric.md`. Run fresh builds and tests. Return per-category grades, overall grade, and concrete 'to reach A' suggestions."

### The Rubric (summary — full rubric in `references/rubric.md`)

| Category | Grades |
|----------|--------|
| Requirements Coverage | Every plan assertion traced to specific code |
| Test Coverage | Every test scenario has a passing test; no sacred tests gutted |
| Design Alignment | Implementation matches plan's Approach, Design, Domain Model |
| Code Quality | Readability, naming, no dead code, no over-engineering |
| Framework Correctness | Project-specific framework idioms respected (per CLAUDE.md) |
| Build & Test Health | Fresh build passes, all tests pass, no new warnings in changed files |
| Scope Discipline | Out of Scope / Invariants list respected |

Each category is graded A/B/C. **Overall grade = worst category.** Grade A requires A across all seven.

### When the reviewer reports back

The orchestrator writes a summary to the todo's **Graded Review** section (date, overall grade, per-category table, key suggestions).

**If Grade A:** Set plan status to **Grade A**. Proceed to Step 5 (or Step 6 if docs are skipped).

**If Grade B or C:** Present category grades and "to reach A" suggestions to the user. The user acknowledges:
- **Accept the grade** — proceed as-is. The user owns the decision.
- **Address specific items** — orchestrator fixes in conversation with user, then re-invokes code-reviewer for re-grade. Append the new grade entry (don't overwrite).

A grade below A is not a blocker by itself. The user's acknowledgment is the gate.

## Step 5: Documentation (Optional)

**Purpose:** Update project business requirements documentation to reflect what was implemented.

Skip if the user confirms the change doesn't affect documented business rules (internal refactor, bug fix restoring documented behavior, test-only).

Invoke **business-requirements-documenter** with:
- The plan file path and todo file path
- The todo's Requirements Review section content
- Summary of what was implemented
- Instruction: "Update business requirements documentation to reflect the completed implementation. Add new rules, update changed rules, resolve gaps identified during review."

### When the documenter reports back

The orchestrator writes a summary to the todo's **Documentation** section (files updated, any developer deliverables).

**Developer deliverables** (source code changes requested by the documenter, such as XML comments, sample code): the orchestrator makes them directly in conversation with the user. Build and test after changes.

### General documentation (rare)

If the plan identifies non-requirements docs (README, API docs, migration guides), invoke a project-specific docs agent (or `docs-writer`) after the requirements documenter finishes. Most todos don't need this.

Set plan status to **Documented**.

## Step 6: Completion

1. Verify the last Graded Review entry exists and the user has acknowledged the grade.
2. Verify documentation is complete (or was skipped with reason).
3. Update todo status to **Complete**, set Last Updated date.
4. Fill in the Results / Conclusions section.
5. Move the todo to `docs/todos/completed/`.
6. Move associated plans to `docs/plans/completed/`.
7. Update plan status to **Complete** in each plan file.

## Resuming Mid-Workflow

Read the todo and any linked plan. Check plan status:

| Plan Status | Next Step |
|-------------|-----------|
| Draft | Step 2 (Requirements Review) unless skipped |
| Vetoed | Step 2 — resolve contradictions with user, re-invoke reviewer |
| Requirements Approved | Step 2.5 (Plan Review) unless skipped; skip → set to Approved |
| Plan Review Concerns | Step 2.5 — address gaps with user, re-invoke plan-reviewer |
| Approved | Step 3 (Implementation) — load plan, skills, CLAUDE.md in fresh context |
| In Progress | Step 3 — continue implementation |
| Awaiting Review | Step 4 (Graded Review) |
| Grade A / B / C | If user acknowledged → Step 5; if not acknowledged → present to user |
| Documented | Step 6 (Completion) |
| Complete | Nothing — work is done |

Full reviewer/documenter findings from prior runs live in the todo sections (Requirements Review, Plan Review, Graded Review, Documentation). No other state to load.

## Plan Status Values

`Draft` · `Vetoed` · `Requirements Approved` · `Plan Review Concerns` · `Approved` · `In Progress` · `Awaiting Review` · `Grade A` · `Grade B` · `Grade C` · `Documented` · `Complete`

## Todo Status Values

`In Progress` · `Complete` · `Blocked`

## Best Practices

1. **The plan is the contract.** Step 3 implementation starts in a fresh context with only the plan. If something is missing from the plan, that's a signal to improve the plan, not to preserve context.
2. **Update the plan during implementation.** Design Decisions and Deferred Scope grow during Step 3. Append, don't overwrite.
3. **Current Behavior Map before design.** Document how it works today before designing how it will work. This catches contradictions earlier than any review.
4. **Out of Scope is a commitment.** If you find yourself changing something on the list, stop. Either remove it from the list (with user agreement) or back out the change.
5. **Graded review is honest, not punitive.** A B or C grade is useful information. The user decides whether to address it. Don't treat A as the only acceptable outcome — treat the suggestions as value.
6. **Re-reviews append, they don't replace.** Every Graded Review run creates a new entry. History matters.
7. **Agents return findings, orchestrator writes summaries.** If an agent's 2000-word response has something worth keeping, paste the relevant section into the todo. Otherwise let it go.
8. **Skip with intent.** Conversational skip is fine, but record it. A skipped Requirements Review six months later without context is a mystery.

## Reference Files

- `references/todo-template.md` — todo template
- `references/plan-template.md` — plan template
- `references/rubric.md` — the seven-category rubric for graded review, with specific A/B/C criteria for each category

---
name: project-todos
version: 6.1.0
description: Use when the user asks to "create a todo", "plan this work", "design this feature", "resume the todo", or "grade the implementation" — i.e., multi-session design-heavy work where the plan needs to outlive the conversation, the codebase has documented business rules to check against, or deferred scope must be tracked into PRs. Provides the structured workflow for creating durable todo/plan files and orchestrating agents through design → review → implement → grade → document. **Skip this skill for single-session tasks**, trivial fixes, or work that fits in Claude Code's built-in plan mode (`Shift+Tab`) — that's the right tool when the plan doesn't need to survive the session.
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

## The Two Agents

### 1. `plan-reviewer` — Step 2 (plan vs. documented rules + plan vs. codebase)

Reads the draft plan and runs two passes in one invocation:

- **Pass A — plan vs. documented requirements.** Searches the project's business requirements docs (locations from CLAUDE.md), identifies contradictions, implicit dependencies, and gaps.
- **Pass B — plan vs. codebase.** Deep-dive on affected aggregates/services/UI. Catches design gaps, missed call sites, infeasible approaches, domain-logic-in-UI smells, framework-correctness risks, and invariant violations before implementation.

One verdict covers both: **APPROVED**, **CONCERNS**, or **REJECTED**. Findings are reported in dedicated subsections so the orchestrator can route fixes correctly.

### 2. `code-reviewer` — Step 4 (graded review)

Reads the plan and actual code, runs fresh builds and tests, grades seven categories A/B/C with confidence-scored findings, produces "to reach A" suggestions. See `references/rubric.md` for the rubric.

### Documentation (Step 5)

The orchestrator updates project requirements documentation directly in conversation with the user. No agent involved — the inputs (plan, todo, Requirements Review section, what was implemented) are already in context, and a dedicated agent has historically just paraphrased that context back as text the orchestrator pastes. Direct edits remove the handoff fragility.

### Optional specialist agents

Domain and framework experts (e.g., `ef-postgres-query-expert`, `grails-legacy-expert`, `blazor-ui`, `dosing-analyst`, `treatment-architect`, `dosing-architect`) are research helpers during Step 1 or deep-dive reviewers the orchestrator calls situationally when a rubric category needs a specialist opinion. They do not own workflow steps.

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

## Multi-Plan Todos — Decompose Up Front, Don't Defer

**Stop thinking "deferral." Start thinking "this is another plan."**

When work is bigger than one coherent plan, the right move is to decompose it into **multiple plans** — either multiple plans within the same todo (when the goal is one thing but execution naturally splits) or sibling todos (when the goals are genuinely distinct). The act of creating the additional plan file or todo file IS the capture mechanism. A bullet-point note that "we'll come back to this" is what historically gets lost; a `docs/plans/{plan-2}.md` file with status `Draft` does not.

The framing shift matters. "Deferral" implies punting — work that should have been here but got pushed away. "Plan decomposition" implies design — the work has its own scope, its own Approach, its own Implementation Steps, and deserves to be planned in its own right rather than bolted onto another plan as a bullet point.

### When to make a new plan vs. a new todo

- **New plan, same todo** — when the work shares this todo's goal and Current Behavior Map but has its own Approach and Implementation Steps. Example: "modernize visit save" → plan 1 (domain refactor), plan 2 (UI rebinding), plan 3 (legacy compatibility shim).
- **Sibling todo** — when the work is its own goal with its own Current Behavior Map and Out of Scope list. Example: a bug found during an enhancement that's worth fixing independently.
- **Truly out of scope** — neither a plan nor a todo, just a one-line note in the Out of Scope list. Use this for things like "we're not redesigning the whole module."

### How it works in the workflow

**At Step 1 (planning)**, the orchestrator and user explicitly ask: *Is this one plan or multiple?* If multiple, list them in the todo's **Plans** section. Draft the first plan in full detail; draft the others as one-paragraph stubs (problem statement + intended Approach) that can be filled in detail later, when their session begins. Stub plans live in `docs/plans/` with status `Draft`.

**At Step 3 (implementation)**, if the orchestrator notices work outside the current plan's scope, the question is *which plan does this belong to?* Either:

1. It belongs to a stub plan that already exists in this todo → just note it in that plan's Approach.
2. It belongs to a new plan in this todo → create `docs/plans/{plan-N}.md` (status `Draft`), link it from the todo's Plans section, briefly describe scope.
3. It belongs to a sibling todo → create `docs/todos/{name}.md` (status `In Progress` or `Draft`), with its own first plan.

The current plan's **Companion Plans** section gets a one-line entry pointing at the new plan/todo file. That section is the audit trail.

**A todo isn't complete until every plan in it has reached `Complete` or `Won't Do`.** Individual plans complete and move to `docs/plans/completed/` while their parent todo stays `In Progress` until all its plans are addressed.

**At Step 6 (completion of the *current plan*)**, the orchestrator surfaces the **Plan Sequence** callout (see Step 6) — every plan in this todo with current status, plus any sibling todos created. That callout goes into the PR description so the user sees what's done, what's still queued, and what spawned off.

The plan-reviewer and code-reviewer both verify Companion Plans entries point at real files. A bullet-point with no plan/todo file → CONCERNS at plan review; automatic C in Scope Discipline at graded review.

Common skip patterns:

- **Step 2 (Plan Review)** — Default yes for Enhancement and Bug-Exposes-Fallacy, plans touching multiple aggregates, or changes that touch documented business behavior. Skip for one-file bug fixes with an obvious blast radius and no business-rule impact. Ask first.
- **Step 5 (Documentation)** — Skip for internal refactors, bug fixes restoring documented behavior, or test-only changes.

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
- **Options Considered** — When the design space has more than one defensible answer, present 2–3 options to the user with trade-offs (cost, complexity, maintainability, blast radius), pick one, and record the decision in Design Decisions. Skip this section when the answer is obvious — it earns its keep when the orchestrator's instinct could plausibly be wrong.
- **Approach** — High-level strategy.
- **Design** — Detailed design (architecture, file structure, data flow).
- **Business Rules (Testable Assertions)** — Numbered WHEN/THEN assertions. Trace each to an existing requirement or mark NEW.
- **Test Scenarios** — Concrete scenarios for each rule with inputs and expected results.
- **Domain Model Behavioral Design** — Computed properties, visibility flags, reactive rules, validation rules.
- **Design Decisions** — Timestamped "chose A over B because C" entries. Grows during implementation as decisions get made.
- **Skills** — Every skill needed at Step 3 with its path and why. Not listed → not loaded at implementation.
- **Implementation Steps** — Ordered steps.
- **Acceptance Criteria** — What "done" looks like for **this plan**.
- **Companion Plans** — Other plans (in this todo) or sibling todos covering work outside this plan's scope. Each entry links to a real plan or todo file (see "Multi-Plan Todos — Decompose Up Front, Don't Defer"). Grows during implementation as the orchestrator notices work that belongs elsewhere.
- **Dependencies** and **Risks**.

### Plan detail vs. implementation — the plan is the design, not the diff

The plan describes **what** changes, **where**, and **why**. The diff is the **implementation**. Drift between these two is the most common bloat in this skill: in high-effort mode the orchestrator transcribes the implementation in markdown — full method bodies, before/after blocks, full Razor markup, "Item 1 / Item 2 / Item 3" code dumps. The plan doubles in length without doubling in design value, and Step 3 becomes "type out what's already in the plan" instead of implementing the design.

**Code in a plan earns its keep when it is:**
- A non-obvious algorithm (cascade logic, state machine, parsing, ordering rules)
- An interface or signature contract that downstream code binds to (~5–10 lines)
- A *single* example of a recurring pattern, not all instances of it
- Pseudocode the implementer must follow exactly

**Code in a plan is bloat when it is:**
- Before/after blocks for mechanical refactors — the diff itself is the artifact
- Full Razor markup (use the component name + structural description)
- Trivial method bodies that follow mechanically from the design (getters, mappers, constructors)
- "Item 1's code, Item 2's code, Item 3's code" — that's transcription, not design

**The smell-test:** if the orchestrator at Step 3 will copy a code block out of the plan with little or no thought, the block didn't belong in the plan. Either it's so trivial it was needless transcription, or it's an implementation detail that should have surfaced organically at Step 3.

**Length budget by todo type** (guidelines, not gates):
- Bug fix → typically under 300 lines, mostly prose
- Refactor → typically under 600 lines, prose + a few signature blocks
- Enhancement / new feature → typically under 1,000 lines, with the largest code blocks reserved for new contracts and non-obvious algorithms
- Bug-Exposes-Fallacy → similar to Enhancement; the Fallacy section is prose

Plans well past these thresholds should be re-read for transcription smell. If the answer is "yes, the algorithm really is that complex" the size is justified — record that justification in Design Decisions. If the answer is "I was just writing out the diff," trim.

Plan mode (the built-in `Shift+Tab` mode) gets brevity for free because it's read-only — it physically can't dump a 30-line code block. project-todos has no such constraint, so the discipline lives in this principle, the plan-reviewer's Pass B code-density check, and the orchestrator's own judgment.

### Decompose first

Before drafting the plan in detail, ask: *Is this one plan or multiple?*

If multiple, list them in the todo's **Plans** section and create stub plan files (`docs/plans/{plan-N}.md`, status `Draft`, with a one-paragraph problem statement and intended Approach). Then draft the *first* plan in full. The stubs are queued for future Step 3 sessions and get fleshed out before each session.

This is the active mechanism for what people used to call "deferring." The plan that gets implemented now is focused; the work for next session is captured as its own real planning artifact, not a bullet point hoping to be remembered.

Link the plan and todo (update both files). Set plan status to `Draft`.

## Step 2: Plan Review

**Purpose:** Catch contradictions and gaps in the draft plan before implementation. Two failure modes get caught here: (a) the plan conflicts with a documented business rule nobody remembered, and (b) the plan misses 5+ call sites, a save path, or a UI binding because the design was sketched without a real codebase pass.

Both passes used to be separate steps with separate agents; they are now one. The reviewer reads the plan once, does both passes in one context, and returns one verdict with subsection findings the orchestrator can route correctly.

Invoke **plan-reviewer** with:
- The todo file path and plan file path
- The project's requirements locations (from CLAUDE.md)
- Instruction: "Review this plan in two passes. Pass A: against the project's documented business requirements — surface contradictions, gaps, implicit dependencies. Pass B: against the actual codebase — verify feasibility, find missed call sites, check domain-logic placement, flag framework-correctness risks, check invariants. Return one verdict (APPROVED / CONCERNS / REJECTED) with findings split by pass."

**When to run:**
- **Default yes** for Enhancement and Bug-Exposes-Fallacy todos
- **Default yes** for any plan that touches multiple aggregates, introduces new patterns, or renames/refactors widely-referenced types
- **Skip** for one-file bug fixes with an obvious blast radius and no business-rule impact (record in Skipped Steps with reason)

**When the reviewer reports back:**

The orchestrator writes a summary to the todo's **Plan Review** section (verdict, date, requirements-pass findings, codebase-pass findings, recommendations).

**If REJECTED:** Fundamental issues with the Approach itself. Rewrite affected plan sections with the user, then re-invoke.

**If CONCERNS:** Present findings to the user. Orchestrator and user update the plan to address each concern. Re-invoke the reviewer. Repeat until APPROVED (or the user explicitly accepts a concern as out-of-scope).

**If APPROVED:** Set plan status to `Approved`.

**If Skipped:** Skip is recorded in the todo's Skipped Steps list. Set plan status to `Approved`.

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

**Optional: tests-first.** When the plan's Test Scenarios are concrete and the rule under test is well-defined, write the failing tests for those scenarios before the production code, run them to confirm they fail for the expected reason, then implement until they pass. The plan already inventories Test Scenarios — capitalizing on them as a tests-first gate cheaply catches "rule was wrong" and "test was tautological" before you've committed to an implementation. Skip when the rule is exploratory or the test surface isn't clear yet. Not a hard gate; use judgment.

**Worktrees.** If the project uses git worktrees, the `docs/todos/` and `docs/plans/` directories must be in the worktree's tracked tree (or in `.worktreeinclude` for tools that need it). The plan file is the contract for Step 3 — losing it because the worktree didn't include it is a real footgun. Verify before starting Step 3 in a worktree.

### The Plan Is Sacred Once Implementation Begins

Once Step 3 starts, the plan body — Overview, Current Behavior Map, Out of Scope / Invariants, Approach, Design, Business Rules, Test Scenarios, Domain Model, Implementation Steps, Acceptance Criteria — is **frozen**. Rewriting it post-hoc to match what got built is plan laundering — it erases the intent-vs-reality gap that the graded review needs to see.

Only **append-only** sections may be updated during/after Step 3: Design Decisions, Companion Plans, Plan Amendments, the todo's review sections (Plan Review, Graded Review, Documentation), and status fields.

**If a major issue surfaces during or after implementation** (design doesn't work, an invariant has to break, a Business Rule was wrong, the Approach is infeasible), stop and present the user three options — don't pick:

1. **Tweak plan + implementation.** Record the change as a dated **Plan Amendment** entry (append-only — do not edit the original Approach/Design text). Continue.
2. **Revert and restart.** Revert the code. Original todo gets a Results section noting why it was reset; a fresh todo/plan begins the cycle.
3. **Ship as-is, spawn a new plan or sibling todo.** Current implementation completes; the unaddressed issue becomes a new plan file in this todo (or a sibling todo) linked from Companion Plans. Graded review sees the gap honestly.

Picking option 1 unilaterally — quietly editing Approach or Design — is the failure mode. Always present the three options.

**If out-of-scope tests fail**, stop. Present: "Test X in area Y started failing, outside the current task. (1) fix root cause, (2) add to bug list, (3) investigate further?"

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

**If Grade A:** Set plan status to `Reviewed`. The grade letter is in the Graded Review entry. Proceed to Step 5 (or Step 6 if docs are skipped).

**If Grade B or C:** Plan status stays at `Awaiting Review` until the user acknowledges. Present category grades and "to reach A" suggestions to the user. The user acknowledges:
- **Accept the grade** — proceed as-is. The user owns the decision.
- **Address specific items** — orchestrator fixes in conversation with user, then re-invokes code-reviewer for re-grade. Append the new grade entry (don't overwrite).

A grade below A is not a blocker by itself. The user's acknowledgment is the gate. Once the user accepts (any grade), set plan status to `Reviewed`.

## Step 5: Documentation (Optional)

**Purpose:** Update project business requirements documentation to reflect what was implemented.

Skip if the change doesn't affect documented business rules (internal refactor, bug fix restoring documented behavior, test-only).

The orchestrator handles this directly — no agent. Inputs needed (plan, todo, the Plan Review section's requirements-pass findings, what was implemented) are already in conversation context. With the user, work through:

1. **Identify affected docs.** From the Plan Review's requirements pass and the implementation summary, list which requirements docs need updates: new rules to add, existing rules that changed, gaps that were filled.
2. **Edit the docs.** Make the edits in conversation with the user. Match the project's existing format (assertion numbering, headers, terminology). For new rules, link back to the plan's numbered Business Rules.
3. **Source code touch-ups (if needed).** XML doc comments on modified domain code, sample code referenced by the docs, anything else the docs cite. Build and test after.
4. **Record what changed.** Write a summary to the todo's **Documentation** section: files updated, rules added/changed/filled.

### General documentation (rare)

If the plan identifies non-requirements docs (README, API docs, migration guides), invoke a project-specific docs agent (or `docs-writer`) for those. Most todos don't need this.

Set plan status to `Documented`.

## Step 6: Completion of *the current plan*

A todo can have multiple plans. This step completes **one plan**. The todo itself only reaches `Complete` when every plan in it is at `Complete` or `Won't Do`.

1. Verify the last Graded Review entry exists and the user has acknowledged the grade.
2. Verify documentation is complete (or was skipped with reason).
3. **Surface the plan sequence.** Walk the plan's Companion Plans list and the parent todo's Plans section. Confirm every linked plan and sibling-todo file exists. Produce the **Plan Sequence** callout (see below) and paste it into the todo's Results / Conclusions section AND present it to the user as the PR-stage summary.
4. Update **this plan's** status to `Complete`. Move it to `docs/plans/completed/`.
5. Update the parent todo:
   - If every plan in the todo is now `Complete` or `Won't Do` → set todo status to `Complete`, fill in the Results / Conclusions section (including the Plan Sequence callout), move to `docs/todos/completed/`.
   - Otherwise → todo stays `In Progress`. Note in Results that this plan finished and which plan(s) remain. The PR for this plan still ships; the next plan starts a new Step 3 session against the same parent todo.

### Plan Sequence Callout (PR-stage)

This is the artifact that surfaces remaining work to the user before the PR ships. Format it as a copy-pasteable block:

```
## Plan Sequence

Plans for this todo (`docs/todos/{todo-name}.md`):
- [x] `docs/plans/{plan-1}.md` — Complete (Grade A)
- [ ] `docs/plans/{plan-2}.md` — Draft, queued for next session
- [ ] `docs/plans/{plan-3}.md` — Draft, queued

Sibling todos created from this work:
- [ ] `docs/todos/{sibling-name}.md` — Draft

(Or "Single-plan todo, no sibling todos — fully self-contained." when there's only one plan and nothing spawned off.)
```

The callout is mandatory at completion **of every plan**, even when there's only one plan and the todo is closing out cleanly. The point is to give the user a final at-a-glance reminder of what's done, what's queued, and what spawned off. Cumulative scope across many todos is what bites later — every completion surfaces it.

## Resuming Mid-Workflow

Read the todo and any linked plan. Check plan status:

| Plan Status | Next Step |
|-------------|-----------|
| Draft | Step 2 (Plan Review). If the latest Plan Review entry shows REJECTED or CONCERNS, address with the user and re-invoke. When APPROVED, set to `Approved`. |
| Approved | Step 3 (Implementation) — load plan, skills, CLAUDE.md in fresh context. |
| In Progress | Step 3 — continue implementation. |
| Awaiting Review | Step 4 (Graded Review). |
| Reviewed | Last Graded Review entry has the verdict letter. If user acknowledged → Step 5. If not → present to user. |
| Documented | Step 6 (Completion). |
| Complete | Nothing — work is done. |

To find the latest verdict at any status, read the most recent entry in the relevant todo section: Requirements Review, Plan Review, or Graded Review.

Full reviewer findings from prior runs live in the todo sections (Plan Review, Graded Review, Documentation). No other state to load.

## Plan Status Values

`Draft` · `Approved` · `In Progress` · `Awaiting Review` · `Reviewed` · `Documented` · `Complete`

Status tracks **workflow position**, not verdict. Verdicts (Vetoed / Concerns / Grade A / B / C) live in the latest review section of the todo, where they belong — that's the audit trail. Status only answers "what step are we on?"

- `Draft` — Plan written, no reviews yet (covers pre-Step 2 and any pending re-review during Step 2 / 2.5).
- `Approved` — Plan Review landed at APPROVED (or was skipped). Ready for Step 3.
- `In Progress` — Step 3 implementation underway.
- `Awaiting Review` — Implementation done, Step 4 pending.
- `Reviewed` — Step 4 graded review complete and the user has acknowledged the grade. Verdict letter is in the latest Graded Review entry.
- `Documented` — Step 5 done (or skipped with reason).
- `Complete` — Step 6 done; todo and plan moved to `completed/`.

## Todo Status Values

`In Progress` · `Complete` · `Blocked`

## Best Practices

1. **The plan is the contract.** Step 3 implementation starts in a fresh context with only the plan. If something is missing from the plan, that's a signal to improve the plan, not to preserve context.
2. **Once implementation starts, the plan body is sacred.** See "The Plan Is Sacred Once Implementation Begins" in Step 3. Only append-only sections update during/after Step 3; major issues get the three-options protocol, never an in-place rewrite.
3. **Current Behavior Map before design.** Document how it works today before designing how it will work. This catches contradictions earlier than any review.
4. **Out of Scope is a commitment.** If you find yourself changing something on the list, stop. Either remove it from the list (with user agreement) or back out the change.
5. **Graded review is honest, not punitive.** A B or C grade is useful information. The user decides whether to address it. Don't treat A as the only acceptable outcome — treat the suggestions as value.
6. **Re-reviews append, they don't replace.** Every Graded Review run creates a new entry. History matters.
7. **Agents return findings, orchestrator writes summaries.** If an agent's 2000-word response has something worth keeping, paste the relevant section into the todo. Otherwise let it go.
8. **Skip with intent.** Conversational skip is fine, but record it. A skipped Plan Review six months later without context is a mystery.
9. **Decompose into multiple plans, don't defer.** When work is bigger than one coherent plan, draft additional plan files (in this todo) or sibling todos up front. The act of creating the plan/todo file IS the capture mechanism — bullet-point "we'll come back to this" notes get lost. See "Multi-Plan Todos — Decompose Up Front, Don't Defer."
10. **Worktree-aware.** If working in a git worktree, confirm `docs/todos/` and `docs/plans/` are tracked in the worktree before starting Step 3. The plan is the contract for fresh-context implementation — losing it because the worktree didn't include it costs a session.
11. **The plan is the design, not the diff.** In high-effort mode the orchestrator drifts toward transcribing the implementation in markdown — full method bodies, before/after blocks, "Item 1's code, Item 2's code." Catch yourself: if a code block in the plan would be copied verbatim at Step 3 without thought, it's bloat. Use prose, file paths, signatures, and code only for non-obvious algorithms or interface contracts. See "Plan detail vs. implementation" in Step 1.

## Reference Files

- `references/todo-template.md` — todo template
- `references/plan-template.md` — plan template (framework-agnostic)
- `references/plan-template-neatoo.md` — extra Domain Model Behavioral Design section for Neatoo / zTreatment-style projects (computed properties, visibility flags, reactive rules, validation rules). Append to the base template when the project uses Neatoo.
- `references/rubric.md` — the seven-category rubric for graded review, with A/B/C criteria and confidence scoring on findings
- `references/rubric-ztreatment.md` — project-specific framework-correctness check list for zTreatment (Neatoo / RemoteFactory / KnockOff / EF UTC / no reflection / no interface-to-concrete casts). Loaded by code-reviewer alongside the base rubric when reviewing zTreatment.

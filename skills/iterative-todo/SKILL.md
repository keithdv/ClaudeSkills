---
name: iterative-todo
version: 0.1.0
description: This skill should be used when the user asks to "create an iterative todo", "iterate on this", "start a small plan", "abandon this plan", "next plan in <todo>", "log a discovery", or "convert to iterative". Use for discovery-heavy, exploratory work where multiple small plans (some likely abandoned) are expected and the durable container is the todo, not any single plan. Skip for bounded, well-understood scope — use the project-todos skill instead. Skip for single-session tasks or trivial fixes.
---

# Iterative Todo, Plans, and Discovery Workflow

Manage exploratory, discovery-heavy project work as a durable **todo** containing many small **plans**. Plans are cheap, possibly wrong, and possibly abandoned. The todo carries cumulative learning across plans via an append-only Discovery Log.

## When to Use This Workflow

Choose `iterative-todo` over `project-todos` when:

- The work is exploratory — gotchas are expected to surface during implementation.
- The scope shape is uncertain — "we'll know more after the first attempt."
- Multiple small attempts are likely, including ones that get abandoned.
- The cost of a speculative mega-plan is higher than the cost of churn across small plans.

Choose `project-todos` instead when scope is bounded, well-understood, and best served by one comprehensive plan reviewed up front.

Skip both for single-session tasks, trivial fixes, or work that fits in built-in plan mode (`Shift+Tab`).

## Core Principle 1: The Todo Is the Durable Artifact

In `project-todos`, the **plan** is durable — designed exhaustively, reviewed, then executed. In `iterative-todo`, the **todo** is durable. Plans are working artifacts: small, drafted quickly, executed quickly, sometimes abandoned. The todo's **Discovery Log** and **Plan Index** carry the narrative across plans so abandoned attempts inform future ones instead of being forgotten.

## Core Principle 2: The Todo Is the Goal. Plans Are Pieces of It.

A todo has one focused goal. Plans are how the goal gets tackled — piece by piece, in order, with the order itself being a working hypothesis.

The goal is defined **before** the todo file exists. Once the goal is clear, the todo's first workflow step is **Discovery & Initial Plan Split**: analyze the affected code, decompose the goal into 2–6 plan stubs (one-paragraph Scope each), and queue them in the Plan Index as `Draft` rows. The split is a **guestimate** — directional, not a contract. Plans get refined, reordered, replaced, or abandoned as discoveries come in.

This means a discovery is never just a local question about the current plan. A discovery brings the **entire todo** back into scope: does the Plan Index still hold? Should queued plans be reordered, dropped, or added? Has the goal itself shifted? The discovery protocol's fourth option (**Re-split**) is the explicit hook for this whole-todo re-evaluation.

### What the Orchestrator Does

- Authors all todo and plan content
- Drafts the next plan as the smallest viable next step
- Implements in conversation with the user
- Logs every discovery to the todo's Discovery Log
- Decides (with user) to amend / abandon / defer when a discovery hits
- Invokes agents for per-plan code review and final reviews
- Writes agent findings into the todo

### What Agents Do

- Review, grade, document
- Return findings; never write to todo or plan files
- Never set status

## Directory Structure

```
docs/todos/{todo-name}/
  todo.md                          # goal, acceptance, out-of-scope, Discovery Log, Plan Index
  plans/
    001-{short-name}.md
    002-{short-name}.md            # may be Abandoned — kept with reason
    003-{short-name}.md
  reviews/
    001-code-review.md             # per-plan, lightweight
    003-code-review.md
    final-graded-review.md         # at the end
    documenter-review.md
```

One folder per todo. Plan numbering is **monotonic** — abandoned plans keep their number so cross-references in the Discovery Log stay stable. Reviews live alongside the plan they cover.

## Reused Sub-Agents

Same agents as `project-todos`, invoked at different cadences:

- **`plan-reviewer`** — optional per plan; default skip. Opt in only for sharp edges (cross-aggregate, schema migration, public API, security, irreversible changes).
- **`code-reviewer`** — encouraged per plan (lightweight); mandatory once at the end (graded, full arc).
- **`business-requirements-documenter`** — invoked once at the end, after acceptance criteria are met.

## Status Values

**Todo:** `In Progress` · `Complete` · `Blocked`

**Plan:** `Draft` · `In Progress` · `Done` · `Abandoned`

Verdicts (Grade A/B/C, plan-review verdicts) live in the relevant review file, not in status fields.

## Workflow

### Prerequisite — Define the Goal (Conversational)

Before any file exists, the user and orchestrator define the goal. What problem is being solved, what success looks like, what's in and out of scope. This is conversation, not a file. The todo file is not created until the goal is clear enough to write down.

No empty-shell todos. If the goal isn't crisp, keep talking — don't open a todo just to have one.

### Step 1 — Discovery & Initial Plan Split

Analyze the affected code with the user. Trace the relevant aggregates, services, UI surfaces, and integration points. Identify the natural seams where the goal decomposes.

Then draft the **initial plan split** — a guestimate of how the work breaks into pieces. Aim for 2–6 plan entries, each a single-paragraph Scope describing one focused chunk of the goal. The split is directional, not a contract; entries will be reordered, replaced, or abandoned as discoveries come in.

Create the todo file in `docs/todos/{todo-name}/todo.md` using `references/todo-template.md`:

- **Goal** — one paragraph, written from the conversation.
- **Acceptance Criteria** — observable, testable. The exit gate for the whole todo.
- **Out of Scope** — bullets; what this todo will not touch.
- **Plan Index** — populated with the initial split. Each row points at a stub plan file.
- **Discovery Log** — empty (the first entry comes during implementation).

For each entry in the initial split, create a stub plan file in `plans/` with status `Draft`, the next monotonic number, and **only the Scope paragraph filled**. Steps and Acceptance are left empty — those get filled at Step 2 when the plan's turn comes.

Set Type, Status `In Progress`, Priority, today's date.

**The initial split is a guestimate, not a commitment.** A plan that turns out to be wrong gets abandoned with a reason; a plan that needs to split further gets re-scoped at Step 2; new plans get added to the index when discoveries surface them. The point of the initial split is to give the first plan context for what comes after, not to lock in the trajectory.

### Step 2 — Draft Next Plan

Pick the next plan to work on — typically the next `Draft` row in the Plan Index whose Scope is still just a stub. Flesh it out:

- **Scope** — already drafted at Step 1; refine if discovery has shifted what this plan should cover.
- **Steps** — ordered bullets, concrete edits. Cap at ~10. Longer means the plan is too big — split into a follow-up plan and queue the new one in the Plan Index.
- **Acceptance** — what "this plan is done" looks like (build/test green, specific behavior).
- **Plan Amendments** — empty at draft time; append-only during implementation.

A plan covers **one concrete deliverable** — typically hours of work. A plan does not duplicate the todo's Goal / Acceptance Criteria / Out of Scope; those live on the todo and the plan inherits them.

If the work needs a new plan that wasn't in the initial split, create a fresh stub plan file (next monotonic number, status `Draft`, Scope filled) and add it to the Plan Index before drafting Steps. New plans always go through the Plan Index — no orphan plan files.

### Step 3 — Plan Review (Optional)

Default: skip. Opt in when the plan touches:

- Cross-aggregate behavior
- Schema migration
- Public API or contract change
- Security-sensitive code
- Anything irreversible

When opted in, invoke **plan-reviewer** with the todo and plan paths. Write the verdict summary to a file under `reviews/{NNN}-plan-review.md`. If REJECTED or CONCERNS, address with the user, re-invoke if needed.

When skipped, record the skip in the todo's **Skipped Steps** with a one-line reason.

### Step 4 — Implement

Work the plan's Steps in order, in conversation with the user. Run tests at natural checkpoints.

**When a discovery hits during implementation**, stop and apply the **discovery protocol**. A discovery is not just a question about the current plan — it brings the **whole todo** back into scope. The Plan Index, queued plans, and even the goal may need to shift.

1. **Append a Discovery Log entry to the todo** — date, plan ID, one sentence of finding, decision (amend / abandon / defer / re-split), follow-up plan ID(s) if any.
2. **Choose with the user**:
   - **Amend** — small correction. Add an entry to the current plan's `Plan Amendments` section. Plan continues. Plan Index unchanged.
   - **Abandon** — current plan is no longer the right path. Set plan status to `Abandoned`, fill the **Abandonment Reason** field, update the Plan Index. Drop into Step 2 to draft a replacement plan with the next monotonic number.
   - **Defer** — finish the current plan as scoped, queue a follow-up plan as a new `Draft` row in the Plan Index.
   - **Re-split** — discovery is significant enough that the **Plan Index itself needs to change**. Reorder queued plans, drop ones that no longer apply, add new ones with stub Scope paragraphs. The current plan may continue, abandon, or amend separately — record both decisions in the Discovery Log entry. If the goal itself has shifted, update the todo's Goal / Acceptance Criteria with the user, and note the goal change in the Discovery Log.

**Never silently expand a plan's scope or quietly add work.** A discovery either amends, abandons, defers, or triggers a re-split — those are the only four options, and the choice is recorded. Re-split is the explicit hook for "this changes more than just the current plan."

When the plan's Steps are complete and Acceptance is met, set plan status to `Done`.

### Step 5 — Per-Plan Code Review (Encouraged)

Invoke **code-reviewer** with the plan and todo paths. Ask for a lightweight review focused on the plan's deliverable: did it land cleanly, are tests passing, are there obvious issues. No formal grade required.

Write the summary to `reviews/{NNN}-code-review.md`. If findings warrant follow-up work, queue a new plan in the Plan Index — do not amend the now-Done plan.

Skip when the change is trivial (test-only, comment-only, mechanical rename). Record skip in the plan or in the todo's Skipped Steps.

### Step 6 — Loop or Fall Through

After Step 5, check the Plan Index:

- **Plans queued (status `Draft`)** → loop back to Step 2 for the next plan.
- **Plan Index has only `Done` and `Abandoned` plans, no queued work** → fall through to Step 7.

Before falling through, verify Acceptance Criteria on the todo. If any criterion is unmet, draft another plan.

### Step 7 — Final Graded Review (Mandatory)

Triggered when the last in-flight plan goes Done **and** the Plan Index has no queued plans. **The orchestrator prompts the user to confirm the todo's Acceptance Criteria are met.** On confirmation, fire the final review.

Invoke **code-reviewer** with the **whole arc** — the todo, every plan in `plans/`, the Discovery Log, and per-plan reviews. Ask for a graded review against the rubric: traces every Acceptance Criterion through real code, evaluates Discovery Log decisions, grades Scope Discipline against the todo's Out of Scope list.

The rubric is `~/.claude/skills/project-todos/references/rubric.md` (and `rubric-ztreatment.md` for zTreatment-specific framework checks). Both are reused from `project-todos` unchanged — same seven categories.

Write the summary to `reviews/final-graded-review.md`. If Grade B or C, present "to reach A" suggestions to the user. The user acknowledges (accept-as-is or address). Re-invoke code-reviewer for re-grade if items are addressed; append, don't overwrite.

### Step 8 — Documentation Review (Mandatory)

Invoke **business-requirements-documenter** with the todo, all plans, the Discovery Log, and the implementation summary. The documenter identifies new business rules, changed rules, filled gaps, and decisions that emerged across plans, and updates the project's permanent docs.

Write the summary to `reviews/documenter-review.md`. The orchestrator applies any developer-deliverable code touch-ups the documenter requested.

Skip ONLY when the change demonstrably touches no documented business behavior (rare for iterative todos — the surface area is usually broad enough that something is documented).

### Step 9 — Completion

Verify:

- Final graded review exists and the user has acknowledged the grade.
- Documentation review exists (or skip is recorded).
- Plan Index status: every plan is `Done` or `Abandoned`.
- Acceptance Criteria all checked.

Set todo status to `Complete`. Move `docs/todos/{todo-name}/` to `docs/todos/completed/{todo-name}/`. The whole folder moves — plans, reviews, todo.md.

Surface the **Plan Sequence Callout** in the PR description:

```
## Plan Sequence

Plans for this todo (`docs/todos/completed/{todo-name}/todo.md`):
- [x] 001-{name} — Done
- [x] 002-{name} — Abandoned (see Abandonment Reason)
- [x] 003-{name} — Done

Discovery Log: {N} entries across implementation.
Final Graded Review: Grade {A/B/C} (acknowledged).
Documentation: {N} rules added/changed.
```

## Discovery Log Format

The Discovery Log is the anti-forgetting mechanism. Each entry is one bullet, terse, navigational:

```
### YYYY-MM-DD — Plan {NNN}
- **Finding:** [one sentence]
- **Decision:** [Amend | Abandon | Defer]
- **Follow-up:** [Plan {NNN} or "n/a"]
```

The point is searchability and cross-reference, not narrative. Save the long form for the affected plan's Plan Amendments or Abandonment Reason.

## Plan Amendments vs. Abandonment Reason

- **Plan Amendments** (append-only on a plan) — used when a discovery led to **Amend**. The original Scope/Steps stay as written; amendments record what changed and why. The plan continues toward `Done`.
- **Abandonment Reason** (one paragraph on a plan) — used when a discovery led to **Abandon**. The plan stops where it is; status goes to `Abandoned`. Reason captures: what we believed when drafting, what turned out to be true, what the next plan should do differently. The reason is what makes abandonment cheap — the next plan inherits the lesson.

Never delete an abandoned plan. The whole point of the iterative shape is that abandoned attempts remain visible.

## Conversion: project-todos Todo → iterative-todo

Use when an existing `project-todos` todo has turned out to be discovery-heavy mid-flight. See `references/conversion-checklist.md` for the step-by-step. High points:

1. Create the new folder structure (`docs/todos/{name}/plans/`, `reviews/`).
2. Move the existing todo's content into the new `todo.md`, keeping Goal / Acceptance / Out of Scope; add empty Discovery Log and Plan Index.
3. Move existing plan files into `plans/` with their original numbers preserved.
4. Mark each existing plan with current status (`Done` / `In Progress` / `Abandoned`).
5. Seed the Discovery Log from any Plan Amendments / Findings on existing plans (one line each, dated).
6. Build the Plan Index from the plans folder.
7. Move existing review files into `reviews/` keyed by plan number.
8. Carry forward "Deferred Scope" / "Companion Plans" entries as **queued** `Draft` plans in the Plan Index.

After conversion, resume at Step 2 (draft next plan) or Step 4 (continue current implementation), depending on where the work stands.

## Resuming Mid-Workflow

Read `todo.md` and inspect the Plan Index. Find the latest plan with status `In Progress` or `Draft`:

| Plan Status | Next Step |
|-------------|-----------|
| Draft | Step 3 (optional plan review) or Step 4 (implement) |
| In Progress | Step 4 (continue) |
| Done | Step 5 (per-plan code review) if not yet done; else Step 6 (loop or fall through) |
| Abandoned | Step 2 (draft next plan with the next monotonic number) |

If every plan is `Done` or `Abandoned` and the Plan Index has no queued plans → Step 7 (prompt user to confirm Acceptance Criteria).

## Best Practices

1. **Keep plans small.** A plan that takes more than a day to draft and execute is too big — split it. The whole point of iterative-todo is fast feedback between design and implementation.
2. **Log every discovery.** If something surprised you, it surprises future-you reading the todo. One-line Discovery Log entries cost nothing and pay back enormously.
3. **Abandonment is normal.** A plan abandonment is not a failure — it's the iterative shape working. The Abandonment Reason is the deliverable; the next plan is the reward.
4. **Never silently expand scope.** Amend / abandon / defer — pick one explicitly with the user. Quietly growing the current plan is the failure mode this skill exists to prevent.
5. **The todo's Acceptance Criteria are the exit gate.** Not "all listed plans done." Plans come and go; Acceptance defines completion.
6. **Final graded review reads the whole arc.** When invoking code-reviewer for the final review, ensure the agent reads every plan and the full Discovery Log — a review that only looks at the last plan misses the cross-plan story.
7. **Don't amend a Done plan.** Findings post-`Done` go into a new follow-up plan, not into the old plan's Amendments. Plans are sealed at `Done`.
8. **Reuse `project-todos` rubric and templates as-is** where they don't change (rubric, neatoo addendum). Don't fork them — drift between the two skills' rubrics will create confusion.

## Reference Files

- `references/todo-template.md` — todo template (with Discovery Log + Plan Index)
- `references/plan-template.md` — small plan template (Scope, Steps, Acceptance, Amendments, Abandonment Reason)
- `references/conversion-checklist.md` — convert a `project-todos` todo to iterative shape
- `~/.claude/skills/project-todos/references/rubric.md` — seven-category rubric for the final graded review (reused unchanged)
- `~/.claude/skills/project-todos/references/rubric-ztreatment.md` — zTreatment framework-correctness checklist (reused unchanged)
- `~/.claude/skills/project-todos/references/plan-template-neatoo.md` — Domain Model Behavioral Design addendum for Neatoo projects, append to a plan when needed

---
name: iterative-todo
version: 0.10.0
description: This skill should be used when the user asks to "create a todo", "create an iterative todo", "iterate on this", "start a small plan", "plan this work", "design this feature", "abandon this plan", "next plan in <todo>", "log a discovery", "add to the punchlist", "dismiss that finding", "run the punchlist sweep", "resume the todo", "cut the arc branch", "open this plan's PR", or "run the close-out audit". Use for multi-session, design-heavy work where the plan needs to outlive the conversation. Plans are small working hypotheses; punchlist items are one-line fixes worked inline; the todo is the durable container that exits on its Goal, not on an empty queue. Skip for single-session tasks, trivial fixes, or work that fits in built-in plan mode (Shift+Tab).
---

# Iterative Todo, Plans, Punchlist, and Discovery Workflow

Manage multi-session project work as a durable **todo** with a bounded set of small **plans** and a **punchlist** of one-line items. The todo exits when its Goal is met — not when its queue is empty.

## Why 0.8.0 exists, and what later versions add

0.7.0 produced todos that never ended. One 20-day todo issued 41 plan numbers; eight of its nine Acceptance Criteria were met on day 7, and every plan after that came from a reviewer finding, not from the Goal. Reviews returned *more* findings as the code matured, because reviewing an edge-case plan yields edge-cases-of-edge-cases. The causes were structural: the loop exited on "queue empty" while the gates were queue producers; every discovery option produced work and none dismissed; reviewers had findings as their only success shape; and the skill itself called 2× index growth "the system working." 0.8.0 changes the exit condition, adds a tier below plans, adds Dismiss, caps plans and findings, gives reviewers a positive verdict, and restores a close-out grade without the old ratchet.

**0.9.0 adds the branch model.** A todo lives on one **arc branch**; every plan and every punchlist branch PRs into it; the arc PRs into `main` once, when the todo closes. It is the shape LCR ran for forty-five PRs on `lcr-rewrite`, written down so the templates and `/closeBranch` know about it.

**0.10.0 schedules the punchlist.** 0.8.0 assumed punchlist rows are worked inline at the moment of discovery, but on TSR/TSP roughly 80% were born at Step 5 gates — after the plan's diff was under review, which is exactly when working an unrelated row would muddy it — so "inline" never triggered for them. The loop consulted only the Acceptance Criteria and the Plan Index, close-out merely carried open rows forward, and the result was rows surviving whole todos untouched (a one-minute file deletion outlived four gated plans; one row crossed two todos). 0.10.0 gives rows two scheduled moments — Step 2's pull-in triage and one Step 6 sweep — **without** putting the punchlist in the exit condition, which would rebuild the 0.7.0 ratchet: the gates are row producers.

## When to Use

Multi-session, design-heavy work where the plan needs to outlive the conversation — bounded or exploratory. Skip for single-session tasks, trivial fixes, or anything that fits built-in plan mode (`Shift+Tab`).

## Three Tiers

| Tier | Size | Form | Gate |
|---|---|---|---|
| **Todo** | the Goal | Goal, Acceptance Criteria, Out of Scope, Plan Index, Punchlist, Dismissed, Discovery Log | close-out audit + grade |
| **Plan** | hours to a day | `references/plan-template.md` | Step 5 gate, two rounds max |
| **Punchlist item** | minutes to an hour | **one line** — what · where · done-when → `[x]` + commit | none |

Punchlist items are worked inline. One that needs a moment's design gets built-in plan mode (`Shift+Tab`) — a plan that lives in the conversation and dies with it. No file, no review, no log entry. Plan-scoped items live in the plan's Punchlist; cross-plan items in the todo's. Work inherited from a prior arc is seeded into the Punchlist at Step 1, one line per item — never as a ledger of paragraphs.

**Inline has a limit.** Most rows are born at Step 5 gates, after the inline window has closed, so a row that misses its moment is not a failure — it waits for one of its two scheduled moments: Step 2's triage pulls rows lying in the next plan's path down onto that plan, and the Step 6 **sweep** works or dismisses everything still open, once, before the todo's last plan or close-out.

**Most findings are punchlist items or dismissals.** A finding becomes a plan only if it passes the sizing test in the discovery protocol.

## Core Principle 1: Plans Are Prescriptions, Not Implementations

A plan describes **what** needs to be true and **why** — the business outcome, the framework patterns to follow, the invariants to preserve, the acceptance signals that prove it worked. It does **not** describe what the code looks like. Line numbers, signatures, file-by-file edit tables, fallback branches: none of it belongs in Scope, Intent, or Steps. Code-level reality observed at pre-flight goes in **Current State**; code-level decisions made at the keyboard go in **Plan Amendments**. If a step reads like code, compress it to intent.

Plans are not locked when implementation starts. When something surprises the implementer: **stop and ask** when it changes intent, contradicts a constraint, or threatens an acceptance signal; **amend** when it changes details but not intent; **keep going** when it's mechanical.

## Core Principle 2: Tests Are Iterative Too

Plans don't enumerate test cases. Every behavioral Acceptance bullet carries one tier tag — `[unit]`, `[integration]`, `[database]`, `[ui]`, or `[explicit-skip: <reason>]` — and that is the plan's whole test surface. Implementation writes tests at the declared tier. Before the gate, the orchestrator fills the **Test Evidence** map: every bullet → the test that pins it → tier confirmed, or `MISSING — <reason>`. The test-reviewer checks that the map is honest — cited tests exist, assert the behavior, sit at the declared tier. The user picks the closing bar. This map has been the single most successful mechanic in the workflow; it stays.

`[ui]` is the one tag that does not invent its own criteria. It is the browser/bench tier, and a `[ui]` bullet **cites a user-confirmed use case** from the catalogue rather than writing acceptance for itself (Core Principle 6). If the bullet needs a case the catalogue does not hold, that is a proposal to the user — not something the plan authors on its own. A `[ui]` bullet citing a Rare Edge Case does not gate the plan.

## Core Principle 3: The Todo Is Durable. The Conversation Is Not.

Write decisions, amendments, and status changes to disk at natural checkpoints. After a session break or a context compaction, re-read `todo.md`, the active plan, and the last few Discovery Log entries before continuing. The files are the source of truth.

## Core Principle 4: The Goal Is the Exit

The todo's Acceptance Criteria are the exit gate. **When every criterion is met or explicitly accepted as a gap, the todo goes to close-out — regardless of what is queued.** Queued Drafts at that moment become the Follow-on list (one line each); if anyone wants them, they are a new todo. A queue never keeps a todo open.

Every plan and every discovery must name the **Acceptance Criterion number** it serves. None → it is not this todo's work: dismiss it, or (rarely) open a sibling. "It advances the Goal" is not an answer; "it serves AC-4" is.

Plan IDs (`{ID}-{NNN}`, e.g. `OVL-025`) are the canonical cross-reference form — never bare `Plan 025`.

## Core Principle 5: Findings Are Cheap; Plans Are Not

A reviewer finding costs the reviewer nothing. A plan costs a draft, a pre-flight, an implementation, a gate, and a review file. The workflow's job is to make sure the second is only paid when it is worth paying — and the default answer is that it is not.

**Dismiss is the expected outcome for most findings**, and it is recorded in one line so the next reviewer does not re-raise it. **Theoretical findings are not triaged at all.** A finding must name a user-reachable path, an observed failure, or a live caller; one that cannot is listed under "Theoretical" by the reviewer and goes no further.

**The orchestrator is the biggest source of findings** — most of a todo's discoveries are the orchestrator noticing things while implementing. Apply the criterion test and the reachability test *before writing anything down*, not after. Do not open a Discovery Log entry to think; think in conversation and log the decision. Do not justify a plan's existence with prose — if it takes four hundred words to defend, it should not exist.

### What the Orchestrator Does

Authors all todo and plan content; drafts each plan as the smallest viable next step at the intent level; runs recon and pre-flights; implements in conversation with the user; triages every finding (dismiss / punch / amend / queue / abandon / re-split) and records the decision; assembles reviewer briefs and writes their findings into `reviews/`; declares the plan cap and stops when it is hit.

### What Agents Do

Review and audit; return a verdict and a capped set of findings, each with reachability stated; never write to todo or plan files; never set status; never re-raise a dismissed finding.

## Core Principle 6: Use Cases Are the User's, and Tiers Bound the Search

The orchestrator does not decide what counts as a use case, and does not decide what blocks. **Regular, repeatable use cases belong to the user**: the orchestrator proposes, the user confirms, and only then is the case captured in the project's **use-case catalogue** — the durable, cross-plan record of how the application is actually used. *(In zTreatment that catalogue is `docs/production-validation/`.)* A catalogue entry the orchestrator filed on its own authority is a gate nobody asked for.

Every catalogue entry carries exactly one tier:

| Tier | What it means | Gates? | Run when |
|---|---|---|---|
| **Happy Path** | Must work for the application to be operational. If it fails, the application cannot achieve its goal in day-to-day use. | **Yes** | Every run |
| **Edge Case** | The user might not even notice these — they surface only on a certain mistake or usage pattern. Failing one is a **user-experience failure**. | **Yes** | Every run |
| **Rare Edge Case** | Technical-only concerns. The user wouldn't know how to describe them. | **No** | **Skipped by default.** The orchestrator may *recommend* including them when a change is significant or lands in their area; the user decides. |

**The tiers do two jobs with one mechanism.**

- **They contain the search.** The confirmed catalogue is the boundary of what a validation run looks for. The orchestrator does not widen it mid-run, does not promote something it found into a gate, and does not treat a self-generated concern as blocking. A Happy Path or Edge Case failure stops the work that provoked the run; a Rare Edge Case failure is recorded and routed, and stops nothing.
- **They capture use cases across plans.** A use case outlives the plan that discovered it. Confirmed cases accumulate in the catalogue instead of scattering through individual plans' acceptance bullets, where they die when the plan closes.

**What the catalogue holds.** Browser-driven cases and hardware/bench cases — the application as a person actually uses it, something a human could be handed and asked to perform. **Unit, integration and database cases do not go in the catalogue**; they stay in the plans' Test Evidence tiers (Core Principle 2). The two are complementary, not alternatives.

**A run is boxed before it starts and runs to the end.** The charter names the entries it will execute — by default every Happy Path and Edge Case in the area, Rare Edge Cases only when the user has said so. A finding, even a real and reachable one, is written into the run record and **the run continues to the next entry**. Whether a finding blocks is the user's call, made at the debrief with the whole run in view. A new case that suggests itself mid-run is raised at the debrief and enters the catalogue only after confirmation — never inserted into the run that thought of it.

**Why this principle exists.** A five-entry bench run stopped after two because the orchestrator kept promoting its own findings to blockers; told to stop doing that, it then closed the arc on its own judgment. Same substitution of the orchestrator's call for the user's, in both directions. Neither the search nor the gate was bounded by anything the user had confirmed.

## Directory Structure

```
docs/todos/{ID}-{todo-name}/
  todo.md                          # goal, criteria, out-of-scope, Plan Index, Punchlist, Dismissed, Discovery Log
  plans/
    001-{short-name}.md
    002-{short-name}.md            # may be Abandoned or Retired — kept with reason
  reviews/
    001-test-review.md             # per-plan gate record
    001-build.log / 001-test.log   # pre-flight logs
    003-plan-review.md             # only when opted in
    003-code-review.md             # only when opted in
    close-out-audit.md             # at the end
```

Plan numbering is monotonic; abandoned and retired plans keep their numbers. **All review output lives in `reviews/`** — never inlined into the Discovery Log or a Status cell.

## Branches and PRs

A todo lives on one **arc branch**. Code reaches the arc only by PR, and the arc reaches `main` by one PR at the end.

| Branch | Name | Cut from | PRs into | Lives from |
|---|---|---|---|---|
| **Arc** | `{id}-arc` | `main` | `main` | Step 1 to Step 8 |
| **Plan** | `{id}-{NNN}-{short-name}` | the arc | the arc | Step 2 to Done |
| **Punchlist** | `{id}-{short-name}` | the arc | the arc | while its rows are worked |

`{id}` is the todo ID in lowercase. The todo header records the arc's actual name, and the header wins over the default — `lcr-rewrite` is LCR's arc.

- **Plan branch.** Cut from the freshly pulled arc when the stub is picked up at Step 2, so the draft, the pre-flight, the implementation, the gate record, and every `todo.md` edit the plan causes land in one PR. Plan-scoped punchlist rows ride it. Two small plans on one seam may share a branch — name it after the lower number and title the PR with both.
- **Punchlist branch.** For todo-level rows worked between plans, and for the Step 6 sweep. Several rows may ride one branch; each closes with the PR number.
- **PR title:** `{ID}-{NNN}: <plan title>`; `{ID}: <what>` for a punchlist PR; `{ID}: <todo title>` for the arc. The body says what landed, what the gates found, and what is deliberately still open — it links the plan file rather than repeating it.
- **The orchestrator opens PRs; the user merges them.** A plan's PR opens at Done — after the gate, never before. AZM-007's PR merged before either gate ran, and the gate then found a sacred-test mapping that had been claimed rather than shown.
- **After every merge, `/closeBranch`.** It follows the PR's base: closing a plan branch lands on the arc, freshly pulled, and the next plan branches from there; closing the arc lands on `main`. The next plan waits for that — stacking on an unmerged plan branch is the user's call, not a default.
- **The arc takes direct commits for the container only** — the Step 1 creation, a Dismissed row or Follow-on edit between plans, the Step 8 completion commit. Code arrives by PR.
- **The arc need not be deployable between plans; `main` always is.** No plan is shaped to keep an intermediate arc shippable.
- **Sibling todos land on the parent's arc:** `{sibling-id}-{NNN}-{name}` → parent arc, recorded in the sibling's header. RIG's plans landed on `lcr-rewrite`.

## Sub-Agents

Every reviewer returns **a verdict plus a capped list of findings**. Veto-tier findings are always listed in full — they are rare by definition. Callouts are capped at **five**; anything beyond is one line: *"N more, lower priority, not listed."* Each finding states `Reachable by:` (user action / observed failure / live caller); findings that cannot go under **Theoretical** and are not triaged. A clean verdict is a complete, expected result — reviewers do not manufacture findings to fill a section.

**Veto-tier means exactly two things:** the work contradicts a documented rule or excluded feature, or it breaks the build / a sacred test / any test. Everything else is a callout, and **callouts never block**.

- **`test-reviewer`** — the mandatory Step 5 gate. Checks that every Acceptance bullet has a real test at its declared tier, that cited tests assert the behavior rather than pass vacuously, that no sacred test was weakened, and that the logs are green. It does **not** hunt for edge cases the plan did not name. Returns CLEAN / CONCERNS. Skip only for trivial plans (test-only, comment-only, mechanical rename), recorded in Skipped Steps.
- **`plan-reviewer`** — opt-in at Step 2 for sharp edges (cross-aggregate, schema migration, public API, security, irreversible). Its diagnoses are reliable; its prescriptions are advisory.
- **`business-requirements-reviewer`** — opt-in at Step 2 when the plan's intent touches documented business rules or excluded features.
- **`code-reviewer`** — opt-in per-plan pass at Step 5 for behavior-changing plans (CLEAN / CONCERNS), and the mandatory **close-out audit** at Step 7, which produces the grade.

## The Review Brief

Every reviewer invocation is a **brief** assembled by the orchestrator — the balance between front-loading (a fat reading list crowds out the walk that produces findings) and free discovery (the reviewer re-derives what the orchestrator already holds). Five parts:

1. **The object under review** — plan, diff, or evidence map. Read fully.
2. **Distilled context, cited, background-only** — facts the review is not checking. Never launder the object's own claims into this block. For Step 5 gates, the plan's Current State section already is this block — point at it.
3. **Sources of record the object must agree with** — the Discovery Log, the Plan Index, prior review files, **and the todo's Dismissed and Punchlist sections**, so the reviewer does not re-raise what has been decided. Named, not summarized.
4. **Code targets with questions attached** — the question is the budget.
5. **Log paths** (Steps 5 and 7) — reviewers grep them, never re-run builds.

State the budget: `tight` (default) or `deep` (safety-seam or irreversible plans). The close-out audit is exempt from `tight`. Reviewers end with a read report — what they pulled beyond the brief and what went unused — and the next brief trims accordingly.

## Status Values

**Todo:** `In Progress` · `Complete` · `Blocked`

**Plan:** `Draft` · `In Progress` · `Done` · `Abandoned` · `Retired`

- **Abandoned** — wrong path; the Abandonment Reason captures the lesson. Never deleted.
- **Retired** — stopped being needed without failing: folded, superseded, or carved out. One-line reason; Index row kept as a tombstone.
- **Stub deletion** — a stub created and killed within one working session, never past a Scope paragraph, may be deleted if the Discovery Log entry recording the re-split names it.

**A Status cell is a status word plus at most five words.** There is no "In Progress — gates run, findings addressed" status: after two gate rounds a plan is Done, or the user has accepted its leftovers and it is Done. Limbo is a violation, not a state.

## Prose Budgets

These are draft-time validation errors, the same as a bare Acceptance bullet:

| Thing | Budget |
|---|---|
| Plan title | ≤ 8 words |
| Plan file when it enters implementation | ≤ 200 lines (Scope one paragraph; Steps ≤ 10; Acceptance ≤ 8) |
| Todo Goal | one paragraph, ≤ 150 words |
| Acceptance Criterion | one sentence, no parentheticals |
| Status cell | status word + ≤ 5 words |
| Discovery Log entry | ≤ 60 words |
| Punchlist / Dismissed / Follow-on row | one line |

A plan that passes 300 lines with amendments should have been two plans. A criterion that needs a paragraph is being renegotiated — renegotiate it in one Discovery Log entry and rewrite the sentence. Over-budget prose is the rabbit hole showing up on disk.

## Workflow

### Prerequisite — Define the Goal (Conversational)

Before any file exists, the user and orchestrator define the goal: what problem, what success looks like, what is in and out of scope. No empty-shell todos.

### Step 1 — Reconnaissance, ID, Initial Split, Plan Cap

**Reconnaissance first.** Fan out read-only Explore agents to map the seams the goal touches, the patterns the codebase already uses there, and what looks risky. Recon returns seams, patterns, and open questions — not edit scripts. The orchestrator still reads the load-bearing files itself.

**Assign a unique todo ID** — 3–5 uppercase letters; propose 2–3, the user picks. Verify uniqueness against `docs/todos/{ID}-*`, `docs/todos/completed/{ID}-*`, and `docs/todos/_ids.md` if it exists. Retired IDs are never reused.

**Draft the initial split.** Contained todos decompose into **2–6** plan stubs; large restructures **6–12**. Each stub is a plan file with the next monotonic number, status `Draft`, and only the Scope paragraph filled. Every stub names the criterion number(s) it serves.

**Declare the plan cap** in the todo header: `cap = max(ceil(N × 1.5), N + 2)` where N is the initial split. The cap counts plan numbers *issued*, including abandoned and retired ones — churn is what it measures. Issuing a number above the cap is a stop-and-ask: close the todo on what is done, or raise the cap with a one-line reason in the Discovery Log. Do not raise it silently.

**Seed the Punchlist** with any inherited items from prior arcs, one line each. Inherited items that pass the sizing test become Draft stubs and count toward N.

Create `docs/todos/{ID}-{kebab-name}/todo.md` from `references/todo-template.md`. Add the `_ids.md` row in the same change.

**Cut the arc branch** from `main` — `{id}-arc`, pushed with `-u` — and record it in the todo header. The Step 1 commit (folder, stubs, `_ids.md` row) is the arc's first, made directly.

### Step 2 — Draft Next Plan

Pick the next `Draft` stub. **Cut its branch from the freshly pulled arc** — `{id}-{NNN}-{short-name}` — and record it in the plan header; everything this plan touches lands there.

**Triage the todo's Punchlist against this plan's path.** Any open todo-level row this plan's Steps will touch anyway moves down into the plan's own Punchlist and rides the plan branch — proximity is how cheap rows actually get done, and it should be a rule, not luck. Rows outside this plan's path stay put for the Step 6 sweep. Flesh it out per `references/plan-template.md`: Scope (one paragraph, including what it does NOT do), Intent, Framework & Architectural Alignment (patterns named, not reproduced), Constraints & Invariants, Steps (≤ 10 intent-bearing bullets), Acceptance (≤ 8 behavioral bullets, every one tier-tagged). Check the prose budgets. A plan covers one deliverable — hours of work, a day at most.

**Declare the review opt-ins** in the header with a one-line reason each: `Plan-review opt-in` (cross-aggregate, schema, public API, security, irreversible; name `business-requirements-reviewer` when the plan touches documented rules) and `Code-review opt-in` (behavior-changing plans; skip for mechanical work).

When a plan review runs, brief it per **The Review Brief** and write the outcome to `reviews/{NNN}-plan-review.md`. Veto-tier findings are addressed before implementation. Callouts are triaged — dismissed, punched, or amended into the plan — and never carried as open prose.

### Step 3 — Current-State Pre-Flight

Before the first edit, walk the plan's Intent and Steps against the actual code — no edits yet. Record what is there in the plan's **Current State** section, the sanctioned home for line numbers and signatures. Surprises that shift the plan become Plan Amendments before the first edit. Keep it proportionate: minutes, not a re-review of the codebase.

### Step 4 — Implement

Work the Steps in order, in conversation with the user. Run scoped tests at natural checkpoints; the full suite runs once at the Step 5 pre-flight.

**Discovery protocol.** When something surprises you, answer three questions *before writing anything*:

1. **Which Acceptance Criterion does it serve?** Name the number. None → **Dismiss**, or (rarely) a sibling todo.
2. **Is it reachable?** A user action, an observed failure, or a live caller. No → **Dismiss**. "Hardening against a subscriber nobody has written yet" is a dismiss.
3. **How big is it?** Under about half a day, doesn't change a criterion, doesn't open a seam no plan touches → **Punch**. Otherwise it is plan-sized.
4. **Is it a use case the user confirmed?** If the finding is about how the application behaves for a person using it, check the catalogue (Core Principle 6). A confirmed Happy Path or Edge Case entry gates. A Rare Edge Case entry does not. **Something the orchestrator generated that is in no catalogue entry gates nothing** — propose it at the debrief and let the user decide whether it becomes one. Discovering a plausible failure does not make it a blocker; only the user does.

Then record the decision:

- **Dismiss** — one line in the todo's Dismissed section: finding, reason. No log entry.
- **Punch** — one line in the plan's or todo's Punchlist. Work it inline (plan mode if it needs thought) — plan-scoped rows on the plan branch, todo-level rows on a punchlist branch. No log entry.
- **Amend** — the current plan's details change, not its intent. Plan Amendments entry + Discovery Log entry. *The most common logged decision.*
- **Queue** — plan-sized and it passed the criterion test: a new `Draft` stub and Index row, against the cap. Discovery Log entry.
- **Abandon** — the current plan is the wrong path. Status `Abandoned`, reason filled, replacement drafted. Discovery Log entry.
- **Re-split** — the Plan Index itself changes: reorder, retire, add. Discovery Log entry with `Index changes:`.

Only Amend, Queue, Abandon, and Re-split get Discovery Log entries. There is no "Note" decision — an entry that records no decision is a journal, and the log is not a journal.

**When the Goal itself shifts (rare):** stop and ask. Sometimes the right move is a sibling todo. If the Goal genuinely shifts, update Goal and Acceptance Criteria together, note it in the triggering entry, and re-verify queued plans.

### Step 5 — Per-Plan Gate: Test Evidence + Test Review (Mandatory, Two Rounds Max)

**Pre-flight 1 — fill the plan's Test Evidence table.** One row per Acceptance bullet: cited test, tier confirmed, or `MISSING — <reason>`. The gate is not invoked until this exists.

**Pre-flight 2 — run build + test ONCE and pass log paths.** Redirect full output to `reviews/{NNN}-build.log` / `reviews/{NNN}-test.log`. Reviewers grep the logs; they never run build or test themselves.

**Invoke `test-reviewer`** with a brief. It returns CLEAN or CONCERNS with must-cover findings (an Acceptance bullet unpinned, a cited test that asserts nothing, a sacred test weakened, a red log), should-cover findings (a reachable plan-introduced path with no test), and tech-debt (one line each, untiered, capped). Then:

1. **Round 1.** Must-cover plan-related findings are addressed. Should-cover: the user picks. Tech-debt: triaged — punchlist, dismissed, or (rarely, if plan-sized) queued.
2. **Round 2** re-invokes to confirm must-cover closed. **Round 2 is the last round.** Anything still open is punched or accepted with a one-line reason. The plan is Done.
3. Write `reviews/{NNN}-test-review.md` (closing tier, what was added, what was punched, what was accepted and why) and the plan's **Gate Record** — one line per round.

**If the plan opted into code review**, invoke `code-reviewer` for a findings-only pass on the same logs (CLEAN / CONCERNS). Veto-tier findings are fixed before Done; callouts are triaged the same way. Write `reviews/{NNN}-code-review.md`.

A plan reaches `Done` when the gate closes or its leftovers are accepted. Not before, and not later.

**Then open the PR** into the arc — `{ID}-{NNN}: <title>` — and record the number in the plan header and the Plan Index's PR column. The user merges; `/closeBranch` follows.

### Step 6 — Loop, Sweep, or Fall Through

**Check the Acceptance Criteria first.** Every criterion met or explicitly accepted as a gap → **the punchlist sweep below, then Step 7**, regardless of queued Drafts; queued Drafts move to the Follow-on list.

Otherwise, check the Plan Index: a queued `Draft` that serves an unmet criterion → Step 2. No queued Draft serves an unmet criterion → draft one (against the cap), or confirm with the user that the criterion is met after all. **If the plan about to be drafted is the todo's last** — nothing else queued and no unmet criterion beyond its Serves — run the sweep first: its rows are about to lose their final in-path chance, and one of them may gate that plan.

**The punchlist sweep — once per todo.** Cut a punchlist branch and **work or dismiss every open todo-level row** in one batch: no per-row gate, one PR, each row closed with the PR number (a run of related rows may share a short commit). A row only the remaining plan can close (rig evidence, an artifact that does not exist yet) records that explicitly and survives; nothing else does. The sweep is deliberately late — after it, the punchlist stops being a queue and Step 8's "all `[x]` or moved to Follow-on" check is a verification rather than a triage.

Step 2 starts from the arc, freshly pulled — after the previous PR has merged and `/closeBranch` has run.

### Step 7 — Close-Out Audit and Grade (Mandatory)

**On the arc branch, with every plan PR merged** — an open plan PR is a container miss, not an audit input. Run build + test once each (`reviews/final-build.log`, `reviews/final-test.log`) and invoke **code-reviewer** in close-out mode with the whole arc — the todo, every plan, every review file, the log paths. Per `references/close-out-audit.md`, the auditor traces every Acceptance Criterion to code, walks container integrity, spot-checks Test Evidence honesty, greps the logs, and returns a **grade**:

- **A** — every criterion traced to code with evidence; no veto-tier findings.
- **B** — every criterion traced or explicitly accepted as a gap with a reason; no veto-tier findings; gaps on the Follow-on list.
- **C** — a criterion neither met nor accepted, or a veto-tier finding open.

**A and B close the todo.** C does not — and C is not "keep iterating": the user picks one of fix-the-named-thing, accept-the-gap (→ B), or close as `Blocked`. There is no "to reach A" list. The grade is a statement about what was done, not a target for what is left.

Write to `reviews/close-out-audit.md`; a re-audit after fixes appends. C-grade fixes go on a punchlist branch and PR into the arc like anything else.

### Step 8 — Completion & Retro

Verify: the audit exists with grade A or B and the user acknowledged it; every plan is `Done` / `Abandoned` / `Retired`; the Punchlist is all `[x]` or moved to Follow-on — the Step 6 sweep is what made that true, and arriving here with open rows and no sweep is a container miss; every Follow-on row is one line.

**Documentation check:** confirm doc deltas shipped with the behavior they describe. Reconcile any internal-contradiction callouts parked by reviewers. Remaining doc debt goes on the Follow-on list or, if large, to `business-requirements-documenter` ad hoc.

**Follow-on list:** everything this todo did not do — queued Drafts, accepted gaps, unpinned tests. One line each. It is a list, not a commitment; a successor todo that adopts an item writes it as an acceptance bullet there.

**Retro (one paragraph):** what this todo taught about the workflow itself. Route lessons to the project's CLAUDE.md, this skill's backlog, or persistent memory. Include the numbers: plans issued vs. cap, findings dismissed vs. punched vs. queued.

Set status `Complete`. Move the folder to `docs/todos/completed/{ID}-{todo-name}/` and move the `_ids.md` row in the same change. That commit is the arc's last. **Open the arc's PR into `main`** — `{ID}: <todo title>` — the user merges, and `/closeBranch` on the arc lands on `main`.

**The user decides when to commit and merges every PR; the orchestrator opens them.**

## Discovery Log Format

```
### YYYY-MM-DD — {ID}-{NNN} · serves AC-{n}
- **Finding:** [one sentence]
- **Decision:** [Amend | Queue | Abandon | Re-split]
- **Index changes:** [Re-split / Queue only; else omit]
- **Follow-up:** [{ID}-{NNN} or "n/a"]
```

**≤ 60 words.** The long form lives on the affected plan; the entry points at it. No review output, no PR descriptions, no file-change lists. Dismissed and punched findings do not get entries — they have their own one-line homes.

## Punchlist, Dismissed, Follow-on Formats

```
## Punchlist
- [ ] <what> · <where> · done when <observable>            (open)
- [x] <what> · <where> · <commit or PR>                     (closed)

## Dismissed
- {ID}-{NNN} · <finding, ≤ 15 words> · <reason, ≤ 15 words>

## Follow-on   (close-out only)
- <item, one line> · <origin: {ID}-{NNN} or review file>
```

## Plan Amendments, Abandonment, Retirement

- **Plan Amendments** (append-only) — what changed and why. Original Scope/Intent/Steps stay frozen.
- **Abandonment Reason** (one paragraph, required when `Abandoned`) — what we believed, what turned out true, what the next plan should do differently.
- **Retirement note** (one line, required when `Retired`) — where the work went.

## Sibling Todos

For work that surfaced here, does not serve any of this todo's criteria, and is worth keeping. Rare. Gets its own folder and ID per Step 1; the relationship is recorded in both todos, and the sibling's branches PR into this todo's arc. If it is not worth keeping, dismiss it.

## Internal vs. External Contradictions

- **External** — plan contradicts a documented business rule or touches an excluded feature. Veto-tier. Address before implementation or get explicit sign-off to change the rule.
- **Internal** — tension with the parent todo's intent, the plan's own sections, or neighboring plans. Callout-tier. Record, keep implementing, reconcile at Step 8.

## Resuming Mid-Workflow

Read `todo.md`, the Plan Index, and the Punchlist; find the latest `In Progress` or `Draft` plan. The files are the source of truth, not the conversation.

Then `git branch --show-current`. An `In Progress` plan should be on the branch its header names; between plans you should be on the arc. On the arc with a plan `In Progress` → check `gh pr list` before switching — the PR may have merged with the header not yet updated.

| Plan Status | Next Step |
|-------------|-----------|
| Draft (stub) | Step 2 |
| Draft (drafted, pre-flight not done) | Step 3 |
| In Progress | Step 4 |
| Done, no test review | Step 5 |
| Done, gate closed | Step 6 |
| Abandoned / Retired | Step 2, next number (against the cap) |

All criteria met → Step 7.

## Converting an Older Todo

Follow `references/conversion-checklist.md`. A 0.7.0-era todo converts by: adding Punchlist / Dismissed sections; triaging every queued Draft through the discovery protocol (most become punchlist rows or dismissals); declaring the cap at the current issued count; and checking the Acceptance Criteria — if they are met, go to Step 7 now. A 0.8.0-era todo picks up 0.9.0 by recording its arc branch in the header and adding the PR column to the Plan Index — the checklist's last section.

## Best Practices

1. **Plans describe intent; Current State holds reality; Amendments hold keyboard decisions.**
2. **Name the criterion number.** For every plan, every discovery, every finding you keep.
3. **Dismiss freely; punch by default; queue rarely.** The cap is there to be felt. A punch is a deferral to a scheduled moment — Step 2's triage or the Step 6 sweep — not a write-off.
4. **Two gate rounds, then Done.** Leftovers are punched or accepted, never carried as a status.
5. **Don't amend a Done plan.** A post-Done finding is a punchlist item or a Follow-on row.
6. **Review output lives in `reviews/`.** The Index cell stays terse.
7. **Project-specific framework idioms live in the project repo**, not this skill: `<repo>/docs/code-review-calibration.md` (what clean means here) and `<repo>/docs/code-review-rubric.md` (audit overlay).
8. **One arc; one PR per plan; `/closeBranch` after every merge.** Code reaches the arc by PR only, and the arc reaches `main` once.

## Reference Files

- `references/todo-template.md` — todo template (Punchlist, Dismissed, Plan Index, Discovery Log, Follow-on)
- `references/plan-template.md` — plan template (Scope, Intent, Alignment, Constraints, Steps, Acceptance, Current State, Test Evidence, Punchlist, Amendments)
- `references/close-out-audit.md` — audit checklist and the grade for Step 7
- `references/conversion-checklist.md` — convert an older todo to this shape
- `references/plan-template-neatoo.md` — Domain Model Behavioral Design addendum for Neatoo projects

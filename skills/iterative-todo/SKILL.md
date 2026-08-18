---
name: iterative-todo
version: 0.7.0
description: This skill should be used when the user asks to "create a todo", "create an iterative todo", "iterate on this", "start a small plan", "plan this work", "design this feature", "abandon this plan", "next plan in <todo>", "log a discovery", "resume the todo", or "run the close-out audit". Use for multi-session, design-heavy work where the plan needs to outlive the conversation — bounded or exploratory. Plans are small working hypotheses; the todo is the durable container with a Discovery Log and Plan Index. Skip for single-session tasks, trivial fixes, or work that fits in built-in plan mode (Shift+Tab).
---

# Iterative Todo, Plans, and Discovery Workflow

Manage exploratory, discovery-heavy project work as a durable **todo** containing many small **plans**. Plans are cheap, possibly wrong, and possibly abandoned. The todo carries cumulative learning across plans via an append-only Discovery Log.

## When to Use This Workflow

Use for any multi-session design-heavy work where the plan needs to outlive the conversation: exploratory work where gotchas are expected, bounded work large enough to span sessions, work where attempts may be abandoned, work with documented business rules to check against. A bounded todo may have two plans and no abandonments; an exploratory todo may have ten plans and three abandonments. Both are the same shape.

Skip for single-session tasks, trivial fixes, or work that fits in built-in plan mode (`Shift+Tab`).

## Core Principle 1: Plans Are Prescriptions, Not Implementations. Discovery Is Welcome at Every Stage.

A plan describes **what** needs to be true and **why** — the business outcome, the framework patterns to follow, the invariants to preserve, the acceptance signals that prove it worked. A plan does **not** describe what the code looks like.

**This is the failure mode the skill exists to prevent:** writing what looks like a thorough plan but is actually pre-implementation reconnaissance dressed up as design — line numbers, exact method signatures, file-by-file edit tables, fallback branches. That kind of plan is wrong as often as it is right, and the right parts could only be settled at the keyboard anyway. It locks the implementer onto a frozen wrong-shape and makes mid-implementation discoveries feel like "deviating from the plan" instead of the normal way work happens.

The refined rule, learned from real usage: **detail written *before* the design conversation kills plans; detail *recording* a settled conversation or a code walk is fine — but it lives in its own labeled home, never in Scope or Steps.** That home is the plan's **Current State** section, filled at pre-flight (Step 3), where line numbers and signatures are explicitly allowed because they're a record of reality, not a prescription.

**Plans are not locked when implementation starts.** The plan is a working hypothesis that survives contact with code by being amendable. When something surprises the implementer: **stop and ask** when the surprise changes intent, contradicts a constraint, or threatens an acceptance signal; **amend the plan** when it changes details but not intent; **keep going** when it's purely mechanical. Restructuring opportunities can be **named** in a plan ("this seam will probably need to move onto the aggregate") but not **designed** — the implementer finds the right shape while editing.

### What belongs in a plan

- Business outcomes and observable behavior changes — the **intent**.
- Framework patterns and architectural rules being applied — named, not reproduced.
- Invariants and constraints the change must preserve.
- High-level seams the work touches (aggregate X, handler Y, factory Z).
- Acceptance signals a reviewer can check by exercising the system or running tests.

### What does NOT belong in Scope / Steps / Intent

Line numbers, exact method signatures, parameter lists, method bodies, code fences longer than two lines, fallback branches ("if A doesn't compile, fall back to B"), file-by-file edit tables. **Heuristic:** if a step contains a type name with a colon and a line number, or specifies a parameter list, the step is too detailed — compress to intent. Code-level reality discovered at pre-flight goes in **Current State**; code-level decisions made at the keyboard go in **Plan Amendments**.

## Core Principle 2: Tests Are Iterative Too. Coverage Is a Loop, Not a Plan-Time Prescription.

Plans don't enumerate test cases. Plans name **behavioral acceptance signals**, and that's the test surface they're responsible for. Plan-time test enumeration fails symmetrically: over-generous lists get silently trimmed; under-generous lists ship features under-tested. Either way the list lies. The fix is the same as for plans: stop pretending we know the answer at design time.

**The iterative shape for tests:**

1. **Plan-time test surface = Acceptance bullets, each tagged with a tier.** Every behavioral bullet ends with one tier tag — `[unit]`, `[integration]`, `[database]`, `[ui]`, or `[explicit-skip: <reason>]`. Bare bullets are a draft-time validation error. The plan does NOT name test methods or classes — only *which tier* pins each signal, decided once at draft time when the orchestrator can think clearly about what kind of evidence the signal needs.
2. **Implementation writes tests at the declared tier.** A unit test where the bullet declared `[integration]` is a tier mismatch — the bullet is **not pinned** until the right-tier test exists.
3. **Before the per-plan gate, the orchestrator fills the Test Evidence map.** Every Acceptance bullet → the test method that pins it → tier confirmation. Bullets with no test are recorded as `MISSING — <reason>` rather than silently omitted. The gate is not invoked until this map exists. This map has proven itself the single most successful mechanic in the workflow — including catching its own corruption (a self-honest re-walk exposing quarantined tests that were cited as evidence).
4. **The test-reviewer closes coverage.** After implementation, `test-reviewer` reads the map and the actual tests, surfaces gaps tiered must-cover / should-cover / nice-to-have, split plan-related vs. pre-existing tech-debt. The independent eye is not optional ceremony: a self-authored evidence map cannot catch false coverage (a vacuous `Assert.All` over an empty enumerable passes and pins nothing — a real catch from this loop).
5. **The user controls "good enough."** The skill defines the tiers; the user picks the closing bar per plan.

## Core Principle 3: The Todo Is Durable. The Conversation Is Not.

The todo's files outlive the conversation — and they need to, because long sessions get summarized and compacted, and the work spans sessions anyway. Write discoveries, amendments, and status changes to disk **promptly at natural checkpoints**, not at session end; anything that exists only in conversation may not survive. After resuming a session — or after a mid-session context compaction — re-read `todo.md`, the active plan, and the last few Discovery Log entries before continuing. The Discovery Log and Plan Index carry the narrative so abandoned attempts inform future ones instead of being forgotten.

## Core Principle 4: The Todo Is the Goal. Plans Are Pieces of It.

A todo has one focused goal, defined **before** the todo file exists. Plans are how the goal gets tackled, with the order itself a working hypothesis. A discovery is never just a local question about the current plan — it brings the **entire todo** back into scope: does the Plan Index still hold? Should queued plans be reordered, dropped, or added? The discovery protocol's **Re-split** option is the explicit hook for this whole-todo re-evaluation.

Plan IDs (`{ID}-{NNN}`, e.g. `OVL-025`) are the canonical cross-reference form — never bare `Plan 025`. The ID form is what keeps references greppable and unambiguous after todos move to `completed/`, after plans get carved out to sibling todos, and across code comments that outlive the todo. The habit decays without reinforcement; hold the line.

### What the Orchestrator Does

Authors all todo and plan content; drafts each plan as the smallest viable next step at the **intent** level; runs reconnaissance and pre-flights; implements in conversation with the user; logs every discovery; decides (with the user) to amend / abandon / defer / re-split; invokes gate agents and writes their findings into `reviews/`; reconciles internal contradictions at todo close.

### What Agents Do

Review and audit; surface external contradictions (against documented rules) as gating findings and internal contradictions as callouts; return findings; never write to todo or plan files; never set status.

## Directory Structure

```
docs/todos/{ID}-{todo-name}/
  todo.md                          # goal, acceptance, out-of-scope, Discovery Log, Plan Index
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

One folder per todo, prefixed with the 3–5 letter `{ID}` assigned at Step 1. Plan numbering is **monotonic** — abandoned and retired plans keep their numbers so cross-references stay stable. **All review-gate output lives in `reviews/`** — never inlined into the Discovery Log or the Plan Index Status column. A todo that skips a gate records the skip in Skipped Steps; a todo that runs a gate gets a review file.

## Sub-Agents

- **`test-reviewer`** — **the mandatory per-plan gate** (Step 5). Reads the Test Evidence map and the actual tests; surfaces tiered coverage gaps split plan-related vs. tech-debt; drives the add-tests → re-review loop. Skip only for trivial plans (test-only, comment-only, mechanical rename), recorded in Skipped Steps.
- **`plan-reviewer`** — opt-in at Step 2, for sharp edges (cross-aggregate, schema migration, public API, security, irreversible changes). **Calibration: its diagnoses are reliable; its prescriptions are advisory.** The reviewer names the problem; the orchestrator and keyboard pick the fix. (Real usage: the diagnoses caught bugs the planned tests would have falsely passed; the one bad outcome came from adopting a prescribed remedy wholesale.)
- **`business-requirements-reviewer`** — opt-in at Step 2 when the plan's intent touches documented business rules or excluded features. External contradictions are VETO; internal contradictions are callouts reconciled at todo close.
- **`code-reviewer`** — two findings-only modes, **no letter grades**: an opt-in per-plan review (Step 5, for behavior-changing plans) and the mandatory **close-out audit** (Step 7, whole arc). Findings are veto-tier or callout-tier.
- **`business-requirements-documenter`** — no longer a workflow step (doc deltas ship in the same PR as the behavior change, per project rules). Available ad hoc at todo close when documentation debt is large enough to warrant a dedicated pass.

## The Review Brief

Every reviewer invocation is assembled by the orchestrator as a **brief**. The brief is the balance point between two failure modes seen in real usage: front-loading (a fat reading list burned ~130k tokens and crowded out the codebase walk that produces findings) and free discovery (the reviewer re-derives context the orchestrator already holds, or re-litigates settled decisions). Five parts:

1. **The object under review** — plan, diff, or evidence map. Read fully; it is small by design.
2. **Distilled context, cited, background-only** — facts the review is *not* checking, stated as prose with sources named. **Never launder the object's own claims into this block**: context is what the review stands on; claims are what it stands over. For Step 5 gates, the plan's Current State section already *is* this block — point at it rather than rewriting it.
3. **Sources of record the object must agree with** — the Discovery Log, the Plan Index, prior review files. Named, not summarized: cross-reference findings live there, and they are grep-cheap. (Real usage: a plan review caught a silently dropped case group only because the parent Discovery Log was named reading and disagreed with the plan. Distilling it would have transmitted the orchestrator's own blind spot.)
4. **Code targets with questions attached** — "is the port-configurability claim plausible from Program.cs?" directs a grep; "read Program.cs" directs two hundred lines. The question is the budget.
5. **Log paths** (Steps 5 and 7) — reviewers grep them, never re-run builds.

**Front-load pointers and distillations, not documents.** If the one-line reason a reviewer needs a document cannot be stated, the document does not go on the list. Whole files "for context" are the anti-pattern: distill the context, or name the section.

**State the budget: `tight` (default) or `deep`.** Deep is for safety-seam or irreversible plans — the reviews a project's rules *require* are the ones that deserve more reading, not less. The close-out audit is exempt from `tight`: whole-arc reading is its definition, and budget discipline there governs *how* (greps, spot-checks) rather than *whether*.

**Close the loop.** Reviewers end with a read report — what they pulled beyond the brief and why, and which named items went unused. The next brief trims the unused and promotes the pulled. Calibration becomes data, not vibes.

## Status Values

**Todo:** `In Progress` · `Complete` · `Blocked`

**Plan:** `Draft` · `In Progress` · `Done` · `Abandoned` · `Retired`

- **Abandoned** — this path was wrong; the Abandonment Reason captures the lesson. Never deleted.
- **Retired** — the plan stopped being needed without failing: folded into another plan, superseded by a re-split, or carved out to a sibling todo. One-line reason in the plan; Index row kept as a tombstone.
- **Stub deletion (the one sanctioned delete):** a stub created and killed **within the same working session**, that never got past a Scope paragraph and was never implemented against, may be deleted outright — provided the Discovery Log entry recording the re-split names the killed stub. Anything that reached drafting or implementation is never deleted; it goes `Abandoned` or `Retired` and stays.

Verdicts and findings live in review files, not in status fields. Keep Plan Index Status cells to a status word plus at most a few words — narrative belongs in the plan or the Discovery Log.

## Workflow

### Prerequisite — Define the Goal (Conversational)

Before any file exists, the user and orchestrator define the goal: what problem, what success looks like, what's in and out of scope. No empty-shell todos — if the goal isn't crisp, keep talking.

### Step 1 — Reconnaissance, ID Assignment & Initial Plan Split

**Reconnaissance first.** Before splitting, map the affected code — and use agents to do the sweeping. Fan out read-only Explore agents (or equivalent) to answer: what are the seams this goal touches? What patterns does the codebase already use at those seams (verb shapes, factory patterns, naming conventions)? What looks risky or surprising? Recon agents return **seams, existing patterns, and open questions** — not edit scripts. The orchestrator still reads the load-bearing files itself where the split depends on them; agent summaries inform the split, they don't replace familiarity. (For sweep-shaped todos — codebase-wide audits — a multi-agent workflow is an option if the user opts in.)

Why this step earns its cost: the recon-shaped failures in real usage — plans drafted against a verb shape the codebase didn't use, splits built on a wrong inventory of what already existed, stubs gone stale against moved code — were all caught whenever someone did recon, and only cost rework when nobody did.

**Assign a unique todo ID.** Every todo carries a 3–5 uppercase-letter ID prefixing its folder and anchoring cross-references. Propose 2–3 candidates; the user picks. Verify uniqueness: `glob docs/todos/{ID}-*` and `docs/todos/completed/{ID}-*` return empty, and no row in `docs/todos/_ids.md` (if it exists) carries the ID. Retired IDs are never reused. If the project lacks `docs/todos/CONVENTIONS.md` / `_ids.md`, ask the user whether to bootstrap them.

**Draft the initial plan split.** Contained todos decompose into **2–6** plan stubs; large restructures legitimately start at **6–12**. Expect the index to grow 1.5–2× over the todo's life — growth through the Plan Index, with Discovery Log entries, is the system working, not scope creep. Each stub is a plan file with the next monotonic number, status `Draft`, and **only the Scope paragraph filled**.

Create `docs/todos/{ID}-{kebab-name}/todo.md` from `references/todo-template.md`: Goal, Acceptance Criteria, Out of Scope, Plan Index (populated with the split), empty Discovery Log. Add the `_ids.md` row in the same change. The split is a guestimate, not a commitment.

### Step 2 — Draft Next Plan

Pick the next `Draft` row whose Scope is still a stub. Flesh it out using `references/plan-template.md`: **Scope** (one paragraph, including what it does NOT do), **Intent**, **Framework & Architectural Alignment** (patterns named, not reproduced), **Constraints & Invariants**, **Steps** (intent-bearing bullets, cap ~10), **Acceptance** (behavioral signals, every bullet tier-tagged). A plan covers one concrete deliverable — typically hours of work. New plans discovered while drafting get a fresh stub and an Index row first — no orphan plan files.

**Declare the review opt-ins in the plan header**, each with a one-line reason:

- `Plan-review opt-in: Yes/No (reason)` — opt in for cross-aggregate behavior, schema migration, public API or contract change, security-sensitive or irreversible work. When the plan touches documented business rules or excluded features, opt in with `business-requirements-reviewer` specifically.
- `Code-review opt-in: Yes/No (reason)` — opt in for behavior-changing plans; skip for mechanical ports, renames, doc-only work.

When a plan review runs, assemble the invocation per **The Review Brief** and write the outcome to `reviews/{NNN}-plan-review.md`. Veto-tier findings (external contradictions, direction errors) are addressed before implementation. Callouts are recorded and carried. **Read the review with the calibration in mind: trust the diagnosis, treat the prescribed fix as one option.** Skips need no file — the header field with its reason is the record.

### Step 3 — Current-State Pre-Flight

Before the first edit, the orchestrator walks the plan's Intent and Steps against the **actual code** at the seams the plan touches — no edits yet. Record what's actually there in the plan's **Current State** section: this is the sanctioned home for line numbers, signatures, and "the code currently does X" observations. Discoveries that shift the plan become Plan Amendments **before the first edit**; a stub that turns out stale (drafted against code that has since moved) gets reshaped here instead of mid-implementation.

This step exists because real usage invented it independently three times. It is deliberately the orchestrator's own walk, not an agent's — the orchestrator is about to edit these files and needs the tactile familiarity. Keep it proportionate: minutes for a contained plan, not a re-review of the codebase.

### Step 4 — Implement

Work the plan's Steps in order, in conversation with the user.

**Testing during implementation: scope-bounded, not testing-free.** Run scoped tests continuously at natural checkpoints — the test files covering the changed code plus obviously adjacent ones. Full-suite runs during implementation are optional: the Step 5 gate runs a fresh full suite by design, and doubling it is insurance theater. Opt in to a mid-implementation full-suite run for cross-aggregate changes, schema migrations, or when a scoped run surfaces something whose spread you need to know now.

**The plan is not locked.** When something surprises you, apply the **discovery protocol**. First question: **does this advance the todo's Goal?**

- **Yes** — pick an in-todo response below.
- **No, but worth keeping** — open a **sibling todo** (rare). Otherwise drop it.

**In-todo responses** (always: append a Discovery Log entry — date, plan ID, one-sentence finding, decision, follow-up — then choose with the user):

- **Amend** — small correction; entry in the plan's Plan Amendments; plan continues. *Most common.*
- **Abandon** — wrong path; status `Abandoned`, Abandonment Reason filled; draft a replacement with the next number.
- **Defer** — finish as scoped; queue a follow-up `Draft` row.
- **Re-split** — the Plan Index itself needs to change: reorder, drop (`Retired`), add. Record the index edits in the same Discovery Log entry (`Index changes:`).

**When the Goal itself shifts (rare):** stop and ask explicitly — sometimes the right move is a sibling todo, not a Goal rewrite. If the Goal genuinely shifts, update Goal and Acceptance Criteria together, note it in the triggering Discovery Log entry, and re-verify queued plans.

**Stop and ask** any time a discovery threatens intent, an invariant, or an acceptance signal. Don't silently expand scope or downgrade an Acceptance bullet to make it pass. Every decision is recorded.

When Steps are complete and Acceptance is met, the plan is ready for the gate.

### Step 5 — Per-Plan Gate: Test Evidence + Test Review (Mandatory)

This is the single mandatory per-plan gate. Skip only for trivial plans (test-only, comment-only, mechanical rename), recorded in Skipped Steps.

**Pre-flight 1 — fill the plan's Test Evidence table.** One row per Acceptance bullet: cited test method, tier confirmation. No test at the right tier → `MISSING — <reason>`. Shipping with `MISSING` rows requires explicit user acknowledgement (ideally with a queued follow-up). The gate is not invoked until this table exists — hard gate, not preference.

**Pre-flight 2 — run build + test ONCE and pass log paths.** Run the project's build and test commands exactly once each, redirect full output to `reviews/{NNN}-build.log` / `reviews/{NNN}-test.log`, and pass those paths to every reviewer invoked this step. **Reviewers grep the logs; they never run build or test themselves** — repeated invocations race shared test databases and have cost 10–20 minutes per false cycle. Reviewers fail out if log paths are missing; that fail-out is the protection working. On a flaky failure, re-run sequentially, overwrite the log, note the re-run.

**Invoke `test-reviewer`** with a brief per **The Review Brief**: the plan (its Test Evidence table and Current State are the object and context), the changed files and test directories as code targets with the questions that matter, and the log paths. It returns tiered findings (must-cover / should-cover / nice-to-have) split plan-related vs. pre-existing tech-debt. Then loop:

1. **Tier the response with the user.** Must-cover plan-related findings are addressed before the plan is Done. Should-cover / nice-to-have: user picks. **Tech-debt at any tier queues as its own Plan Index entry** — absorbing it silently is scope creep; keep it visible.
2. **Add the chosen tests**, re-invoke, repeat until must-cover is closed (or explicitly accepted with a recorded reason — rare) and the user is satisfied with the rest.
3. Write the summary to `reviews/{NNN}-test-review.md` with the closing tier: tier picture at close, what was added, what was queued, explicit accepts with reasons.

**If the plan opted into code review**, invoke `code-reviewer` (briefed per **The Review Brief**) for a findings-only pass (veto/callout, no grade) on the same logs — focused on whether the deliverable landed cleanly, the shape is right, and no framework rules or sacred tests were violated. Veto-tier findings are fixed before Done; material callouts queue as Index entries. Write to `reviews/{NNN}-code-review.md`. Discovery here is welcome — a reviewer redirecting on shape is the system working, not a planning failure.

A plan reaches `Done` only after this gate closes.

### Step 6 — Loop or Fall Through

Check the Plan Index: queued `Draft` plans → back to Step 2. Only `Done` / `Abandoned` / `Retired` plans and unmet Acceptance Criteria → draft another plan. All criteria covered → Step 7.

### Step 7 — Close-Out Audit (Mandatory)

Triggered when the last plan closes and the Index has no queued work. The orchestrator prompts the user to confirm the todo's Acceptance Criteria are met, runs the build+test pre-flight once each (`reviews/final-build.log`, `reviews/final-test.log`), then invokes **code-reviewer** in close-out mode with the **whole arc** — the todo, every plan, the Discovery Log, every review file, plus the log paths. (The Review Brief's `tight` default does not apply here — whole-arc reading is the audit's definition; its budget discipline is greps and spot-checks, not scope cuts.)

The audit is **findings-only — no letter grades**. (Grading was dropped after real usage showed final grades were always confirmation, never discovery; the audit's verification content is what earns the step.) Per `references/close-out-audit.md`, the auditor:

- Traces every todo-level Acceptance Criterion to specific code.
- Audits container integrity: Plan Index ↔ `plans/` reconciliation, monotonic numbering, Abandonment/Retirement Reasons present, every deferral phrase in any plan body traced to an Index entry, `MISSING` Test Evidence rows acknowledged.
- Spot-checks Test Evidence honesty (cited tests exist, at the declared tier) and closing tiers against risk.
- Checks framework rules per the project's CLAUDE.md and any project-local overlay; greps the logs for build/test health.
- Produces the **Deferred Work Carrying Forward** table — every deferral, where it's queued, what it costs — so debt doesn't accumulate invisibly across todos.

Veto-tier findings are fixed before completion; callouts queue as plans or are accepted with recorded reasons. Write to `reviews/close-out-audit.md`; re-invoke after fixes (append, don't overwrite).

### Step 8 — Completion & Retro

Verify: close-out audit exists and the user acknowledged it; every plan is `Done` / `Abandoned` / `Retired`; Acceptance Criteria all checked.

**Documentation check (replaces the old documenter step):** confirm doc deltas shipped in the same PRs as the behavior they describe (per project rules). Reconcile any internal-contradiction callouts parked by reviewers — the implementation has settled, so the right resolution is usually obvious now; update the documented rules to match. If documentation debt remains, queue it as a plan or sibling todo, or invoke `business-requirements-documenter` ad hoc for a dedicated pass.

**Cross-todo deferrals:** if this todo closes partial, every deferred commitment (un-skipped tests, inherited acceptance bullets) must land as **acceptance bullets in the successor todo's plans** — not as prose. Prose-level inheritance has had to be re-traced by hand; bullets survive.

**Retro (one paragraph):** what did this todo teach about the *workflow itself* — a gate that misfired, a mechanic that got skipped, a convention that decayed? Route lessons to where they'll act: the project's CLAUDE.md, this skill's backlog, or persistent memory. The best improvements to this workflow all came from retro moments; capture them while they're fresh.

Set todo status `Complete`. Move the whole folder to `docs/todos/completed/{ID}-{todo-name}/` (the `{ID}` prefix preserves cross-references) and move the `_ids.md` row in the same change.

**The user decides when to commit and when to open PRs.** Suggest commits at natural milestones; never commit, push, or open PRs without an explicit yes. Never assume a PR cadence.

## Discovery Log Format

The Discovery Log is the anti-forgetting mechanism — searchable and navigational, not a journal.

```
### YYYY-MM-DD — {ID}-{NNN}
- **Finding:** [one sentence]
- **Decision:** [Amend | Abandon | Defer | Re-split]
- **Index changes:** [Re-split only — plans added/dropped/reordered; else omit]
- **Follow-up:** [{ID}-{NNN} or "n/a"]
```

**Budget: ~100 words per entry.** The long form lives on the affected plan (Plan Amendments or Abandonment Reason) — the log entry points at it. PR descriptions, file-change enumerations, and reviewer findings do not belong here: **review output goes to `reviews/`, always** — a log entry may summarize a review's outcome in one line and link the file. Cite plans in `{ID}-{NNN}` form so entries stay greppable after the todo moves. When the template's decision taxonomy is skipped, the decisions stop being greppable — use the fields.

## Plan Amendments, Abandonment, Retirement

- **Plan Amendments** (append-only) — a discovery led to **Amend**. Original Scope/Intent/Steps stay frozen; each amendment records what changed and why. The visible record that the plan was a hypothesis, not a contract.
- **Abandonment Reason** (one paragraph, required when `Abandoned`) — what we believed at draft, what turned out true, what the next plan should do differently. This is what makes abandonment cheap: the next plan inherits the lesson. Never delete an abandoned plan.
- **Retirement note** (one line, required when `Retired`) — where the work went (folded into {ID}-{NNN}, superseded by re-split, carved out to sibling {ID}).

## Sibling Todos

A sibling todo is the **capture-or-lose** mechanism for work that surfaced here but doesn't advance this todo's Goal — yet is worth keeping. The test is narrow: *does the discovery advance this Goal?* No, and worth keeping → sibling. Yes → in-todo response. Most discoveries are in-todo; siblings are rare. A sibling gets its own folder and ID per Step 1; record the relationship in both todos' Sibling Todos sections. If it isn't worth keeping, drop it — capturing every stray observation is the noise the system avoids.

## Internal vs. External Contradictions

- **External contradiction** — plan contradicts a documented business rule or touches an excluded feature. **Veto-tier.** Address before implementation, or get explicit user sign-off to change the documented rule.
- **Internal contradiction** — tension with the parent todo's intent, the plan's own sections, or neighboring plans. **Callout-tier.** Record and keep implementing; reconcile at Step 8 when the implementation has settled and the right resolution is usually obvious. Internal contradictions look bigger before the code is written than after — forcing plan-time reconciliation produces guesses.

## Converting an Older Todo

To convert a flat-file or `project-todos`-era todo to this shape, follow `references/conversion-checklist.md`.

## Resuming Mid-Workflow

Read `todo.md` and the Plan Index; find the latest `In Progress` or `Draft` plan. This applies after a session break **and** after a mid-session context compaction — the files are the source of truth, not the conversation.

| Plan Status | Next Step |
|-------------|-----------|
| Draft (stub) | Step 2 (draft) |
| Draft (drafted, pre-flight not done) | Step 3 (pre-flight) |
| In Progress | Step 4 (continue) |
| Done, no test review | Step 5 (per-plan gate) |
| Done, gate closed | Step 6 (loop or fall through) |
| Abandoned / Retired | Step 2 (next plan, next monotonic number) |

All plans closed, no queued work → Step 7 (confirm Acceptance Criteria, run the close-out audit).

## Best Practices

1. **Plans describe intent; Current State holds reality; Amendments hold keyboard decisions.** When a Step starts reading like code, compress it and ask which of the other two homes the detail belongs in.
2. **Keep plans small.** More than a day of draft-plus-execution means split it.
3. **Log every discovery — briefly.** One ~100-word entry, ID-form citation, pointer to the long form.
4. **Abandonment is normal; retirement is normal.** The reason is the deliverable; the next plan is the reward.
5. **Don't amend a Done plan.** Post-`Done` findings go in a follow-up plan.
6. **The todo's Acceptance Criteria are the exit gate** — not "all listed plans done." Plans come and go.
7. **Review output lives in `reviews/`.** The Discovery Log links it; the Index Status cell stays terse.
8. **Project-specific framework idioms live in the project repo**, not this skill: `<repo>/.claude/skills/iterative-todo/references/rubric-framework.md` or `<repo>/docs/code-review-rubric.md` (audit overlay), `<repo>/docs/code-review-calibration.md` (what clean means for this project).

## Reference Files

- `references/todo-template.md` — todo template (Discovery Log + Plan Index + Sibling Todos)
- `references/plan-template.md` — plan template (Scope, Intent, Alignment, Constraints, Steps, Acceptance, Current State, Test Evidence, Amendments)
- `references/close-out-audit.md` — findings-only audit checklist for Step 7
- `references/conversion-checklist.md` — convert an older todo to this shape
- `references/plan-template-neatoo.md` — Domain Model Behavioral Design addendum for Neatoo projects

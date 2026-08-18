---
name: iterative-todo
version: 0.5.0
description: This skill should be used when the user asks to "create a todo", "create an iterative todo", "iterate on this", "start a small plan", "plan this work", "design this feature", "abandon this plan", "next plan in <todo>", "log a discovery", "resume the todo", or "grade the implementation". Use for multi-session, design-heavy work where the plan needs to outlive the conversation — bounded or exploratory. Plans are small working hypotheses; the todo is the durable container with a Discovery Log and Plan Index. Skip for single-session tasks, trivial fixes, or work that fits in built-in plan mode (Shift+Tab).
---

# Iterative Todo, Plans, and Discovery Workflow

Manage exploratory, discovery-heavy project work as a durable **todo** containing many small **plans**. Plans are cheap, possibly wrong, and possibly abandoned. The todo carries cumulative learning across plans via an append-only Discovery Log.

## When to Use This Workflow

Use `iterative-todo` for any multi-session design-heavy work where the plan needs to outlive the conversation:

- Exploratory work where gotchas are expected to surface during implementation.
- Bounded work that's still large enough to span multiple sessions or warrant decomposition.
- Work where multiple small attempts are likely, including ones that get abandoned.
- Work where the codebase has documented business rules to check against, or where deferred scope must be tracked.

The shape adapts to the work: a bounded todo may have one or two plans and no abandonments; an exploratory todo may have six plans and three abandonments. Both are the same shape.

Skip for single-session tasks, trivial fixes, or work that fits in built-in plan mode (`Shift+Tab`).

## Core Principle 1: Plans Are Prescriptions, Not Implementations. Discovery Is Welcome at Every Stage.

A plan describes **what** needs to be true and **why** — the business outcome, the framework patterns to follow, the invariants to preserve, the acceptance signals that prove it worked. A plan does **not** describe what the code looks like.

**This is the failure mode the skill exists to prevent:** writing what looks like a thorough plan but is actually pre-implementation reconnaissance dressed up as design — line numbers, exact method signatures, parameter lists, "if X isn't `[Remote]` then add it" reconnaissance, file-by-file edit tables, fallback branches. That kind of plan is wrong as often as it is right, and the right parts could only be settled at the keyboard anyway. The plan looks impressive and feels safe; in practice it locks the implementer onto a frozen wrong-shape and makes mid-implementation discoveries feel like "deviating from the plan" instead of the normal way work happens.

**Plans are not locked when implementation starts.** The plan is a working hypothesis that survives contact with code by being amendable. When something surprises the implementer:

- **Stop and ask** when the surprise changes the plan's intent, contradicts a constraint, or threatens an acceptance signal.
- **Amend the plan** when the surprise changes details but not intent — record what shifted and why in Plan Amendments.
- **Keep going** when the surprise is purely mechanical and the intent still holds.

**Discovery is welcome at every stage** — at draft (informs the next plan in the index), during implementation (becomes a Plan Amendment, an Abandonment Reason, or a re-split), and at code review (the reviewer redirecting on shape is the system working, not a planning failure). Restructuring opportunities can be **named** in a plan ("this seam will probably need to move onto the aggregate") but not **designed** — the implementer finds the right shape while editing.

This mirrors how humans actually code. Humans don't write production code from a frozen design doc; they sketch the direction, start typing, discover what was wrong about the sketch, adjust, ask when stuck, and let reviewers catch what they didn't see. The skill exists to make that flow legible and durable, not to extract a perfect specification before any code gets touched.

### What belongs in a plan

- Business outcomes and observable behavior changes — the **intent**.
- Framework patterns and architectural rules being applied — named, not reproduced.
- Invariants and constraints the change must preserve.
- High-level seams the work touches (aggregate X, handler Y, factory Z).
- Acceptance signals a reviewer can check by exercising the system or running tests.

### What does NOT belong in a plan

- Specific line numbers (`StandardTreatmentV2:271`).
- Exact method signatures, parameter lists, constructor injection lists.
- Method bodies, before/after diffs, or pseudocode-as-design.
- "If service X isn't `[Remote]` then add `[Remote]`" — reconnaissance, not design.
- "Pre-flight verification" steps that are really implementation discovery.
- Fallback branches ("if A doesn't compile, fall back to B") — discover that at the keyboard, capture it as a Plan Amendment if it actually happens.
- File-by-file tables of "delete this, rewire that" — diff-grade artifacts written during implementation.

**Heuristic:** if a step contains a fully-qualified type name with a colon and a line number, or specifies the parameter list of a method, or embeds a code fence longer than two lines, the step is too detailed. Compress to the intent: *"Move regenerate-and-clear onto the aggregate as a domain verb so the handler reduces to the standard Neatoo lifecycle"* — not *"Add `Task RegenerateRecommended()` to `ITreatmentV2`; concrete on `StandardTreatmentV2:113`; constructor takes `ISignsLookBackServiceV2`, `ITreatmentGenerationServiceV2`, …"*

**The tradeoff this is buying:** plan-time review catches fewer concrete code-smells, but the line-level prescriptions in over-detailed plans were unreliable anyway. Code-level issues get caught at code-review time (Step 5 / Step 7), where the actual code exists to review against. The plan's job is to ensure the *direction* is right; the keyboard's job is to settle the *shape*.

## Core Principle 2: Tests Are Iterative Too. Coverage Is a Loop, Not a Plan-Time Prescription.

Plans don't enumerate test cases. Plans name **behavioral acceptance signals** — observable outcomes the implementation has to produce — and that's the test surface they're responsible for. Specific test classes, test names, test tiers per business rule, and "X must have at least 3 unit tests and 1 integration test" are downstream concerns that don't survive contact with code.

This principle exists because the symmetric failure mode to over-prescribed plans is over-prescribed tests. In `project-todos`, exhaustive test scenarios drafted at plan time were either over-generous (and got silently trimmed during implementation, hiding what was skipped) or under-generous (and the feature shipped under-tested with nobody noticing). Either way the test list lied about what got tested. The fix is the same as for plans: stop pretending we know the answer at design time.

**The iterative shape for tests:**

1. **Plan-time test surface = Acceptance bullets, each tagged with a tier.** Each acceptance bullet is a behavioral signal that must be pinned by at least one test. **Every behavioral bullet ends with one tier tag** — `[unit]`, `[integration]`, `[database]`, `[ui]`, or `[explicit-skip: <reason>]`. Bare bullets are a draft-time validation error. The plan still does NOT enumerate test method names, test class names, or specific test scenarios — only *which tier* the signal gets pinned at. The tier decision is made once, at draft time, when the orchestrator can think clearly about what kind of evidence the signal actually needs (e.g., "Plan.Protocol stays null after load" requires `[database]` because nothing else proves persistence-or-its-absence).
2. **Implementation writes tests at the declared tier.** The implementer writes tests during implementation that exercise each Acceptance signal at the tag's tier, plus obvious edge cases the keyboard surfaces. Writing only unit tests when a bullet declared `[integration]` is a tier mismatch — the bullet is **not pinned** until the right-tier test exists, even if the unit test passes.
3. **Before invoking code-reviewer, the orchestrator fills in a Test Evidence map.** Every Acceptance bullet → the test method that pins it → tier confirmation. Bullets with no test are recorded as `MISSING — <reason>` rather than silently omitted. Code-reviewer is **not invoked until this map exists** in the plan body. This step is the load-bearing fix for the failure mode where prescribed test tiers got skipped without anyone noticing — the map turns "did I do it" from a vibes call into a checkable artifact.
4. **A post-implementation test-review loop closes coverage.** After the per-plan code review (Step 5), the orchestrator runs **`test-reviewer`** (Step 5b — mandatory by default). The agent reads the Test Evidence map and the actual tests, surfaces remaining gaps tiered must-cover / should-cover / nice-to-have, and splits them by source (plan-related vs. pre-existing tech-debt). The orchestrator addresses must-cover findings, re-invokes, and closes the loop at the tier the user is targeting for *this* plan. Tech-debt findings queue as their own Plan Index entries — never absorbed silently.
5. **The user controls "good enough."** A spike or exploration may close at must-cover only. A production-bound plan may close at should-cover or higher. The skill defines the tiers; the user picks the closing bar per plan.

Why this matches how humans code: humans don't write tests from a frozen test plan. They write tests as they implement, ship when the code is right *and* the critical behaviors are pinned, then strengthen coverage in follow-up passes when reviewers or production teach them what they missed. The tier-tag + Test Evidence map mechanism preserves that flow — the *which-tier* decision is plan-time (forces honesty), but *which-test-method* is keyboard-time (preserves discovery). Step 5b is the formalization of "show this to a colleague before you call it done" — bounded, discrete, and outside the implementation conversation so it actually catches things.

## Core Principle 3: The Todo Is the Durable Artifact

The **todo** is durable. Plans are working artifacts: small, drafted quickly, executed quickly, sometimes abandoned. The todo's **Discovery Log** and **Plan Index** carry the narrative across plans so abandoned attempts inform future ones instead of being forgotten.

## Core Principle 4: The Todo Is the Goal. Plans Are Pieces of It.

A todo has one focused goal. Plans are how the goal gets tackled — piece by piece, in order, with the order itself being a working hypothesis.

The goal is defined **before** the todo file exists. Once the goal is clear, the todo's first workflow step is **Discovery & Initial Plan Split**: analyze the affected code, decompose the goal into 2–6 plan stubs (one-paragraph Scope each), and queue them in the Plan Index as `Draft` rows. The split is a **guestimate** — directional, not a contract. Plans get refined, reordered, replaced, or abandoned as discoveries come in.

This means a discovery is never just a local question about the current plan. A discovery brings the **entire todo** back into scope: does the Plan Index still hold? Should queued plans be reordered, dropped, or added? Has the goal itself shifted? The discovery protocol's fourth option (**Re-split**) is the explicit hook for this whole-todo re-evaluation.

### What the Orchestrator Does

- Authors all todo and plan content
- Drafts the next plan as the smallest viable next step — at the **intent** level
- Implements in conversation with the user, treating discovery as expected
- Logs every discovery to the todo's Discovery Log
- Decides (with user) to amend / abandon / defer / re-split when a discovery hits
- Invokes agents for per-plan code review and final reviews
- Writes agent findings into the todo
- Reconciles internal contradictions (between the plan's own intent and other parts of the same todo) at the **end** of the todo, during the documenter step — not as a plan-review block

### What Agents Do

- Review, grade, document
- Surface external contradictions (against documented business rules) as gating findings
- Surface internal contradictions and gotchas as **callouts**, not blocks
- Return findings; never write to todo or plan files
- Never set status

## Directory Structure

```
docs/todos/{ID}-{todo-name}/
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

One folder per todo, prefixed with the 3–5 letter `{ID}` assigned at Step 1 (e.g. `OVL-office-visit-lifecycle-production-ready/`). Cross-references to plans use the `{ID}-{NNN}` form (e.g. `OVL-025`) — never bare `Plan 025`. Plan numbering is **monotonic** — abandoned plans keep their number so cross-references in the Discovery Log stay stable. Reviews live alongside the plan they cover.

## Sub-Agents

Five agents handle review, grading, and documentation, invoked at different points in the workflow:

- **`plan-reviewer`** — optional per plan; default skip. Opt in only for sharp edges (cross-aggregate, schema migration, public API, security, irreversible changes). Looks for **gotchas, gaps, and direction errors**, not enumerative coverage.
- **`business-requirements-reviewer`** — optional per plan; default skip unless the plan's intent touches documented business rules. Surfaces **external contradictions** (against documented rules) as VETO; surfaces **internal contradictions** (within the plan or against parent-todo intent) as callouts to address at end of todo.
- **`code-reviewer`** — encouraged per plan (lightweight); mandatory once at the end (graded, full arc). Discovery here is welcome and expected — reviewer findings that redirect shape are the system working.
- **`test-reviewer`** — **mandatory per plan by default.** Runs after the per-plan code review. Surfaces plan-related coverage gaps and pre-existing tech-debt gaps separately, tiered must-cover / should-cover / nice-to-have. Drives the **add-tests → re-review loop** that closes the plan's coverage at the user's chosen tier. Skip is allowed for trivial plans (record reason in Skipped Steps). See Step 5b.
- **`business-requirements-documenter`** — invoked once at the end, after acceptance criteria are met. Reconciles internal contradictions surfaced earlier and updates documented rules.

## Status Values

**Todo:** `In Progress` · `Complete` · `Blocked`

**Plan:** `Draft` · `In Progress` · `Done` · `Abandoned`

Verdicts (Grade A/B/C, plan-review verdicts) live in the relevant review file, not in status fields.

## Workflow

### Prerequisite — Define the Goal (Conversational)

Before any file exists, the user and orchestrator define the goal. What problem is being solved, what success looks like, what's in and out of scope. This is conversation, not a file. The todo file is not created until the goal is clear enough to write down.

No empty-shell todos. If the goal isn't crisp, keep talking — don't open a todo just to have one.

### Step 1 — Discovery, ID Assignment, & Initial Plan Split

Analyze the affected code with the user. Trace the relevant aggregates, services, UI surfaces, and integration points. Identify the natural seams where the goal decomposes.

**Assign a unique todo ID.** Every todo carries a 3–5 uppercase-letter ID that prefixes its folder/file name and is the canonical handle in cross-references (`OVL-025`, never bare `Plan 025`). Propose 2–3 candidate IDs derived from the todo name; the user picks. Verify uniqueness:

- `glob docs/todos/{ID}-*` returns empty.
- `glob docs/todos/completed/{ID}-*` returns empty.
- If a project registry exists at `docs/todos/_ids.md`, no row carries the proposed ID (active or retired).

If any check fails, propose a different ID. Retired IDs are never reused. If the project does not yet have `docs/todos/CONVENTIONS.md` or `docs/todos/_ids.md`, ask the user whether to bootstrap them — the convention works without the registry, but the registry makes uniqueness checks robust over time.

Then draft the **initial plan split** — a guestimate of how the work breaks into pieces. Aim for 2–6 plan entries, each a single-paragraph Scope describing one focused chunk of the goal. The split is directional, not a contract; entries will be reordered, replaced, or abandoned as discoveries come in.

Create the todo file at `docs/todos/{ID}-{kebab-name}/todo.md` (folder-based) or `docs/todos/{ID}-{kebab-name}.md` (single-file) using `references/todo-template.md`:

- **ID** — the 3–5 letter ID assigned above.
- **Goal** — one paragraph, written from the conversation.
- **Acceptance Criteria** — observable, testable. The exit gate for the whole todo.
- **Out of Scope** — bullets; what this todo will not touch.
- **Plan Index** — populated with the initial split. Each row points at a stub plan file.
- **Discovery Log** — empty (the first entry comes during implementation).

For each entry in the initial split, create a stub plan file in `plans/` with status `Draft`, the next monotonic number, and **only the Scope paragraph filled**. Other sections are left empty — they get filled at Step 2 when the plan's turn comes.

If the project maintains `docs/todos/_ids.md`, add a row under **Active** with the new ID and folder/file name in the same change.

Set Type, Status `In Progress`, Priority, today's date.

**The initial split is a guestimate, not a commitment.** A plan that turns out to be wrong gets abandoned with a reason; a plan that needs to split further gets re-scoped at Step 2; new plans get added to the index when discoveries surface them. The point of the initial split is to give the first plan context for what comes after, not to lock in the trajectory.

### Step 2 — Draft Next Plan

Pick the next plan to work on — typically the next `Draft` row in the Plan Index whose Scope is still just a stub. Flesh it out using `references/plan-template.md`. The template's sections enforce the prescriptive shape; follow them.

A drafted plan has:

- **Scope** — one paragraph; what this plan does and what it explicitly does NOT do. Already drafted at Step 1; refine if discovery has shifted it.
- **Intent** — the business outcome or behavioral change this plan delivers. Not the code shape.
- **Framework & Architectural Alignment** — which framework patterns and architectural rules this plan follows. Name them; do not reproduce them.
- **Constraints & Invariants** — what must remain true. Business invariants, system invariants, boundary rules.
- **Steps** — high-level, intent-bearing bullets. Each step names *what changes* and *why*, not *exactly how*. Cap at ~10. If you find yourself writing line numbers or method bodies, stop — the plan is shifting into implementation. Compress back to intent.
- **Acceptance** — observable, behavioral signals. Things a reviewer can check by exercising the system or running tests, not "line 271 is deleted."
- **Plan Amendments** — empty at draft time; append-only during implementation when discoveries shift details (not intent).

A plan covers **one concrete deliverable** — typically hours of work. A plan does not duplicate the todo's Goal / Acceptance Criteria / Out of Scope; those live on the todo and the plan inherits them.

If, while drafting, you realize the work needs a new plan that wasn't in the initial split, create a fresh stub plan file (next monotonic number, status `Draft`, Scope filled) and add it to the Plan Index before drafting Steps. New plans always go through the Plan Index — no orphan plan files.

**The plan is a working hypothesis, not a contract.** It does not lock when implementation begins. The Plan Amendments section exists precisely so the plan can stay accurate without rewriting Scope/Steps.

### Step 3 — Plan Review (Optional)

Default: skip. Opt in when the plan touches:

- Cross-aggregate behavior
- Schema migration
- Public API or contract change
- Security-sensitive code
- Anything irreversible
- Documented business rules (in which case opt in for `business-requirements-reviewer` specifically)

When opted in, invoke the appropriate reviewer with the todo and plan paths. Reviewers look for **gotchas, gaps, and direction errors** — not enumerative coverage. Reviewer findings come in three flavors:

- **External contradiction** (business-requirements-reviewer only) — plan contradicts a documented business rule. Veto-tier; address before implementation.
- **Direction error / framework violation** (plan-reviewer) — plan points at the wrong seams, names the wrong framework pattern, or threatens a stated invariant. Veto-tier; address before implementation.
- **Internal contradiction / gotcha / callout** (either reviewer) — plan has a tension with parent-todo intent, or names a seam where an obvious gotcha lurks, or surfaces a question worth knowing the answer to before typing. **Not veto-tier.** Recorded as a callout; addressed at the end of the todo (during the documenter step), or earlier if implementation surfaces it as a real blocker.

Write the review to `reviews/{NNN}-plan-review.md`. If veto-tier findings exist, address with the user, re-invoke if needed. Callouts are tracked but do not block implementation.

When skipped, record the skip in the todo's **Skipped Steps** with a one-line reason.

### Step 4 — Implement

Work the plan's Steps in order, in conversation with the user.

#### Testing during implementation: scope-bounded, not testing-free

Implementation isn't testing-free, just **scope-bounded**. Run **scoped tests** continuously at natural checkpoints — the test files that cover the code being changed, plus the obviously adjacent ones (same aggregate, same handler, same touched seam). Those are fast and catch what you'd otherwise catch in thirty seconds at the keyboard.

**Full-suite runs during implementation are optional, not default.** The reflex of running the full suite at every checkpoint is mostly insurance theater — it's slow, it's almost always green for unrelated areas, and the per-plan code review (Step 5) and the test review (Step 5b) both run a fresh full-suite as part of their gate. Those reviewers don't trust the implementer's reported results anyway; they're the canonical full-suite checkpoint by design. Doubling the work during implementation is redundant.

Opt **in** to a full-suite run during implementation when:

- The change is **cross-aggregate** — touching seams whose unrelated callers might break.
- The change is a **schema migration** or otherwise touches infrastructure shared across the codebase.
- The change is **irreversible** in a way that makes "find out at Step 5" too late (rare).
- A scoped run surfaces something unexpected and you want to know how far it spreads before continuing.

Otherwise: scoped tests during implementation, full-suite at the reviewers. The time saved across the cases where the full-suite run was redundant dwarfs the cases where catching it earlier would have helped.

**The plan is not locked.** Discovery during implementation is normal — that's why this skill exists. When something surprises the implementer, apply the **discovery protocol**.

The first question every discovery raises is: **does this advance the todo's Goal?**

- **Yes** — the discovery is about how to reach the Goal. Pick from the four in-todo responses below: Amend / Abandon / Defer / Re-split.
- **No** — the discovery surfaced work that fell out of doing this todo but doesn't advance its Goal. Decide with the user: drop it (if not worth keeping) or open a **sibling todo** to capture it. Sibling todos are rare — most discoveries are the "yes" case.

#### In-todo responses (Goal unchanged)

1. **Append a Discovery Log entry to the todo** — date, plan ID, one sentence of finding, decision, follow-up plan ID(s) if any.
2. **Choose with the user**:
   - **Amend** — small correction. Add an entry to the current plan's `Plan Amendments` section. Plan continues. Plan Index unchanged. *Most common.*
   - **Abandon** — current plan is no longer the right path. Set status to `Abandoned`, fill the **Abandonment Reason** field, update the Plan Index. Drop into Step 2 to draft a replacement plan with the next monotonic number.
   - **Defer** — finish the current plan as scoped, queue a follow-up plan as a new `Draft` row in the Plan Index.
   - **Re-split** — the **Plan Index itself needs to change**. The plans for advancing the Goal aren't decomposed correctly anymore: reorder queued plans, drop ones that no longer apply, add new ones with stub Scope paragraphs. The current plan may continue, abandon, or amend separately — record both decisions in the same Discovery Log entry, with `Index changes:` listing the edits.

Re-split is about *plan decomposition under an unchanged Goal*. The Goal almost always survives a Re-split intact — Re-split says "the path was wrong," not "the destination was wrong."

#### When the Goal itself shifts (rare)

A Re-split very occasionally reveals that the original Goal was incomplete, mis-specified, or pointed at the wrong outcome. When that happens:

1. **Stop and ask explicitly.** Goal shifts are a strong signal — sometimes the right move is a sibling todo (the work in front of you belongs to a different goal), not a Goal rewrite.
2. If you and the user agree the Goal genuinely needs to shift, **update the todo's Goal and Acceptance Criteria together** and note the change in the same Discovery Log entry that triggered it.
3. Verify queued plans still make sense under the new Goal; abandon or rewrite Scope on any that don't.

**Stop and ask** any time a discovery threatens the plan's intent, contradicts a stated invariant, makes an Acceptance signal unreachable, or seems to be pulling the work away from the Goal. Don't silently expand scope, don't quietly add work, don't downgrade an Acceptance bullet to make it pass. The decision is always recorded — Amend, Abandon, Defer, Re-split, sibling todo, or Goal shift.

When the plan's Steps are complete and Acceptance is met, set plan status to `Done`.

### Step 5 — Per-Plan Code Review (Encouraged)

**Pre-flight: fill in the plan's Test Evidence section.** Before invoking code-reviewer, the orchestrator MUST populate the plan's `## Test Evidence` table — one row per Acceptance bullet, with the cited test method and a confirmation that its tier matches the bullet's tier tag. Bullets with no test of the right tier are recorded as `MISSING — <one-line reason>`. Shipping with `MISSING` rows requires explicit user acknowledgement (and ideally a queued follow-up plan); silent omission is the failure mode this section eliminates.

The orchestrator does NOT invoke code-reviewer until the Test Evidence table exists. This is a hard gate, not a soft preference. The map is the difference between "tests prescribed at draft → tests written at keyboard" being a checkable fact vs. a vibes call.

**Pre-flight: run build + test ONCE and pass the log paths to the reviewer.** Before invoking code-reviewer, the orchestrator runs the project's build and test commands (as documented in CLAUDE.md) **exactly once each**, redirects all output to log files, and passes those file paths into the reviewer's prompt. The reviewer is forbidden from running build or test itself — it greps the provided logs. This eliminates the failure mode where the reviewer issues multiple `dotnet test` invocations to get different output formats, racing the shared test database and inflating review time by 10-20 minutes.

Suggested file layout (adapt commands to the project):

```
reviews/{NNN}-build.log   # full output of one build run
reviews/{NNN}-test.log    # full output of one test run
```

Pass both paths into the code-reviewer invocation: "Build log: reviews/{NNN}-build.log. Test log: reviews/{NNN}-test.log. Do NOT run build or test yourself; grep the logs."

**code-reviewer fails out if the log paths are missing.** The agent is instructed to return a one-line error and refuse to proceed rather than run build/test itself. If you see that error, run the pre-flight and re-invoke. Do not interpret the error as a reason to relax the rule — the fail-out is the protection working.

If the build or test command surfaces a flaky / transient failure, the orchestrator re-runs sequentially (never in parallel), overwrites the log, and notes the re-run when invoking the reviewer.

Then invoke **code-reviewer** with the plan and todo paths plus the log paths. Ask for a lightweight review focused on the plan's deliverable: did it land cleanly, are tests passing, are there obvious issues, is the shape right. The reviewer reads the Test Evidence table, spot-checks that the cited test methods exist and pin the claimed signal, and grades Test Coverage against tier-match — see `references/rubric.md`.

**Discovery at code review is welcome.** A reviewer finding "this should have been done differently" is the system working, not a planning failure. The plan-time decision was a working hypothesis; the reviewer has the actual code to look at and may see something the plan-time view missed. Treat reviewer suggestions as redirect signals, not as evidence the plan was bad.

Reviewer findings split the same three ways as plan review:

- **Veto-tier** (broken acceptance, framework violation, business-rule contradiction) — fix before marking the plan Done.
- **Callout** (shape suggestion, alternative approach, follow-up worth doing) — record in the review file. If material, queue a new plan in the Plan Index. Do not retroactively amend a Done plan.

Write the summary to `reviews/{NNN}-code-review.md`. Skip when the change is trivial (test-only, comment-only, mechanical rename). Record skip in the plan or in the todo's Skipped Steps.

### Step 5b — Test Review & Add-Tests Loop (Mandatory by Default)

After the per-plan code review, run the test-coverage loop. **This step is mandatory by default** — skip is allowed only for trivial plans (test-only, comment-only, mechanical rename) and must be recorded in the todo's Skipped Steps with a one-line reason.

The loop exists because plan-time test prescriptions are unreliable (see Core Principle 2). Coverage gets pinned here, against actual code, by running an agent whose only job is to find what's missing.

#### Loop shape

1. **Invoke `test-reviewer`** with the plan path, parent todo path, the changed source files, and the test directories. The agent returns tiered findings split by source — plan-related vs. pre-existing tech-debt — with each finding tagged **must-cover**, **should-cover**, or **nice-to-have**.
2. **Tier the response with the user.** Confirm which findings to address this loop. Defaults:
   - **must-cover (plan-related)** — address before the loop closes. A plan with unaddressed must-cover findings should not be considered Done.
   - **should-cover / nice-to-have (plan-related)** — user picks. Address now if cheap; queue otherwise.
   - **tech-debt at any tier** — typically **queue as a separate plan in the Plan Index** rather than absorbing into this plan. Tech-debt absorption is silent scope creep; keep it visible.
3. **Add tests** for whatever the user chose to address. Orchestrator writes the tests in conversation with the user.
4. **Re-invoke `test-reviewer`.** It re-checks must-cover and reports remaining findings.
5. **Close the loop** when:
   - Must-cover plan-related findings are all addressed (or the user has explicitly accepted them with a recorded reason — rare; this is the bar that protects against silent deferral), AND
   - The user is satisfied with the should-cover / nice-to-have / tech-debt picture (typically: "addressed what's worth addressing, queued the rest").

Write the final test-review summary to `reviews/{NNN}-test-review.md`. Include: tier picture at close, what was added this loop, what was queued (with new Plan Index entries linked), what was explicitly accepted with reason.

#### Tier-closure record

The closing tier of each plan is part of the per-plan review record. Useful at Step 7 (final graded review) so the grader can compare each plan's coverage tier against what the todo claimed at completion.

Suggested format inside `reviews/{NNN}-test-review.md`:

```
**Closing tier:** must-cover | should-cover | nice-to-have
**Plan-related findings closed at this tier:** [count]
**Tech-debt queued:** Plan {NNN}, Plan {NNN}, ...
**Explicit accepts (rare):** [list with reasons]
```

#### Project-specific test-tier guidance

If the project has a project-level `test-reviewer` agent (under `<repo>/.claude/agents/test-reviewer.md`), it carries the project's test-project layout, framework conventions, and tier-mapping rules. The generic agent under `~/.claude/agents/test-reviewer.md` defers to it. The orchestrator should invoke whichever exists; both reduce to the same loop shape above.

### Step 6 — Loop or Fall Through

After Step 5b, check the Plan Index:

- **Plans queued (status `Draft`)** → loop back to Step 2 for the next plan.
- **Plan Index has only `Done` and `Abandoned` plans, no queued work** → fall through to Step 7.

A plan reaches `Done` only after Step 5b's must-cover findings are closed (or explicitly accepted by the user). Tech-debt plans queued out of Step 5b show up here as new `Draft` rows; the user decides whether to work them in this todo's loop or leave them for after.

Before falling through, verify Acceptance Criteria on the todo. If any criterion is unmet, draft another plan.

### Step 7 — Final Graded Review (Mandatory)

Triggered when the last in-flight plan goes Done **and** the Plan Index has no queued plans. **The orchestrator prompts the user to confirm the todo's Acceptance Criteria are met.** On confirmation, run the same build+test pre-flight as Step 5 (once each, captured to `reviews/final-build.log` and `reviews/final-test.log`), then fire the final review.

Invoke **code-reviewer** with the **whole arc** — the todo, every plan in `plans/`, the Discovery Log, per-plan reviews, **plus the build and test log paths**. Ask for a graded review against the rubric: traces every Acceptance Criterion through real code, evaluates Discovery Log decisions, grades Scope Discipline against the todo's Out of Scope list. The reviewer greps the provided logs for build/test signal; it does NOT run build or test itself.

The rubric is `references/rubric.md`. Section 5 (Framework Correctness) is framework-agnostic in this user-skill — project-specific idiom checklists live in the project repo, typically at `<repo>/.claude/skills/iterative-todo/references/rubric-framework.md` or `<repo>/docs/code-review-rubric.md`. The reviewer adds those to its checks if found.

Discovery at the final review is also welcome. The reviewer reads the full arc and may surface things missed across plans. These become callouts to address before completion or queued plans if they're material enough.

Write the summary to `reviews/final-graded-review.md`. If Grade B or C, present "to reach A" suggestions to the user. The user acknowledges (accept-as-is or address). Re-invoke code-reviewer for re-grade if items are addressed; append, don't overwrite.

### Step 8 — Documentation Review (Mandatory)

Invoke **business-requirements-documenter** with the todo, all plans, the Discovery Log, all per-plan and final reviews, and any internal-contradiction callouts surfaced earlier. The documenter:

1. Identifies new business rules, changed rules, filled gaps, and decisions that emerged across plans.
2. **Reconciles internal contradictions** that earlier reviewers called out — now that the implementation has settled, the right resolution is usually clear, and the documented rules get updated to match.
3. Updates the project's permanent docs.

Write the summary to `reviews/documenter-review.md`. The orchestrator applies any developer-deliverable code touch-ups the documenter requested.

Skip ONLY when the change demonstrably touches no documented business behavior (rare for iterative todos — the surface area is usually broad enough that something is documented).

### Step 9 — Completion

Verify:

- Final graded review exists and the user has acknowledged the grade.
- Documentation review exists (or skip is recorded), including reconciliation of any earlier internal-contradiction callouts.
- Plan Index status: every plan is `Done` or `Abandoned`.
- Acceptance Criteria all checked.

Set todo status to `Complete`. Move `docs/todos/{ID}-{todo-name}/` to `docs/todos/completed/{ID}-{todo-name}/`. The whole folder moves — plans, reviews, todo.md. The `{ID}` prefix is preserved in the move so cross-references (like `OVL-025`) continue to resolve. If the project maintains `docs/todos/_ids.md`, move the row from the **Active** section to the **Complete / Withdrawn / Superseded** section in the same change.

**The user decides when to commit and when to open PRs.** The orchestrator may *suggest* a commit at natural milestones — most commonly when a plan moves to `Done`, after a per-plan code review lands, or after the final graded review — but the suggestion is a question, not an action. The orchestrator does not commit, push, or open PRs without the user saying yes. PRs in particular are entirely the user's call; never assume a PR cadence (per plan, per todo, or otherwise).

## Discovery Log Format

The Discovery Log is the anti-forgetting mechanism. Each entry is one bullet, terse, navigational:

```
### YYYY-MM-DD — Plan {NNN}
- **Finding:** [one sentence]
- **Decision:** [Amend | Abandon | Defer | Re-split]
- **Index changes:** [only on Re-split — what plans were added, dropped, or reordered; or "n/a"]
- **Follow-up:** [Plan {NNN} or "n/a"]
```

The point is searchability and cross-reference, not narrative. Save the long form for the affected plan's Plan Amendments or Abandonment Reason. The `Index changes:` line only applies to **Re-split** decisions — list the specific Plan Index edits inline so the change is auditable. Omit it (or write "n/a") for Amend / Abandon / Defer.

## Plan Amendments vs. Abandonment Reason

- **Plan Amendments** (append-only on a plan) — used when a discovery led to **Amend**. The original Scope/Intent/Steps stay as written; amendments record what changed and why. The plan continues toward `Done`. Amendments are how the plan stays accurate without rewriting — they are the visible record that the plan was a working hypothesis, not a contract.
- **Abandonment Reason** (one paragraph on a plan) — used when a discovery led to **Abandon**. The plan stops where it is; status goes to `Abandoned`. Reason captures: what we believed when drafting, what turned out to be true, what the next plan should do differently. The reason is what makes abandonment cheap — the next plan inherits the lesson.

Never delete an abandoned plan. The whole point of the iterative shape is that abandoned attempts remain visible.

## Sibling Todos — Capture Work That Falls Out

A todo has one focused goal. Implementation often surfaces work that **doesn't advance that goal** but is still worth not losing. A sibling todo is the **capture-or-lose** mechanism for that work — its only job is to keep the discovery from evaporating once you go back to the goal you were actually working on.

The test is narrow:

- **Does this discovery advance the todo's Goal?** No — and yet it's worth keeping. → Sibling todo.

If it advances the Goal, it's not a sibling — it's an in-todo response (Amend / Abandon / Defer / Re-split). Most discoveries are in-todo. Sibling todos are rare.

The triggers that are **not** by themselves enough for a sibling: distinct branch sequencing, separate PR, "this is bigger than a plan." All of those can also be true of in-todo work. The deciding question is always whether the discovery moves *this* Goal forward.

When you do open a sibling, it's its own folder under `docs/todos/{ID}-{sibling-name}/` (with its own freshly-assigned ID per Step 1) with its own goal, plans, Discovery Log, and graded review. Record the relationship in the parent todo's **Sibling Todos** section (one bullet per sibling, one line on why it surfaced here). The sibling's `todo.md` should mirror the back-reference. The sibling proceeds independently — the parent doesn't wait for it unless there's a real dependency, and even then dependencies are rare.

If the work isn't worth keeping, just drop it. Capturing every stray observation as a sibling is the noise the system is trying to avoid.

## Internal vs. External Contradictions

Reviewers will surface two kinds of tension. They have different gating:

- **External contradiction** — plan contradicts a documented business rule (`docs/business-rules.md` or equivalent). **Veto-tier.** Address before implementation, either by adjusting the plan or by getting explicit user sign-off to overwrite the documented rule.
- **Internal contradiction** — plan has a tension with the parent todo's stated intent, or with assertions made elsewhere in the same plan, or with rules implied by other plans in the same todo's Plan Index. **Callout-tier, not veto.** Record the callout, keep implementing. Reconcile at the documenter step (Step 8) when the implementation has settled and the right resolution is usually obvious. Some internal contradictions resolve themselves during implementation (the discovery clarifies which side was right); others get explicitly resolved by updating the documented rules during Step 8.

This split exists because internal contradictions usually look bigger before the code is written than after. Forcing reconciliation at plan time often produces guesses that turn out wrong; deferring to Step 8 gets the right answer cheaper.

## Conversion: project-todos Todo → iterative-todo

Use when an existing `project-todos` todo has turned out to be discovery-heavy mid-flight. See `references/conversion-checklist.md` for the step-by-step. High points:

1. Create the new folder structure (`docs/todos/{ID}-{name}/plans/`, `reviews/`) — assign an ID per Step 1 if the existing todo doesn't have one.
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
| Done (no code review yet) | Step 5 (per-plan code review) |
| Done (code review done, no test review yet) | Step 5b (test review loop) |
| Done (test review closed) | Step 6 (loop or fall through) |
| Abandoned | Step 2 (draft next plan with the next monotonic number) |

If every plan is `Done` or `Abandoned` and the Plan Index has no queued plans → Step 7 (prompt user to confirm Acceptance Criteria).

## Best Practices

1. **Plans describe intent, not code.** When in doubt, compress. A step that names a fully-qualified type with a line number is too detailed; a step that says "move regenerate-and-clear onto the aggregate as a domain verb" is right.
1a. **Tests are iterative too.** Plans don't enumerate test cases — Acceptance bullets are the test surface. Coverage gets pinned in Step 5b's post-implementation loop, not in the plan body. Closing-tier per plan is the user's call; tech-debt findings queue as their own plans.
2. **Keep plans small.** A plan that takes more than a day to draft and execute is too big — split it. Fast feedback between design and implementation is the whole point.
3. **Plans are not locked at implementation start.** The Plan Amendments section exists so the plan can stay accurate as discoveries land. Use it.
4. **Log every discovery.** If something surprised you, it surprises future-you reading the todo. One-line Discovery Log entries cost nothing and pay back enormously.
5. **Stop and ask** when a discovery threatens intent, an invariant, or an acceptance signal. Silent scope creep is the failure mode this skill exists to prevent.
6. **Abandonment is normal.** A plan abandonment is not a failure — it's the iterative shape working. The Abandonment Reason is the deliverable; the next plan is the reward.
7. **Discovery at code review is welcome.** A reviewer redirecting on shape is the system working. Treat redirect findings as the natural complement to plans-as-prescriptions.
8. **Internal contradictions get reconciled at Step 8, not at plan time.** Don't block the plan on tensions that the implementation will likely clarify on its own.
9. **The todo's Acceptance Criteria are the exit gate.** Not "all listed plans done." Plans come and go; Acceptance defines completion.
10. **Final graded review reads the whole arc.** When invoking code-reviewer for the final review, ensure the agent reads every plan and the full Discovery Log — a review that only looks at the last plan misses the cross-plan story.
11. **Don't amend a Done plan.** Findings post-`Done` go into a new follow-up plan, not into the old plan's Amendments. Plans are sealed at `Done`.
12. **Project-specific framework idioms live in the project repo, not in this user skill.** The base rubric stays framework-agnostic. The reviewer adds project-local idiom checks if the project provides them at `<repo>/.claude/skills/iterative-todo/references/rubric-framework.md` or `<repo>/docs/code-review-rubric.md`.

## Reference Files

- `references/todo-template.md` — todo template (with Discovery Log + Plan Index + Sibling Todos)
- `references/plan-template.md` — small plan template (Scope, Intent, Framework Alignment, Constraints, Steps, Acceptance, Amendments, Abandonment Reason)
- `references/conversion-checklist.md` — convert an older flat-file todo to the iterative folder shape
- `references/rubric.md` — seven-category rubric for the final graded review
- `references/plan-template-neatoo.md` — Domain Model Behavioral Design addendum for Neatoo projects; append to a plan when needed

Project-local overlays the reviewer picks up if present:

- `<repo>/.claude/skills/iterative-todo/references/rubric-framework.md` — project-specific framework-correctness idioms (added to base rubric Section 5)
- `<repo>/docs/code-review-rubric.md` — alternate location for the same overlay
- `<repo>/docs/code-review-calibration.md` — what Grade A means for this project

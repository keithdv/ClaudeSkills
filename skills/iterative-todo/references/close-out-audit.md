# Close-Out Audit Checklist — iterative-todo

The code-reviewer runs this audit at the iterative-todo close-out (Step 7), over the **whole arc** — the todo, every plan, the Discovery Log, every review file. The same checklist's per-plan subset informs opt-in per-plan code reviews at Step 5.

**The audit is findings-only. There are no letter grades.** Every finding is either **veto-tier** (fix before the todo completes) or **callout-tier** (queue as a plan, or accept with a recorded reason). The audit's value is verification and drift-detection, not scoring — the orchestrator and user act on findings, not on a grade.

## Project Calibration Takes Precedence

Before applying this checklist, load the project's calibration document if it exists:

- `docs/code-review-calibration.md`
- `docs/review-calibration.md`

The calibration defines what "clean" means for the specific project and lists overreach categories reviewers must not flag. **When this checklist and the calibration disagree, the calibration wins.** A finding whose only justification is a generic best practice not backed by the calibration or the project's CLAUDE.md is overreach — drop it. If no calibration exists, proceed and flag its absence as a one-line note.

## Confidence on Findings

Every finding carries a confidence label:

- **High** — verifiable from the code/logs in front of you. A test fails, a citation is wrong, a CLAUDE.md rule is plainly violated. Actionable.
- **Medium** — plausible from patterns and standards but context-dependent. Worth raising and discussing.
- **Low** — speculative or stylistic without backing in CLAUDE.md or the calibration. Default: don't include. If included, mark Low so the user can dismiss without weight.

Only High and Medium findings can be veto-tier.

## Audit Areas

Work through all seven. Each produces findings (or an explicit "clean" with evidence), not a grade.

### 1. Acceptance Criteria Traced

Every Acceptance Criterion on the parent `todo.md` is traced to specific code (file:method:line) and the implemented behavior actually satisfies it. Read the code that implements each criterion — don't assume a well-named file means the criterion holds.

- Untraceable criterion, or traced code that doesn't satisfy it → **veto-tier**.
- Weak trace (points at related code rather than the exact logic) → **callout-tier**.

Also spot-check each Done plan's own Acceptance bullets. A plan marked `Done` with an unmet bullet is a container-integrity finding (area 7).

### 2. Test Evidence Honesty

The per-plan Test Evidence maps and Step 5 closing-tier records are the artifacts; verify they're honest. **Do not re-do the test-reviewer's job** — no re-enumeration of test scenarios.

- Every behavioral Acceptance bullet has a row; silent omissions (no row at all) → **veto-tier**.
- Cited test methods exist (grep the test files); a cited method that doesn't exist is a lie → **veto-tier**.
- Tier matches: a bullet declared `[integration]` cited with a unit-only test is not pinned → **veto-tier** unless the user's recorded acceptance covers it.
- `MISSING — <reason>` rows are acceptable when the user acknowledged them; verify the acknowledgement exists (Discovery Log, plan, or review file).
- Each Done plan has a `reviews/{NNN}-test-review.md` with a closing tier (or a recorded skip for trivial plans); a closing tier that looks light against the work's risk profile → **callout-tier**.
- **Sacred-test rule:** an existing test weakened to make new code pass (assertions removed, cases deleted, expected values bent to broken behavior) → **veto-tier**, always.

### 3. Design Alignment (Silent Drift)

The implementation matches each plan's Intent and Steps, **or** the divergence is recorded — in Plan Amendments, the Discovery Log, or a Re-split. The point is catching silent drift, not penalizing keyboard discovery: a plan whose final shape differs from its draft is fine if the divergence is captured; the same divergence uncaptured is a finding.

- Material divergence with no Amendment / Discovery Log entry / Re-split → **veto-tier**.
- Minor uncaptured divergence (helper split differently, property renamed), obviously harmless → **callout-tier**.

### 4. Code Quality

Readability, naming, abstraction level, dead code, speculative generality. Findings here are almost always **callout-tier**; reserve veto-tier for code that is genuinely misleading (naming that lies, dead paths that look live).

### 5. Framework Correctness

Idioms come from the project's CLAUDE.md plus a project-local overlay if present:

- `<repo>/.claude/skills/iterative-todo/references/rubric-framework.md`
- `<repo>/docs/code-review-rubric.md`

The overlay's idiom list is **added** to the checks. A CLAUDE.md hard rule broken or a load-bearing idiom violated → **veto-tier**. Minor deviations (missing XML comment, cosmetic attribute omission on working code) → **callout-tier**.

### 6. Build & Test Health

**Grep the logs the orchestrator provided** (`reviews/final-build.log`, `reviews/final-test.log`). Do NOT run build or test yourself — if log paths are missing, fail out per the agent's rules.

- Build failure, or **any** failing test → **veto-tier**. Report every failing test by name; do not classify failures as "pre-existing" — that's the user's call.
- New warnings in changed files → **callout-tier** (veto-tier if they mask real defects).

### 7. Container Integrity (Mandatory Walk)

The workflow stays honest only if the container reflects reality. Walk all of it:

1. **Plan Index ↔ `plans/` reconciliation.** Every file in `plans/` has an Index row; every Index row points at a real file; numbering is monotonic with no duplicates.
2. **Abandoned plans** have a filled Abandonment Reason; **Retired plans** have a one-line retirement note naming where the work went.
3. **Deferral sweep.** Grep every plan body and the todo for deferral phrases ("deferred," "future plan," "follow-up plan," "next plan will," "later in this todo," "covered by {ID}-NNN," "pass 2," "phase 2"). Each hit must trace to a Plan Index entry (any status) or a Sibling Todo. An untraced deferral is work evaporating → **veto-tier**.
4. **Out of Scope respected.** Every item on the todo's Out of Scope list still holds; an Out of Scope item changed without an authorizing Discovery Log entry → **veto-tier**. A todo with no Out of Scope list is itself a callout.
5. **Skipped Steps** entries exist for every gate that didn't run.

## Output Format

```markdown
## Close-Out Audit — [YYYY-MM-DD]

**Verdict: [CLEAN | CONCERNS]**  (CONCERNS = one or more veto-tier findings)

### Veto-Tier Findings
[Each: area, file:line evidence, confidence, what must change. "None" if clean.]

### Callout-Tier Findings
[Each: area, evidence, confidence, suggested disposition (queue as plan / accept with reason / fix inline). "None" if clean.]

### Acceptance Criteria Trace
| Criterion | Evidence (file:method:line) | Holds? |
|---|---|---|

### Build & Test Evidence
- Build: [PASSED/FAILED — from {log path}]
- Tests: [N passed, N failed — from {log path}; every failure named]

### Plan Index Snapshot
| # | File | Status | One-line summary |
|---|------|--------|------------------|

**Sibling Todos:** [each with one line, or "None."]

## Deferred Work Carrying Forward

[EVERY deferral — queued plan, sibling todo, accepted MISSING row — so the user sees at a glance what this todo did NOT do. Acceptance doesn't make a deferral disappear; it makes it OK to ship. If zero: "No deferred work — todo is fully self-contained."]

| # | Description | Where queued / how accepted | Cost / carry-forward |
|---|-------------|------------------------------|----------------------|
```

The orchestrator writes the summary into the todo's Close-Out Audit section and `reviews/close-out-audit.md`.

## Re-Audit Behavior

When re-invoked after fixes: read the most recent audit entry, verify each veto-tier finding was addressed (cite the fixing change), then re-walk all seven areas — fixes can introduce new drift. Return a fresh response; the orchestrator appends, never overwrites.

# Close-Out Audit — iterative-todo Step 7

The code-reviewer runs this over the **whole arc** — on the arc branch with every plan PR merged: the todo, every plan, every review file, the logs. It returns a **grade** and a capped set of findings. The grade is a statement about what was done, not a target for what is left: **there is no "to reach A" section.**

## The Grade

- **A** — every Acceptance Criterion traced to specific code with evidence; no veto-tier findings.
- **B** — every criterion either traced or explicitly accepted as a gap by the user with a recorded reason; every accepted gap is a Should or Could; no veto-tier findings; every gap on the Follow-on list.
- **C** — at least one criterion neither traced nor accepted, a Must criterion accepted as a gap without a `Reprioritize` entry demoting it first, or at least one veto-tier finding open.

A and B close the todo. C names the specific item(s); the user picks fix / accept (→ B) / close as Blocked. The auditor does not recommend which.

**Veto-tier means exactly two things:** the work contradicts a documented rule or excluded feature, or the build / a sacred test / any test is red. Everything else is a callout.

## Calibration and Confidence

Load `docs/code-review-calibration.md` (or `docs/review-calibration.md`) if it exists; when it and this checklist disagree, the calibration wins. A finding whose only justification is a generic best practice not backed by the calibration or CLAUDE.md is overreach — drop it.

Every finding carries a confidence label — High (verifiable from code/logs in front of you), Medium (plausible, context-dependent), Low (speculative; default: omit). Only High and Medium can be veto-tier.

## Finding Budget and Reachability

- **Veto-tier: list all.** They are rare by definition; more than five means the todo was not ready for audit — say so.
- **Every callout states `Affects: AC-n (word)`** — the criterion it bears on and that criterion's priority word. Callouts affecting a **Must** criterion are listed in full; more than five of them is itself the lead finding. Callouts affecting Should or Could criteria: **at most five** together, ordered by consequence; beyond five, one line, "N more, lower priority, not listed."
- **Every callout states `Reachable by:`** — a user action, an observed failure, or a live caller. A callout that cannot goes under **Theoretical** as one line and is not triaged.
- **Check the Dismissed section before raising anything.** A finding already dismissed is not re-raised; if you believe the dismissal was wrong, one line under Theoretical with the reason.

A clean audit is a complete, expected result. Do not manufacture callouts.

## Audit Areas

### 1. Acceptance Criteria Traced (the grade's substance)

For every criterion on `todo.md`: cite the file:method:line that implements it and confirm by reading that the behavior holds. A well-named file is not evidence. Untraceable or not-actually-satisfied → the grade is C for that criterion unless the user has recorded an accepted gap (then B) — and an accepted gap on a Must criterion counts only if a `Reprioritize` entry demoted it first; otherwise C.

### 2. Test Evidence Honesty

Do not redo the test-reviewer's job. Verify the artifacts: every behavioral Acceptance bullet on every Done plan has a Test Evidence row; cited methods exist (grep); tiers match; `MISSING` rows have a recorded acceptance and none of them is a Must bullet without a demotion in the Gate Record; each Done plan has a Gate Record with at most two rounds. A cited test that does not exist, or a sacred test weakened, is veto-tier.

### 3. Build & Test Health

Grep the provided logs (`reviews/final-build.log`, `reviews/final-test.log`). Do NOT run build or test; fail out if paths are missing. Any failing test → veto-tier, every failure named.

### 4. Framework Correctness

CLAUDE.md hard rules plus the project overlay (`docs/code-review-rubric.md`) if present. A hard rule broken → veto-tier. Minor idiom drift → callout.

### 5. Design Alignment

Implementation matches each plan's Intent, or the divergence is recorded in Amendments / Discovery Log / Re-split. Silent material drift → callout (veto only if it contradicts a documented rule).

### 6. Container Integrity

Walk it all; each miss is a callout unless noted:

1. Plan Index ↔ `plans/` reconciled; numbering monotonic; **plans issued ≤ cap, or the raise is logged**.
2. Abandoned plans have a reason; Retired plans have a one-line note.
3. Every Status cell is a word plus ≤ 5 words; no limbo states.
4. Every plan and Discovery Log entry names its `AC-n`.
5. Deferral phrases in any plan body ("deferred", "follow-up plan", "later", "phase 2") trace to a Punchlist row, a Plan Index row, a Dismissed row, or the Follow-on list. Untraced deferral → veto-tier (work evaporating).
6. Punchlist rows are one line; every open row is on the Follow-on list.
7. Out of Scope respected; a change to it has an authorizing Discovery Log entry.
8. Prose budgets: Goal ≤ 150 words, log entries ≤ 60 words. Over-budget → callout, one line naming the worst offender. Plan length (~200 lines at implementation entry, ~300 with amendments) is a recommendation, not a budget — never a miss on its own.
9. Every Done plan's Plan Index row carries a merged PR number into the arc, and no plan or punchlist branch is unmerged (`gh pr list --state open --base {arc}` is empty). An open PR is a miss, not an input.
10. Every Acceptance Criterion and every plan Acceptance bullet carries a priority word; every priority change has a `Reprioritize` entry (todo) or a Gate Record line (plan); Follow-on rows carry their word. A Must accepted as a gap without a demotion → C, not a callout.

## Output Format

```markdown
## Close-Out Audit — [YYYY-MM-DD]

**Grade: [A | B | C]**

### Acceptance Criteria Trace
| AC | Word | Evidence (file:method:line) | Holds? | If not: accepted gap? |
|---|---|---|---|---|

### Veto-Tier Findings
[All. Each: area, file:line, confidence, what must change. "None" if clean.]

### Callouts (Must in full; ≤ 5 Should/Could)
[Must-affecting first, in full; then ≤ 5 Should/Could. Each: area, evidence, confidence, `Affects: AC-n (word)`, `Reachable by:`, suggested disposition (punch / dismiss / accept / Follow-on). "None" if clean.]
[N more, lower priority, not listed.]

### Theoretical (not triaged)
[One line each, or "None".]

### Build & Test
- Build: [PASSED/FAILED — {log path}]
- Tests: [N passed, N failed — {log path}; every failure named]

### Container
- Plans issued / cap: [n / m]
- Status cells over budget: [n]
- Untraced deferrals: [list or "None"]
- Prose over budget: [worst offender or "None"]
- Open PRs into the arc: [None | #n …]
- Must accepted as gap without demotion: [None | AC-n]

### Follow-on (draft for Step 8)
[One line each: queued Drafts at close, accepted gaps, open punchlist rows, unpinned tests, doc debt. "None — fully self-contained."]

### Read report
- Read beyond the brief: [...]
- Named but unused: [...]
```

## Re-Audit

When re-invoked after fixes: read the previous audit entry, verify each veto-tier finding (or the C-grade item) was addressed with a cited change, re-walk the areas, return a fresh grade. The orchestrator appends; never overwrites.

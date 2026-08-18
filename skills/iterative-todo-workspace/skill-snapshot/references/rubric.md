# Graded Code Review Rubric — iterative-todo

The code-reviewer agent grades seven categories at the iterative-todo final review (Step 7). Each category gets A, B, or C. The overall grade is the **worst** category — Grade A requires A across all seven.

The same rubric also informs the per-plan code review at Step 5, but per-plan reviews are lightweight: the reviewer flags veto-tier and callout-tier findings and can grade only the categories that have meaningful evidence at that point. The full seven-category grading is reserved for Step 7, where the whole arc is in scope.

## Project Calibration Takes Precedence

Before applying this rubric, the code-reviewer MUST load the project's calibration document if it exists. Typical locations:

- `docs/code-review-calibration.md`
- `docs/review-calibration.md`
- `docs/grade-a-calibration.md`

The calibration document defines what Grade A means **for that specific project** — team size, user count, architectural scope — and lists overreach categories reviewers must not flag. **When this rubric and the project calibration disagree, the calibration wins.** A finding whose only justification is a generic best practice not backed by the calibration doc or the project's CLAUDE.md is overreach — drop it.

If no calibration document exists, proceed with the rubric below and flag the missing calibration as a one-line note at the end of the review.

Output for each category:
- Grade (A / B / C)
- One-line justification referencing specific evidence (file:line, test name, etc.)
- If not A: concrete "To reach A" suggestions with file:line citations, **each tagged with a confidence level**

## Confidence on Findings

Every "to reach A" suggestion carries a confidence label: **High**, **Medium**, or **Low**.

- **High** — the issue is verifiable from the code in front of you. A test fails, a citation is wrong, a CLAUDE.md rule is plainly violated. The orchestrator and user should treat this as actionable.
- **Medium** — the issue is plausible based on patterns and standards, but it depends on context the reviewer doesn't have. Worth raising, worth discussing, not necessarily a blocker.
- **Low** — speculative, "while you're in there" suggestions, style preferences without backing in CLAUDE.md or the calibration doc. Default: don't include them at all. If included, mark Low so the user can dismiss without weight.

A category grade reflects only High and Medium findings. Low findings inform but never lower the grade.

## Iterative-Todo Specifics

**The unit being graded is the whole todo, not a single plan.** Step 7 reads every plan in `plans/`, the Discovery Log, every per-plan review under `reviews/`, and the parent `todo.md`. Acceptance is measured against the **todo's** Acceptance Criteria, not any one plan's Acceptance section. Each plan's individual Acceptance bullets are sub-goals; the todo's Acceptance Criteria are the exit gate.

**Discovery is welcome.** A reviewer redirecting on shape, finding gaps the implementer didn't see, or noting work that should queue as a new plan is the system working. Treat redirects as natural complements to plans-as-prescriptions, not as evidence the plans were bad.

**Abandoned plans are not graded for implementation quality.** They're graded for *abandonment quality* — does the plan have an Abandonment Reason that captures what was learned and what the next plan should do differently? A missing Abandonment Reason on an Abandoned plan is a Scope Discipline finding.

## 1. Acceptance Criteria Coverage

Every Acceptance Criterion on the parent `todo.md` is traced to specific code (file:method:line) and the implemented behavior actually satisfies it.

| Grade | Criteria |
|-------|----------|
| A | Every todo-level Acceptance Criterion has a file:method:line citation. Each citation verifies the criterion holds. |
| B | All criteria are traced, but 1–2 traces are weak (point to related code rather than the exact logic), OR one criterion's logic is questionable but functional. |
| C | One or more criteria cannot be traced to specific code, OR the traced code does not actually satisfy the criterion. |

The reviewer should also spot-check each plan's individual Acceptance bullets to confirm they were met when that plan went `Done`. A plan marked `Done` with an unmet Acceptance bullet is a Scope Discipline finding (and likely a sign the plan should have stayed `In Progress`).

## 2. Test Coverage

Coverage is graded against two artifacts: the per-plan **Test Evidence** map (filled before code-review per Step 5) and the per-plan **closing tier** record from Step 5b. The first proves the prescribed-tier tests actually got written; the second proves the post-implementation review loop ran. Code-reviewer **does not re-do the test-reviewer's job** — it verifies both artifacts exist, that the cited test methods exist and pin the claimed signal, and that the closing tier is appropriate for the work's risk profile.

### Per-plan Test Evidence map (Step 5 pre-flight)

Each plan's `## Test Evidence` table maps every Acceptance bullet to a test method at the bullet's tier-tag. The reviewer spot-checks:

- **Every behavioral Acceptance bullet has a row.** Bullets without rows are gaps the orchestrator silently elided — automatic finding.
- **Cited test methods exist.** Grep the test files; if `ProjectName.Tests.X.Y` is cited but doesn't exist, the row is a lie.
- **Tier matches.** A bullet declared `[integration]` cited with a unit-only test is a tier mismatch — the bullet is **not pinned** at its declared tier even if the unit test passes.
- **`MISSING` rows are explicit.** A `MISSING — <reason>` row is acceptable when the user accepted the gap; a missing row (no entry at all) is not.

### Closing tier (Step 5b)

Each Done plan has `reviews/{NNN}-test-review.md` with a closing tier. The reviewer checks the closing tier against the work's risk profile.

### Grades

| Grade | Criteria |
|-------|----------|
| A | Every Done plan has a fully-populated Test Evidence table with all cited tests existing at the declared tier (or `MISSING` rows with explicit reasons), AND a `reviews/{NNN}-test-review.md` with a closing tier. No plan-related must-cover findings remain unaddressed. No sacred test was gutted. Closing-tier picture matches what the orchestrator and user committed to in the todo. |
| B | Test Evidence and test-review records exist for every Done plan, but 1–2 minor gaps: one tier mismatch where the cited unit test materially exercises the behavior (close call), or one plan closed at a tier that looks light given the behavior changed. No sacred test was gutted, no `MISSING` rows lack explicit reasons. |
| C | One or more Done plans have a missing or under-populated Test Evidence table (silent omissions, not explicit `MISSING` rows), OR cited tests don't exist or don't match the declared tier in a way that means the bullet isn't actually pinned, OR a plan-related must-cover finding was silently deferred (no recorded "explicit accept with reason"), OR an existing (sacred) test was modified in a way that weakens its original intent. |

**"Sacred test" rule** (from CLAUDE.md): existing tests must never be gutted to make new code pass. Even one weakened existing test is automatic C in this category.

**What this category is NOT:** an enumeration of every test scenario the reviewer would have written from scratch. The post-implementation `test-reviewer` loop already evaluated coverage against actual code, with the user picking the closing tier. The code-reviewer's job is to verify *the artifacts the orchestrator committed to* (the tier tags in Acceptance, the Test Evidence map, the closing tier) are honest — not to re-run the test-review loop.

## 3. Design Alignment

The implementation matches each plan's **Intent** and **Steps**. Divergence is OK if it's recorded — in **Plan Amendments** on the plan, in the todo's **Discovery Log**, or as an explicit Re-split that updated the Plan Index.

| Grade | Criteria |
|-------|----------|
| A | Implementation follows each plan's Intent and Steps. Any divergence is captured in Plan Amendments or the Discovery Log with a clear Why. |
| B | Implementation follows each plan overall, but 1–2 minor divergences aren't captured in Amendments or the Discovery Log (e.g., a helper split differently, a property named differently). The divergences are obviously harmless. |
| C | Implementation materially diverges from one or more plans (different approach, missing intent, different aggregate boundary) without a Plan Amendment, Discovery Log entry, or Re-split that explains the change. |

The point of this category is to catch silent drift — implementation that ignored what the plan said and didn't tell anyone. It is **not** to penalize legitimate keyboard discoveries; those are exactly what the Plan Amendments and Discovery Log mechanisms exist to absorb.

## 4. Code Quality

Readability, naming, abstraction level, absence of dead code.

| Grade | Criteria |
|-------|----------|
| A | Clear naming, right level of abstraction for the task, no dead code, no speculative generality, no unused parameters or methods. Comments only where the "why" is non-obvious. |
| B | Mostly clean but minor issues: one awkward name, one commented-out block, one method that could be collapsed or split. |
| C | Material issues: unclear naming that requires inspection to understand, dead code left in place, over-engineered abstraction for a simple task, or meaningful duplication that warrants extraction. |

## 5. Framework Correctness

Project-specific framework idioms are respected. The code-reviewer must read the project's CLAUDE.md for the framework rules to check, and the project's calibration doc (if any) for which rules are load-bearing vs. nice-to-have.

This rubric stays framework-agnostic. The list of idioms-to-check comes from the project's CLAUDE.md and any project-local rubric overlay. The reviewer should look for a project-local overlay at one of:

- `<repo>/.claude/skills/iterative-todo/references/rubric-framework.md`
- `<repo>/docs/code-review-rubric.md`

If found, the overlay's idiom list is **added** to Section 5 checks (it does not replace this rubric). The user skill never carries project-specific idioms.

| Grade | Criteria |
|-------|----------|
| A | All applicable framework idioms (per CLAUDE.md and project-specific rubric reference) followed correctly. |
| B | One minor deviation (e.g., a missing XML comment, a framework attribute omitted on code that works anyway). |
| C | One or more material violations (a CLAUDE.md hard rule broken, a load-bearing framework idiom violated, a known footgun left in place). |

## 6. Build & Test Health

The code-reviewer runs a fresh build and the project's test command. No trusting of reported results.

| Grade | Criteria |
|-------|----------|
| A | Build passes with no new warnings in changed files. All tests pass. |
| B | Build passes, all tests pass, but one or two new warnings in changed files (style, nullability). |
| C | Build fails, OR any test fails (including tests classified as "pre-existing" — the user is the only one who can classify a failure as acceptable), OR significant new warnings in changed files. |

**Any test failure is automatic C.** Report the failure; do not judge whether it is acceptable. That's the user's call.

## 7. Scope Discipline

The implementation respects the parent todo's **Out of Scope** list AND the **Plan Index** is internally consistent — every plan has a status, every Abandoned plan has an Abandonment Reason, every deferral phrase in any plan body traces to a Plan Index entry.

| Grade | Criteria |
|-------|----------|
| A | Every item on the todo's Out of Scope list still holds after the change. Plan Index lists every plan in `plans/` with current status. Every `Abandoned` plan has an Abandonment Reason paragraph. No phrases like "future plan," "follow-up plan," "deferred," "covered by Plan NNN," "later in this todo," or "next plan will" appear in any plan body without a corresponding Plan Index entry (status `Draft`, `In Progress`, or `Done`). |
| B | One Out of Scope item was incidentally touched but behavior is preserved. Plan Index is complete. All deferrals trace to Plan Index entries. |
| C | One or more Out of Scope items were changed without a Plan Amendment or Discovery Log entry authorizing it, OR the Plan Index is missing a plan that exists in `plans/`, OR an Abandoned plan has no Abandonment Reason, OR an in-body deferral phrase doesn't trace to a Plan Index entry. |

**Plan Index audit is mandatory.** The reviewer must:

1. List every file in `plans/` and confirm each has a matching row in the parent `todo.md`'s Plan Index.
2. For each `Abandoned` plan, confirm the **Abandonment Reason** section is filled.
3. Sweep every plan body (and the todo body) for deferral phrases. Each hit must trace back to a Plan Index entry by number or title.
4. List every gap with file location in the "To Reach A" section under Scope Discipline.

Reasoning: the iterative-todo workflow only stays honest if the Plan Index reflects reality. A queued follow-up that never made it into the index is the same silent-drop-of-scope failure project-todos hit with un-linked Companion Plans entries — the work evaporates. The fix is the same: every deferral becomes an index entry.

If the parent todo lacks an Out of Scope list, the code-reviewer notes this as a planning gap and grades on apparent intent (not a free pass — a missing list is itself a concern to flag).

---

## Output Format

The code-reviewer returns findings in this structure:

```markdown
## Final Graded Review — [YYYY-MM-DD]

**Overall Grade: [A / B / C]** (worst category)

| Category | Grade | One-line justification |
|----------|-------|------------------------|
| Acceptance Criteria Coverage | A | All 5 todo-level criteria traced; verified. |
| Test Coverage | B | All Done plans have test reviews; Plan 003 closed at must-cover only on a state-mutation path that warrants should-cover. |
| Design Alignment | A | Plan 002 amendments capture the seam shift; rest match Intent. |
| Code Quality | A | Clean naming; no dead code. |
| Framework Correctness | B | Missing .ToUtcForDb() on one DateTime assignment in PaymentEdit.cs. |
| Build & Test Health | A | Build clean, all 247 tests pass. |
| Scope Discipline | A | Out-of-scope list preserved. Plan Index consistent with plans/ folder. Plan 002 Abandonment Reason captures the lesson. |

### To Reach A

**Test Coverage:**
- [Medium] `reviews/003-test-review.md` closed at must-cover only. Plan 003's state transition at `VisitV2.cs:142` would benefit from a should-cover boundary test on the in-flight state. Suggest queuing a small follow-up plan or addressing inline.

**Framework Correctness:**
- [High] `PaymentEdit.cs:87` — `entity.Date = this.Date` needs `.ToUtcForDb()` per CLAUDE.md DateTime rules.

### Build & Test Evidence

- Build: PASSED (0 errors, 0 new warnings in changed files)
- Tests: 247 passed, 0 failed (command: `dotnet test -m:1`)

## Plan Index Snapshot

[Walk the parent todo's Plan Index. List every plan with its final status and a one-line summary. List every Sibling Todo. This is the artifact the user uses to confirm the whole arc is captured.]

| # | File | Status | Description |
|---|------|--------|-------------|
| 001 | `plans/001-{name}.md` | Done | [Summary] |
| 002 | `plans/002-{name}.md` | Abandoned | [Summary + 1-line on Abandonment Reason] |
| 003 | `plans/003-{name}.md` | Done | [Summary] |

**Sibling Todos:**
- `docs/todos/{ID}-{name}/todo.md` — [why separate]

(Or "No sibling todos." if none.)
```

The orchestrator reads this response and writes a summary into the todo's Final Graded Review section.

## Re-Review Behavior

When re-invoked after the orchestrator addresses items, the code-reviewer:
1. Reads the most recent Final Graded Review entry in the todo to see what was flagged
2. Focuses first on those items — did they get addressed?
3. Re-grades all categories (issues may have been introduced while fixing others)
4. Returns a fresh graded response; the orchestrator appends a new dated entry (does not overwrite)

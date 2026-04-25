# Graded Code Review Rubric

The code-reviewer agent grades seven categories. Each category gets A, B, or C. The overall grade is the **worst** category — Grade A requires A across all seven.

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

A category grade reflects only High and Medium findings. Low findings inform but never lower the grade. This stops "to reach A" from becoming a wishlist of unconfirmed nits — the failure mode where every review burns the orchestrator's time chasing low-value suggestions.

## 1. Requirements Coverage

Every numbered business rule assertion in the plan is traced to specific code (file:method:line) and the logic matches the expected behavior.

| Grade | Criteria |
|-------|----------|
| A | Every assertion has a file:method:line citation. Each citation verifies the assertion holds. |
| B | All assertions are traced, but 1-2 traces are weak (point to related code rather than the exact logic), OR one assertion's logic is questionable but functional. |
| C | One or more assertions cannot be traced to specific code, OR the traced code does not actually satisfy the assertion. |

## 2. Test Coverage

Every test scenario in the plan has a corresponding test method that exercises it. No existing (sacred) tests were gutted.

| Grade | Criteria |
|-------|----------|
| A | Every scenario has a test method that exercises the exact inputs and expected result. No existing test assertions removed or weakened. |
| B | Every scenario has a test method, but 1-2 tests are thin (test the happy path only, skip a stated edge case). No existing tests gutted. |
| C | One or more scenarios have no test, OR an existing test was modified in a way that weakens its original intent (removed assertions, changed expected values to match broken behavior, deleted). |

**"Sacred test" rule** (from CLAUDE.md): existing tests must never be gutted to make new code pass. Even one weakened existing test is automatic C in this category.

## 3. Design Alignment

The implementation structure matches the plan's Approach, Design, and Domain Model Behavioral Design sections.

| Grade | Criteria |
|-------|----------|
| A | Implementation follows the plan's approach, file structure, and domain model design. No shortcuts that diverge. |
| B | Implementation follows the plan overall but with minor divergence (e.g., a helper split differently, a property named differently). Divergence is documented in Design Decisions or is obviously harmless. |
| C | Implementation materially diverges from the plan (different approach, missing domain model elements, different aggregate boundary) without a Design Decisions entry justifying the change. |

## 4. Code Quality

Readability, naming, abstraction level, absence of dead code.

| Grade | Criteria |
|-------|----------|
| A | Clear naming, right level of abstraction for the task, no dead code, no speculative generality, no unused parameters or methods. Comments only where the "why" is non-obvious. |
| B | Mostly clean but minor issues: one awkward name, one commented-out block, one method that could be collapsed or split. |
| C | Material issues: unclear naming that requires inspection to understand, dead code left in place, over-engineered abstraction for a simple task, or meaningful duplication that warrants extraction. |

## 5. Framework Correctness

Project-specific framework idioms are respected. The code-reviewer must read the project's CLAUDE.md for the framework rules to check, and the project's calibration doc (if any) for which rules are load-bearing vs. nice-to-have.

This rubric stays framework-agnostic. The list of idioms-to-check comes from the project's CLAUDE.md, not from this file. For project-specific check lists, see `references/rubric-{project}.md` (e.g., `rubric-ztreatment.md` for the zTreatment-specific Neatoo / RemoteFactory / KnockOff / EF UTC list). The reviewer loads the project-specific reference if one exists for the active project.

| Grade | Criteria |
|-------|----------|
| A | All applicable framework idioms (per CLAUDE.md and project-specific rubric reference) followed correctly. |
| B | One minor deviation (e.g., a XML comment missing, a framework attribute omitted on code that works anyway). |
| C | One or more material violations (a CLAUDE.md hard rule broken, a load-bearing framework idiom violated, a known footgun left in place). |

## 6. Build & Test Health

The code-reviewer runs a fresh `dotnet build` and the project's test command. No trusting of reported results.

| Grade | Criteria |
|-------|----------|
| A | Build passes with no new warnings in changed files. All tests pass. |
| B | Build passes, all tests pass, but one or two new warnings in changed files (style, nullability). |
| C | Build fails, OR any test fails (including tests classified as "pre-existing" — the user is the only one who can classify a failure as acceptable), OR significant new warnings in changed files. |

**Any test failure is automatic C.** Report the failure; do not judge whether it is acceptable. That's the user's call.

## 7. Scope Discipline

The implementation respects the plan's **Out of Scope / Invariants** list AND every Companion Plans entry points at a real plan or sibling-todo file. Decomposing into multiple plans is encouraged; what's not allowed is bullet-point notes that scope-cuts will happen "later" without a real plan/todo file backing them.

| Grade | Criteria |
|-------|----------|
| A | Every item on the Out of Scope / Invariants list still holds after the change. **Every Companion Plans entry points at a real plan (`docs/plans/{name}.md`) or sibling-todo (`docs/todos/{name}.md`) file AND that file exists.** No phrases like "future phase," "Phase N+1," "later," "follow-up," "out of phase X," "deferred," "not in this todo" appear anywhere in the plan or implementation summary without a corresponding linked Companion Plans entry. |
| B | One item on the Out of Scope list was incidentally touched but behavior is preserved. All Companion Plans entries link to real files. |
| C | One or more invariants were changed without a Design Decisions entry authorizing it, OR **one or more Companion Plans entries lack a real-file link (or the linked file does not exist)**, OR there are in-line deferral phrases that don't trace back to a linked Companion Plans entry. |

**Companion Plans capture is mandatory** — see project-todos SKILL "Multi-Plan Todos — Decompose Up Front, Don't Defer." A single missing or broken link is automatic C. The reviewer must:

1. Inventory the plan's Companion Plans section. Every entry needs a link to either `docs/plans/{name}.md` (companion plan in this todo) or `docs/todos/{name}.md` (sibling todo).
2. Verify each linked file actually exists on disk. A dead link is the same as a missing one.
3. Sweep the rest of the plan (Approach, Design, Implementation Steps, Phase descriptions, etc.) for deferral phrases. Each hit must trace back to a Companion Plans entry.
4. List every unlinked or broken-linked entry with file location and what it covers, in the "To Reach A" section under Scope Discipline.

Reasoning: the user has been burned by orchestrators marking todos "complete" with bullet-point notes that scope-cuts would happen "later" — that work then evaporates. The fix is to make the act of capturing scope-cuts the same act as creating the plan/todo file for them. A real file is queue-able, schedule-able, and surfaces in the Plan Sequence callout at PR-stage.

If the plan lacks an Out of Scope / Invariants list, the code-reviewer notes this as a planning gap and grades based on apparent intent (not a free pass — a missing list is itself a concern to flag).

---

## Output Format

The code-reviewer returns findings in this structure:

```markdown
## Graded Review — [YYYY-MM-DD]

**Overall Grade: [A / B / C]** (worst category)

| Category | Grade | One-line justification |
|----------|-------|------------------------|
| Requirements Coverage | A | All 8 assertions traced to specific code; verified. |
| Test Coverage | B | 7 of 8 scenarios have tests; scenario 4 (zero-amount validation) missing. |
| Design Alignment | A | Implementation matches plan's domain model design. |
| Code Quality | A | Clean naming; no dead code. |
| Framework Correctness | B | Missing .ToUtcForDb() on one DateTime assignment. |
| Build & Test Health | A | Build clean, all 247 tests pass. |
| Scope Discipline | A | Out-of-scope list preserved. |

### To Reach A

**Test Coverage:**
- Add test `Payment_ZeroAmount_ValidationFails` in `PaymentEditTests.cs`. Scenario 4 requires zero-amount path be tested; currently only positive and negative amounts are covered.

**Framework Correctness:**
- `PaymentEdit.cs:87` — `entity.Date = this.Date` needs `.ToUtcForDb()` per CLAUDE.md DateTime rules.

### Build & Test Evidence

- Build: PASSED (0 errors, 0 new warnings in changed files)
- Tests: 247 passed, 0 failed (command: `dotnet test -m:1`)

## Plan Sequence

| # | Type | File | Exists? | Description |
|---|------|------|---------|-------------|
| 1 | Plan (this todo) | `docs/plans/visit-domain-refactor.md` | ✅ | Domain refactor — this plan, just completed |
| 2 | Plan (this todo) | `docs/plans/visit-ui-rebind.md` | ✅ | UI rebinding — Draft, queued for next session |
| 3 | Sibling todo | `docs/todos/visit-legacy-shim.md` | ✅ | Legacy compatibility shim — its own goal, separate todo |

(Or "Single-plan todo, no companion plans or sibling todos — fully self-contained." if there are no Companion Plans entries.)
```

**The Plan Sequence section is mandatory at the end of every graded review**, even when there's only one plan and the todo is closing out cleanly. It is the artifact the orchestrator copies into the PR description at Step 6 so the user sees what's done, what's queued, and what spawned off. The reviewer's job is to verify every linked file actually exists on disk — a Companion Plans entry pointing at a non-existent file is the same as a silent drop, and grades C in this category.

The orchestrator reads this response and writes a summary into the todo's Graded Review section.

## Re-Review Behavior

When re-invoked after the orchestrator addresses items, the code-reviewer:
1. Reads the most recent Graded Review entry in the todo to see what was flagged
2. Focuses first on those items — did they get addressed?
3. Re-grades all categories (issues may have been introduced while fixing others)
4. Returns a fresh graded response; the orchestrator appends a new dated entry (does not overwrite)

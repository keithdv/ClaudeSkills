# [Title of Work]

**ID:** XYZ ([3–5 uppercase letters; assigned at Step 1; unique across all todos active and completed; never reused. Plans referenced as `XYZ-NNN`. See project's `docs/todos/CONVENTIONS.md` if one exists.])
**Type:** Enhancement | Bug | Bug-Exposes-Fallacy
**Status:** In Progress | Complete | Blocked
**Priority:** High | Medium | Low
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

---

## Goal

[One paragraph. What success looks like in plain language. Inherits across every plan in this todo — plans do not duplicate this. The Goal is durable: most discoveries don't touch it. Goal shifts are rare and require explicit user agreement; when they do happen, update this section and note the change in the same Discovery Log entry that triggered it.]

## Acceptance Criteria

[Observable, testable. This is the exit gate — `iterative-todo` only completes when every criterion below is checked. Plans come and go; these criteria define done.]

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Out of Scope

[What this todo will not touch. Plans inherit this — a plan that touches anything here triggers the discovery protocol.]

- [Specific behavior, integration, or area]

---

## Plan Index

[Monotonic numbering. Abandoned plans keep their number. Pre-populated at Step 1 with the **initial plan split** (the directional guestimate of how the goal decomposes — typically 2–6 entries, each backed by a stub plan file with only Scope filled). Index evolves as plans are drafted, completed, abandoned, or re-split. Status: `Draft` / `In Progress` / `Done` / `Abandoned`.]

| # | File | Title | Status |
|---|------|-------|--------|
| 001 | [001-{name}](./plans/001-{name}.md) | [short title] | Done |
| 002 | [002-{name}](./plans/002-{name}.md) | [short title] | Abandoned |
| 003 | [003-{name}](./plans/003-{name}.md) | [short title] | In Progress |

---

## Discovery Log

[Append-only. One entry per discovery during implementation. Terse, navigational — long-form context lives on the affected plan (Plan Amendments or Abandonment Reason).

Decision values: `Amend` / `Abandon` / `Defer` / `Re-split`. Re-split is used when the discovery is significant enough to change the Plan Index itself (reorder queued plans, drop ones that no longer apply, add new ones, or shift the goal). For Re-split, list the index changes inline.]

### YYYY-MM-DD — Plan 003
- **Finding:** [one sentence]
- **Decision:** Re-split
- **Index changes:** Plan 004 dropped (no longer needed). Plan 005 added (Scope: ...). Plan 003 continues as scoped.
- **Follow-up:** Plan 005

### YYYY-MM-DD — Plan 002
- **Finding:** [one sentence]
- **Decision:** Abandon
- **Follow-up:** Plan 003

### YYYY-MM-DD — Plan 001
- **Finding:** [one sentence]
- **Decision:** Amend
- **Follow-up:** n/a

---

## Skipped Steps

[Workflow steps explicitly skipped. Each entry: step name + reason. Empty if no steps skipped.]

- [e.g., Plan 002 — Plan Review skipped (single-file change, obvious blast radius)]

---

## Sibling Todos

[Capture-or-lose mechanism. Work that surfaced during this todo but does NOT advance this todo's Goal — yet is worth keeping rather than dropping. Rare; most discoveries get handled as Amend / Abandon / Defer / Re-split inside this todo. Empty if none.]

- [ ] [Sibling Todo Title](../{sibling-name}/todo.md) — [one line: why this surfaced here, why it isn't part of this Goal]

---

## Final Graded Review

[Filled in at Step 7, when last in-flight plan goes Done and Plan Index has no queued plans, AND the user has confirmed Acceptance Criteria are met. Re-runs append; do not overwrite.]

### YYYY-MM-DD — Grade [A | B | C]

| Category | Grade | Justification |
|----------|-------|---------------|
| Requirements Coverage | A | [1-line] |
| Test Coverage | A | [1-line] |
| Design Alignment | A | [1-line] |
| Code Quality | A | [1-line] |
| Framework Correctness | A | [1-line] |
| Build & Test Health | A | [1-line] |
| Scope Discipline | A | [1-line] |

**To reach A:** [Suggestions if not already A; "N/A" if already A]

**User acknowledgment:** [Date — "Accepted" or "Addressing [specific items]"]

**Full review:** [`reviews/final-graded-review.md`](./reviews/final-graded-review.md)

---

## Documentation Review

[Filled in at Step 8.]

**Completed:** YYYY-MM-DD
**Files updated:**
- [file path] — [what changed]

**Developer deliverables** (source-code touch-ups requested by documenter):
- [file path] — [what changed, by orchestrator]

**Full review:** [`reviews/documenter-review.md`](./reviews/documenter-review.md)

---

## Results / Conclusions

[Filled in at Step 9. Summary of what was learned across plans and key decisions captured in Discovery Log. The skill does not create commits or PRs — packaging the work into commits or PRs is the user's call.]

### Plan Sequence

```
Plans for this todo (`docs/todos/completed/{todo-name}/todo.md`):
- [x] 001-{name} — Done
- [x] 002-{name} — Abandoned (see Abandonment Reason)
- [x] 003-{name} — Done

Discovery Log: {N} entries across implementation.
Final Graded Review: Grade {A/B/C} (acknowledged).
Documentation: {N} rules added/changed.
```

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

[Monotonic numbering. Abandoned and Retired plans keep their numbers. Pre-populated at Step 1 with the **initial plan split** — 2–6 stubs for contained todos, 6–12 for large restructures; growing 1.5–2× over the todo's life through this index is the system working. Status: `Draft` / `In Progress` / `Done` / `Abandoned` / `Retired`. Keep Status cells terse — a status word plus at most a few words; narrative lives in the plan or the Discovery Log, review verdicts live in `reviews/`.]

| # | File | Title | Status |
|---|------|-------|--------|
| 001 | [001-{name}](./plans/001-{name}.md) | [short title] | Done |
| 002 | [002-{name}](./plans/002-{name}.md) | [short title] | Abandoned |
| 003 | [003-{name}](./plans/003-{name}.md) | [short title] | In Progress |
| 004 | [004-{name}](./plans/004-{name}.md) | [short title] | Retired (folded into 003) |

---

## Discovery Log

[Append-only. One entry per discovery during implementation. Terse, navigational — **budget ~100 words per entry**; long-form context lives on the affected plan (Plan Amendments or Abandonment Reason) and the entry points at it. Cite plans in `{ID}-{NNN}` form so entries stay greppable after the todo moves.

**Review output never goes here** — test-review and code-review findings live in `reviews/{NNN}-*.md`; an entry may summarize a review's outcome in one line and link the file. PR descriptions and file-change enumerations don't belong here either.

Decision values: `Amend` / `Abandon` / `Defer` / `Re-split`. Use the fields — when the taxonomy is skipped, decisions stop being greppable. Re-split changes the Plan Index itself (reorder, drop/`Retired`, add); list the index changes inline.]

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

## Close-Out Audit

[Filled in at Step 7, when the last plan closes and the Plan Index has no queued work, AND the user has confirmed Acceptance Criteria are met. Findings-only — no grades. Re-runs append; do not overwrite.]

### YYYY-MM-DD — Verdict: [CLEAN | CONCERNS]

**Veto-tier findings:** [resolved items with one line each, or "None"]
**Callouts:** [each with disposition — queued as {ID}-{NNN} / accepted with reason / fixed inline]
**Deferred work carrying forward:** [one line per item, or "None — fully self-contained"]

**User acknowledgment:** [Date — "Accepted" or "Addressing [specific items]"]

**Full audit:** [`reviews/close-out-audit.md`](./reviews/close-out-audit.md)

---

## Docs & Retro

[Filled in at Step 8 — Completion.]

**Documentation:** [Confirmation that doc deltas shipped in the same PRs as the behavior they describe, per project rules. Internal-contradiction callouts reconciled: list each with the resolution. Remaining doc debt queued as: {ID}-{NNN} / sibling todo / "none".]

**Retro (one paragraph):** [What this todo taught about the *workflow itself* — a gate that misfired, a mechanic that got skipped, a convention that decayed. Route lessons to where they'll act: project CLAUDE.md, the iterative-todo skill backlog, or persistent memory. "Nothing notable" is a valid retro.]

---

## Results / Conclusions

[Filled in at Step 8. Summary of what was learned across plans and key decisions captured in Discovery Log. The skill does not create commits or PRs — packaging the work into commits or PRs is the user's call.]

### Plan Sequence

```
Plans for this todo (`docs/todos/completed/{todo-name}/todo.md`):
- [x] 001-{name} — Done
- [x] 002-{name} — Abandoned (see Abandonment Reason)
- [x] 003-{name} — Done
- [x] 004-{name} — Retired (folded into 003)

Discovery Log: {N} entries across implementation.
Close-Out Audit: {CLEAN | CONCERNS → resolved} (acknowledged).
Documentation: {N} rules added/changed, shipped in-PR.
```

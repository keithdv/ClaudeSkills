# [Title of Work]

**Type:** Enhancement | Bug | Bug-Exposes-Fallacy
**Status:** In Progress | Complete | Blocked
**Priority:** High | Medium | Low
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

---

## Problem

[What problem are we solving?]

## Solution

[High-level approach]

---

## Skipped Steps

[Steps explicitly skipped from the project-todos workflow. Each entry has the step and the reason. Empty if no steps skipped.]

- [e.g., Step 5 (Documentation) — internal refactor, no business rule changes]

---

## Plans

[A todo can have multiple plans. List every plan, with current status. The todo only reaches `Complete` when every plan reaches `Complete` or `Won't Do`. See "Multi-Plan Todos — Decompose Up Front, Don't Defer" in the project-todos SKILL for when to split into multiple plans vs. a sibling todo.]

- [ ] [Plan 1 Title](../plans/{plan-1-filename}.md) — `Draft` / `Approved` / `In Progress` / `Awaiting Review` / `Reviewed` / `Documented` / `Complete` / `Won't Do`
- [ ] [Plan 2 Title](../plans/{plan-2-filename}.md) — `Draft` (stub — full design at next session)

## Sibling Todos

[Todos created from work discovered during this todo's planning or implementation, where the work belongs to its own goal rather than another plan in this todo. Empty if none.]

- [ ] [Sibling Todo Title](./{sibling-todo-filename}.md)

---

## Plan Review

[Filled in during Step 2 (one agent invocation, two passes). If re-run, append new dated entries. Omit this section entirely if the step was skipped — record the skip under Skipped Steps.]

### YYYY-MM-DD — [APPROVED | CONCERNS | REJECTED]
**Summary:** [One-paragraph summary of overall findings]

**Pass A — vs. documented requirements:**
- Requirement docs consulted: [paths or "none — no documented requirements"]
- Contradictions: [list or "None"]
- Implicit dependencies missed: [list or "None"]
- Coverage gaps: [list or "None"]
- Rules marked NEW: [list or "None"]

**Pass B — vs. codebase:**
- Files examined: [count and brief scope — e.g., "12 files across Treatment, Visit, VisitHub.razor"]
- Gaps: [list or "None"]
- Domain logic placement: [concerns or "Clean"]
- Framework-correctness risks: [list or "None"]
- Invariant / scope violations: [list or "None"]

**Resolution:** [What changed in the plan, or "User accepted as-is with explicit sign-off"]

---

## Graded Review

[Filled in during Step 4. Each re-run appends a new dated entry — do not overwrite.]

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

---

## Documentation

[Filled in during Step 5. Skip this section if documentation was skipped.]

**Completed:** YYYY-MM-DD
**Files updated:**
- [file path] — [what changed]

**Developer deliverables** (source code changes requested by documenter):
- [file path] — [what changed, by orchestrator]

---

## Progress Log

### YYYY-MM-DD
- [What happened]

---

## Results / Conclusions

[What was learned? What decisions were made? Filled in at Step 6 completion.]

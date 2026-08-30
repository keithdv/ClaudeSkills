# [Plan Title — ≤ 8 words]

**Plan #:** {NNN}
**Date:** YYYY-MM-DD
**Related Todo:** [../todo.md](../todo.md)
**Serves:** AC-n[, AC-m] — every plan names the Acceptance Criteria it advances; a plan that serves none is not this todo's work
**Status:** Draft
**Last Updated:** YYYY-MM-DD
**Plan-review opt-in:** [Yes/No (one-line reason — cross-aggregate, schema, public API, security, irreversible; name `business-requirements-reviewer` when documented rules are touched)]
**Code-review opt-in:** [Yes/No (one-line reason — behavior-changing plans; skip for mechanical work)]
**Branch:** {id}-{NNN}-{short-name} — cut from the arc at Step 2
**PR:** — [#n once opened at Done, into the arc, titled `{ID}-{NNN}: <title>`; the user merges]

<!-- Status: Draft | In Progress | Done | Abandoned | Retired. A status is a word plus at most five words; there is no "gates run, findings addressed" state. -->

---

## A note on what this template wants

A plan is a **prescription** — what needs to be true and why, at the intent level. Not what the code looks like. Line numbers, signatures, file-by-file edit lists, code fences over two lines, and fallback branches belong in **Current State** (reality, recorded at pre-flight) or **Plan Amendments** (keyboard decisions) — never in Scope, Intent, or Steps.

A plan is a **working hypothesis**. It does not lock at implementation. Surprises become Amendments (details change), an Abandonment Reason (wrong path), or — most often — a Punchlist row or a Dismiss on the todo.

**Budget: ≤ 200 lines when this plan enters implementation.** Scope one paragraph; Steps ≤ 10; Acceptance ≤ 8. If the plan does not fit, it is two plans. If a section is defending why the plan exists, the plan should not exist.

---

## Scope

[One paragraph. What this plan does and what it explicitly does NOT do. Do not restate the todo's Goal, Criteria, or Out of Scope.]

---

## Intent

[Why this plan exists — the business outcome or behavior change a user would observe after it lands. 3–5 bullets or one short paragraph. Not "what the code looks like."]

---

## Framework & Architectural Alignment

[Which patterns and rules this plan follows — named, not reproduced. Reviewers check this against the framework skills.]

---

## Constraints & Invariants

[What must remain true after this plan lands. Bullets: business invariants, system invariants, boundary constraints, tests that stay green.]

---

## Steps

[≤ 10 intent-bearing bullets — what changes and why, not how. A step containing a type name with a line number, a signature, a parameter list, or an "if A fails, B" branch is too detailed; compress it. Name the seam, not the line.

Good: *Move Trigger A's regenerate-and-clear logic onto the aggregate as a domain verb so the handler reduces to the standard lifecycle.*
Bad: *Add `Task RegenerateRecommended()` to `ITreatmentV2`; in `StandardTreatmentV2:113` delete `GenerateForVisit`; constructor takes …*]

1. 
2. 
3. 

---

## Acceptance

[≤ 8 observable, behavioral bullets — verifiable by exercising the system or running tests, not by diffing. **Every behavioral bullet ends with one tier tag**; a bare bullet is a draft-time error.

- `[unit]` — pure logic, no DI/DB/I/O.
- `[integration]` — full RemoteFactory client/server round-trip with stubbed repositories; real Save, real rules.
- `[database]` — real DB; what gets persisted or stays unwritten.
- `[ui]` — Blazor / browser interaction.
- `[explicit-skip: <reason>]` — non-test bullets (build green, doc updated). Reason mandatory.

Tag what the signal *needs*, not what is cheapest. Do not name test methods here — that is Test Evidence, filled after implementation.]

- [ ] [behavior] `[tier]`
- [ ] [behavior] `[tier]`
- [ ] Build/test green `[explicit-skip: meta-bullet]`

---

## Current State (Pre-Flight)

[**Filled at Step 3, before the first edit.** The sanctioned home for code-level detail: line numbers, signatures, "the handler currently does X at `Foo.cs:142`", existing verb shapes. A record of reality, not a prescription. Surprises that shift the plan become Amendments before the first edit. Minutes of walking, not a codebase re-review.]

- 

---

## Punchlist

[Plan-scoped small items discovered during this plan — **one line each**: what · where · done-when. Worked inline (plan mode if it needs thought); no gate, no log entry. Cross-plan items go on the todo's Punchlist instead. Anything still open when this plan goes Done moves to the todo's Punchlist or is dismissed.]

- [ ] <what> · <where> · done when <observable>
- [x] <what> · <where> · <commit>

---

## Test Evidence

[**Filled after implementation, before invoking `test-reviewer`.** One row per Acceptance bullet: the test that pins it, at the declared tier — or `MISSING — <reason>`. The gate is not invoked until this exists. A tier mismatch is a MISSING. Shipping with MISSING rows requires the user's recorded acceptance.]

| Acceptance bullet (short) | Tier declared | Test method | Tier confirmed |
|---|---|---|---|
| | `[unit]` | `Project.Tests.Class.Method` | ✓ |
| | `[integration]` | MISSING — accepted, see Gate Record | ✗ |

---

## Gate Record

[Filled at Step 5 close. **Two rounds maximum.** One line per round; leftovers are punched or accepted here, not carried as a status.]

- Round 1 (YYYY-MM-DD): [CLEAN | CONCERNS — n must-cover addressed, n should-cover punched, n tech-debt dismissed] — `reviews/{NNN}-test-review.md`
- Round 2 (YYYY-MM-DD): [CLEAN | leftovers accepted: <one line each with reason>] — Done

---

## Plan Amendments

[Append-only; one entry per **Amend** decision. Original Scope/Intent/Steps stay frozen.]

### YYYY-MM-DD — [Short title]

- **Section affected:** 
- **Original said:** 
- **What changed:** 
- **Why:** 
- **Discovery Log:** [date / {ID}-{NNN}]

---

## Abandonment / Retirement Reason

<!-- Only when Status is Abandoned or Retired. -->

[**Abandoned** (one paragraph): what we believed at draft, what turned out true, what the next plan should do differently.
**Retired** (one line): where the work went — folded into {ID}-{NNN}, superseded by re-split, carved out to sibling {ID}.]

---

## Notes

[Optional. Skills loaded, open questions for the user. Not design, not justification.]

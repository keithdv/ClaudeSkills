# [Plan Title]

**Plan #:** {NNN}
**Date:** YYYY-MM-DD
**Related Todo:** [Link to ../todo.md]
**Status:** Draft
**Last Updated:** YYYY-MM-DD
**Plan-review opt-in:** [Yes/No (one-line reason — e.g., "Yes (production data migration)" or "No (mechanical refactor, narrow blast radius)")]
**Code-review opt-in:** [Yes/No (one-line reason — opt in for behavior-changing plans; skip for mechanical ports, renames, doc-only)]

<!-- Valid status values: Draft | In Progress | Done | Abandoned | Retired -->

---

## A note on what this template wants

A plan is a **prescription** — it describes **what** needs to be true and **why**, at the intent level. The plan is **not** the implementation; it does **not** describe what the code looks like. Specific identifiers, line numbers, exact method signatures, file-by-file edit lists, code fences longer than two lines, and fallback branches all belong elsewhere: **code-level reality observed before implementation goes in the Current State section (filled at pre-flight, Step 3); code-level decisions made while editing go in Plan Amendments.** Scope, Intent, and Steps stay at the intent level.

The plan is a **working hypothesis**, not a contract. It does not lock when implementation begins. Discoveries during implementation become Plan Amendments (small shifts), an Abandonment Reason (wrong path), or trigger a re-split of the parent todo's Plan Index (significant). Restructuring opportunities can be **named** in a step ("this seam will probably need to move onto the aggregate") but not **designed** — the implementer finds the right shape while editing.

If a step is reading like code, compress it back to intent.

---

## Scope

[One paragraph. What this plan does, and what it explicitly does NOT do. Inherit Goal / Acceptance / Out of Scope from the parent todo — do NOT restate them here. If the work doesn't fit in one paragraph, the plan is too big — split it.]

---

## Intent

[Why this plan exists. The business outcome or behavioral change a user/reviewer would observe after this plan lands. One short paragraph or 3–5 bullets. Not "what the code looks like."]

---

## Framework & Architectural Alignment

[Which framework patterns and architectural rules this plan follows. Examples: "standard Neatoo three-phase lifecycle," "static `[Execute]` factory for polymorphic dispatch," "no repositories on aggregate constructors," "transaction participates in caller's ambient `IRepositoryTransaction`," "V1 ↔ V2 imports stay symmetric-forbidden."

Name the pattern; do not reproduce it. Reviewers check this section against the framework skills, not against the plan's own restated mechanics.]

---

## Constraints & Invariants

[What must remain true after this plan lands. Bullets.

- Business invariants — "EXECUTED rows untouched on Trigger A"
- System invariants — "allowlist count not regressed"
- Boundary constraints — "no V1 imports added in V2 sources"
- Test-coverage invariants — "the existing X test stays green"

Reviewers check the plan's intent against this list; the implementer checks their work against it.]

---

## Steps

[High-level, intent-bearing bullets — not a code edit list. Each step names *what changes* and *why*, not *exactly how*. Cap at ~10. If you need more, split into a follow-up plan and queue it in the Plan Index.

**A good step:**
*Move Trigger A's regenerate-and-clear logic onto the aggregate as a domain verb so the handler reduces to the standard Neatoo lifecycle.*

**A bad step (too detailed — implementation, not design):**
*Add `Task RegenerateRecommended()` to `ITreatmentV2`. In `StandardTreatmentV2:113` delete `GenerateForVisit`. Constructor takes `ISignsLookBackServiceV2`, `ITreatmentGenerationServiceV2`, …*

If a step contains a fully-qualified type name with a colon and a line number, an exact method signature, a parameter list, a method body, or a "fall back to B if A doesn't compile" branch — compress it. Those discoveries belong to the keyboard. The plan can name the seam ("the `[Update]` paths on both Standard and WD") without naming the line.]

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Acceptance

[What "this plan is done" looks like. Specific, observable, **behavioral** — verifiable by exercising the system or running tests, not by diffing.

Not the same as the todo's Acceptance Criteria — that's the exit gate for the whole todo. This is the exit gate for this plan only.

**Good acceptance bullet:** *"On first signs save for a new patient, a treatment row exists with RECOMMENDED populated and APPROVED empty. `[database]`"*
**Bad acceptance bullet:** *"`StandardTreatmentV2:271` is deleted."* (That's a code-shape assertion, not a behavior.)

### Tier tags — REQUIRED

Every behavioral acceptance bullet ends with **one** tier tag declaring the test tier that should pin it:

- `[unit]` — pure-logic assertion, no DI, no DB, no I/O. Resolver branches, computed properties, rule fires/doesn't-fire.
- `[integration]` — full RemoteFactory client/server round-trip with stubbed repositories; real factory `Save`, real validation rules. Use this when the signal involves *Save / serialization / cross-tier flow* but doesn't require real persistence.
- `[database]` — real DB. Use this when the signal involves *what gets persisted* (or what stays unwritten), schema invariants, transaction boundaries.
- `[ui]` — Blazor / browser interaction (where applicable to the project).
- `[explicit-skip: <one-line reason>]` — for non-test bullets like "build green", "allowlist not regressed", or "doc updated". The reason is mandatory.

Bare bullets — no tag — are a draft-time validation error. The plan is not ready for implementation until every behavioral bullet is tagged.

**The tag is a decision, not a wish.** Tag what the bullet's signal *needs*, not what's cheapest to write. A bullet that asserts "Plan.Protocol stays null after the load path runs" is `[database]` because nothing else proves persistence (or its absence). A bullet that asserts "the resolver returns the inherited value" is `[unit]` because logic is the whole signal.]

- [ ] [Observable behavior — what changes, verifiable by exercising the system] `[tier]`
- [ ] [Behavioral signal — e.g., "the X workflow produces Y end-to-end"] `[tier]`
- [ ] [System gate — e.g., "`scripts/check-v2-no-v1-deps.sh` exits 0; allowlist not regressed"] `[explicit-skip: build/script gate, not a behavior test]`
- [ ] Build/test green `[explicit-skip: meta-bullet, satisfied by Step 4 verification]`

**Note on test enumeration:** Acceptance bullets are the test surface and the tier tag declares where each signal gets pinned. Do **not** enumerate specific test files or test method names in this section — that's the Test Evidence section below, filled in *after* implementation. The tag answers *which tier*; Test Evidence answers *which test method, written by the keyboard*. Splitting these prevents the "the plan said integration, I forgot" failure mode without going back to over-prescribed plan-time test lists.

---

## Current State (Pre-Flight)

[**Filled at Step 3, after draft and before the first edit.** The orchestrator walks the plan's Intent and Steps against the actual code at the seams this plan touches — no edits yet — and records what's actually there.

This is the **sanctioned home for code-level detail**: line numbers, signatures, "the handler currently does X at `Foo.cs:142`," existing verb shapes, current test placement. It's allowed here because this section is a *record of reality*, not a prescription — keeping it here is what keeps Scope/Steps at intent level.

Discoveries that shift the plan become Plan Amendments **before the first edit**. A stub that turns out stale (drafted against code that has since moved) gets reshaped here instead of mid-implementation. Keep it proportionate — minutes of walking for a contained plan, not a codebase re-review.]

- [Seam: what's actually there today, with file/line citations as needed]
- [Existing pattern the implementation should match (e.g., the codebase's established fetch-or-create verb shape)]
- [Surprises → Plan Amendment references]

---

## Test Evidence

[**Filled in after implementation, before invoking `test-reviewer` (Step 5 per-plan gate).** Maps every Acceptance bullet to the test method that pins it, at the tier the bullet declared. The orchestrator does NOT invoke the gate until this section exists.

This is the artifact that makes "did I write the prescribed tests" a checkable fact instead of a vibes call. It is short — one row per Acceptance bullet — and lives in the plan body so reviewers can grep against it.

If a bullet has no test, the row is `MISSING — <one-line reason>`. Shipping with `MISSING` rows requires explicit user acknowledgement and ideally a queued follow-up plan. Silent omission is the failure mode the section eliminates.

Tier *mismatch* (bullet declared `[integration]`, test cited is unit-only) is also a `MISSING` — the right test of the right tier did not get written.]

| Acceptance bullet (short) | Tier declared | Test method | Tier confirmed |
|---|---|---|---|
| [first 6–10 words of the bullet] | `[unit]` | `ProjectName.Tests.SomeClass.SomeMethod` | ✓ |
| [...] | `[database]` | `ProjectName.DatabaseTests.X.Y` | ✓ |
| [...] | `[integration]` | MISSING — covered by Plan {NNN+1} follow-up | ✗ |

---

## Plan Amendments

[Append-only. Used when a discovery during implementation led to **Amend** (one of the four discovery-protocol options).

The plan is a working hypothesis; the Amendments section is how it stays accurate without rewriting Scope/Intent/Steps. Original Scope/Intent/Steps stay frozen — each amendment records what changed and why. The plan continues toward `Done`.

Empty if no amendments. Multiple amendments stack newest-first or oldest-first, your call — be consistent within the file.]

### YYYY-MM-DD — [Short title]

- **Section affected:** [e.g., "Step 3", "Constraints"]
- **Original said:** [one-line summary]
- **What changed:** [what the implementation actually does instead]
- **Why:** [the discovery that surfaced]
- **Discovery Log link:** [date/plan-ID of the matching todo Discovery Log entry]

---

## Abandonment / Retirement Reason

<!-- ONLY filled in if Status: Abandoned or Retired. Remove or leave empty otherwise. -->

[**Abandoned** (one paragraph, required): capture what we believed when this plan was drafted, what turned out to be true (the discovery that abandoned it), and what the next plan should do differently. This is what makes abandonment cheap — the next plan inherits the lesson instead of re-discovering it. The abandoned plan stays in the Plan Index with its number; never delete it.

**Retired** (one line, required): where the work went — folded into {ID}-{NNN}, superseded by a re-split, or carved out to sibling todo {ID}. Retirement means the plan stopped being needed without failing; the Index row stays as a tombstone.]

---

## Notes

[Optional — anything orchestrator wants to remember during the plan that doesn't fit the structured sections above. Skills loaded, files of interest, partial findings, open questions worth flagging to the user. NOT a place for design — design lives in Intent / Framework Alignment / Constraints / Steps.]

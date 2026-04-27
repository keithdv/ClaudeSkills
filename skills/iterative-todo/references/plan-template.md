# [Plan Title]

**Plan #:** {NNN}
**Date:** YYYY-MM-DD
**Related Todo:** [Link to ../todo.md]
**Status:** Draft
**Last Updated:** YYYY-MM-DD

<!-- Valid status values: Draft | In Progress | Done | Abandoned -->

---

## A note on what this template wants

A plan is a **prescription** — it describes **what** needs to be true and **why**, at the intent level. The plan is **not** the implementation; it does **not** describe what the code looks like. Specific identifiers, line numbers, exact method signatures, file-by-file edit lists, code fences longer than two lines, fallback branches, and pre-flight code reconnaissance all belong at the keyboard, not in the plan body.

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

**Good acceptance bullet:** *"On first signs save for a new patient, a treatment row exists with RECOMMENDED populated and APPROVED empty."*
**Bad acceptance bullet:** *"`StandardTreatmentV2:271` is deleted."* (That's a code-shape assertion, not a behavior.)]

- [ ] [Observable behavior — what changes, verifiable by exercising the system]
- [ ] [Behavioral signal — e.g., "the X workflow produces Y end-to-end" — naming the *behavior*, not the test that asserts it]
- [ ] [System gate — e.g., "`scripts/check-v2-no-v1-deps.sh` exits 0; allowlist not regressed"]
- [ ] [Build/test green]

**Note on tests:** Acceptance bullets are the test surface — they name behaviors that should be pinned by tests after implementation. Do **not** enumerate specific test files, test methods, or test tiers in this section. That's the post-implementation `test-reviewer` loop's job (iterative-todo Step 5b), against actual code. Naming a *behavior* an existing test exercises ("workflow X completes successfully") is fine; prescribing *new* tests by name is the failure mode being eliminated.

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

## Abandonment Reason

<!-- ONLY filled in if Status: Abandoned. Remove or leave empty otherwise. -->

[One paragraph. Required when the plan is abandoned. Capture:
- What we believed when this plan was drafted
- What turned out to be true (the discovery that abandoned this plan)
- What the next plan should do differently

This is what makes abandonment cheap — the next plan inherits the lesson instead of re-discovering it. The abandoned plan stays in the Plan Index with its number; never delete it.]

---

## Notes

[Optional — anything orchestrator wants to remember during the plan that doesn't fit the structured sections above. Skills loaded, files of interest, partial findings, open questions worth flagging to the user. NOT a place for design — design lives in Intent / Framework Alignment / Constraints / Steps.]

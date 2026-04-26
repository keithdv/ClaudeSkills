# [Plan Title]

**Plan #:** {NNN}
**Date:** YYYY-MM-DD
**Related Todo:** [Link to ../todo.md]
**Status:** Draft
**Last Updated:** YYYY-MM-DD

<!-- Valid status values:
Draft | In Progress | Done | Abandoned
-->

---

## Scope

[One paragraph. What this plan does, and what it explicitly does NOT do. Inherit Goal / Acceptance / Out of Scope from the parent todo — do NOT restate them here. If the work doesn't fit in one paragraph of scope, the plan is too big — split it.]

---

## Steps

[Ordered, concrete edits. Cap at ~10. If you need more, split into a follow-up plan and queue it in the Plan Index.]

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Acceptance

[What "this plan is done" looks like. Specific, observable. Not the same as the todo's Acceptance Criteria — that's the exit gate for the whole todo. This is the exit gate for this plan only.]

- [ ] [Build/test passes]
- [ ] [Specific behavior verifiable]
- [ ] [Specific code in place]

---

## Plan Amendments

[Append-only. Used when a discovery during implementation led to **Amend** (one of the three discovery-protocol options).

Original Scope and Steps stay frozen. Each amendment records what changed and why. The plan continues toward `Done`.

Empty if no amendments.]

### YYYY-MM-DD — [Short title]

- **Section affected:** [e.g., "Step 3", "Scope"]
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

This is what makes abandonment cheap — the next plan inherits the lesson instead of re-discovering it.]

---

## Notes

[Optional — anything orchestrator wants to remember during the plan that doesn't fit the structured sections above. Skills loaded, files of interest, partial findings. NOT a place for design — design lives in Scope and Steps.]

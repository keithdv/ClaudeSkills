# [Title of Work]

**ID:** XYZ (3–5 uppercase letters; assigned at Step 1; unique across active and completed todos; never reused. Plans referenced as `XYZ-NNN`.)
**Type:** Enhancement | Bug | Bug-Exposes-Fallacy
**Status:** In Progress | Complete | Blocked
**Priority:** High | Medium | Low
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Initial split:** N plans
**Plan cap:** max(ceil(N × 1.5), N + 2) — counts plan numbers *issued*, including Abandoned and Retired. Issuing a number above the cap is a stop-and-ask: close on what is done, or raise the cap with a one-line Discovery Log reason.

---

## Goal

[One paragraph, ≤ 150 words. What success looks like in plain language. Durable — Goal shifts are rare and require explicit user agreement; when one happens, update this section and the Acceptance Criteria together and note it in the triggering Discovery Log entry.]

## Acceptance Criteria

[Observable, testable, **one sentence each, no parentheticals**. Numbered so plans and discoveries cite `AC-n`. This is the exit gate: when every criterion is checked or explicitly accepted as a gap, the todo goes to close-out regardless of what is queued. A criterion that needs a paragraph is being renegotiated — renegotiate it in one Discovery Log entry and rewrite the sentence.]

- [ ] **AC-1** — 
- [ ] **AC-2** — 
- [ ] **AC-3** — 

## Out of Scope

[What this todo will not touch. A plan or discovery that lands here is a Dismiss, or (rarely) a sibling todo.]

- 

---

## Plan Index

[Monotonic numbering; Abandoned and Retired plans keep their numbers. Pre-populated at Step 1 with the initial split — 2–6 stubs for contained todos, 6–12 for large restructures. Every row names the criteria it serves. **Status cell = status word + at most five words.** Narrative lives in the plan; review output lives in `reviews/`. There is no "gates run, findings addressed" state — after two gate rounds a plan is Done.]

| # | File | Title (≤ 8 words) | Serves | Status |
|---|------|-------|--------|--------|
| 001 | [001-{name}](./plans/001-{name}.md) | [title] | AC-1 | Done |
| 002 | [002-{name}](./plans/002-{name}.md) | [title] | AC-2 | Abandoned |
| 003 | [003-{name}](./plans/003-{name}.md) | [title] | AC-1, AC-3 | In Progress |
| 004 | [004-{name}](./plans/004-{name}.md) | [title] | AC-2 | Retired — folded into 003 |

---

## Punchlist

[Cross-plan items only — plan-scoped items live in the plan. **One line each**: what · where · done-when. Worked inline, plan mode (`Shift+Tab`) if it needs a moment's design; no gate, no review, no log entry. Work inherited from a prior arc is seeded here at Step 1, one line per item. Close with `[x]` and a commit or PR.]

- [ ] <what> · <where> · done when <observable>
- [x] <what> · <where> · <commit or PR>

## Dismissed

[Findings looked at and not acted on — failed the criterion test, the reachability test, or simply not worth it. **One line each**, so the next reviewer does not re-raise them; this section is named in every Review Brief as a source of record. No log entry.]

- {ID}-{NNN} · <finding, ≤ 15 words> · <reason, ≤ 15 words>

---

## Discovery Log

[Append-only. **≤ 60 words per entry.** Only decisions that change files get entries: `Amend` / `Queue` / `Abandon` / `Re-split`. Dismissed and punched findings have their own one-line sections above. No "Note" entries — an entry with no decision is a journal. Review output lives in `reviews/`; an entry may link a review in one line. Cite plans as `{ID}-{NNN}`.]

### YYYY-MM-DD — {ID}-003 · serves AC-1
- **Finding:** [one sentence]
- **Decision:** Re-split
- **Index changes:** 004 Retired (folded into 003). 005 added (Scope: …). Cap: 5 of 6 issued.
- **Follow-up:** {ID}-005

### YYYY-MM-DD — {ID}-002 · serves AC-2
- **Finding:** [one sentence]
- **Decision:** Abandon
- **Follow-up:** {ID}-003

### YYYY-MM-DD — {ID}-001 · serves AC-1
- **Finding:** [one sentence]
- **Decision:** Amend
- **Follow-up:** n/a

---

## Skipped Steps

[Workflow steps explicitly skipped: step name + one-line reason.]

- 

---

## Sibling Todos

[Work that surfaced here, serves none of this todo's criteria, and is worth keeping. Rare. One line each with a link.]

- 

---

## Close-Out Audit

[Filled at Step 7. Grade A or B closes the todo; C names the item and the user picks fix / accept (→ B) / Blocked. No "to reach A." Re-runs append.]

### YYYY-MM-DD — Grade: [A | B | C]

**Veto-tier findings:** [one line each, or "None"]
**Callouts:** [≤ 5, each with disposition: punched / dismissed / accepted with reason]
**Accepted gaps (B only):** [AC-n — reason]
**User acknowledgment:** [Date — "Accepted" or "Fixing AC-n"]
**Full audit:** [`reviews/close-out-audit.md`](./reviews/close-out-audit.md)

---

## Follow-on

[Filled at Step 8. Everything this todo did not do — queued Drafts at close, accepted gaps, open punchlist rows, unpinned tests, doc debt. **One line each.** A list, not a commitment; a successor todo that adopts an item writes it as an acceptance bullet there.]

- <item> · <origin: {ID}-{NNN} or review file>

---

## Docs & Retro

[Filled at Step 8.]

**Documentation:** [Doc deltas shipped with the behavior they describe — confirmed. Internal-contradiction callouts reconciled: one line each. Remaining doc debt → Follow-on.]

**Retro (one paragraph):** [What this todo taught about the workflow itself. Include the numbers: plans issued vs. cap; findings dismissed / punched / queued. Route lessons to the project CLAUDE.md, the skill backlog, or memory.]

---

## Results / Conclusions

[Filled at Step 8. What was built and decided, in one short paragraph.]

```
Plans: {issued} issued of {cap} cap — {done} Done, {abandoned} Abandoned, {retired} Retired.
Punchlist: {closed} closed. Dismissed: {n}. Follow-on: {n}.
Close-Out Audit: Grade {A|B} (acknowledged YYYY-MM-DD).
```

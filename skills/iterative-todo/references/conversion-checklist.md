# Converting an Older Flat-File Todo to the Iterative Folder Shape

Use this checklist when an existing flat-file todo (`docs/todos/{name}.md` with sibling `docs/plans/{name}.md`) needs to be migrated to the iterative folder shape (`docs/todos/{ID}-{name}/todo.md` with `plans/` and `reviews/` subdirectories — `{ID}` is the 3–5 letter unique todo ID assigned per SKILL.md Step 1).

The conversion is **structural and additive**. Existing plan content is preserved. New structure (Discovery Log, Plan Index, per-plan reviews folder, Sibling Todos section) is overlaid.

## When to Convert

Convert when:

- The todo lives in the older flat-file shape (`docs/todos/{name}.md` + `docs/plans/{name}.md`) and you want it on the iterative folder shape going forward.
- Discoveries during implementation keep surfacing — the original plan's assumptions are eroding — and adding a Discovery Log on the todo would help.
- More plans are likely; the cost of trying to predict them is higher than the cost of drafting them on demand.

Do NOT convert if:

- The todo is nearly done — finish it as-is and use the iterative folder shape on the next todo.
- The todo's scope is bounded, single-plan, and the original plan still holds.

## Conversion Steps

### 1. Confirm with the user

Conversions touch durable working files. Confirm with the user before starting:

> "This todo has hit {N} discoveries / amendments. I'd like to convert it to iterative-todo so future plans are smaller and discoveries get logged on the todo. The conversion preserves existing plan content, adds a Discovery Log, builds a Plan Index from existing plans, and queues any deferred work as new draft plans. Proceed?"

On confirmation, continue.

### 2. Assign an ID and create the new folder structure

Assign a 3–5 letter unique todo ID per SKILL.md Step 1 (verify uniqueness against `docs/todos/{ID}-*`, `docs/todos/completed/{ID}-*`, and any project registry at `docs/todos/_ids.md`).

```bash
mkdir -p docs/todos/{ID}-{todo-name}/plans
mkdir -p docs/todos/{ID}-{todo-name}/reviews
```

The todo file moves to `docs/todos/{ID}-{todo-name}/todo.md`. Add the `**ID:**` line near the top of the todo header.

### 3. Rewrite todo.md to the iterative shape

Use `references/todo-template.md` as the target shape. Keep:

- **Goal** / **Acceptance Criteria** / **Out of Scope** — copy from original todo verbatim. If the original had these as "Problem" / "Solution", restate as Goal + Acceptance Criteria with the user.
- **Type / Status / Priority / Created** — copy.

Add (new for iterative):

- **Plan Index** — empty for now, will be populated in step 5.
- **Discovery Log** — empty, will be seeded in step 6.
- **Skipped Steps** — copy any from the original todo.

Remove:

- Old Plan Review section, old Graded Review section — those are tied to specific plans and will move into per-plan review files in step 7.

### 4. Move plan files into `plans/` with original numbers

Plan numbering is **monotonic** — preserve the original numbers. If the original used names without numbers, assign monotonic numbers in the order plans were drafted (chronological by creation date).

```
docs/plans/{plan-1}.md  →  docs/todos/{ID}-{todo-name}/plans/001-{name}.md
docs/plans/{plan-2}.md  →  docs/todos/{ID}-{todo-name}/plans/002-{name}.md
```

For each plan, decide its current iterative status:

- `Done` — plan was completed and moved to `plans/completed/` in the old shape, or has a passing review of any era (graded reviews from the pre-0.6 workflow count).
- `In Progress` — plan was the active one when conversion started.
- `Abandoned` — plan was started but explicitly stopped. Add an **Abandonment Reason** paragraph (the user provides this in conversation — what was learned, why it stopped).
- `Draft` — plan was queued (e.g., a stub plan from the original "Multi-Plan Todos" pattern).

Translate each plan's old shape into the new lean shape:

- `Overview` → `Scope` (one paragraph, condensed).
- `Implementation Steps` → `Steps`. Cap at ~10; if there are more, keep them but flag in Notes.
- `Acceptance Criteria` → `Acceptance` (specific to this plan, not the whole todo).
- `Plan Amendments` → keep as-is (already append-only).
- `Design Decisions` → fold into `Notes` or migrate notable decisions to the todo's Discovery Log.
- `Current Behavior Map` / `Out of Scope` / `Business Rules` — these belong on the todo level in the iterative shape. Pull anything still relevant up to the todo. Most won't need to migrate — the original todo already had Goal / Out of Scope.
- `Companion Plans` — these become rows in the Plan Index, not a section on the plan.

### 5. Build the Plan Index on todo.md

Walk the `plans/` folder. Each plan gets one row:

```
| 001 | [001-{name}](./plans/001-{name}.md) | [short title] | Done |
| 002 | [002-{name}](./plans/002-{name}.md) | [short title] | Abandoned |
| 003 | [003-{name}](./plans/003-{name}.md) | [short title] | In Progress |
```

### 6. Seed the Discovery Log from existing Plan Amendments and Findings

For each entry in any existing plan's `Plan Amendments` section, write a one-line Discovery Log entry on the todo:

```
### YYYY-MM-DD — Plan {NNN}
- **Finding:** [one sentence — extract from amendment "Why"]
- **Decision:** Amend  (or Abandon if the plan ended up Abandoned)
- **Follow-up:** [follow-up plan number, or "n/a"]
```

For abandoned plans, write a Discovery Log entry summarizing the reason in one line. The full reason stays on the plan in Abandonment Reason.

The seeded log is intentionally terse. The point is to give future-you a navigation index across plans, not to retell the saga.

### 7. Move existing reviews into `reviews/`

If the original todo or plans had review entries embedded inline, extract them into per-plan review files:

```
reviews/001-plan-review.md      # if plan 001 had a Plan Review
reviews/001-code-review.md      # if plan 001 had a Graded Review
```

If reviews are too entangled to map cleanly, create `reviews/historical.md` with the original content verbatim and note the mapping is approximate.

### 8. Carry deferred work as queued Draft plans

Any "Companion Plans" entry, "Deferred Scope" item, or "future plan" reference from the original becomes a new `Draft` plan in the Plan Index. Create a stub plan file with status `Draft`, fill in just the Scope paragraph from what the original noted, leave Steps empty.

These are the natural starting points for the iterative phase.

### 9. Update the todo's Plan Sequence reference (if it had one)

Old shape had a Plan Sequence Callout in Results. The iterative shape generates this at Step 8 (Completion & Retro) from the Plan Index. Remove the old callout if it's stale.

### 10. Resume

Where work stands determines the resume point:

- An `In Progress` plan exists → resume at Step 4 (Implement) of the iterative workflow.
- All plans `Done` or `Abandoned` and queued `Draft` plans exist → resume at Step 2 (draft next plan — flesh out the next Draft).
- All plans `Done` or `Abandoned` and Plan Index empty → prompt user to confirm Acceptance Criteria → Step 7 (Close-Out Audit).

## Verification

After conversion, verify:

- [ ] `docs/todos/{ID}-{todo-name}/todo.md` exists and uses iterative-todo template
- [ ] Every plan from the original is in `plans/` with monotonic numbering preserved
- [ ] Plan Index lists every plan with current status
- [ ] Discovery Log has at least one entry per Plan Amendment and per abandoned plan
- [ ] Each abandoned plan has an Abandonment Reason paragraph
- [ ] Existing reviews are in `reviews/` (or `reviews/historical.md`)
- [ ] Deferred work is queued as `Draft` plans in Plan Index
- [ ] Old `docs/plans/{name}.md` and `docs/plans/completed/{name}.md` files are removed (or moved into the new structure)
- [ ] Original `docs/todos/{name}.md` is removed (replaced by the new folder)

## Notes for the orchestrator

- **Conversion is a one-time event per todo.** Do not convert mid-plan — finish the in-flight plan first if reasonable, or abandon it explicitly with a reason and start fresh in the iterative shape.
- **The conversion itself is not a plan.** It's a structural rewrite. Don't create `plans/000-conversion.md` — just do the conversion in conversation with the user and note the conversion date in the todo's Last Updated field.
- **If the original was a sibling of other todos, leave the siblings alone.** Conversion is per-todo; siblings can stay on `project-todos` if their shape suits.

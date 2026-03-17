---
name: ui-todos
description: This skill should be used when the user asks to "create a ui todo", "add a ui task", "track ui work", "ui change needed", "fix the UI layout", "match the legacy screen", "build a UI component", "ui implementation workflow", "visual fix", "CSS fix", "fix the page layout", "style the page", "make it look like the legacy screen", "ui what's next", "resume ui work", "launch ui agent", "delegate UI work to agent", or describes UI/visual/layout changes that need structured agent-driven tracking. Manages the full lifecycle of UI work items where all source code changes are made exclusively by agents. Use this skill instead of project-todos when work is primarily visual. When ambiguous, prefer this skill if the work centers on page presentation, components, or CSS.
---

# UI Todos — Agent-Driven UI Workflow

Manage UI work using structured todo/plan files with all code changes delegated to the UI agent. Conversation handles orchestration: creating todos, discussing requirements, deciding next steps, and launching agents.

## When to Use This Workflow

**Use ui-todos when:**
- The work is primarily UI/visual: pages, components, CSS, layout
- Matching or adapting a legacy screen
- Building new UI components or fixing visual issues
- UI work that needs small backend changes as prerequisites (e.g., adding a property, a new factory method)
- The user explicitly requests a UI todo or agent-driven UI work

**Use project-todos instead when:**
- The work is primarily backend: domain models, business logic, repositories
- The task is full-stack with substantial backend and UI work equally weighted
- The work needs architect/developer review cycles for complex domain design

**Boundary rule:** Backend prerequisites are "small" if they touch 2-3 entities or fewer, do not require new aggregates, and do not introduce complex business rules. Handle these as an optional step within this workflow using the developer agent. Anything beyond that threshold belongs in project-todos for the backend portion.

---

## Core Rule: No Code in Conversation

When this skill is loaded:

- **ALL source code changes** (`.cs`, `.razor`, `.css`, `.js`, etc.) happen inside agents — UI agent for frontend, developer agent for backend prerequisites
- **Plan creation** is delegated to the UI agent (the agent investigates and writes the plan)
- **Conversation creates and updates todo files** — these are orchestration markdown, not source code
- **Conversation may write plan files** only with explicit user permission (e.g., when a plan was worked out through discussion and needs capturing)
- **Conversation orchestrates**: what step are we on, what agent to launch next, reviewing agent output

---

## Prerequisites

Before starting the workflow, check `.claude/agents/` for project-specific agents:

1. **UI agent** (required) — The project's frontend/UI agent. Handles all UI code changes, plan creation, plan review, implementation, and verification.
2. **Developer agent** (required if backend prerequisites arise) — The project's backend/domain agent. Handles targeted backend changes needed to support the UI work. If the plan identifies backend prerequisites but no developer agent exists, STOP and inform the user — suggest either creating one or using project-todos for the backend portion.
3. **Legacy reference agent** (optional) — An agent that can analyze the legacy application for screen matching. Used in Step 2. Skip Step 2 if not found and no legacy reference is needed.

---

## Directory Structure

```
docs/
├── todos/
│   ├── {todo-name}.md
│   └── completed/
├── plans/
│   ├── {plan-name}.md
│   └── completed/
```

Filename convention: lowercase, hyphens for spaces, no dates, 2-5 words.

---

## Workflow

### Step 1: Create Todo (Conversation)

Discuss the UI work with the user. Focus on WHAT should change visually, not HOW to implement it.

1. Gather: title, visual description, current state, affected pages/components
2. Create todo file in `docs/todos/` using `references/ui-todo-template.md`
3. Set status to "In Progress"
4. **Do NOT create a plan yet** — flesh out the todo first

A todo is ready for planning when:
- The visual requirements are clear and specific
- The scope is understood (which pages/components)
- The user confirms they're ready to proceed

### Step 2: Legacy Reference (Optional)

When the work involves matching or referencing a legacy screen:

1. Launch the **legacy reference agent** to analyze the relevant legacy templates
2. Provide: the screen name or URL path, what to look for
3. Add the agent's findings to the todo file (Legacy Reference section)
4. Skip this step if the work is new functionality with no legacy equivalent

### Step 3: Create Plan (UI agent)

Launch the **UI agent** to create the implementation plan.

Plans created too early accumulate technical debt before implementation starts. Only proceed to this step when the todo's visual requirements are clear and the user is ready.

Provide the agent with:
- The todo file path
- Instruction: "Read this todo, investigate the codebase, and create an implementation plan in `docs/plans/` following project UI patterns and best practices. Write the plan file yourself."
- The plan template from this skill's `references/ui-plan-template.md`

The agent should:
1. Read the todo to understand visual requirements
2. Investigate existing components, layout patterns, and CSS conventions
3. Design the component strategy (framework components, layout approach)
4. Write the plan file in `docs/plans/`
5. Link the plan to the todo (update both files)

### Step 4: Review Plan (FRESH UI agent + Conversation)

**MUST be a fresh agent — no shared context with the plan creation agent.**

Launch a new (fresh) **UI agent** with:
- The plan file path
- The todo file path
- Instruction: "Review this UI implementation plan. You did NOT create it — review with fresh eyes. Check that the component strategy is sound, CSS approach follows project patterns, implementation steps are complete, and visual acceptance criteria are specific enough. Note any concerns or gaps."

After the review agent reports:
1. Present the review findings to the user
2. Discuss any concerns raised
3. Update the plan with user permission, or re-launch agents for revisions
4. Mark plan as "Approved" when the user is satisfied

### Step 4.5: Backend Prerequisites (Developer agent — Optional)

**Skip this step if the plan has no Backend Prerequisites section or it is empty.**

When the plan identifies backend changes needed to support the UI work (new properties, factory methods, endpoints, etc.), launch the **developer agent** with targeted instructions.

**Size threshold:** This step is for small, focused backend changes clearly in service of the UI. If the backend work involves more than 2-3 entities, requires new aggregates, or needs complex business rules, STOP and recommend using project-todos for the backend portion instead.

Provide the developer agent with:
- The plan file path (pointing to the Backend Prerequisites section)
- Instruction: "Implement these specific backend changes needed for UI work. These are targeted prerequisites, not a full feature. Implement the changes, add appropriate tests, run all tests, and report results. Do NOT modify any UI files."

The developer agent should:
1. Read the Backend Prerequisites section of the plan
2. Implement the specific changes listed
3. Add tests appropriate to the project's test architecture
4. Run all tests — **all tests must pass**
5. Report: what was changed, what tests were added, test results

**Verification gate:** All tests passing is sufficient proof for targeted backend prerequisites. No separate architect verification is needed for this step.

After the developer agent completes successfully, update the plan's Backend Prerequisites section with the results and proceed to Step 5.

If tests fail, report to the user before proceeding. Do NOT continue to UI implementation with failing backend tests.

### Step 5: Implementation (UI agent)

Launch the **UI agent** to implement the approved plan.

Provide the agent with:
- The plan file path
- The todo file path
- Instruction: "Implement this approved UI plan. Update the Implementation Progress section as you work. When done, fill the Completion Evidence section and set status to Awaiting Verification. Do NOT mark the todo as Complete."

**Splitting large work**: For plans with multiple independent components or pages, consider launching separate agents for each portion. Each agent gets the plan but focuses on its assigned section.

The agent should:
1. Work through the implementation steps in the plan
2. Follow the project's CSS/styling priorities (framework utilities first, scoped styles second, global styles last)
3. Update Implementation Progress as milestones complete
4. Run `dotnet build` to verify compilation
5. Fill Completion Evidence when done
6. Set plan status to "Awaiting Verification"
7. **STOP** — do not mark as complete

### Step 6: Verification (FRESH UI agent)

**MUST be a fresh agent — no shared context with the implementation agent.**

Launch a new (fresh) **UI agent** with:
- The plan file path
- The todo file path
- List of changed files (from implementation agent's output)
- Instruction: "Independently verify this UI implementation. You did NOT implement this — review it with fresh eyes. Check visual correctness, framework usage, CSS/styling quality, and component patterns. Fill the Verification section."

The fresh agent should:
1. Read the plan's visual requirements and acceptance criteria
2. Review each changed file for quality and correctness
3. Check framework component usage follows project patterns
4. Verify CSS follows priorities (utilities > scoped > global)
5. Look for regressions in related components
6. Run `dotnet build` independently
7. Render verdict: **VERIFIED** or **SENT BACK** with specific issues

If **SENT BACK**: Report issues to the user. Launch an implementation agent (can resume the original or start fresh) to address the specific issues. Then re-verify with another fresh agent.

### Step 7: Completion

Only after verification passes:

1. Update todo status to "Complete" and Last Updated date
2. Fill Results/Conclusions section
3. Move todo to `docs/todos/completed/`
4. Move plan to `docs/plans/completed/`
5. Update plan status to "Complete"

---

## Fresh Agent Optimization

### Always Fresh

- **Verification** (Step 6) — mandatory, independent review requires clean context
- **Plan review** (Step 4) — reviewer must not be biased by having created the plan
- **Plan creation** (Step 3) — agent needs unbiased codebase investigation

### Usually Fresh

- **Implementation of a new plan** — clean context to focus on the plan
- **After conversation pivots** — when requirements changed significantly
- **Large independent portions** — separate components or pages

### Resume When

- **Follow-up fixes** from verification feedback (agent knows what it built)
- **Iterating on the same component** (minor tweaks, same scope)
- **Continuing implementation** of the same plan section after interruption
- **Small corrections** to recent agent work

### What "Fresh" Means Operationally

A fresh agent means launching a new Agent tool invocation. A resumed agent means calling `SendMessage(to: "agent-name", message: "new instructions")` — the agent resumes from its transcript in the background. Agents must be spawned with `run_in_background: true` to be resumable. Wait for the task-notification. Do NOT launch a duplicate Agent call after SendMessage.

### Principle

Fresh agents provide unbiased investigation and review. Resumed agents preserve valuable implementation context. Default to fresh unless context reuse clearly helps.

---

## Status Values

### Todo Status

- `In Progress` — Active work item, being discussed or worked on
- `Blocked` — Waiting on a dependency (backend work, external input, etc.)
- `Complete` — Verified and moved to completed/

### Plan Status

- `Draft` — Agent creating the plan
- `Under Review` — User reviewing in conversation
- `Approved` — Ready for implementation
- `In Progress` — Implementation underway
- `Awaiting Verification` — Implementation done, needs fresh agent review
- `Sent Back` — Verification failed, needs fixes
- `Complete` — Verified and moved to completed/

---

## Common Workflows

### Simple UI Fix

1. Create todo (Step 1)
2. Skip legacy reference
3. Create plan via agent (Step 3) — may be brief for small fixes
4. Quick review (Step 4)
5. Implement (Step 5)
6. Verify with fresh agent (Step 6)
7. Complete (Step 7)

### Legacy Screen Match

1. Create todo (Step 1)
2. Launch legacy reference agent (Step 2)
3. Create plan via UI agent (Step 3)
4. Review plan (Step 4)
5. Implement (Step 5)
6. Verify with fresh agent (Step 6)
7. Complete (Step 7)

### UI Work with Backend Prerequisites

1. Create todo (Step 1)
2. Create plan via UI agent (Step 3) — plan identifies backend prerequisites
3. Review plan (Step 4) — confirm prerequisites are correctly scoped
4. Developer agent handles backend prerequisites (Step 4.5) — tests must pass
5. UI agent implements (Step 5)
6. Verify with fresh UI agent (Step 6)
7. Complete (Step 7)

### Todo Only (No Implementation Yet)

1. Create todo file
2. Inform user of file location
3. Return to it later with "resume ui work"

---

## Best Practices

1. **Don't rush planning** — flesh out the todo in conversation before launching agents
2. **No code in conversation** — all file edits to source code happen in agents
3. **Fresh for verification** — always use a fresh agent for Step 6
4. **Clear agent instructions** — provide file paths, template paths, and specific instructions
5. **One todo per UI task** — don't combine unrelated UI changes
6. **Visual-first descriptions** — describe what the user should SEE, not implementation details
7. **Link maintenance** — update both todo and plan files when creating links
8. **Status accuracy** — update status fields promptly as workflow progresses

---

## Reference Files

- UI todo template: `references/ui-todo-template.md`
- UI plan template: `references/ui-plan-template.md`

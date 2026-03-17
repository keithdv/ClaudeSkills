---
name: ui-todos
description: This skill should be used when the user asks to "create a ui todo", "add a ui task", "track ui work", "build a UI component", "fix the UI layout", "visual fix", "CSS fix", "style the page", "update the form layout", "MudBlazor component", "responsive layout", "ui what's next", "resume ui work", "launch ui agent", "delegate UI work to agent", or describes UI/visual/layout changes that need structured agent-driven tracking. Manages the full lifecycle of UI work items where all source code changes are made exclusively by agents. Prefer this skill when work centers on page presentation, components, or CSS.
---

# UI Todos — Agent-Driven UI Workflow

Manage UI work using structured todo/plan files with all code changes delegated to agents. The orchestrator handles todo/plan file management, agent coordination, and user communication. Agents handle all source code changes.

## When to Use This Workflow

**Use ui-todos when:**
- The work is primarily UI/visual: pages, components, CSS, layout
- Building new UI components or fixing visual issues
- UI work that needs small backend changes as prerequisites (2-3 entities or fewer)
- The user explicitly requests a UI todo or agent-driven UI work

**Use project-todos instead when:**
- The work is primarily backend: domain models, business logic, repositories
- The task is full-stack with substantial backend and UI work equally weighted
- The work needs architect/developer review cycles for complex domain design

---

## Core Rules

### No Code in Conversation

- **ALL source code changes** (`.cs`, `.razor`, `.css`, `.js`, etc.) happen inside agents
- **Plan creation** is delegated to the UI agent
- **Conversation creates and updates todo files** — orchestration markdown, not source code
- **Conversation orchestrates**: what step are we on, what agent to launch next, reviewing agent output

### Discovery vs Analysis

The orchestrator may **discover** (look things up, resolve ambiguity, find file paths, check component existence) but must not **analyze** (draw conclusions about what should change in source code). Analysis and design decisions belong to agents. Before reading a file, ask: "Am I looking something up, or building a case?" If building a case, invoke an agent instead.

---

## Prerequisites

Before starting the workflow, check `.claude/agents/` for project-specific agents (project-specific agents take priority over user-level agents at `~/.claude/agents/`):

1. **UI agent** (required) — Frontend/UI agent. Handles plan creation, implementation, and code changes.
2. **Developer agent** (required if backend prerequisites arise) — Backend/domain agent for targeted backend changes. If prerequisites are identified but no developer agent exists, STOP and inform the user.
3. **Business-requirements-reviewer** (optional) — Reviews proposed work against documented business requirements. Skip Step 2 if not found and no requirements check is needed.

---

## Agent Resume Strategy

Resume agents across steps to preserve accumulated context. Track agent IDs in the plan's Agent IDs section.

| Agent | Fresh At | Resume At |
|-------|----------|-----------|
| Requirements Reviewer | Step 2 | — |
| UI Agent | Step 3 (Plan) | Step 5 (Implement) |
| Developer Agent | Step 4.5 (Backend) | — |
| Verification Agent | Step 6 (Verify) | — |

Start a fresh agent only if the resumed agent is failing or the context has grown too large.

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
2. **Discover** — Glob/Grep to resolve ambiguity: find file paths, check if components exist, locate prior related work
3. Create todo file in `docs/todos/` using `references/ui-todo-template.md`
4. Set status to "In Progress"
5. Update the todo's **Progress Log** at creation and at each workflow transition (plan created, implementation started, verification passed, etc.)
6. **Do NOT create a plan yet** — flesh out the todo first

A todo is ready for the next step when:
- The visual requirements are clear and specific
- The scope is understood (which pages/components)
- The user confirms they're ready to proceed

### Step 2: Requirements Review (Optional)

**When to include:** The proposed UI work involves data display, form fields, workflow steps, or business-visible behavior changes. **When to skip:** Pure styling fixes (spacing, colors, fonts, layout reorganization) that don't change what data is shown or how workflows operate.

Invoke the **business-requirements-reviewer** agent with:
- The todo file path
- The project's business requirements locations (from CLAUDE.md)
- Instruction: "Review this UI todo against the project's existing business requirements. Write findings into the todo's Requirements Review section. VETO if contradictions are found."

The reviewer should:
1. Read the todo to understand the proposed visual changes
2. Search requirements docs for rules related to the affected data and workflows
3. Identify relevant requirements, gaps, and contradictions
4. Write findings into the todo's **Requirements Review** section
5. Set verdict: **APPROVED** or **VETOED**

**If VETOED:** Present contradictions to the user. STOP. The user decides how to resolve. Re-invoke reviewer after resolution to confirm APPROVED.

**If skipped:** Note "Requirements Review: Skipped — pure styling/layout work" in the todo.

### Step 3: Create Plan + Grade (Fresh UI Agent)

Launch a **fresh UI agent** to create the implementation plan.

Provide the agent with:
- The todo file path (with Requirements Review section if populated)
- Instruction: "Read this todo, investigate the codebase, and create an implementation plan in `docs/plans/`. Grade difficulty and risk. Write the plan file yourself."
- The plan template from `references/ui-plan-template.md`

The agent should:
1. Read the todo to understand visual requirements (and Requirements Review if present)
2. Investigate existing components, layout patterns, and CSS conventions
3. Design the component strategy
4. Write the plan file in `docs/plans/`
5. Link the plan to the todo (update both files)
6. **Grade Difficulty and Risk** — Low/Medium/High for each with justification
7. Set plan status to "Draft"

**Save the UI agent ID** in the plan's Agent IDs section.

**Present the Difficulty & Risk grade to the user.** If High difficulty or risk, the user may escalate to `project-todos` for the backend-heavy portion.

### Step 4: User Reviews Plan (Conversation)

Present the plan to the user for review. The user decides:
- **Approve** — Proceed to implementation (or backend prerequisites first)
- **Request changes** — Resume the UI agent from Step 3 to revise the plan
- **Escalate** — Move to `project-todos` if scope is larger than expected

Mark plan as "Approved" when the user is satisfied.

### Step 4.5: Backend Prerequisites (Developer Agent — Optional)

**Skip if the plan has no Backend Prerequisites section or it is empty.**

Launch the **developer agent** with:
- The plan file path (pointing to the Backend Prerequisites section)
- Instruction: "Implement these specific backend changes needed for UI work. Targeted prerequisites only. Implement, add tests, run all tests, and report results. Do NOT modify UI files."

**Size threshold:** If the backend work involves more than 2-3 entities, requires new aggregates, or needs complex business rules, STOP and recommend `project-todos` for the backend portion.

After completion, update the plan's Backend Prerequisites section with results. All tests must pass before proceeding.

### Step 5: Implementation (Resume UI Agent)

**Resume the UI agent** from Step 3 with:
- Instruction: "Implement the approved plan. Update Implementation Progress as you work. When done, fill Completion Evidence and set status to Awaiting Verification. Do NOT mark the todo as Complete."

The agent should:
1. Work through the implementation steps in the plan
2. Follow CSS priorities (MudBlazor utilities first, scoped CSS second, global CSS last)
3. Update Implementation Progress as milestones complete
4. Run `dotnet build` to verify compilation
5. Fill Completion Evidence when done
6. Set plan status to "Awaiting Verification"
7. **STOP** — do not mark as complete

### Step 6: Verification (Fresh UI Agent)

**MUST be a fresh agent — no shared context with the implementation agent.**

Launch a new **fresh UI agent** with:
- The plan file path
- The todo file path
- List of changed files (from implementation agent's output)
- Instruction: "Independently verify this UI implementation. You did NOT implement this — review with fresh eyes. Check visual correctness, framework usage, CSS quality, and component patterns. Fill the Verification section."

The fresh agent should:
1. Read the plan's visual requirements and acceptance criteria
2. Review each changed file for quality and correctness
3. Check framework component usage follows project patterns
4. Verify CSS follows priorities
5. Look for regressions in related components
6. Run `dotnet build` independently
7. Render verdict: **VERIFIED** or **SENT BACK** with specific issues

If **SENT BACK**: Report issues to the user. Resume the implementation agent from Step 5 to fix. Then verify again with another fresh agent.

### Step 7: Completion

Only after verification passes:

1. Update todo status to "Complete" and Last Updated date
2. Fill Results/Conclusions section
3. Move todo to `docs/todos/completed/`
4. Move plan to `docs/plans/completed/`
5. Update plan status to "Complete"

---

## Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the todo file. Check if a plan exists (Plans section).
2. **If no plan exists**, check the todo's Requirements Review section:
   - Not present and work involves data/workflows → Step 2
   - Skipped or APPROVED → Step 3 (create plan)
   - VETOED → Step 2 (resolve contradictions with user)
3. **If a plan exists**, read its Status field:
   - `Draft` → Step 3 (agent still working) or Step 4 (user review)
   - `Approved` → Step 4.5 (backend prerequisites) or Step 5 (implementation)
   - `In Progress` → Step 5 (implementation continues)
   - `Awaiting Verification` → Step 6 (verification)
   - `Sent Back` → Step 5 (fix issues, read Verification section for what failed)
   - `Complete` → Step 7 (completion)
4. Check the plan's Agent IDs section for stored IDs to resume the correct agents.

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

- `In Progress` — Active work item
- `Blocked` — Waiting on a dependency
- `Complete` — Verified and moved to completed/

### Plan Status

- `Draft` — Agent creating the plan
- `Approved` — User approved, ready for implementation
- `In Progress` — Implementation underway
- `Awaiting Verification` — Implementation done, needs fresh agent review
- `Sent Back` — Verification failed, needs fixes
- `Complete` — Verified and moved to completed/

---

## Common Workflows

### Simple UI Fix

1. Create todo → Skip requirements review → Create plan + grade → User approves → Implement (resume) → Verify (fresh) → Complete

### UI Work with Business Data

1. Create todo → Requirements review → Create plan + grade → User approves → Implement (resume) → Verify (fresh) → Complete

### UI Work with Backend Prerequisites

1. Create todo → Requirements review → Create plan + grade → User approves → Developer handles backend → Implement (resume) → Verify (fresh) → Complete

### Todo Only (No Implementation Yet)

1. Create todo file → Return to it later with "resume ui work"

---

## Best Practices

1. **Don't rush planning** — flesh out the todo in conversation before launching agents
2. **No code in conversation** — all source code edits happen in agents
3. **Fresh for verification** — always use a fresh agent for Step 6
4. **Resume for implementation** — resume the plan-creation agent to preserve codebase knowledge
5. **Requirements over legacy** — documented business requirements are the authority, not the legacy application
6. **One todo per UI task** — don't combine unrelated UI changes
7. **Visual-first descriptions** — describe what the user should SEE, not implementation details
8. **Track Agent IDs** — record agent IDs in the plan for cross-session resume

---

## Reference Files

- UI todo template: `references/ui-todo-template.md`
- UI plan template: `references/ui-plan-template.md`

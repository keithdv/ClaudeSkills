---
name: short-todo
version: 2.0.0
description: |
  This skill should be used when the user asks to "create a short todo", "quick todo", "small todo", "simple todo", "simple task", "short workflow", "lightweight todo", "short-todo", "don't need the full workflow", or mentions straightforward work that needs tracking but not the full project-todos workflow. Provides a streamlined agent collaboration workflow with simplified templates and no requirements review phase, designed for small, well-understood changes.
---

# Short Todo Workflow

Streamlined agent collaboration workflow for straightforward, small todos. Same orchestrator rules as project-todos but with a simplified workflow (no requirements review, no agent phasing, no domain model behavioral design) and slimmed templates.

## Core Rules

The same core rules from project-todos apply:

1. **The orchestrator is the planner and implementer.** The orchestrator creates plans and implements code in conversation with the user.
2. **Agents review and report back.** Agents validate, verify, and review — they don't write to shared files (plans, todos) or set status.
3. **Agents write to their own memory files only.** The orchestrator reads agent memory files and manages all shared documents.

Full details on these rules are in `~/.claude/skills/project-todos/SKILL.md`.

## Agent Strategy

Every agent invocation is a **fresh** Agent call. Provide full context (todo path, plan path, agent memory file path, relevant instructions) each time. Do not attempt to resume agents across steps.

## Prerequisites

Before starting, check for project-specific resources:

1. **Agents** -- Check the project root's `.claude/agents/` for project-specific agents (architect, developer, documenter). Fall back to general agents at `~/.claude/agents/`. Project-specific agents take priority.
2. **Domain skill** -- Check for domain-specific skills that provide codebase context. Reference these when invoking agents.

---

## Agent Memory Files

Each plan has a companion memory directory where agents store their private working state. For key rules, base format, and orchestrator responsibilities, see `~/.claude/skills/shared/references/agent-memory.md`.

### Structure

```
docs/plans/
├── feature-name-plan.md              # Design only — shared by all agents
└── feature-name-plan.memory/
    ├── architect.md                   # Architect's private notes
    ├── developer.md                   # Developer's private notes
    └── documenter.md                  # Documenter's private notes (if applicable)
```

### What Lives in Memory Files vs. Plan

| Content | Location |
|---------|----------|
| Design (Overview, Business Rules, Approach, Design, Implementation Steps, Acceptance Criteria) | Plan file |
| Difficulty & Risk Assessment, Risks / Considerations | Plan file |
| Developer Review (concerns, verdict) | `developer.md` |
| Implementation Contract (scope, stop conditions) | `developer.md` |
| Implementation Progress (milestones, evidence) | `developer.md` |
| Completion Evidence (test results, contract status) | `developer.md` |
| Architect Verification (verdict, build/test results, design match) | `architect.md` |
| Documentation tracking (files updated) | `documenter.md` |

---

## Workflow

### Step 1: Create Todo

Capture the user's description. Discover/resolve ambiguity (Glob/Grep for file paths, prior work references). Create the todo file in `docs/todos/` (project-relative) using this skill's `references/todo-template.md`. Set status to "In Progress."

**Do NOT create the plan file.** The architect creates it in Step 3.

### Step 2: Draft Plan (Orchestrator + User)

Working in conversation with the user, create the complete plan:

1. Create the plan file in `docs/plans/` (project-relative) using this skill's `references/plan-template.md`
2. Link the plan to the todo (update both files)
3. Write business rules as WHEN/THEN assertions
4. Design the approach and implementation steps
5. **Grade Difficulty and Risk** -- Low/Medium/High for each with justification
6. Set plan status to "Draft"

**Present the Difficulty & Risk grade to the user before proceeding.** This is where the user can decide to escalate to the full project-todos workflow if the scope is larger than expected.

### Step 3: Architect Validation (Fresh)

Invoke a **fresh architect agent** with:
- The plan file path (all sections already populated)
- The todo file path
- The architect's memory file path: `docs/plans/{plan-name}.memory/architect.md`
- Instruction: "Validate this plan. Check that business rules are correct, approach is feasible, and implementation steps are sound. Write findings to your memory file at [path]. Report back with your verdict."

The architect should:
1. Validate the business rules and design against codebase reality
2. Check for gaps, ambiguities, and risks
3. Write findings to their memory file
4. Report verdict: **Approved** or **Concerns**

**If concerns:**
1. Present concerns to the user
2. The orchestrator updates the plan based on user's direction
3. Re-invoke architect to validate
4. Repeat until approved

On approval, the orchestrator sets plan status to "Ready for Implementation."

### Step 4: Implementation (Orchestrator + User)

The orchestrator implements code changes directly in conversation with the user:

1. Set plan status to "In Progress"
2. Work through the implementation steps
3. Run tests at milestones
4. **STOP and report** if out-of-scope tests fail
5. When complete, run all builds and tests
6. Set plan status to "Awaiting Verification"

### Step 5: Developer Code Review (Fresh)

Invoke a **fresh developer agent** with:
- The plan file path
- The developer's memory file path: `docs/plans/{plan-name}.memory/developer.md`
- A summary of what was implemented: files changed, tests written, test results
- Instruction: "Review the implementation against the plan's business rules. Trace each assertion through the actual code. Write findings to your memory file at [path]. Report back with your verdict."

The developer should:
1. Review the business rules against actual code
2. Check test coverage for each scenario
3. Write findings to their memory file
4. Report verdict: **Approved** or **Concerns**

**If concerns:**
1. Present concerns to the user
2. The orchestrator fixes issues in conversation with the user
3. Re-invoke developer for re-review
4. Repeat until approved

On approval, the orchestrator sets plan status to "Awaiting Verification."

### Step 6: Architect Verification (Fresh Architect)

Invoke a **fresh architect agent** with:
- The plan file path
- The todo file path
- The architect's memory file path: `docs/plans/{plan-name}.memory/architect.md`
- A summary of what was implemented: files changed, tests written, build/test results
- Instruction: "Verify the completed implementation. Independently run builds and tests. Do NOT trust previously reported results. Write your verification verdict to your agent memory file at [path]. Report back with your verdict."

The architect should:
1. Independently run all builds and tests
2. Zero failures allowed
3. Check implementation matches the design
4. Write verification verdict to the architect's memory file
5. Report verdict to orchestrator: **VERIFIED** or **SENT BACK**

The orchestrator sets plan status based on the verdict. If SENT BACK: the orchestrator fixes issues in conversation with the user, then re-invokes the architect to verify.

### Step 7: Documentation (Fresh Documenter)

Invoke the **documenter agent** (fall back to developer agent if no documenter exists) with:
- The plan file path
- The todo file path
- The documenter's memory file path: `docs/plans/{plan-name}.memory/documenter.md`
- The developer's completion evidence (relayed by the orchestrator from `developer.md` — the documenter does NOT read `developer.md` directly)
- Instruction: "Identify what documentation needs updating based on this implementation. Update it. Write all documentation tracking to your agent memory file at [path]."

The documenter should:
1. Identify documentation affected by the implementation
2. Update it
3. Record all changes in the documenter's agent memory file
4. Set plan status to "Documentation Complete"

If the documenter identifies source code changes needed, flag them -- the orchestrator decides how to handle.

### Step 8: Completion

The orchestrator performs this step directly:
1. Verify architect verdict is "VERIFIED" (read from `docs/plans/{plan-name}.memory/architect.md`)
2. Verify documentation step is complete
3. Update todo status to "Complete" and Last Updated date
4. Fill Results/Conclusions section
5. Set plan status to "Complete"
6. Move todo and plan to `completed/` directories

## Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the todo file. Check if a plan exists (Plans section).
2. **If no plan exists** -> Step 2 (draft plan with the user)
3. **If a plan exists**, read its Status field:
   - `Draft` -> Step 3 (architect validation)
   - `Concerns Raised` -> Step 3 (address architect concerns with user, re-invoke architect)
   - `Ready for Implementation` -> Step 4 (orchestrator implements in conversation)
   - `In Progress` -> Step 4 (implementation continues in conversation)
   - `Awaiting Code Review` -> Step 5 (developer code review)
   - `Awaiting Verification` -> Step 6 (verification). Read the developer's memory file to understand what the code review confirmed.
   - `Sent Back` -> Read the architect's memory file to determine what failed. The orchestrator fixes issues in conversation with the user, then returns to Step 5 or Step 6 as appropriate.
   - `Documentation Complete` -> Step 8 (completion)
4. Invoke a fresh agent for review/verification steps, providing the todo path, plan path, and agent memory file path. Include relevant context from other agents' memory files in the spawn prompt (the fresh agent must NOT read other agents' memory files directly).

## Filename Convention

Same as project-todos: lowercase, hyphens, no dates, 2-5 words. Examples: `fix-auth.md`, `add-export.md`, `update-visit-flow-validation.md`

Always use relative paths between todos and plans (`../todos/`, `../plans/`). Update BOTH files when linking.

## Reference Files

- **`references/todo-template.md`** -- Simplified todo template
- **`references/plan-template.md`** -- Simplified plan template (design only — workflow state goes to agent memory files)
- **`~/.claude/skills/shared/references/agent-memory.md`** -- Shared agent memory pattern (key rules, base format, orchestrator responsibilities)

---
name: short-todo
description: |
  This skill should be used when the user asks to "create a short todo", "quick todo", "small todo", "simple todo", "short workflow", "lightweight todo", "short-todo", or mentions straightforward work that needs tracking but not the full project-todos workflow. Provides a shortened agent collaboration workflow with fewer steps and simplified templates for small, well-understood changes.
---

# Short Todo Workflow

Shortened agent collaboration workflow for straightforward, small todos. Same orchestrator rules as project-todos but with fewer steps and simplified templates.

## Core Rules

The same core rules from project-todos apply:

1. **The orchestrator NEVER modifies source code.** All source changes go through agents. No exceptions for "small" fixes.
2. **Discovery vs Analysis.** The orchestrator may discover (look things up, resolve ambiguity) but must not analyze (draw conclusions about what should change).

Full details on these rules are in `~/.claude/skills/project-todos/SKILL.md`.

## Agent Strategy

Every agent invocation is a **fresh** Agent call. Provide full context (todo path, plan path, relevant instructions) each time. Do not attempt to resume agents across steps.

## Prerequisites

Before starting, check for project-specific resources:

1. **Agents** -- Check the project root's `.claude/agents/` for project-specific agents (architect, developer, documenter). Fall back to general agents at `~/.claude/agents/`. Project-specific agents take priority.
2. **Domain skill** -- Check for domain-specific skills that provide codebase context. Reference these when invoking agents.

## Workflow

### Step 1: Create Todo

Capture the user's description. Discover/resolve ambiguity (Glob/Grep for file paths, prior work references). Create the todo file in `docs/todos/` (project-relative) using this skill's `references/todo-template.md`. Set status to "In Progress."

**Do NOT create the plan file.** The architect creates it in Step 3.

### Step 2: Architect Questions (Fresh)

Invoke a **fresh architect agent** with:
- The todo file path
- Any domain skill references
- Instruction: "Read this todo. Confirm you understand the problem and proposed solution. Return clarifying questions or confirm Ready."

If the architect has questions:
1. Present questions to the user
2. Record answers in the todo's Clarifications section
3. Invoke a fresh architect agent with the updated todo
4. Repeat until "Ready"

### Step 3: Architect Plan (Fresh)

Invoke a **fresh architect agent** with:
- The todo file path (with Clarifications populated)
- Instruction: "Create the plan file for this todo. Design the implementation and grade difficulty and risk."

The architect should:
1. Create the plan file in `docs/plans/` (project-relative) using this skill's `references/plan-template.md`
2. Link the plan to the todo (update both files)
3. Write business rules as WHEN/THEN assertions
4. Design the approach and implementation steps
5. **Grade Difficulty and Risk** -- Low/Medium/High for each with justification
6. Set plan status to "Draft"

**Present the Difficulty & Risk grade to the user before proceeding.** This is where the user can decide to escalate to the full project-todos workflow if the scope is larger than expected.

### Step 4: Developer Review (Fresh)

Invoke a **fresh developer agent** with:
- The plan file path
- The todo file path
- Instruction: "Review this plan for completeness, correctness, and implementability. Raise concerns or approve."

The developer should:
1. Review the business rules and design
2. Check for gaps, ambiguities, and risks
3. Render a verdict: **Approved** or **Concerns Raised**

**If concerns -> Clarification Loop:**
1. Present concerns to the user
2. User decides: clarify themselves, or have the architect address
3. If architect: invoke a **fresh architect agent** to address concerns and update the plan
4. Invoke a **fresh developer agent** to re-review
5. Repeat until approved

On approval: developer creates the Implementation Contract section (In Scope, Out of Scope, Stop Conditions). Set plan status to "Ready for Implementation."

### Step 5: Implementation (Fresh Developer)

Invoke a **fresh developer agent** with:
- The plan file path (with implementation contract)
- Instruction: "Implement the approved plan following the implementation contract."

The developer should:
1. Set plan status to "In Progress"
2. Work through the implementation contract
3. Run tests at milestones
4. **STOP and report** if out-of-scope tests fail
5. Write Completion Evidence, set plan status to "Awaiting Verification"
6. **Do NOT mark the todo as Complete**

### Step 6: Architect Verification (Fresh Architect)

Invoke a **fresh architect agent** with:
- The plan file path
- The todo file path
- Instruction: "Verify the completed implementation. Independently run builds and tests. Do NOT trust the developer's reported results."

The architect should:
1. Independently run all builds and tests
2. Zero failures allowed
3. Check implementation matches the design
4. Render a verdict:
   - **VERIFIED** -> proceed to Step 7
   - **SENT BACK** -> document issues, set plan status to "Sent Back"

If SENT BACK: invoke a fresh developer agent to fix issues, then a fresh architect agent to re-verify.

### Step 7: Documentation (Fresh Documenter)

Invoke the **documenter agent** (fall back to developer agent if no documenter exists) with:
- The plan file path
- The todo file path
- Instruction: "Identify what documentation needs updating based on this implementation. Update it. Report what was changed."

The documenter should:
1. Identify documentation affected by the implementation
2. Update it
3. Record all changes in the plan's Documentation section
4. Set plan status to "Documentation Complete"

If the documenter identifies source code changes needed, flag them -- the orchestrator decides how to handle.

### Step 8: Completion

The orchestrator performs this step directly:
1. Verify architect verdict is "VERIFIED"
2. Verify documentation step is complete
3. Update todo status to "Complete" and Last Updated date
4. Fill Results/Conclusions section
5. Set plan status to "Complete"
6. Move todo and plan to `completed/` directories

## Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the todo file. Check if a plan exists (Plans section).
2. **If no plan exists**, check Clarifications section:
   - Empty -> Step 2 (architect questions)
   - Answered, architect confirmed "Ready" -> Step 3 (architect plan)
3. **If a plan exists**, read its Status field:
   - `Draft` -> Step 3 (architect still working)
   - `Under Review` -> Step 4 (developer review)
   - `Concerns Raised` -> Clarification Loop (Step 4)
   - `Ready for Implementation` -> Step 5 (implementation)
   - `In Progress` -> Step 5 (implementation continues)
   - `Awaiting Verification` -> Step 6 (verification)
   - `Sent Back` -> Step 5 (developer fixes, read Architect Verification for what failed)
   - `Documentation Complete` -> Step 8 (completion)

## Filename Convention

Same as project-todos: lowercase, hyphens, no dates, 2-5 words. Examples: `fix-auth.md`, `add-export.md`, `update-visit-flow-validation.md`

Always use relative paths between todos and plans (`../todos/`, `../plans/`). Update BOTH files when linking.

## Reference Files

- **`references/todo-template.md`** -- Simplified todo template
- **`references/plan-template.md`** -- Simplified plan template

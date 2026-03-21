---
name: short-todo
version: 2.0.0
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

Every agent invocation is a **fresh** Agent call. Provide full context (todo path, plan path, agent memory file path, relevant instructions) each time. Do not attempt to resume agents across steps.

## Prerequisites

Before starting, check for project-specific resources:

1. **Agents** -- Check the project root's `.claude/agents/` for project-specific agents (architect, developer, documenter). Fall back to general agents at `~/.claude/agents/`. Project-specific agents take priority.
2. **Domain skill** -- Check for domain-specific skills that provide codebase context. Reference these when invoking agents.

---

## Agent Memory Files

Each plan has a companion memory directory where agents store their private working state. This keeps the plan file focused on design and prevents bloat from accumulating workflow artifacts.

### Structure

```
docs/plans/
├── feature-name-plan.md              # Design only — shared by all agents
└── feature-name-plan.memory/
    ├── architect.md                   # Architect's private notes
    ├── developer.md                   # Developer's private notes
    └── documenter.md                  # Documenter's private notes (if applicable)
```

The memory directory name is derived from the plan filename: `{plan-name}.memory/`.

### Key Rules

1. **Plan = shared design document.** All agents read it. Contains ONLY the design — what to build and why.
2. **Memory = private notes for the agent's own future self.** Only that agent and the orchestrator read it.
3. **Agents must NOT read each other's memory files.** The orchestrator mediates all cross-agent communication.
4. **Orchestrator relays cross-agent information via spawn prompts.** When the developer raises concerns, the orchestrator reads `developer.md`, extracts the concerns, and includes them in the architect's spawn prompt. The architect never opens `developer.md`.
5. **Memory format: curated summary** — not an append-only log. The agent rewrites the file each run, keeping only what's still relevant.
6. **Agents create the memory directory and their file** the first time they write. Use the Write tool — the directory is created automatically.

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

### Memory File Base Format

Each memory file follows this base format, plus agent-specific sections:

```markdown
# [Agent Role] — [Plan Name]

Last updated: YYYY-MM-DD
Current step: [what this agent is doing or last did]

## Key Context
[Curated summary — decisions, corrections, discoveries
that matter for the next fresh run of THIS agent]

## Mistakes to Avoid
[Things this agent got wrong and was corrected on]

## User Corrections
[Direct quotes/paraphrases of user overrides]

## [Agent-Specific Sections]
[See workflow steps for required sections per agent]
```

### Orchestrator Responsibilities for Memory Files

When spawning agents, the orchestrator MUST:

1. **Include the memory file path** in the spawn prompt: "Write your findings to `docs/plans/{plan-name}.memory/{agent}.md`"
2. **Relay cross-agent context** when needed: Read the relevant memory file and include extracted information in the spawn prompt — agents never read each other's files
3. **Check memory files for routing decisions**: After an agent completes, read its memory file to determine the next workflow step (verdict, concerns, evidence)

When resuming mid-workflow:

1. Read the plan status to determine which step is current
2. Read the relevant agent memory file(s) to understand the details (what was the concern, what evidence was collected, what was the verdict)
3. Include relevant context from memory files in the fresh agent's spawn prompt

---

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
- The architect's memory file path: `docs/plans/{plan-name}.memory/architect.md`
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
- The developer's memory file path: `docs/plans/{plan-name}.memory/developer.md`
- Instruction: "Review this plan for completeness, correctness, and implementability. Write your review findings (concerns, verdict) to your agent memory file at [path]. Raise concerns or approve."

The developer should:
1. Review the business rules and design
2. Check for gaps, ambiguities, and risks
3. Render a verdict: **Approved** or **Concerns Raised**
4. **Write all findings** (concerns, verdict) to the developer's agent memory file

**If concerns -> Clarification Loop:**
1. Present concerns to the user (read from `docs/plans/{plan-name}.memory/developer.md`)
2. User decides: clarify themselves, or have the architect address
3. If architect: invoke a **fresh architect agent** with the concerns (extracted from developer's memory by the orchestrator — the architect does NOT read `developer.md`)
4. Invoke a **fresh developer agent** to re-review
5. Repeat until approved

On approval: developer writes the **Implementation Contract** to the developer's memory file (In Scope, Out of Scope, Stop Conditions). Set plan status to "Ready for Implementation."

### Step 5: Implementation (Fresh Developer)

Invoke a **fresh developer agent** with:
- The plan file path
- The developer's memory file path: `docs/plans/{plan-name}.memory/developer.md` (contains the implementation contract from Step 4)
- Instruction: "Implement the approved plan following the implementation contract in your memory file. Write progress and evidence to your memory file."

The developer should:
1. Set plan status to "In Progress"
2. Work through the implementation contract (in memory file)
3. Run tests at milestones
4. **STOP and report** if out-of-scope tests fail
5. Write **Implementation Progress** and **Completion Evidence** to the developer's memory file, set plan status to "Awaiting Verification"
6. **Do NOT mark the todo as Complete**

### Step 6: Architect Verification (Fresh Architect)

Invoke a **fresh architect agent** with:
- The plan file path
- The todo file path
- The architect's memory file path: `docs/plans/{plan-name}.memory/architect.md`
- The developer's completion evidence (relayed by the orchestrator from `docs/plans/{plan-name}.memory/developer.md` — the architect does NOT read `developer.md` directly)
- Instruction: "Verify the completed implementation. The developer's completion evidence is included below. Independently run builds and tests. Do NOT trust the developer's reported results. Write your verification verdict to your agent memory file at [path]."

The architect should:
1. Independently run all builds and tests
2. Zero failures allowed
3. Check implementation matches the design
4. **Write verification verdict** to the architect's memory file
5. Render a verdict:
   - **VERIFIED** -> proceed to Step 7
   - **SENT BACK** -> write issues to architect's memory file, set plan status to "Sent Back"

If SENT BACK: invoke a fresh developer agent to fix issues (relay the architect's issues from memory file in the spawn prompt), then a fresh architect agent to re-verify.

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
2. **If no plan exists**, check Clarifications section:
   - Empty -> Step 2 (architect questions)
   - Answered, architect confirmed "Ready" -> Step 3 (architect plan)
3. **If a plan exists**, read its Status field:
   - `Draft` -> Step 3 (architect still working)
   - `Under Review` -> Step 4 (developer review)
   - `Concerns Raised` -> Step 4 clarification loop. Read the developer's memory file to extract concerns for the user.
   - `Ready for Implementation` -> Step 5 (implementation)
   - `In Progress` -> Step 5 (implementation continues). Read the developer's memory file to understand progress so far and include it in the spawn prompt.
   - `Awaiting Verification` -> Step 6 (verification). Read the developer's memory file to extract completion evidence for the architect's spawn prompt.
   - `Sent Back` -> Step 5 (developer fixes). Read the architect's memory file to determine what failed. Include the issues in the developer's spawn prompt.
   - `Documentation Complete` -> Step 8 (completion)
4. Invoke a fresh agent for that step, providing the todo path, plan path, and agent memory file path. Include relevant context from other agents' memory files in the spawn prompt (the fresh agent must NOT read other agents' memory files directly).

## Filename Convention

Same as project-todos: lowercase, hyphens, no dates, 2-5 words. Examples: `fix-auth.md`, `add-export.md`, `update-visit-flow-validation.md`

Always use relative paths between todos and plans (`../todos/`, `../plans/`). Update BOTH files when linking.

## Reference Files

- **`references/todo-template.md`** -- Simplified todo template
- **`references/plan-template.md`** -- Simplified plan template (design only — workflow state goes to agent memory files)

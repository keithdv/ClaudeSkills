---
name: project-todos
description: This skill should be used when the user asks to "create a todo", "add a plan", "plan this work", "track this work", "document this task", "complete a todo", "verify the implementation", "run architect verification", "hand off to the developer", "start the implementation", "update docs for this feature", "what's the next step", "what's the plan status", "resume the todo", "what's blocked", "pick up where we left off", "design this feature", or mentions managing project todos, plans, and multi-agent workflows. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration through the full design-review-implement-verify-document lifecycle.
---

# Project Todos, Plans, and Agent Workflow

Manage significant project work using structured markdown files and coordinate agent collaboration through the full design-review-implement-document lifecycle.

## Core Rule: The Orchestrator NEVER Modifies Source Code

**STOP before calling Edit, Write, or any file-modifying tool on a source file.** Source files include `.cs`, `.csproj`, `.sln`, `.json`, `.yaml`, `.yml`, `.xml`, `.props`, `.targets`, `.razor`, `.css`, `.js`, `.ts`, `.html`, and any other non-markdown file. If the action would change a source file, invoke an agent to do it instead.

**Decision gate — ask before every file modification:**
1. Is this file a todo or plan markdown file in `docs/todos/` or `docs/plans/`? → Orchestrator may edit it.
2. Is this file anything else? → **STOP. Invoke an agent.**

There are no exceptions. Not for "small" fixes, not for "obvious" one-liners, not for config tweaks, not for "it's faster if I just do it." Every source code change goes through an agent.

### What the Orchestrator Does

- Create and manage todo/plan files (create, update status fields, record user answers)
- Invoke agents with clear instructions and file references
- Present agent results and concerns to the user
- Make workflow decisions (which agent to invoke next, when to loop)
- Read any file to gather context (reading is always fine)

### What the Orchestrator Does NOT Do

- **NEVER** call Edit or Write on source files — invoke an agent
- **NEVER** call Bash to run sed, awk, or any command that modifies source files — invoke an agent
- **NEVER** rationalize a "quick fix" as being too small to need an agent — invoke an agent

Agents also write to plan files as part of their work — design content, implementation progress, completion evidence, verification results, and documentation records. Plan/todo files are shared between the orchestrator and agents. The hard boundary is source code: only agents touch it.

If a source code change is needed and no agent is currently active, invoke the appropriate agent to make it.

---

## When to Use This Workflow

Create a todo when:
- The user explicitly requests it ("create a todo", "track this work")
- Starting significant work that requires tracking across sessions
- Work involves multiple steps or spans multiple days
- The task needs design/planning before implementation

Do NOT create a todo for:
- Trivial tasks or quick fixes
- Work already tracked in session-level task lists
- Simple documentation updates

---

## Directory Structure

```
docs/
├── todos/
│   ├── {todo-name}.md           # Active todos
│   └── completed/
│       └── {todo-name}.md       # Completed todos
└── plans/
    ├── {plan-name}.md           # Active plans
    └── completed/
        └── {plan-name}.md       # Completed plans
```

All paths are relative to the project root.

---

## Agent Collaboration Workflow

This is the full lifecycle for significant work. Each step uses the appropriate agent.

### Prerequisites

Before starting the workflow, check for project-specific resources:

1. **Agents** — Check `.claude/agents/` for project-specific agents: architect, developer, specialized (e.g., UI, integration), and documentation. Use project-specific agents when found; fall back to general-purpose agents otherwise. Specialized implementation agents handle specific portions of Step 5 work (e.g., a UI agent handles page components and styling).
2. **Domain skill** — Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
3. **Design projects** — Check if the project has design/stub projects (e.g., `src/Design/`) used for compilation verification. The architect agent should use these to verify scope claims.
4. **Documentation samples** — Check if the project has documentation sample projects. The documentation agent should use these when updating docs.

### Step 1: Create Todo

1. Gather information from the user (title, priority, problem, solution)
2. Create the todo file in `docs/todos/` using the todo template
3. Set status to "In Progress"

### Step 2: Architect Review & Plan Creation

Invoke the **architect agent** with:
- The todo file path
- Any domain skill references found in prerequisites
- Instruction: "Review this todo, ask clarifying questions if needed, then create an implementation plan"

The architect agent should:
1. Read the todo to understand the problem and solution
2. Explore the codebase to understand current architecture
3. Ask the user clarifying questions about requirements or approach
4. **Extract business rules as testable assertions** — Before designing anything, analyze the legacy code, user requirements, and codebase to produce a numbered list of crisp, unambiguous business rules. Format: `WHEN [conditions], THEN [property/method] RETURNS [value]`. These go in the plan's "Business Rules (Testable Assertions)" section. This is NOT optional — it is the first section completed.
5. **Create concrete test scenarios** — For each business rule, create at least one scenario with specific inputs and expected result. These go in the "Test Scenarios" table. The architect must show the evaluation for each scenario. These scenarios become the acceptance tests.
6. Create the rest of the plan in `docs/plans/` using the plan template. **Design against the assertions** — every design decision must trace to one or more business rule assertions.
7. **If design projects exist**: verify scope claims by writing compilable code. Leave failing code as acceptance criteria for features that need implementation.
8. **Identify fresh agent phases**: Analyze the implementation steps and determine which phases would benefit from a fresh agent with a clean context window. Document this in the plan's "Agent Phasing" section. Consider:
   - Phases that are independent and don't need prior implementation context
   - Phases that touch more than ~10 files or involve substantial code generation
   - Phases that span different domains (e.g., backend vs. frontend vs. tests)
   - Phases that could run in parallel
9. Link the plan to the todo (update both files)
10. Set plan status to "Draft (Architect)"
11. Hand off to developer review

### Step 3: Developer Review

Invoke the **developer agent** with:
- The plan file path
- The todo file path
- Instruction: "Review this plan. First: for EACH business rule assertion in the 'Business Rules' section, trace through the proposed implementation and verify the expected result matches. Fill in the Assertion Trace Verification table. Each Implementation Path entry must cite a specific method name and condition expression. Entries that say 'handled correctly' or 'matches design' without specifics are insufficient — send back for detail. Then review for completeness, correctness, and implementability. Raise concerns or approve."

The developer agent should:
1. **Verify business rules first** — For EACH numbered assertion in the plan's "Business Rules" section, trace through the proposed implementation (the specific method, condition, or code path) and verify the expected result. Fill in the "Assertion Trace Verification" table in the Developer Review section. Each Implementation Path entry must cite a specific method name and the condition expression from the design. Entries without specifics (e.g., "handled in implementation", "matches design") are insufficient — reject and request detail from the architect. **This is the primary review task — do it before anything else.**
2. **Verify test scenarios** — For each test scenario in the plan, mentally execute it against the proposed implementation and confirm the expected result matches.
3. If any assertion trace produces a result that contradicts the business rule, this is a **blocking concern** — the plan has a logic error.
4. Investigate the codebase to verify plan claims
5. **If the architect provided design project verification**: confirm the evidence exists and makes sense
6. **If the architect did NOT provide design project verification** (and design projects exist): reject the plan back to the architect
7. Check for gaps, ambiguities, edge cases, and risks
8. Review the Agent Phasing section — confirm the phasing is practical and the fresh/resume decisions make sense for the implementation work
9. Render a verdict: **Concerns Raised** or **Approved**

### Step 4: Clarification Loop

If the developer raises concerns:
1. Present concerns to the user
2. Ask the user: "Would you like to clarify these yourself, or should the architect agent address them?"
3. Based on user's choice:
   - **User clarifies**: Orchestrator updates the plan with the user's answers, then returns to Step 3
   - **Architect clarifies**: Invoke architect agent with the concerns, then return to Step 3
4. Repeat until the developer approves

When the developer approves:
- Developer creates an **Implementation Contract** in the plan (scope, out-of-scope, verification gates)
- If design projects have failing acceptance criteria code, list them in the contract
- Set plan status to "Ready for Implementation"

### Step 5: Implementation

**STOP — Do not write code here. Invoke an agent for all implementation work.**

Invoke the **developer agent** for implementation with:
- The plan file path (with implementation contract)
- Instruction: "Implement the approved plan following the implementation contract"

**Specialized agent routing**: If the implementation includes work that matches a specialized agent's scope (identified in Prerequisites step 1), split the implementation:
- **Developer agent**: Domain models, repositories, services, tests, backend logic
- **Specialized UI agent** (if found): Pages, components, templates, CSS, layout
- **Other specialized agents**: Route according to their declared file scope and capabilities

Coordinate by having the developer agent complete backend work first (or in parallel if independent), then invoke the specialized agent for its portion with the same plan file.

**Fresh agent phasing**: Follow the plan's "Agent Phasing" section (created by the architect in Step 2). For each phase marked "Fresh Agent? Yes", start a fresh Agent invocation (the default behavior) so the phase begins with a clean context window focused on its specific deliverable. For phases marked "Fresh Agent? No", resume the prior phase's agent (using the `resume` parameter with its agent ID) to preserve accumulated context. When starting a fresh invocation for a phase, provide:
- The plan file path (so the agent can read scope and prior progress)
- The specific phase description and deliverables
- Any outputs from prior phases that this phase depends on

The developer agent (or specialized agents) should:
1. Work through the implementation contract checklist
2. Run tests at each verification gate
3. **STOP and report** if out-of-scope tests fail or architectural contradictions are discovered
4. Collect evidence (test output, generated code samples)
5. **When finished**: Write "Implementation Progress" and "Completion Evidence" sections in the plan, set plan status to "Awaiting Verification", then **STOP**. Do NOT mark the todo or plan as Complete.

### Step 6: Architect Verification (Mandatory)

**The developer may NOT mark work as Complete. A different agent must verify.**

Invoke the **architect agent** with:
- The plan file path
- The todo file path
- Instruction: "Perform post-implementation verification of the completed work. The developer reports it is done. Independently verify."

The architect agent should:
1. Read the plan's "Completion Evidence" section to understand what the developer claims
2. **Independently run all builds and tests** — do NOT trust the developer's reported results
3. **Check EVERY test result** — zero failures allowed. If any test fails, the work is NOT complete, even if the developer classified failures as "pre-existing"
4. Verify the implementation matches the original design (compare generated code against the plan's expected patterns)
5. If design projects exist, verify they compile
6. Render a verdict:
   - **VERIFIED**: All builds pass, all tests pass, implementation matches design → proceed to Step 7
   - **SENT BACK**: Failures found → document issues in "Architect Verification" section, set plan status to "Sent Back", report to orchestrator for developer to fix

**Critical rule**: Any test failure — even one the developer classified as "pre-existing" — must be reported. Only the user can decide whether a failure is acceptable.

### Step 7: Documentation

Invoke the **documentation agent** (if one exists) with:
- The plan file path
- The todo file path
- Instruction: "Review the completed implementation and update all affected documentation. See the Documentation section of the plan for expected deliverables."

If no documentation agent exists, the developer agent handles documentation.

The documentation agent should:
1. Read the plan to understand what was implemented
2. Review the plan's Documentation section for expected deliverables
3. Update affected files:
   - API or architecture documentation
   - Domain skill reference files (in `.claude/skills/`)
   - Documentation samples (if the project has sample projects)
   - README or getting-started guides (if affected)
4. Record work in the plan's Documentation section — list each file created or updated
5. Set plan status to "Documentation Complete"

**Quality criteria**: Documentation must match implemented behavior (not the plan's original design). New patterns need at least one example. Changed behavior notes what changed and why.

See `references/documentation-step-guide.md` for detailed guidance.

### Step 8: Completion

**Only after the architect has VERIFIED the work in Step 6 and documentation is complete (or N/A) from Step 7.**

The orchestrator performs this step directly (no agent invocation needed).

1. Verify architect verification verdict is "VERIFIED"
2. Verify documentation step is complete (plan status is "Documentation Complete") or was marked N/A
3. Update todo status to "Complete" and Last Updated date
4. Fill in the Results/Conclusions section
5. Move todo and associated plans to `completed/` directories
6. Update plan statuses to "Complete"

---

## Creating a Todo

### Filename Convention

- Convert title to lowercase
- Replace spaces with hyphens
- Remove special characters
- Keep concise (2-5 words)
- **No dates** in filename

Examples: `fix-authentication.md`, `add-dark-mode.md`, `refactor-api-layer.md`

### Write the Todo File

Use the template from `references/todo-template.md`. Fill in:

- **Title**: The work title
- **Status**: "In Progress" (default)
- **Priority**: High, Medium, or Low
- **Created**: Today's date (YYYY-MM-DD)
- **Last Updated**: Same as Created
- **Problem**: The problem statement
- **Solution**: High-level approach
- **Plans**: Leave empty (populated when plans are created)
- **Tasks**: Initial task list if known
- **Progress Log**: Empty
- **Results / Conclusions**: Empty

File location: `docs/todos/{filename}.md`

---

## Creating a Plan

### Write the Plan File

Use the same filename convention as todos (lowercase, hyphens, concise, no dates). Be descriptive of the plan's purpose. Examples: `authentication-fix-design.md`, `dark-mode-implementation.md`

Use the template from `references/plan-template.md`. Fill in:

- **Title**: Descriptive plan title
- **Date**: Today's date
- **Related Todo**: Relative link to parent todo
- **Status**: "Draft" (default)
- **Last Updated**: Same as Date
- Core sections: Overview, Approach, Design, Implementation Steps, Acceptance Criteria, Dependencies, Risks

For valid plan status values, see `references/plan-template.md`.

### Plan Workflow Sections

Plans that go through the agent collaboration workflow include additional sections for architectural verification, agent phasing, developer review, implementation contract, progress tracking, completion evidence, documentation, and architect verification.

These sections are defined in `references/plan-template.md`. When creating a plan for the full agent workflow, use the complete template. The key sections and their purposes:

- **Architectural Verification** -- Architect's scope analysis and design project evidence
- **Agent Phasing** -- Which implementation phases benefit from fresh vs resumed agents
- **Developer Review** -- Developer's verdict on the plan
- **Implementation Contract** -- Approved scope, verification gates, stop conditions
- **Implementation Progress** -- Milestone tracking during implementation
- **Completion Evidence** -- Developer's evidence that work is done
- **Documentation** -- Expected and completed documentation deliverables
- **Architect Verification** -- Independent verification of completed work

### Link Plan to Todo

**Critical**: Update BOTH files:

1. In the plan: `**Related Todo:** [Title](../todos/{todo-filename}.md)`
2. In the todo: Add plan link to "Plans" section: `- [Plan Title](../plans/{plan-filename}.md)`
3. Update todo's Last Updated date

Always use relative paths (`../todos/`, `../plans/`).

---

## Completing Todos

1. Update todo status to "Complete" and Last Updated date
2. Fill Results/Conclusions section
3. Find associated plans: search `docs/plans/` for links to this todo
4. Move todo to `docs/todos/completed/`
5. Move each associated plan to `docs/plans/completed/`
6. Update each plan's status to "Complete" and Last Updated date

---

## Common Workflows

### Todo Only

1. Create todo file with template
2. Inform user of file location

### Todo with Full Agent Workflow

1. Create todo (Step 1)
2. Invoke architect agent (Step 2)
3. Developer reviews (Step 3)
4. Clarification loop if needed (Step 4)
5. Implementation (Step 5) — route to developer and/or specialized agents
6. Architect verification (Step 6) — developer may NOT self-certify
7. Documentation (Step 7) — documentation agent updates docs, or developer if no documentation agent
8. Completion (Step 8) — only after architect verification passes

### Adding a Plan to Existing Todo

1. Read existing todo for context
2. Write plan file with template
3. Link plan to todo (both files)
4. Continue with Step 3 (developer review)

### Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the plan file and check its **Status** field
2. Map the status to the corresponding workflow step:
   - `Draft (Architect)` → Step 2 (architect still working)
   - `Under Review (Developer)` → Step 3 (developer review)
   - `Concerns Raised` → Step 4 (clarification loop)
   - `Ready for Implementation` → Step 5 (implementation)
   - `In Progress` → Step 5 (implementation continues)
   - `Awaiting Verification` → Step 6 (architect verification)
   - `Sent Back` → Step 5 (developer fixes issues from verification)
   - `Documentation Complete` → Step 8 (completion)
3. Resume from that step, providing the plan and todo file paths to the appropriate agent

---

## Best Practices

1. **Status accuracy**: Update status fields promptly as workflow progresses.
2. **Progress logging**: Update progress log as work happens, not just at the end.
3. **Link maintenance**: Always update both files when creating links.
4. **Multiple plans OK**: A todo can have multiple plans. One todo per file.
5. **Last Updated**: Always update when modifying any content.
6. **Design project verification**: When the project has design/stub projects, the compiler is the source of truth for scope claims. Grepping code is secondary.
7. **Agent phasing**: The architect identifies phases benefiting from fresh agents during planning. The orchestrator follows this phasing during implementation, invoking fresh agent instances for each identified phase.
8. **Documentation deliverables**: Identify expected documentation deliverables during planning (Step 2) or implementation contract (Step 4), not as an afterthought.
9. **Assertion-trace workflow**: The assertion-trace workflow in Steps 2-3 is the primary defense against logic errors. Do not skip or abbreviate it.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`
- Documentation step guide: `references/documentation-step-guide.md`

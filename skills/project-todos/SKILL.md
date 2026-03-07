---
name: project-todos
description: This skill should be used when the user asks to "create a todo", "add a plan", "plan this work", "track this work", "document this task", "complete a todo", "verify the implementation", "run architect verification", "hand off to the developer", "start the implementation", "update docs for this feature", "what's the next step", "what's the plan status", "resume the todo", "what's blocked", "pick up where we left off", "design this feature", "check business requirements", "review requirements", "review against requirements", "check for requirement conflicts", or mentions managing project todos, plans, and multi-agent workflows. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration through the full design-review-implement-verify-document lifecycle.
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

1. **Agents** — Check `.claude/agents/` for project-specific agents: architect, developer, specialized (e.g., UI, integration), documentation, **business-requirements-reviewer**, and **business-requirements-documenter**. Also check `~/.claude/agents/` for general agents. **Project-specific agents always take priority over user-level agents of the same role.** Fall back to general-purpose agents only when no project-specific agent exists for that role. Specialized implementation agents handle specific portions of Step 6 work (e.g., a UI agent handles page components and styling).
2. **Business requirements** — Check the project's CLAUDE.md for where business requirements documentation lives (business rules, user stories, workflows, data dictionaries). **If CLAUDE.md does not clearly indicate where business requirements are documented, STOP and ask the user before proceeding.** This information is required for Step 2.
3. **Domain skill** — Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
4. **Design projects** — Check if the project has design/stub projects (e.g., `src/Design/`) used for compilation verification. The architect agent should use these to verify scope claims.
5. **Documentation samples** — Check if the project has documentation sample projects. The documentation agent should use these when updating docs.

### Step 1: Create Todo

1. Gather information from the user (title, priority, problem, solution)
2. Create the todo file in `docs/todos/` using the todo template
3. Set status to "In Progress"

**IMPORTANT: Do NOT create the plan file.** The architect creates the plan in Step 3. Proceed directly to Step 2 (requirements review) after creating the todo.

### Step 2: Business Requirements Review

**Purpose:** Compare the proposed work against the project's EXISTING DOCUMENTED business requirements (business rules, user stories, workflows, data definitions already in the codebase) before design begins. This is NOT the same as gathering the user's problem and solution in Step 1 — this step searches the project's requirements documentation for contradictions with the proposed work. This step catches contradictions that would otherwise become bugs — especially implicit dependencies where changing one behavior breaks assumptions in other parts of the system.

Invoke the **business-requirements-reviewer** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The todo file path
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Review this todo against the project's existing business requirements. Write your findings into the todo's Requirements Review section. VETO if contradictions are found."

The reviewer agent should:
1. Read the todo to understand the problem and proposed solution
2. Discover business requirements documentation paths from CLAUDE.md. **If paths are unclear, STOP and return questions for the user — do NOT guess.**
3. Search requirements docs for rules, user stories, workflows, and data definitions related to the todo's scope
4. Identify relevant requirements, gaps, and contradictions
5. Pay special attention to **implicit dependencies** — changes that technically work but alter behavior governed by other business rules (e.g., changing when data is loaded affects when it's considered "part of" a record)
6. Write findings into the todo's **Requirements Review** section (Relevant Requirements Found, Gaps, Contradictions, Recommendations for Architect)
7. Set the verdict in the todo's Requirements Review section:
   - **APPROVED** — No contradictions. Proceed to Step 3 (architect creates the plan).
   - **VETOED** — Contradictions found. Must be resolved before design.

**The reviewer does NOT create the plan file.** The plan is created by the architect in Step 3.

**If VETOED:**
1. Present the specific contradictions to the product owner (the user), including exact requirement references, file paths, and why they conflict with the proposed work
2. **STOP.** Do not proceed with the workflow. The product owner decides how to resolve the contradiction — whether to modify the approach, update outdated requirements, override, or take a different path entirely
3. After the product owner provides direction, follow it. If requirements need updating, invoke the appropriate agent (developer agent for `.cs` files, documenter agent for markdown). Then re-invoke the reviewer to confirm the contradiction is resolved
4. Repeat until APPROVED

### Step 3: Architect Plan Creation & Design

Invoke the **architect agent** with:
- The todo file path (with Requirements Review section populated by the reviewer in Step 2)
- Any domain skill references found in prerequisites
- Instruction: "Create the plan file for this todo. Read the todo's Requirements Review section first — incorporate those findings into the plan's Business Requirements Context. Then design the implementation, building on the documented requirements. Create business rules as testable assertions that trace to the existing requirements where they exist."

The architect agent should:
1. Read the todo to understand the problem, solution, and **the Requirements Review section** written by the reviewer
2. **Create the plan file** in `docs/plans/` using the plan template. Populate the Business Requirements Context section from the reviewer's findings in the todo. Link the plan to the todo (update both files).
3. The architect MUST NOT invent business rules that contradict the documented requirements identified by the reviewer.
4. Explore the codebase to understand current architecture
5. Ask the user clarifying questions about requirements or approach
6. **Extract business rules as testable assertions** — Before designing anything, analyze the legacy code, user requirements, and codebase to produce a numbered list of crisp, unambiguous business rules. Format: `WHEN [conditions], THEN [property/method] RETURNS [value]`. **Trace each assertion to an existing documented requirement where one exists.** New assertions (for gaps identified by the reviewer) must be clearly marked as new. These go in the plan's "Business Rules (Testable Assertions)" section. This is NOT optional — it is the first section completed.
7. **Create concrete test scenarios** — For each business rule, create at least one scenario with specific inputs and expected result. These go in the "Test Scenarios" table. The architect must show the evaluation for each scenario. These scenarios become the acceptance tests.
8. Fill in the remaining plan sections (Approach, Design, Implementation Steps, etc.). **Design against the assertions** — every design decision must trace to one or more business rule assertions.
9. **If design projects exist**: verify scope claims by writing compilable code. Leave failing code as acceptance criteria for features that need implementation.
10. **Identify fresh agent phases**: Analyze the implementation steps and determine which phases would benefit from a fresh agent with a clean context window. Document this in the plan's "Agent Phasing" section. Consider:
    - Phases that are independent and don't need prior implementation context
    - Phases that touch more than ~10 files or involve substantial code generation
    - Phases that span different domains (e.g., backend vs. frontend vs. tests)
    - Phases that could run in parallel
11. Update plan status to "Draft (Architect)"
12. Hand off to developer review

### Step 4: Developer Review

Invoke the **developer agent** with:
- The plan file path
- The todo file path
- Instruction: "Review this plan. First: for EACH business rule assertion in the 'Business Rules' section, trace through the proposed implementation and verify the expected result matches. Fill in the Assertion Trace Verification table. Each Implementation Path entry must cite a specific method name and condition expression. Entries that say 'handled correctly' or 'matches design' without specifics are insufficient — send back for detail. Then review for completeness, correctness, and implementability. Raise concerns or approve."

The developer agent should:
1. **Verify business rules first** — For EACH numbered assertion in the plan's "Business Rules" section, trace through the proposed implementation (the specific method, condition, or code path) and verify the expected result. Fill in the "Assertion Trace Verification" table in the Developer Review section. Each Implementation Path entry must cite a specific method name and the condition expression from the design. Entries without specifics (e.g., "handled in implementation", "matches design") are insufficient — reject and request detail from the architect. **This is the primary review task — do it before anything else.**
2. **Verify test scenarios** — For each test scenario in the plan, mentally execute it against the proposed implementation and confirm the expected result matches.
3. If any assertion trace produces a result that contradicts the business rule, this is a **blocking concern** — the plan has a logic error.
4. **Check against Requirements Context** — Verify the design respects the requirements identified in the Business Requirements Context section. Flag if the design introduced approaches that contradict documented requirements.
5. Investigate the codebase to verify plan claims
6. **If the architect provided design project verification**: confirm the evidence exists and makes sense
7. **If the architect did NOT provide design project verification** (and design projects exist): reject the plan back to the architect
8. Check for gaps, ambiguities, edge cases, and risks
9. Review the Agent Phasing section — confirm the phasing is practical and the fresh/resume decisions make sense for the implementation work
10. Render a verdict: **Concerns Raised** or **Approved**

### Step 5: Clarification Loop

If the developer raises concerns:
1. Present concerns to the user
2. Ask the user: "Would you like to clarify these yourself, or should the architect agent address them?"
3. Based on user's choice:
   - **User clarifies**: Orchestrator updates the plan with the user's answers, then returns to Step 4
   - **Architect clarifies**: Invoke architect agent with the concerns, then return to Step 4
4. Repeat until the developer approves

When the developer approves:
- Developer creates an **Implementation Contract** in the plan (scope, out-of-scope, verification gates)
- If design projects have failing acceptance criteria code, list them in the contract
- Set plan status to "Ready for Implementation"

### Step 6: Implementation

**STOP — Do not write code here. Invoke an agent for all implementation work.**

Invoke the **developer agent** for implementation with:
- The plan file path (with implementation contract)
- Instruction: "Implement the approved plan following the implementation contract"

**Specialized agent routing**: If the implementation includes work that matches a specialized agent's scope (identified in Prerequisites step 1), split the implementation:
- **Developer agent**: Domain models, repositories, services, tests, backend logic
- **Specialized UI agent** (if found): Pages, components, templates, CSS, layout
- **Other specialized agents**: Route according to their declared file scope and capabilities

Coordinate by having the developer agent complete backend work first (or in parallel if independent), then invoke the specialized agent for its portion with the same plan file.

**Fresh agent phasing**: Follow the plan's "Agent Phasing" section (created by the architect in Step 3). For each phase marked "Fresh Agent? Yes", start a fresh Agent invocation (the default behavior) so the phase begins with a clean context window focused on its specific deliverable. For phases marked "Fresh Agent? No", resume the prior phase's agent (using the `resume` parameter with its agent ID) to preserve accumulated context. When starting a fresh invocation for a phase, provide:
- The plan file path (so the agent can read scope and prior progress)
- The specific phase description and deliverables
- Any outputs from prior phases that this phase depends on

The developer agent (or specialized agents) should:
1. Work through the implementation contract checklist
2. Run tests at each verification gate
3. **STOP and report** if out-of-scope tests fail or architectural contradictions are discovered
4. Collect evidence (test output, generated code samples)
5. **When finished**: Write "Implementation Progress" and "Completion Evidence" sections in the plan, set plan status to "Awaiting Verification", then **STOP**. Do NOT mark the todo or plan as Complete.

### Step 7: Verification (Architect + Requirements)

**The developer may NOT mark work as Complete. Verification is mandatory.**

This step has two parts: technical verification and requirements verification. Both must pass.

#### Part A: Architect Verification

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
   - **VERIFIED**: All builds pass, all tests pass, implementation matches design → proceed to Part B
   - **SENT BACK**: Failures found → document issues in "Architect Verification" section, set plan status to "Sent Back", report to orchestrator for developer to fix

**Critical rule**: Any test failure — even one the developer classified as "pre-existing" — must be reported. Only the user can decide whether a failure is acceptable.

#### Part B: Requirements Verification

**Only if Part A passes (VERIFIED).**

Invoke the **business-requirements-reviewer** agent (same agent resolution as Step 2 — project-specific first, user-level fallback) with:
- The plan file path
- Instruction: "Perform post-implementation requirements verification. Confirm the implementation satisfies the documented business requirements identified in the Business Requirements Context section. Check for unintended side effects on other business rules."

The reviewer agent should:
1. Read the plan's Business Requirements Context, Completion Evidence, and Implementation Progress sections
2. For each requirement identified as relevant, trace through the implementation to verify compliance
3. Check for unintended side effects — changes that technically work but alter behavior governed by other business rules
4. Fill in the Requirements Verification section of the plan
5. Render a verdict:
   - **REQUIREMENTS SATISFIED**: Implementation respects all documented requirements → proceed to Step 8
   - **REQUIREMENTS VIOLATION**: Implementation violates documented requirements → document violations, set plan status to "Sent Back", report to orchestrator

### Step 8: Requirements Documentation

**Purpose:** Update the project's business requirements documentation to reflect what was actually implemented — new rules, changed rules, resolved gaps. This closes the loop: the reviewer identified the requirements landscape in Step 2, and now the documentation sources are updated to stay current.

#### Part A: Markdown Requirements Documentation

Invoke the **business-requirements-documenter** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The plan file path
- The todo file path
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Update markdown-based business requirements documentation to reflect the completed implementation. Update docs/ and skill behavioral contract reference files. Identify any .cs file changes needed (Design projects, code comments, samples) and report them as Developer Deliverables in the plan's Documentation section — do NOT modify .cs files."

The documenter agent should:
1. Read the plan's Business Requirements Context, Business Rules (Testable Assertions), Completion Evidence, and Implementation Progress sections
2. Compare: identify new requirements (marked NEW in the assertions), changed requirements, and gaps that were filled
3. Update **markdown** requirements sources:
   - User-facing documentation (`docs/`) — new rules, changed rules, filled gaps, affected workflows
   - Skill behavioral contract reference files — reference files encoding what the framework does (e.g., `entities.md`, `collections.md`, `validation.md`, `properties.md`)
4. Identify `.cs` deliverables — Design project tests/examples, framework source code comments, or documentation samples (`src/samples/`) that need creating or updating — and list them in the plan's Documentation section as **Developer Deliverables** with specific descriptions of what each file should contain
5. Record all markdown work in the plan's Documentation section
6. Set plan status to "Requirements Documented"

**Critical rule**: Document what was *implemented*, not what was *planned*. If the implementation diverged from the plan, the documentation must match the implementation.

#### Part B: Source Code Requirements Documentation

**Only if the documenter identified Developer Deliverables in Part A.**

Invoke the **developer agent** with:
- The plan file path
- Instruction: "Complete the .cs requirements documentation deliverables listed in the Documentation section's Developer Deliverables. This includes Design project tests/examples, framework code comments, and/or documentation samples. Build and test after changes."

The developer agent should:
1. Read the Documentation section's Developer Deliverables list
2. Make the identified `.cs` changes (Design.Tests, Design.Domain, framework code comments, `src/samples/`)
3. Run `dotnet build` and `dotnet test` to verify changes compile and pass
4. Mark each Developer Deliverable as completed in the Documentation section

#### Part C: General Documentation (if applicable)

If the plan identifies non-requirements documentation deliverables (API docs, README changes, migration guides, getting-started updates, instructional skill references like `testing.md` or `pitfalls.md`), invoke the **documentation agent** (or developer agent if no documentation agent exists) with:
- The plan file path
- The todo file path
- Instruction: "Update non-requirements documentation affected by this implementation. See the Documentation section of the plan for expected deliverables."

**Skill file boundary:**
- **Part A** (documenter): Skill reference files encoding **behavioral contracts** — what the framework does, how state properties behave, what factory operations produce, entity lifecycle rules
- **Part C** (docs agent): Skill reference files that are **instructional** — how to test, common pitfalls, integration guides, tutorials

After all applicable parts complete, set plan status to "Documentation Complete."

See `references/documentation-step-guide.md` for detailed guidance.

### Step 9: Completion

**Only after verification has passed (Step 7, both parts) and documentation is complete (or N/A) from Step 8.**

The orchestrator performs this step directly (no agent invocation needed).

1. Verify architect verification verdict is "VERIFIED"
2. Verify requirements verification verdict is "REQUIREMENTS SATISFIED"
3. Verify documentation step is complete (plan status is "Documentation Complete") or was marked N/A
4. Update todo status to "Complete" and Last Updated date
5. Fill in the Results/Conclusions section
6. Move todo and associated plans to `completed/` directories
7. Update plan statuses to "Complete"

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

> **Agent Workflow Note:** In the full Agent Collaboration Workflow (Steps 1-9), the architect agent creates the plan file in Step 3. Neither the orchestrator nor the reviewer creates the plan. This section is only for standalone plan creation outside the agent workflow.

### Write the Plan File

Use the same filename convention as todos (lowercase, hyphens, concise, no dates). Be descriptive of the plan's purpose. Examples: `authentication-fix-design.md`, `dark-mode-implementation.md`

Use the template from `references/plan-template.md`. Fill in:

- **Title**: Descriptive plan title
- **Date**: Today's date
- **Related Todo**: Relative link to parent todo
- **Status**: "Draft" for standalone plans; "Draft (Architect)" when created by the architect in the agent workflow (Step 3)
- **Last Updated**: Same as Date
- Core sections: Overview, Business Requirements Context (populated by architect from todo's Requirements Review), Business Rules, Approach, Design, Implementation Steps, Acceptance Criteria, Dependencies, Risks

For valid plan status values, see `references/plan-template.md`.

### Plan Workflow Sections

Plans that go through the agent collaboration workflow include additional sections for business requirements context, architectural verification, agent phasing, developer review, implementation contract, progress tracking, completion evidence, documentation, architect verification, and requirements verification.

These sections are defined in `references/plan-template.md`. When creating a plan for the full agent workflow, use the complete template. The key sections and their purposes:

- **Business Requirements Context** -- Architect populates from the todo's Requirements Review (filled in Step 3)
- **Architectural Verification** -- Architect's scope analysis and design project evidence
- **Agent Phasing** -- Which implementation phases benefit from fresh vs resumed agents
- **Developer Review** -- Developer's verdict on the plan
- **Implementation Contract** -- Approved scope, verification gates, stop conditions
- **Implementation Progress** -- Milestone tracking during implementation
- **Completion Evidence** -- Developer's evidence that work is done
- **Documentation** -- Expected and completed documentation deliverables
- **Architect Verification** -- Independent verification of completed work
- **Requirements Verification** -- Reviewer's verification that implementation satisfies documented requirements

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
2. Business requirements review (Step 2) — reviewer writes findings into todo, checks for contradictions
3. Architect creates plan and designs (Step 3) — architect creates plan file, incorporates reviewer findings, designs implementation
4. Developer reviews (Step 4)
5. Clarification loop if needed (Step 5)
6. Implementation (Step 6) — route to developer and/or specialized agents
7. Verification (Step 7) — architect verifies builds/tests, then reviewer verifies requirements compliance
8. Documentation (Step 8) — documenter updates markdown requirements, developer handles .cs deliverables, docs agent handles general docs
9. Completion (Step 9) — only after both verifications pass

### Adding a Plan to Existing Todo

1. Read existing todo for context
2. Invoke business-requirements-reviewer to write findings into todo's Requirements Review section (Step 2)
3. Invoke architect to create plan and design (Step 3)

### Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the todo file. Check if a plan file exists (look in the todo's Plans section for a link).
2. **If no plan exists**, check the todo's **Requirements Review** section:
   - No review yet (Verdict: Pending) → Step 2 (run the reviewer)
   - Verdict: APPROVED → Step 3 (architect creates the plan)
   - Verdict: VETOED → Step 2 (resolve contradictions with user)
3. **If a plan exists**, read it and check its **Status** field:
   - `Draft (Architect)` → Step 3 (architect still working)
   - `Under Review (Developer)` → Step 4 (developer review)
   - `Concerns Raised` → Step 5 (clarification loop)
   - `Ready for Implementation` → Step 6 (implementation)
   - `In Progress` → Step 6 (implementation continues)
   - `Awaiting Verification` → Step 7 (verification)
   - `Sent Back` → Step 6 (developer fixes issues). Read both the Architect Verification and Requirements Verification sections of the plan to determine which verification failed and what the developer needs to fix.
   - `Requirements Documented` → Check Documentation section for pending Developer Deliverables (Part B). If none, proceed to Part C (general documentation, if applicable) or Step 9 (completion)
   - `Documentation Complete` → Step 9 (completion)
4. Resume from that step, providing the todo and plan file paths (if plan exists) to the appropriate agent

---

## Best Practices

1. **Status accuracy**: Update status fields promptly as workflow progresses.
2. **Progress logging**: Update progress log as work happens, not just at the end.
3. **Link maintenance**: Always update both files when creating links.
4. **Multiple plans OK**: A todo can have multiple plans. One todo per file.
5. **Last Updated**: Always update when modifying any content.
6. **Requirements review first**: Never skip the business requirements review (Step 2). The most expensive bugs come from contradicting existing requirements — especially implicit dependencies.
7. **Design project verification**: When the project has design/stub projects, the compiler is the source of truth for scope claims. Grepping code is secondary.
8. **Agent phasing**: The architect identifies phases benefiting from fresh agents during planning. The orchestrator follows this phasing during implementation, invoking fresh agent instances for each identified phase.
9. **Documentation deliverables**: Identify expected documentation deliverables during planning (Step 3) or implementation contract (Step 5), not as an afterthought.
10. **Assertion-trace workflow**: The assertion-trace workflow in Steps 3-4 is the primary defense against logic errors. Do not skip or abbreviate it.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`
- Documentation step guide: `references/documentation-step-guide.md`

---
name: project-todos
version: 3.0.0
description: This skill should be used when the user asks to "create a todo", "add a plan", "plan this work", "track this work", "document this task", "complete a todo", "verify the implementation", "run architect verification", "hand off to the developer", "start the implementation", "update docs for this feature", "what's the next step", "what's the plan status", "resume the todo", "what's blocked", "pick up where we left off", "design this feature", "check business requirements", "review requirements", "review against requirements", "check for requirement conflicts", or mentions managing project todos, plans, and multi-agent workflows. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration through the full design-review-implement-verify-document lifecycle.
---

# Project Todos, Plans, and Agent Workflow

Manage significant project work using structured markdown files and coordinate agent collaboration through the full design-review-implement-document lifecycle.

## Core Rule: The Orchestrator NEVER Modifies Source Code

**STOP before calling Edit, Write, or any file-modifying tool on a source file.** Source files include `.cs`, `.csproj`, `.sln`, `.json`, `.yaml`, `.yml`, `.xml`, `.props`, `.targets`, `.razor`, `.css`, `.js`, `.ts`, `.html`, and any other non-markdown file. If the action would change a source file, invoke an agent to do it instead.

**Decision gate — ask before every file modification:**
1. Is this file a todo or plan markdown file in `docs/todos/` or `docs/plans/`? -> Orchestrator may edit it.
2. Is this file anything else? -> **STOP. Invoke an agent.**

There are no exceptions. Not for "small" fixes, not for "obvious" one-liners, not for config tweaks, not for "it's faster if I just do it." Every source code change goes through an agent.

### What the Orchestrator Does

- Create and manage todo/plan files (create, update status fields, record user answers)
- **Analyze the codebase with the user** — the orchestrator is the user's design partner, not just a file-fetcher
- Invoke agents with clear instructions and file references
- Present agent results and concerns to the user
- Make workflow decisions (which agent to invoke next, when to loop)
- Read workflow files (todos, plans, agent definitions) to make routing decisions

### What the Orchestrator Does NOT Do

- **NEVER** call Edit or Write on source files — invoke an agent
- **NEVER** call Bash to run sed, awk, or any command that modifies source files — invoke an agent
- **NEVER** rationalize a "quick fix" as being too small to need an agent — invoke an agent

---

Agents write design content to plan files and workflow state to their own agent memory files (see Agent Memory Files section below). Plan files are shared and contain only the design. Agent memory files are private to each agent and the orchestrator. The hard boundary is source code: only agents touch it.

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
+-- todos/
|   +-- {todo-name}.md           # Active todos
|   +-- completed/
|       +-- {todo-name}.md       # Completed todos
+-- plans/
    +-- {plan-name}.md           # Active plans
    +-- completed/
        +-- {plan-name}.md       # Completed plans
```

All paths are relative to the project root.

---

## Agent Memory Files

Each plan has a companion memory directory where agents store their private working state. For key rules, base format, system prompt placement, and orchestrator responsibilities, see `~/.claude/skills/shared/references/agent-memory.md`.

**Agent system prompt placement:** Every agent that participates in this workflow must have a `## REQUIRED FIRST STEP` section immediately after its one-line role description — before modes of work, expertise, or any other section. This ensures agents check for and read their memory file before doing anything else. See the shared reference and migration guide for the template and checklist.

### Structure

```
docs/plans/
+-- feature-name-plan.md              # Design only — shared by all agents
+-- feature-name-plan.memory/
    +-- architect.md                   # Architect's private notes
    +-- developer.md                   # Developer's private notes
    +-- requirements-reviewer.md       # Reviewer's private notes
    +-- requirements-documenter.md     # Documenter's private notes
```

### What Lives in Memory Files vs. Plan

| Content | Location |
|---------|----------|
| Design (Overview, Business Rules, Approach, Domain Model, Implementation Steps) | Plan file |
| Business Requirements Context, Acceptance Criteria, Agent Phasing | Plan file |
| Architect Review (codebase findings, concerns, testable assertions draft) | `architect.md` |
| Developer Review (assertion traces, concerns, verdict) | `developer.md` |
| Implementation Contract (scope, gates, stop conditions) | `developer.md` |
| Implementation Progress (milestones, evidence) | `developer.md` |
| Completion Evidence (test results, contract status) | `developer.md` |
| Architect Verification (post-implementation verdict) | `architect.md` |
| Requirements Verification (post-implementation) | `requirements-reviewer.md` |
| Documentation tracking (files updated, deliverables) | `requirements-documenter.md` |

---

## Agent Collaboration Workflow

This is the full lifecycle for significant work. Each step uses the appropriate agent.

### Prerequisites

Before starting the workflow, check for project-specific resources:

1. **Agents** — Check `.claude/agents/` for project-specific agents: architect, developer, specialized (e.g., UI, integration), documentation, **business-requirements-reviewer**, and **business-requirements-documenter**. Also check `~/.claude/agents/` for general agents. **Project-specific agents always take priority over user-level agents of the same role.** Fall back to general-purpose agents only when no project-specific agent exists for that role. Specialized implementation agents handle specific portions of Step 6 work (e.g., a UI agent handles page components and styling).
2. **Business requirements** — Check the project's CLAUDE.md for where business requirements documentation lives (business rules, user stories, workflows, data dictionaries). **If CLAUDE.md does not clearly indicate where business requirements are documented, STOP and ask the user before proceeding.** This information is required for Step 2.
3. **Domain skill** — Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
4. **Verification resources** — Check if the project has additional verification resources (e.g., sample projects, integration test suites) that the architect should use to verify scope claims.

### Agent Strategy

Every agent invocation is a **fresh** Agent call. Provide full context (todo path, plan path, relevant instructions) each time. Do not attempt to resume agents across steps.

### Step 1: Create Todo and Draft Plan (User + Orchestrator)

**The user is the designer.** The orchestrator is the user's design partner — analyzing code, tracing patterns, fetching data, and helping structure the design. This step replaces the old separate "orchestrator creates todo, architect creates plan" split.

#### Part A: Create the Todo

1. Capture the user's description of the problem and desired outcome
2. **Analyze the codebase together** — search code, trace patterns, identify affected aggregates, check existing tests, read prior completed todos/plans. The orchestrator actively helps the user understand the current state and implications.
3. Create the todo file in `docs/todos/` using the todo template
4. Set status to "In Progress"

#### Part B: Draft the Plan

Working in conversation or plan mode, collaborate with the user to design the solution:

1. Create the plan file in `docs/plans/` using the plan template
2. Link the plan to the todo (update both files)
3. Fill in the user-authored sections together:
   - **Overview** — what the plan addresses
   - **Approach** — high-level strategy
   - **Design** — detailed design (architecture, file structure, data flow)
   - **Implementation Steps** — ordered steps for the developer
   - **Acceptance Criteria** — what "done" looks like
   - **Dependencies** and **Risks**
4. Leave these sections for the architect to fill during review (Step 3):
   - **Business Requirements Context** — populated from the reviewer's findings
   - **Business Rules (Testable Assertions)** — the architect extracts these from the design
   - **Test Scenarios** — concrete scenarios for each business rule
   - **Domain Model Behavioral Design** — computed properties, visibility flags, reactive rules, validation
   - **Agent Phasing** — which implementation phases benefit from fresh agents
5. Set plan status to `Draft`

**The plan should reflect the user's design decisions.** The orchestrator helps structure and flesh out the design but does not override the user's choices.

### Step 2: Business Requirements Review

**Purpose:** Compare the user's draft plan against the project's EXISTING DOCUMENTED business requirements before finalizing. This catches contradictions that would otherwise become bugs — especially implicit dependencies where changing one behavior breaks assumptions in other parts of the system.

Invoke the **business-requirements-reviewer** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The todo file path
- The plan file path
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Review this todo and draft plan against the project's existing business requirements. Write your findings into the todo's Requirements Review section. VETO if contradictions are found."

The reviewer agent should:
1. Read the todo and draft plan to understand the problem, proposed solution, and design
2. Discover business requirements documentation paths from CLAUDE.md. **If paths are unclear, STOP and return questions for the user — do NOT guess.**
3. Search requirements docs for rules, user stories, workflows, and data definitions related to the scope
4. Identify relevant requirements, gaps, and contradictions
5. Pay special attention to **implicit dependencies** — changes that technically work but alter behavior governed by other business rules
6. Write findings into the todo's **Requirements Review** section (Relevant Requirements Found, Gaps, Contradictions, Recommendations for Architect)
7. Set the verdict in the todo's Requirements Review section:
   - **APPROVED** — No contradictions. Proceed to Step 3 (Architect Review).
   - **VETOED** — Contradictions found. Must be resolved before proceeding.

**If VETOED:**
1. Present the specific contradictions to the user, including exact requirement references, file paths, and why they conflict with the proposed work
2. **STOP.** The user decides how to resolve the contradiction — whether to modify the plan, update outdated requirements, override, or take a different path entirely
3. After the user provides direction, update the plan accordingly. If requirements need updating, invoke the appropriate agent. Then re-invoke the reviewer to confirm the contradiction is resolved
4. Repeat until APPROVED

### Step 3: Architect Review

**Purpose:** The architect performs a deep codebase dive to validate the user's design, fill in the technical validation sections, and catch architectural issues the user may have missed. The architect is a **reviewer and enhancer**, not the designer.

Set plan status to `Under Review (Architect)` before invoking the agent.

Invoke the **architect agent** with:
- The plan file path
- The todo file path (with Requirements Review section populated from Step 2)
- Any domain skill references found in prerequisites
- Instruction: "Review this plan created by the user. Perform a deep codebase analysis. Fill in the Business Requirements Context (from the todo's Requirements Review), Business Rules (Testable Assertions), Test Scenarios, Domain Model Behavioral Design, and Agent Phasing sections. Validate the design against codebase reality. Raise concerns or approve."

The architect agent should:
1. Read the plan and todo (including the Requirements Review section)
2. **Populate Business Requirements Context** from the reviewer's findings in the todo — so the plan is self-contained
3. **Perform a deep codebase dive** — examine affected aggregates, existing patterns, related tests, repository implementations. Document files examined.
4. **Extract business rules as testable assertions** — Analyze the user's design, legacy code, and codebase to produce numbered assertions. Format: `WHEN [conditions], THEN [property/method] RETURNS [value]`. Trace each to an existing documented requirement where one exists. New assertions must be marked as NEW. **If the architect struggles to write clear assertions, this is an architectural smell** — the design may not be concrete enough. Report this to the orchestrator.
5. **Create concrete test scenarios** — For each business rule, at least one scenario with specific inputs and expected result.
6. **Fill in Domain Model Behavioral Design** — computed properties, visibility flags, reactive rules, validation rules.
7. **Identify agent phases** — Analyze implementation steps and determine which phases benefit from fresh agents.
8. **Validate the design** against codebase reality:
   - Are aggregate boundaries correct?
   - Do proposed changes conflict with existing patterns?
   - Are there affected tests the user didn't account for?
   - Is the implementation approach feasible given the framework constraints?
9. If verification resources exist, verify scope claims using them
10. Write review findings to the architect's memory file
11. Render a verdict:
    - **Approved** — Design is sound, all sections filled. Proceed to Step 4 (Developer Review).
    - **Concerns** — Issues found that the user should address. Return concerns to the orchestrator.
    - **Rejected** — Fundamental problems with the design that require significant rework.
12. Update plan status:
    - Approved: `Under Review (Developer)`
    - Concerns/Rejected: `Concerns Raised (Architect)`

**If Concerns or Rejected:**
1. Present the architect's findings to the user
2. The user decides how to address them — modify the plan, override, or ask for more detail
3. After the user updates the plan, re-invoke the architect to review changes
4. Repeat until Approved

### Step 4: Developer Review

Invoke the **developer agent** with:
- The plan file path
- The todo file path
- The agent memory file path: `docs/plans/{plan-name}.memory/developer.md`
- If the architect wrote review notes, relay the key findings from `docs/plans/{plan-name}.memory/architect.md` in the spawn prompt (the developer must NOT read the architect's memory file directly)
- Instruction: "Review this plan. For EACH business rule assertion, trace through the proposed implementation and verify the expected result matches. Write all review findings — assertion trace, concerns, verdict — to your agent memory file at [path]. Raise concerns or approve."

The developer agent should:
1. **Verify business rules first** — For EACH numbered assertion in the plan's "Business Rules" section, trace through the proposed implementation (the specific method, condition, or code path) and verify the expected result. Create an "Assertion Trace Verification" table in the developer's memory file. Each Implementation Path entry must cite a specific method name and the condition expression from the design. Entries without specifics (e.g., "handled in implementation", "matches design") are insufficient — reject and request detail from the architect. **This is the primary review task — do it before anything else.**
2. **Verify test scenarios** — For each test scenario in the plan, mentally execute it against the proposed implementation and confirm the expected result matches.
3. If any assertion trace produces a result that contradicts the business rule, this is a **blocking concern** — the plan has a logic error.
4. **Check against Requirements Context** — Verify the design respects the requirements identified in the Business Requirements Context section. Flag if the design introduced approaches that contradict documented requirements.
5. Investigate the codebase to verify plan claims
6. **If the architect provided verification evidence** (relayed by the orchestrator from the architect's memory): confirm it exists and makes sense
7. **If verification resources exist but the architect did not use them**: reject the plan back to the architect
8. Check for gaps, ambiguities, edge cases, and risks
9. Review the Agent Phasing section — confirm the phasing is practical and the fresh/resume decisions make sense for the implementation work
10. Render a verdict: **Concerns Raised** or **Approved**
11. **Write all findings** (assertion trace, concerns, verdict) to the developer's agent memory file

### Step 5: Clarification Loop

If the developer raises concerns (read from `docs/plans/{plan-name}.memory/developer.md`):

1. **Route to architect first** — Invoke a fresh architect with the developer's concerns (extracted from developer's memory by the orchestrator — the architect does NOT read `developer.md`). Instruct: "The developer raised these concerns about the plan. Address what you can. For any concern that involves a design change (not just a technical implementation detail), STOP and escalate to the user instead of resolving it yourself."

2. **Architect triages concerns:**
   - **Technical implementation details** — The architect addresses these directly (e.g., "the correct Include pattern is X", "this factory method needs attribute Y", "the test should use EntityBaseServices not DI")
   - **Design changes** — The architect STOPS and escalates to the user (e.g., "the developer suggests a different aggregate boundary", "the approach conflicts with an existing pattern the user may want to preserve", "this changes the scope of what's being built"). **When in doubt, escalate.**

3. **If the architect escalated concerns to the user:**
   - Present the escalated concerns to the user with the architect's assessment
   - The user decides how to resolve them
   - Update the plan with the user's decisions

4. **Re-invoke developer** (from Step 4) for re-review with the architect's responses and any user decisions
5. Repeat until the developer approves

When the developer approves:
- Developer creates an **Implementation Contract** in the developer's memory file (scope, out-of-scope, verification gates)
- If verification resources have failing acceptance criteria, list them in the contract
- Set plan status to "Ready for Implementation"

### Step 6: Implementation

**STOP — Do not write code here. Invoke an agent for all implementation work.**

Invoke the **developer agent** for implementation with:
- The plan file path
- The agent memory file path: `docs/plans/{plan-name}.memory/developer.md` (contains the implementation contract from Step 5)
- Instruction: "Implement the approved plan following the implementation contract in your memory file. Write progress and evidence to your memory file."

**Specialized agent routing**: If the implementation includes work that matches a specialized agent's scope (identified in Prerequisites step 1), split the implementation:
- **Developer agent**: Domain models, repositories, services, tests, backend logic
- **Specialized UI agent** (if found): Pages, components, templates, CSS, layout
- **Other specialized agents**: Route according to their declared file scope and capabilities

Coordinate by having the developer agent complete backend work first (or in parallel if independent), then invoke the specialized agent for its portion with the same plan file.

**Agent phasing**: Follow the plan's "Agent Phasing" section (created by the architect in Step 3). Each phase gets a fresh Agent invocation with a clean context window. Provide:
- The plan file path (so the agent can read the design)
- The agent memory file path (so the agent can read prior progress and write new progress)
- The specific phase description and deliverables
- Any outputs from prior phases that this phase depends on (relayed by the orchestrator from the prior agent's memory)

The developer agent (or specialized agents) should:
1. Work through the implementation contract checklist (in their memory file)
2. Run tests at each verification gate
3. **STOP and report** if out-of-scope tests fail or architectural contradictions are discovered. The project's CLAUDE.md defines which tests are "sacred" (existing tests are never gutted to make new code pass). When the developer reports an out-of-scope failure, present it to the user with: "Test X started failing. It tests [feature], which is outside the current task. Should I (1) fix the underlying issue, (2) add to the bug list, or (3) investigate further?"
4. Collect evidence (test output, generated code samples)
5. **Do NOT update documentation markdown** — skill markdown, user-facing docs markdown, and release notes are handled in Step 8 by the documenter agent. The developer's scope is source code only. Code comments (XML docs) on modified code are in scope. Design project code (`src/Design/`) and sample code (`src/samples/`) are source code — update them during implementation if in scope, or as Developer Deliverables routed from the documenter in Step 8.
6. **When finished**: Write "Implementation Progress" and "Completion Evidence" to the developer's memory file, set plan status to "Awaiting Verification", then **STOP**. Do NOT mark the todo or plan as Complete.

### Step 7: Verification (Architect + Requirements)

**The developer may NOT mark work as Complete. Verification is mandatory.**

This step has two parts. Both must pass before proceeding. See `references/verification-step-guide.md` for detailed agent invocation instructions.

#### Part A: Architect Verification

Invoke the **architect agent** to independently verify the implementation:
- Run all builds and tests (do NOT trust the developer's reported results)
- Cross-check every test scenario against actual test methods
- Verify implementation matches the plan's design
- Zero tolerance for test failures — any failure is SENT BACK

Verdicts: **VERIFIED** (proceed to Part B) or **SENT BACK** (developer fixes issues).

**Critical rule**: Any test failure — even one the developer classified as "pre-existing" — must be reported. Only the user can decide whether a failure is acceptable.

#### Part B: Requirements Verification

**Only if Part A passes (VERIFIED).**

Invoke the **business-requirements-reviewer** agent to confirm the implementation satisfies documented business requirements:
- Trace each relevant requirement through the implementation
- Check for unintended side effects on other business rules

Verdicts: **REQUIREMENTS SATISFIED** (proceed to Step 8) or **REQUIREMENTS VIOLATION** (plan status "Sent Back").

### Step 8: Requirements Documentation

**Purpose:** Update the project's business requirements documentation to reflect what was actually implemented — new rules, changed rules, resolved gaps. This closes the loop: the reviewer identified the requirements landscape in Step 2, and now the documentation sources are updated to stay current.

Every project organizes documentation differently. The documenter agent and the project's CLAUDE.md provide the project-specific knowledge of where requirements live and how they're structured. This step defines the workflow, not the project details.

#### Part A: Requirements Documentation

Invoke the **business-requirements-documenter** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The plan file path
- The todo file path
- The documenter's memory file path: `docs/plans/{plan-name}.memory/requirements-documenter.md`
- The developer's completion evidence (relayed by the orchestrator from `developer.md` — the documenter does NOT read `developer.md` directly)
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Update business requirements documentation to reflect the completed implementation. Add new rules, update changed rules, resolve gaps. If source code changes are needed (code comments, samples, design project tests), list them as Developer Deliverables in your memory file — do NOT modify source code. Write all documentation tracking to your agent memory file at [path]."

The documenter agent should:
1. Read the plan's Business Requirements Context and Business Rules (Testable Assertions) sections
2. Review the developer's completion evidence (relayed in the spawn prompt)
3. Compare: identify new requirements (marked NEW in the assertions), changed requirements, and gaps that were filled
4. Update requirements documentation — new rules, changed rules, filled gaps, affected workflows
5. If source code changes are needed (code comments, samples, design project tests), list them in the documenter's memory file as **Developer Deliverables** — the orchestrator routes these to the developer agent
6. Record all work in the documenter's memory file (files updated, deliverables completed)
7. Set plan status to "Requirements Documented"

**Critical rule**: Document what was *implemented*, not what was *planned*. If the implementation diverged from the plan, the documentation must match the implementation.

**Developer Deliverables**: If the documenter identified source code changes needed (read from the documenter's memory file), invoke a fresh **developer agent** to complete them. The developer builds and tests after changes.

#### Part B: General Documentation (if applicable)

Invoke a fresh **documentation agent** (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/` such as `docs-writer`; use the developer agent as a final fallback if no documentation agent exists).

If the plan identifies non-requirements documentation deliverables (API docs, README changes, migration guides, architecture docs, getting-started updates), invoke the documentation agent with:
- The plan file path
- The todo file path
- Instruction: "Update non-requirements documentation affected by this implementation."

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
- **Problem**: The user's description of the problem — in their words, at their level of detail
- **Solution**: The user's proposed approach — high-level or detailed depending on how much design was done
- **Plans**: Populate when the plan is created in Step 1 Part B
- **Tasks**: Workflow steps only (requirements review, architect review, developer review, etc.)
- **Progress Log**: Record that the todo was created and from what context
- **Results / Conclusions**: Empty

File location: `docs/todos/{filename}.md`

---

## Creating a Plan

### Write the Plan File

Use the same filename convention as todos (lowercase, hyphens, concise, no dates). Be descriptive of the plan's purpose. Examples: `authentication-fix-design.md`, `dark-mode-implementation.md`

Use the template from `references/plan-template.md`. Fill in user-authored sections:

- **Title**: Descriptive plan title
- **Date**: Today's date
- **Related Todo**: Relative link to parent todo
- **Status**: "Draft" (initial status when user creates the plan)
- **Last Updated**: Same as Date
- **Overview**, **Approach**, **Design**, **Implementation Steps**, **Acceptance Criteria**, **Dependencies**, **Risks**

Leave architect-review sections empty (the architect fills these in Step 3):
- **Business Requirements Context** (populated from todo's Requirements Review)
- **Business Rules (Testable Assertions)** and **Test Scenarios**
- **Domain Model Behavioral Design**
- **Agent Phasing**

For valid plan status values, see `references/plan-template.md`.

### Plan Workflow Sections

Plans that go through the agent collaboration workflow contain design sections only. Workflow state (reviews, contracts, progress, evidence, verification results) is stored in agent memory files — see the **Agent Memory Files** section above.

**In the plan file** (design content shared by all agents):

- **Business Requirements Context** — Architect populates from the todo's Requirements Review (filled in Step 3)
- **Business Rules (Testable Assertions)** — Architect extracts from the user's design (filled in Step 3)
- **Agent Phasing** — Architect identifies phases (filled in Step 3)
- **Domain Model Behavioral Design** — Architect specifies (filled in Step 3)

**In agent memory files** (private workflow state):

- **Architect Review** (codebase findings, concerns, verdict), **Architect Verification** (post-implementation) -> `architect.md`
- **Developer Review**, **Implementation Contract**, **Implementation Progress**, **Completion Evidence** -> `developer.md`
- **Requirements Verification** -> `requirements-reviewer.md`
- **Documentation tracking** -> `requirements-documenter.md`

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

1. Create todo and draft plan with the user (Step 1)
2. Business requirements review (Step 2) — reviewer writes findings into todo, checks for contradictions
3. Architect review (Step 3) — architect validates design, fills testable assertions, domain model design, agent phasing
4. Developer reviews (Step 4)
5. Clarification loop if needed (Step 5) — architect handles technical concerns, escalates design changes to user
6. Implementation (Step 6) — route to developer and/or specialized agents
7. Verification (Step 7) — architect verifies builds/tests, then reviewer verifies requirements compliance
8. Documentation (Step 8) — documenter updates requirements docs, developer handles source code deliverables if any, docs agent handles general docs
9. Completion (Step 9) — only after both verifications pass

### Adding a Plan to Existing Todo

1. Read existing todo for context
2. Draft the plan with the user (Step 1 Part B)
3. Invoke business-requirements-reviewer to write findings into todo's Requirements Review section (Step 2)
4. Invoke architect to review the plan (Step 3)

### Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the todo file. Check if a plan file exists (look in the todo's Plans section for a link).
2. **If no plan exists**:
   - Plan hasn't been created yet -> Step 1 Part B (draft the plan with the user)
3. **If a plan exists**, read it and check its **Status** field:
   - `Draft` -> Check the todo's **Requirements Review** section:
     - No review yet (Verdict: Pending) -> Step 2 (run the reviewer)
     - Verdict: APPROVED -> Step 3 (architect review)
     - Verdict: VETOED -> Step 2 (resolve contradictions with user)
   - `Under Review (Architect)` -> Step 3 (architect review in progress, re-invoke architect)
   - `Concerns Raised (Architect)` -> Step 3 (user addresses architect concerns, re-invoke architect)
   - `Under Review (Developer)` -> Step 4 (developer review)
   - `Concerns Raised` -> Step 5 (clarification loop). Read the developer's memory file to extract concerns.
   - `Ready for Implementation` -> Step 6 (implementation)
   - `In Progress` -> Step 6 (implementation continues). Read the developer's memory file to understand progress so far and include it in the spawn prompt.
   - `Awaiting Verification` -> Step 7 (verification). Read the developer's memory file to extract completion evidence for the architect's spawn prompt.
   - `Sent Back` -> Step 6 (developer fixes issues). Read the architect's memory file and/or reviewer's memory file to determine which verification failed and what needs fixing. Include the issues in the developer's spawn prompt.
   - `Requirements Documented` -> Read the documenter's memory file for pending Developer Deliverables (from Part A). If none, proceed to Part B (general documentation, if applicable) or Step 9 (completion).
   - `Documentation Complete` -> Step 9 (completion)
4. Invoke a fresh agent for that step, providing the todo path, plan path, and agent memory file path. Include relevant context from other agents' memory files in the spawn prompt (the fresh agent must NOT read other agents' memory files directly).

---

## Best Practices

1. **Status accuracy**: Update status fields promptly as workflow progresses.
2. **Progress logging**: Update progress log as work happens, not just at the end.
3. **Link maintenance**: Always update both files when creating links.
4. **Multiple plans OK**: A todo can have multiple plans. One todo per file.
5. **Last Updated**: Always update when modifying any content.
6. **Requirements review before architect**: Never skip the business requirements review (Step 2). The most expensive bugs come from contradicting existing requirements — especially implicit dependencies.
7. **Verification resources**: When the project has verification resources (design projects, sample projects, integration suites), use them. Compilation and test results are the source of truth for scope claims.
8. **Agent phasing**: The architect identifies phases benefiting from fresh agents during review (Step 3). The orchestrator follows this phasing during implementation.
9. **Documentation deliverables**: Identify expected documentation deliverables during planning or implementation contract, not as an afterthought.
10. **Assertion-trace workflow**: The assertion-trace workflow in Steps 3-4 is the primary defense against logic errors. Do not skip or abbreviate it.
11. **Architect struggles = smell**: If the architect cannot write clear testable assertions from the user's design, the design needs more work. Return to the user.
12. **Escalation over guessing**: In the clarification loop (Step 5), the architect should escalate design questions to the user rather than making design decisions autonomously. Technical details the architect handles; design changes go to the user.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`
- Verification step guide: `references/verification-step-guide.md` — detailed Step 7 agent invocation instructions
- Documentation step guide: `references/documentation-step-guide.md` — detailed Step 8 agent invocation instructions
- Agent migration guide (v2 -> v3): `references/agent-migration-v3.md`
- Agent migration guide (v1 -> v2): `references/agent-memory-migration.md`
- Shared agent memory pattern: `~/.claude/skills/shared/references/agent-memory.md` — key rules, base format, orchestrator responsibilities

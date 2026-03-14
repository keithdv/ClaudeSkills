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
- Read workflow files (todos, plans, agent definitions) to make routing decisions
- **Discover** — search code, docs, todos, and tests to understand the user's request (see Discovery vs Analysis rule below)

### What the Orchestrator Does NOT Do

- **NEVER** call Edit or Write on source files — invoke an agent
- **NEVER** call Bash to run sed, awk, or any command that modifies source files — invoke an agent
- **NEVER** rationalize a "quick fix" as being too small to need an agent — invoke an agent
- **NEVER** draw architectural conclusions from reading source files — that is the architect's job (Step 4)
- **NEVER** put orchestrator analysis into a todo — the todo captures the USER's description plus discovered references; analysis belongs in the plan

## Core Rule: Discovery vs Analysis

The orchestrator may **discover** but must not **analyze**. Discovery resolves ambiguity in the user's request so the todo is precise and the architect starts with clear context. Analysis draws conclusions about what should change — that is the architect's job.

### Discovery (Orchestrator MAY do)

Search code, docs, todos, and tests to understand what the user is referring to:

- **Identify things** — Glob/Grep to find what "visit flow" is (a class? a page? a concept?)
- **Locate prior work** — Search completed todos/plans to find the one the user references
- **Confirm existence** — Check whether a domain model, test suite, or feature exists
- **Resolve vocabulary** — Map the user's words to specific files, classes, or concepts
- **Read interfaces/signatures** — Skim a file to understand what something IS, not what's wrong with it

### Analysis (Orchestrator must NOT do)

Draw conclusions about what should change — this pigeonholes the architect:

- **Architectural conclusions** — "VisitFlow.razor has logic that belongs in the domain model"
- **Gap assessments** — "These 5 methods lack test coverage"
- **Design recommendations** — "The solution should use property changed events"
- **Current state writeups** — Building a "Current State Analysis" section for the todo

### The Test

Before reading a file, ask: **"Am I looking something up, or building a case?"**

- "What is VisitFlow?" → **Lookup** — search for files, read the interface → allowed
- "Does a VisitFlow test suite exist?" → **Lookup** — Glob for test files → allowed
- "Which completed todo used property changed events?" → **Lookup** — search completed todos → allowed
- "VisitFlow has scattered UI logic that should move to the domain" → **Analysis** — STOP, that's the architect's conclusion to draw

### What Goes in the Todo from Discovery

- **File paths and links** — "VisitFlow is at `zTreatment.DomainModels/Workflow/VisitFlow.cs`"
- **References to prior work** — "Related completed todo: [workflow-objects-refactoring](../todos/completed/workflow-objects-refactoring.md)"
- **Existence facts** — "A VisitFlow test suite exists at X" or "No dedicated VisitFlow tests were found"
- **The user's words** — The problem and solution in the user's framing

### What Does NOT Go in the Todo from Discovery

- Conclusions about what's wrong with the code
- Lists of methods that "should" move or change
- Test coverage gap analysis
- Architectural recommendations

---

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
2. **Business requirements** — Check the project's CLAUDE.md for where business requirements documentation lives (business rules, user stories, workflows, data dictionaries). **If CLAUDE.md does not clearly indicate where business requirements are documented, STOP and ask the user before proceeding.** This information is required for Step 3.
3. **Domain skill** — Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
4. **Verification resources** — Check if the project has additional verification resources (e.g., sample projects, integration test suites) that the architect should use to verify scope claims.

### Step 1: Create Todo

1. Capture the user's description of the problem and desired outcome — in THEIR words
2. **Discover** — Before asking clarifying questions, search the codebase to resolve ambiguity in the user's request:
   - If the user references prior work (e.g., "same exercise as the Consultation work"), find and read that completed todo/plan
   - If the user mentions a concept by name (e.g., "visit flow"), Glob/Grep to identify what it is (a class? a page? a domain model?)
   - If the user asks about test coverage, check whether test files exist (not whether they're adequate — that's the architect's job)
   - If questions remain after discovery, ask the user — but only questions that discovery couldn't answer
3. Create the todo file in `docs/todos/` using the todo template
4. Set status to "In Progress"

**The todo captures the user's request plus discovered references.** The Problem and Solution sections use the user's framing and language. Discovery adds precision (file paths, links to prior work, existence facts) without adding conclusions.

**What belongs in the todo:**
- The user's description of the problem
- The user's proposed solution or desired outcome
- References to prior related work (links to completed todos — found via discovery)
- Discovered file paths and existence facts (e.g., "VisitFlow domain model is at X", "No dedicated VisitFlow unit tests exist")
- The user's stated priority and context

**What does NOT belong in the todo:**
- Architectural conclusions drawn by the orchestrator (e.g., "UI logic that should move to the domain model")
- Test coverage gap analysis (beyond existence facts)
- Design recommendations or solution approaches not stated by the user

**IMPORTANT: Do NOT create the plan file.** The architect creates the plan in Step 4. Proceed directly to Step 2 (architect comprehension check) after creating the todo.

### Step 2: Architect Comprehension Check

**Purpose:** Before investing in requirements review and full design work, confirm the architect understands the problem and proposed solution. This is a lightweight pass — just questions, not design. A clear, well-scoped todo ensures the requirements reviewer (Step 3) evaluates against the actual intent.

Invoke the **architect agent** with:
- The todo file path
- Any domain skill references found in prerequisites
- Instruction: "Read this todo. Before designing anything, confirm you understand the problem and proposed solution. Return any clarifying questions you have. If the request is clear, state that you're ready to proceed."

The architect agent should:
1. Read the todo to understand the problem and proposed solution
2. Assess whether the problem statement is clear and unambiguous
3. Return one of:
   - **Questions** — A numbered list of specific clarifying questions
   - **Ready** — Confirmation that the request is understood and no questions remain

**If the architect has questions:**
1. Present the questions to the user
2. Record the user's answers in the todo's **Clarifications** section
3. Re-invoke the architect with the updated todo to confirm understanding or ask follow-up questions
4. Repeat until the architect confirms "Ready"

**When the architect confirms "Ready":** Proceed to Step 3 (Business Requirements Review).

### Step 3: Business Requirements Review

**Purpose:** Compare the proposed work against the project's EXISTING DOCUMENTED business requirements (business rules, user stories, workflows, data definitions already in the codebase) before design begins. This is NOT the same as gathering the user's problem and solution in Step 1 — this step searches the project's requirements documentation for contradictions with the proposed work. This step catches contradictions that would otherwise become bugs — especially implicit dependencies where changing one behavior breaks assumptions in other parts of the system.

Invoke the **business-requirements-reviewer** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The todo file path (with Clarifications section populated from Step 2)
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Review this todo against the project's existing business requirements. Read the Clarifications section for additional context from the architect's comprehension check. Write your findings into the todo's Requirements Review section. VETO if contradictions are found."

The reviewer agent should:
1. Read the todo to understand the problem, proposed solution, and any Clarifications from Step 2
2. Discover business requirements documentation paths from CLAUDE.md. **If paths are unclear, STOP and return questions for the user — do NOT guess.**
3. Search requirements docs for rules, user stories, workflows, and data definitions related to the todo's scope
4. Identify relevant requirements, gaps, and contradictions
5. Pay special attention to **implicit dependencies** — changes that technically work but alter behavior governed by other business rules (e.g., changing when data is loaded affects when it's considered "part of" a record)
6. Write findings into the todo's **Requirements Review** section (Relevant Requirements Found, Gaps, Contradictions, Recommendations for Architect)
7. Set the verdict in the todo's Requirements Review section:
   - **APPROVED** — No contradictions. Proceed to Step 4 (Architect Plan Creation & Design).
   - **VETOED** — Contradictions found. Must be resolved before design.

**The reviewer does NOT create the plan file.** The plan is created by the architect in Step 4.

**If VETOED:**
1. Present the specific contradictions to the product owner (the user), including exact requirement references, file paths, and why they conflict with the proposed work
2. **STOP.** Do not proceed with the workflow. The product owner decides how to resolve the contradiction — whether to modify the approach, update outdated requirements, override, or take a different path entirely
3. After the product owner provides direction, follow it. If requirements need updating, invoke the appropriate agent (developer agent for `.cs` files, documenter agent for markdown). Then re-invoke the reviewer to confirm the contradiction is resolved
4. Repeat until APPROVED

### Step 4: Architect Plan Creation & Design

Invoke the **architect agent** with:
- The todo file path (with Requirements Review and Clarifications sections populated)
- Any domain skill references found in prerequisites
- Instruction: "Create the plan file for this todo. Read the todo's Requirements Review and Clarifications sections first — incorporate those findings into the plan's Business Requirements Context. Then design the implementation, building on the documented requirements. Create business rules as testable assertions that trace to the existing requirements where they exist."

The architect agent should:
1. Read the todo to understand the problem, solution, **the Requirements Review section** written by the reviewer, and **the Clarifications** from Step 2
2. **Create the plan file** in `docs/plans/` using the plan template. Populate the Business Requirements Context section from the reviewer's findings in the todo. Link the plan to the todo (update both files).
3. The architect MUST NOT invent business rules that contradict the documented requirements identified by the reviewer.
4. Explore the codebase to understand current architecture
5. **Extract business rules as testable assertions** — Before designing anything, analyze the legacy code, user requirements, and codebase to produce a numbered list of crisp, unambiguous business rules. Format: `WHEN [conditions], THEN [property/method] RETURNS [value]`. **Trace each assertion to an existing documented requirement where one exists.** New assertions (for gaps identified by the reviewer) must be clearly marked as new. These go in the plan's "Business Rules (Testable Assertions)" section. This is NOT optional — it is the first section completed.
6. **Create concrete test scenarios** — For each business rule, create at least one scenario with specific inputs and expected result. These go in the "Test Scenarios" table. The architect must show the evaluation for each scenario. These scenarios become the acceptance tests.
7. Fill in the remaining plan sections (Approach, Design, Implementation Steps, etc.). **Design against the assertions** — every design decision must trace to one or more business rule assertions. **Implementation steps must cover only source code changes** — do NOT include documentation updates (skill docs, user-facing docs, samples, design reference files, release notes) in implementation phases. List expected documentation deliverables in the plan's "Documentation" section for Step 9.
8. **If verification resources exist** (design projects, sample projects, etc.): verify scope claims using them. Leave failing tests or code as acceptance criteria for features that need implementation.
9. **Identify fresh agent phases**: Analyze the implementation steps and determine which phases would benefit from a fresh agent with a clean context window. Document this in the plan's "Agent Phasing" section. Consider:
    - Phases that are independent and don't need prior implementation context
    - Phases that touch more than ~10 files or involve substantial code generation
    - Phases that span different domains (e.g., backend vs. frontend vs. tests)
    - Phases that could run in parallel
10. Update plan status to "Draft (Architect)"
11. Hand off to developer review

### Step 5: Developer Review

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
6. **If the architect provided verification evidence** (design projects, compilation results, etc.): confirm it exists and makes sense
7. **If verification resources exist but the architect did not use them**: reject the plan back to the architect
8. Check for gaps, ambiguities, edge cases, and risks
9. Review the Agent Phasing section — confirm the phasing is practical and the fresh/resume decisions make sense for the implementation work
10. Render a verdict: **Concerns Raised** or **Approved**

### Step 6: Clarification Loop

If the developer raises concerns:
1. Present concerns to the user
2. Ask the user: "Would you like to clarify these yourself, or should the architect agent address them?"
3. Based on user's choice:
   - **User clarifies**: Orchestrator updates the plan with the user's answers, then returns to Step 5
   - **Architect clarifies**: Invoke architect agent with the concerns, then return to Step 5
4. Repeat until the developer approves

When the developer approves:
- Developer creates an **Implementation Contract** in the plan (scope, out-of-scope, verification gates)
- If verification resources have failing acceptance criteria, list them in the contract
- Set plan status to "Ready for Implementation"

### Step 7: Implementation

**STOP — Do not write code here. Invoke an agent for all implementation work.**

Invoke the **developer agent** for implementation with:
- The plan file path (with implementation contract)
- Instruction: "Implement the approved plan following the implementation contract"

**Specialized agent routing**: If the implementation includes work that matches a specialized agent's scope (identified in Prerequisites step 1), split the implementation:
- **Developer agent**: Domain models, repositories, services, tests, backend logic
- **Specialized UI agent** (if found): Pages, components, templates, CSS, layout
- **Other specialized agents**: Route according to their declared file scope and capabilities

Coordinate by having the developer agent complete backend work first (or in parallel if independent), then invoke the specialized agent for its portion with the same plan file.

**Fresh agent phasing**: Follow the plan's "Agent Phasing" section (created by the architect in Step 4). For each phase marked "Fresh Agent? Yes", start a fresh Agent invocation (the default behavior) so the phase begins with a clean context window focused on its specific deliverable. For phases marked "Fresh Agent? No", resume the prior phase's agent (using the `resume` parameter with its agent ID) to preserve accumulated context. When starting a fresh invocation for a phase, provide:
- The plan file path (so the agent can read scope and prior progress)
- The specific phase description and deliverables
- Any outputs from prior phases that this phase depends on

The developer agent (or specialized agents) should:
1. Work through the implementation contract checklist
2. Run tests at each verification gate
3. **STOP and report** if out-of-scope tests fail or architectural contradictions are discovered
4. Collect evidence (test output, generated code samples)
5. **Do NOT update documentation markdown** — skill markdown, user-facing docs markdown, and release notes are handled in Step 9 by the documenter agent. The developer's scope is source code only. Code comments (XML docs) on modified code are in scope. Design project code (`src/Design/`) and sample code (`src/samples/`) are source code — update them during implementation if in scope, or as Developer Deliverables routed from the documenter in Step 9.
6. **When finished**: Write "Implementation Progress" and "Completion Evidence" sections in the plan, set plan status to "Awaiting Verification", then **STOP**. Do NOT mark the todo or plan as Complete.

### Step 8: Verification (Architect + Requirements)

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
5. If verification resources exist, verify they still pass
6. Render a verdict:
   - **VERIFIED**: All builds pass, all tests pass, implementation matches design → proceed to Part B
   - **SENT BACK**: Failures found → document issues in "Architect Verification" section, set plan status to "Sent Back", report to orchestrator for developer to fix

**Critical rule**: Any test failure — even one the developer classified as "pre-existing" — must be reported. Only the user can decide whether a failure is acceptable.

#### Part B: Requirements Verification

**Only if Part A passes (VERIFIED).**

Invoke the **business-requirements-reviewer** agent (same agent resolution as Step 3 — project-specific first, user-level fallback) with:
- The plan file path
- Instruction: "Perform post-implementation requirements verification. Confirm the implementation satisfies the documented business requirements identified in the Business Requirements Context section. Check for unintended side effects on other business rules."

The reviewer agent should:
1. Read the plan's Business Requirements Context, Completion Evidence, and Implementation Progress sections
2. For each requirement identified as relevant, trace through the implementation to verify compliance
3. Check for unintended side effects — changes that technically work but alter behavior governed by other business rules
4. Fill in the Requirements Verification section of the plan
5. Render a verdict:
   - **REQUIREMENTS SATISFIED**: Implementation respects all documented requirements → proceed to Step 9
   - **REQUIREMENTS VIOLATION**: Implementation violates documented requirements → document violations, set plan status to "Sent Back", report to orchestrator

### Step 9: Requirements Documentation

**Purpose:** Update the project's business requirements documentation to reflect what was actually implemented — new rules, changed rules, resolved gaps. This closes the loop: the reviewer identified the requirements landscape in Step 3, and now the documentation sources are updated to stay current.

Every project organizes documentation differently. The documenter agent and the project's CLAUDE.md provide the project-specific knowledge of where requirements live and how they're structured. This step defines the workflow, not the project details.

#### Part A: Requirements Documentation

Invoke the **business-requirements-documenter** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The plan file path
- The todo file path
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Update business requirements documentation to reflect the completed implementation. Add new rules, update changed rules, resolve gaps. If source code changes are needed (code comments, samples, design project tests), list them as Developer Deliverables in the plan's Documentation section — do NOT modify source code."

The documenter agent should:
1. Read the plan's Business Requirements Context, Business Rules (Testable Assertions), Completion Evidence, and Implementation Progress sections
2. Compare: identify new requirements (marked NEW in the assertions), changed requirements, and gaps that were filled
3. Update requirements documentation — new rules, changed rules, filled gaps, affected workflows
4. If source code changes are needed (code comments, samples, design project tests), list them in the plan's Documentation section as **Developer Deliverables** — the orchestrator routes these to the developer agent
5. Record all work in the plan's Documentation section
6. Set plan status to "Requirements Documented"

**Critical rule**: Document what was *implemented*, not what was *planned*. If the implementation diverged from the plan, the documentation must match the implementation.

**Developer Deliverables**: If the documenter identified source code changes needed, invoke the **developer agent** to complete them. The developer builds and tests after changes, then marks each deliverable as completed in the Documentation section.

#### Part B: General Documentation (if applicable)

If the plan identifies non-requirements documentation deliverables (API docs, README changes, migration guides, architecture docs, getting-started updates), invoke the **documentation agent** (or developer agent if no documentation agent exists) with:
- The plan file path
- The todo file path
- Instruction: "Update non-requirements documentation affected by this implementation. See the Documentation section of the plan for expected deliverables."

After all applicable parts complete, set plan status to "Documentation Complete."

See `references/documentation-step-guide.md` for detailed guidance.

### Step 10: Completion

**Only after verification has passed (Step 8, both parts) and documentation is complete (or N/A) from Step 9.**

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
- **Solution**: The user's proposed approach — high-level, not a technical analysis
- **Plans**: Leave empty (populated when plans are created)
- **Tasks**: Workflow steps only (requirements review, architect plan, developer review, etc.)
- **Progress Log**: Record that the todo was created and from what context
- **Results / Conclusions**: Empty

**Keep it brief.** A todo should be 30-50 lines, not 100+. If the user said "do the same exercise as the Consultation work for VisitFlow," the Problem section should say that — not a multi-paragraph analysis of VisitFlow.cs with line number references. The architect will do the deep analysis when creating the plan.

File location: `docs/todos/{filename}.md`

---

## Creating a Plan

> **Agent Workflow Note:** In the full Agent Collaboration Workflow (Steps 1-10), the architect agent creates the plan file in Step 4. Neither the orchestrator nor the reviewer creates the plan. This section is only for standalone plan creation outside the agent workflow.

### Write the Plan File

Use the same filename convention as todos (lowercase, hyphens, concise, no dates). Be descriptive of the plan's purpose. Examples: `authentication-fix-design.md`, `dark-mode-implementation.md`

Use the template from `references/plan-template.md`. Fill in:

- **Title**: Descriptive plan title
- **Date**: Today's date
- **Related Todo**: Relative link to parent todo
- **Status**: "Draft" for standalone plans; "Draft (Architect)" when created by the architect in the agent workflow (Step 4)
- **Last Updated**: Same as Date
- Core sections: Overview, Business Requirements Context (populated by architect from todo's Requirements Review), Business Rules, Approach, Design, Implementation Steps, Acceptance Criteria, Dependencies, Risks

For valid plan status values, see `references/plan-template.md`.

### Plan Workflow Sections

Plans that go through the agent collaboration workflow include additional sections for business requirements context, architectural verification, agent phasing, developer review, implementation contract, progress tracking, completion evidence, documentation, architect verification, and requirements verification.

These sections are defined in `references/plan-template.md`. When creating a plan for the full agent workflow, use the complete template. The key sections and their purposes:

- **Business Requirements Context** -- Architect populates from the todo's Requirements Review (filled in Step 4)
- **Architectural Verification** -- Architect's scope analysis and verification evidence
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
2. Architect comprehension check (Step 2) — architect reads todo and asks clarifying questions before reviewing
3. Business requirements review (Step 3) — reviewer writes findings into todo, checks for contradictions
4. Architect creates plan and designs (Step 4) — architect creates plan file, incorporates reviewer findings, designs implementation
5. Developer reviews (Step 5)
6. Clarification loop if needed (Step 6)
7. Implementation (Step 7) — route to developer and/or specialized agents
8. Verification (Step 8) — architect verifies builds/tests, then reviewer verifies requirements compliance
9. Documentation (Step 9) — documenter updates requirements docs, developer handles source code deliverables if any, docs agent handles general docs
10. Completion (Step 10) — only after both verifications pass

### Adding a Plan to Existing Todo

1. Read existing todo for context
2. Architect comprehension check (Step 2)
3. Invoke business-requirements-reviewer to write findings into todo's Requirements Review section (Step 3)
4. Invoke architect to create plan and design (Step 4)

### Resuming Mid-Workflow

When a session was interrupted or the user asks to resume:

1. Read the todo file. Check if a plan file exists (look in the todo's Plans section for a link).
2. **If no plan exists**, check the todo's **Clarifications** section:
   - Empty or not present → Step 2 (architect comprehension check)
   - Contains answered Q&A and architect confirmed "Ready" → Check the todo's **Requirements Review** section:
     - No review yet (Verdict: Pending) → Step 3 (run the reviewer)
     - Verdict: APPROVED → Step 4 (architect creates the plan)
     - Verdict: VETOED → Step 3 (resolve contradictions with user)
3. **If a plan exists**, read it and check its **Status** field:
   - `Draft (Architect)` → Step 4 (architect still working)
   - `Under Review (Developer)` → Step 5 (developer review)
   - `Concerns Raised` → Step 6 (clarification loop)
   - `Ready for Implementation` → Step 7 (implementation)
   - `In Progress` → Step 7 (implementation continues)
   - `Awaiting Verification` → Step 8 (verification)
   - `Sent Back` → Step 7 (developer fixes issues). Read both the Architect Verification and Requirements Verification sections of the plan to determine which verification failed and what the developer needs to fix.
   - `Requirements Documented` → Check Documentation section for pending Developer Deliverables (from Part A). If none, proceed to Part B (general documentation, if applicable) or Step 10 (completion)
   - `Documentation Complete` → Step 10 (completion)
4. Resume from that step, providing the todo and plan file paths (if plan exists) to the appropriate agent

---

## Best Practices

1. **Status accuracy**: Update status fields promptly as workflow progresses.
2. **Progress logging**: Update progress log as work happens, not just at the end.
3. **Link maintenance**: Always update both files when creating links.
4. **Multiple plans OK**: A todo can have multiple plans. One todo per file.
5. **Last Updated**: Always update when modifying any content.
6. **Comprehension check first**: The architect comprehension check (Step 2) catches misunderstandings before requirements review and design. Do not skip it — a vague todo leads to unreliable requirements review and plan rewrites.
7. **Requirements review before design**: Never skip the business requirements review (Step 3). The most expensive bugs come from contradicting existing requirements — especially implicit dependencies.
8. **Verification resources**: When the project has verification resources (design projects, sample projects, integration suites), use them. Compilation and test results are the source of truth for scope claims.
9. **Agent phasing**: The architect identifies phases benefiting from fresh agents during planning. The orchestrator follows this phasing during implementation, invoking fresh agent instances for each identified phase.
10. **Documentation deliverables**: Identify expected documentation deliverables during planning (Step 4) or implementation contract (Step 6), not as an afterthought.
11. **Assertion-trace workflow**: The assertion-trace workflow in Steps 4-5 is the primary defense against logic errors. Do not skip or abbreviate it.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`
- Documentation step guide: `references/documentation-step-guide.md`

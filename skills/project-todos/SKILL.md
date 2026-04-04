---
name: project-todos
version: 5.0.0
description: This skill should be used when the user asks to "create a todo", "add a plan", "plan this work", "track this work", "document this task", "complete a todo", "verify the implementation", "run architect verification", "start the implementation", "update docs for this feature", "what's the next step", "what's the plan status", "resume the todo", "what's blocked", "pick up where we left off", "design this feature", "check business requirements", "review requirements", "review against requirements", "check for requirement conflicts", or mentions managing project todos, plans, and multi-agent workflows. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration through the full design-review-implement-verify-document lifecycle.
---

# Project Todos, Plans, and Agent Workflow

Manage significant project work using structured markdown files and coordinate agent collaboration through the full design-review-implement-verify-document lifecycle.

## Core Rule: Agents Review, Orchestrator Implements

The orchestrator is the user's design partner AND implementer. Agents handle reviews, verification, and documentation — never implementation.

### What the Orchestrator Does

- **Author all plan content** — business rules, test scenarios, domain model design, implementation steps — everything in the plan file
- **Write all shared files** — the orchestrator is the ONLY writer of todo files, plan files, and status fields
- **Analyze the codebase with the user** — the orchestrator is the user's design partner
- **Implement code changes in conversation with the user** — the user watches, steers, and course-corrects in real time
- Track implementation progress through conversation tasks
- Invoke agents for reviews, research, verification, and documentation
- Present agent findings and concerns to the user
- Make workflow decisions (which agent to invoke next, when to loop)
- Set plan/todo status based on agent verdicts

### What Agents Do

- **Review and validate** — requirements review, architecture validation, code review, verification
- **Research and answer questions** — investigate codebase, trace patterns, check legacy behavior
- **Update documentation** — the documenter agent writes to docs/ files (its specialized purpose)
- **Write to their own memory files** — agents store findings in their memory file, never in the plan or todo
- **Report back to the orchestrator** — findings, verdicts, and concerns come back as the agent's response

### What Agents Do NOT Do

- **NEVER** write to plan files or todo files — only the orchestrator writes shared documents
- **NEVER** set plan or todo status — only the orchestrator manages status
- **NEVER** address other agents — agents report to the orchestrator, not to each other

### Mandatory Steps the Orchestrator Cannot Skip

- Requirements review (Step 2), architect validation (Step 3), developer code review (Step 5), and verification (Step 6) are mandatory
- The orchestrator cannot mark implementation as verified — agents must independently verify
- Work cannot be marked Complete without verification passing (Step 6, both parts)

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
    +-- developer.md                   # Developer code review notes
    +-- requirements-reviewer.md       # Reviewer's private notes
    +-- requirements-documenter.md     # Documenter's private notes
```

### What Lives in Memory Files vs. Plan

| Content | Location | Written By |
|---------|----------|------------|
| All design content (Overview, Business Rules, Test Scenarios, Approach, Domain Model, Implementation Steps, Acceptance Criteria) | Plan file | Orchestrator |
| Plan status, todo status, review verdicts (one-liners) | Plan/todo files | Orchestrator |
| Architect validation findings (codebase analysis, concerns, verdict) | `architect.md` | Architect agent |
| Architect verification (post-implementation verdict) | `architect.md` | Architect agent |
| Developer code review (assertion traces, concerns, verdict) | `developer.md` | Developer agent |
| Requirements review findings (relevant rules, gaps, contradictions, verdict) | `requirements-reviewer.md` | Reviewer agent |
| Requirements verification (post-implementation) | `requirements-reviewer.md` | Reviewer agent |
| Documentation tracking (files updated, deliverables) | `requirements-documenter.md` | Documenter agent |

---

## Agent Collaboration Workflow

This is the full lifecycle for significant work. Each step uses the appropriate agent or the orchestrator.

### Prerequisites

Before starting the workflow, check for project-specific resources:

1. **Agents** — Check `.claude/agents/` for project-specific agents: architect, developer (for code review), specialized, documentation, **business-requirements-reviewer**, and **business-requirements-documenter**. Also check `~/.claude/agents/` for general agents. **Project-specific agents always take priority over user-level agents of the same role.** Fall back to general-purpose agents only when no project-specific agent exists for that role.
2. **Business requirements** — Check the project's CLAUDE.md for where business requirements documentation lives (business rules, user stories, workflows, data dictionaries). **If CLAUDE.md does not clearly indicate where business requirements are documented, STOP and ask the user before proceeding.** This information is required for Step 2.
3. **Domain skill** — Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
4. **Verification resources** — Check if the project has additional verification resources (e.g., sample projects, integration test suites) that the architect should use to verify scope claims.

### Agent Strategy

Every agent invocation is a **fresh** Agent call. Provide full context (todo path, plan path, relevant instructions) each time. Do not attempt to resume agents across steps.

### Step 1: Create Todo and Draft Plan (User + Orchestrator)

**The user is the designer.** The orchestrator is the user's design partner — analyzing code, tracing patterns, fetching data, and helping structure the design.

#### Part A: Create the Todo

1. Capture the user's description of the problem and desired outcome
2. **Analyze the codebase together** — search code, trace patterns, identify affected aggregates, check existing tests, read prior completed todos/plans. The orchestrator actively helps the user understand the current state and implications.
3. Create the todo file in `docs/todos/` using the todo template
4. Set status to "In Progress"

#### Part B: Draft the Plan

Working in conversation or plan mode, collaborate with the user to design the complete solution:

1. Create the plan file in `docs/plans/` using the plan template
2. Link the plan to the todo (update both files)
3. Fill in ALL sections together with the user:
   - **Overview** — what the plan addresses
   - **Approach** — high-level strategy
   - **Design** — detailed design (architecture, file structure, data flow)
   - **Business Rules (Testable Assertions)** — extract ALL business rules from the design as numbered, unambiguous WHEN/THEN assertions. Trace each to an existing documented requirement where one exists. New assertions must be marked as NEW.
   - **Test Scenarios** — concrete scenarios for each business rule with specific inputs and expected results
   - **Domain Model Behavioral Design** — computed properties, visibility flags, reactive rules, validation rules
   - **Implementation Steps** — ordered steps for implementation
   - **Acceptance Criteria** — what "done" looks like
   - **Dependencies** and **Risks**
4. Set plan status to `Draft`

**The plan should reflect the user's design decisions.** The orchestrator helps structure and flesh out the design but does not override the user's choices.

### Step 2: Business Requirements Review

**Purpose:** Compare the user's draft plan against the project's EXISTING DOCUMENTED business requirements before finalizing. This catches contradictions that would otherwise become bugs — especially implicit dependencies where changing one behavior breaks assumptions in other parts of the system.

Invoke the **business-requirements-reviewer** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The todo file path
- The plan file path
- The reviewer's memory file path: `docs/plans/{plan-name}.memory/requirements-reviewer.md`
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Review this todo and draft plan against the project's existing business requirements. Write your findings to your memory file at [path]. Report back with your verdict and a summary of findings. VETO if contradictions are found."

The reviewer agent should:
1. Read the todo and draft plan to understand the problem, proposed solution, and design
2. Search requirements docs for rules, user stories, workflows, and data definitions related to the scope
3. Identify relevant requirements, gaps, and contradictions
4. Pay special attention to **implicit dependencies** — changes that technically work but alter behavior governed by other business rules
5. Write detailed findings to their **memory file** (relevant requirements found, gaps, contradictions, recommendations)
6. Report back to the orchestrator with: verdict (APPROVED or VETOED), summary of findings

**After the reviewer reports back:**
- The orchestrator records the verdict and a one-line summary in the todo's **Requirements Review** section
- Full findings stay in the reviewer's memory file — the orchestrator reads it when needed, not copied into the plan

**If VETOED:**
1. Present the specific contradictions to the user, including exact requirement references, file paths, and why they conflict with the proposed work
2. **STOP.** The user decides how to resolve the contradiction — whether to modify the plan, update outdated requirements, override, or take a different path entirely
3. After the user provides direction, update the plan accordingly. If requirements need updating, invoke the appropriate agent. Then re-invoke the reviewer to confirm the contradiction is resolved
4. Repeat until APPROVED

### Step 3: Architect Validation

**Purpose:** The architect performs a deep codebase dive to validate the user's complete plan — checking that business rules are correct, test scenarios are adequate, domain model design is sound, and the approach is feasible. The architect is a **validator**, not the author.

Set plan status to `Under Review (Architect)` before invoking the agent.

Invoke the **architect agent** with:
- The plan file path (all sections already populated by the orchestrator)
- The todo file path
- The architect's memory file path: `docs/plans/{plan-name}.memory/architect.md`
- Any domain skill references found in prerequisites
- The reviewer's memory file path (so the architect can read it for requirements context if needed)
- Instruction: "Validate this plan. Perform a deep codebase analysis. Check that the business rules are correct and complete, test scenarios are adequate, domain model design is sound, and the approach is feasible. The reviewer's findings are in [reviewer memory path] if you need requirements context. Write your findings to your memory file at [path]. Report back with your verdict."

The architect agent should:
1. Read the complete plan (all sections already filled by the orchestrator)
2. **Perform a deep codebase dive** — examine affected aggregates, existing patterns, related tests, repository implementations. Document files examined.
3. **Validate business rules** — Are the assertions correct? Are any missing? Are any ambiguous? If the architect finds issues with the assertions, report them — don't rewrite them.
4. **Validate test scenarios** — Are they adequate? Do they cover the business rules? Are any missing?
5. **Validate domain model design** — Are computed properties, visibility flags, reactive rules, and validation rules correctly designed?
6. **Validate the approach** against codebase reality:
   - Are aggregate boundaries correct?
   - Do proposed changes conflict with existing patterns?
   - Are there affected tests the user didn't account for?
   - Is the implementation approach feasible given the framework constraints?
7. If verification resources exist, verify scope claims using them
8. Write all findings to the architect's **memory file** (codebase analysis, concerns, verdict)
9. Report back to the orchestrator with: verdict (Approved, Concerns, or Rejected), summary of findings

The orchestrator updates plan status based on the verdict:
- Approved: `Ready for Implementation`
- Concerns/Rejected: `Concerns Raised (Architect)`

**If Concerns or Rejected:**
1. Present the architect's findings to the user
2. The user decides how to address them — modify the plan, override, or ask for more detail
3. After the user updates the plan, re-invoke the architect to review changes
4. Repeat until Approved

### Step 4: Implementation (Orchestrator + User)

**The orchestrator implements code changes directly in conversation with the user.**

The orchestrator should:
1. Read the plan's Implementation Steps, Business Rules, and Domain Model Behavioral Design
2. Work through the implementation steps in order, in conversation with the user
3. Run tests at natural checkpoints (after completing a logical unit of work)
4. **STOP and report** if out-of-scope tests fail. The project's CLAUDE.md defines which tests are "sacred" (existing tests are never gutted to make new code pass). When an out-of-scope test fails, present it to the user with: "Test X started failing. It tests [feature], which is outside the current task. Should I (1) fix the underlying issue, (2) add to the bug list, or (3) investigate further?"
5. **Do NOT update documentation markdown** — skill markdown, user-facing docs, and release notes are handled in Step 7 by the documenter agent. Implementation scope is source code only. Code comments (XML docs) on modified code are in scope.
6. When implementation is complete, run all builds and tests. Set plan status to `Awaiting Code Review`.

**Advantages of orchestrator implementation:**
- The user can course-correct in real time ("wait, not that approach — try this instead")
- No context loss between implementation phases
- Ambiguities are resolved immediately through conversation
- The feedback loop is tight and natural

### Step 5: Developer Code Review

**Purpose:** An independent agent reviews the actual code against the plan's business rules and design. This catches logic errors, missed assertions, and design drift that the orchestrator and user may have missed during implementation.

Invoke the **developer agent** with:
- The plan file path
- The developer's memory file path: `docs/plans/{plan-name}.memory/developer.md`
- A summary of what was implemented: files changed, tests written, test results
- Instruction: "Review the implementation against the plan's business rules and design. For EACH business rule assertion, trace through the actual code and verify it holds. Check test coverage for each test scenario. Write findings to your agent memory file at [path]."

The developer agent should:
1. Read the plan's Business Rules (Testable Assertions) and Test Scenarios
2. Read the actual code files that were changed
3. **For EACH business rule assertion**, trace through the real code to verify it holds. Create a "Code Review Trace" table in the developer's memory file. Each entry must cite the specific file, method, and line where the assertion is satisfied. Entries without specifics are insufficient.
4. **For EACH test scenario**, verify a corresponding test method exists and covers the scenario
5. Check for design drift — does the implementation match the plan's approach?
6. Check for logic errors, missed edge cases, and unhandled conditions
7. Write findings to the developer's memory file
8. Render a verdict:
   - **Approved** — Code matches plan, all assertions verified, adequate test coverage. Proceed to Step 6 (Verification).
   - **Concerns** — Issues found that need addressing. Return concerns to the orchestrator.

**If Concerns:**
1. Present the developer's concerns to the user (read from `developer.md`)
2. The orchestrator addresses the issues in conversation with the user (fix code, add tests, etc.)
3. Re-invoke the developer agent for re-review
4. Repeat until Approved

When approved, the orchestrator sets plan status to `Awaiting Verification`.

### Step 6: Verification (Architect + Requirements)

**The orchestrator may NOT mark work as Complete. Verification is mandatory.**

This step has two parts. Both must pass before proceeding. See `references/verification-step-guide.md` for detailed agent invocation instructions.

#### Part A: Architect Verification

Invoke the **architect agent** to independently verify the implementation:
- Run all builds and tests (do NOT trust previously reported results)
- Cross-check every test scenario against actual test methods
- Verify implementation matches the plan's design
- Zero tolerance for test failures — any failure is SENT BACK

The architect reports back with verdict and findings. The orchestrator reads the architect's memory file for details.

Verdicts: **VERIFIED** (proceed to Part B) or **SENT BACK** (orchestrator sets plan status to "Sent Back", fixes issues in conversation with user).

**Critical rule**: Any test failure — even one classified as "pre-existing" — must be reported. Only the user can decide whether a failure is acceptable.

#### Part B: Requirements Verification

**Only if Part A passes (VERIFIED).**

Invoke the **business-requirements-reviewer** agent to confirm the implementation satisfies documented business requirements:
- Trace each relevant requirement through the implementation
- Check for unintended side effects on other business rules
- Write findings to the reviewer's memory file
- Report back with verdict

The reviewer reports back. The orchestrator reads the reviewer's memory file for details and sets plan status accordingly.

Verdicts: **REQUIREMENTS SATISFIED** (proceed to Step 7) or **REQUIREMENTS VIOLATION** (orchestrator sets plan status to "Sent Back").

### Step 7: Requirements Documentation

**Purpose:** Update the project's business requirements documentation to reflect what was actually implemented — new rules, changed rules, resolved gaps. This closes the loop: the reviewer identified the requirements landscape in Step 2, and now the documentation sources are updated to stay current.

Every project organizes documentation differently. The documenter agent and the project's CLAUDE.md provide the project-specific knowledge of where requirements live and how they're structured. This step defines the workflow, not the project details.

#### Part A: Requirements Documentation

Invoke the **business-requirements-documenter** agent (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`) with:
- The plan file path
- The todo file path
- The documenter's memory file path: `docs/plans/{plan-name}.memory/requirements-documenter.md`
- The reviewer's memory file path: `docs/plans/{plan-name}.memory/requirements-reviewer.md` (for requirements context)
- A summary of what was implemented (files changed, test results)
- The project's business requirements locations (from CLAUDE.md, identified in Prerequisites)
- Instruction: "Update business requirements documentation to reflect the completed implementation. The reviewer's memory file has the requirements context. Add new rules, update changed rules, resolve gaps. If source code changes are needed (code comments, samples, design project tests), list them as Developer Deliverables in your memory file — do NOT modify source code. Write all documentation tracking to your agent memory file at [path]."

The documenter agent should:
1. Read the reviewer's memory file for requirements context, and the plan's Business Rules (Testable Assertions) section
2. Review the implementation summary (relayed in the spawn prompt)
3. Compare: identify new requirements (marked NEW in the assertions), changed requirements, and gaps that were filled
4. Update requirements documentation — new rules, changed rules, filled gaps, affected workflows
5. If source code changes are needed (code comments, samples, design project tests), list them in the documenter's memory file as **Developer Deliverables** — the orchestrator handles these directly
6. Record all work in the documenter's memory file (files updated, deliverables completed)
7. Report back to the orchestrator with: summary of changes, any developer deliverables needed

The orchestrator sets plan status to "Requirements Documented" after the documenter reports back.

**Critical rule**: Document what was *implemented*, not what was *planned*. If the implementation diverged from the plan, the documentation must match the implementation.

**Developer Deliverables**: If the documenter identified source code changes needed (read from the documenter's memory file), the orchestrator makes them directly in conversation with the user. Build and test after changes.

#### Part B: General Documentation (if applicable)

Invoke a fresh **documentation agent** (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/` such as `docs-writer`; use the orchestrator as a final fallback if no documentation agent exists).

If the plan identifies non-requirements documentation deliverables (API docs, README changes, migration guides, architecture docs, getting-started updates), invoke the documentation agent with:
- The plan file path
- The todo file path
- Instruction: "Update non-requirements documentation affected by this implementation."

After all applicable parts complete, set plan status to "Documentation Complete."

See `references/documentation-step-guide.md` for detailed guidance.

### Step 8: Completion

**Only after verification has passed (Step 6, both parts) and documentation is complete (or N/A) from Step 7.**

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
- **Tasks**: Workflow steps only (requirements review, architect review, implementation, code review, verification, etc.)
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

For valid plan status values, see `references/plan-template.md`.

### Plan Workflow Sections

Plans that go through the agent collaboration workflow contain design sections only. Workflow state (reviews, progress, evidence, verification results) is stored in agent memory files — see the **Agent Memory Files** section above.

**In the plan file** (all content written by the orchestrator):

- All design sections: Overview, Approach, Design, Implementation Steps, Acceptance Criteria
- **Business Rules (Testable Assertions)** — Orchestrator writes during Step 1
- **Test Scenarios** — Orchestrator writes during Step 1
- **Domain Model Behavioral Design** — Orchestrator writes during Step 1

**In agent memory files** (private findings — agents write here, orchestrator reads):

- **Architect validation** (codebase analysis, concerns, verdict), **Architect verification** (post-implementation) -> `architect.md`
- **Developer code review** (assertion traces against actual code, concerns, verdict) -> `developer.md`
- **Requirements review findings** (relevant rules, gaps, contradictions, verdict) -> `requirements-reviewer.md`
- **Requirements verification** (post-implementation) -> `requirements-reviewer.md`
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

1. Create todo and draft complete plan with the user (Step 1) — orchestrator writes all sections
2. Business requirements review (Step 2) — reviewer reports findings, orchestrator writes into todo and plan
3. Architect validation (Step 3) — architect validates the plan, reports concerns or approval
4. Implementation (Step 4) — orchestrator implements in conversation with the user
5. Developer code review (Step 5) — developer reviews actual code against plan's business rules, reports back
6. Verification (Step 6) — architect verifies builds/tests, reviewer verifies requirements, both report back
7. Documentation (Step 7) — documenter updates requirements docs, reports back; orchestrator handles source code deliverables
8. Completion (Step 8) — orchestrator marks complete only after both verifications pass

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
   - `Ready for Implementation` -> Step 4 (orchestrator implements in conversation)
   - `In Progress` -> Step 4 (implementation continues in conversation)
   - `Awaiting Code Review` -> Step 5 (developer code review)
   - `Code Review Concerns` -> Step 5 (orchestrator addresses concerns, re-invoke developer)
   - `Awaiting Verification` -> Step 6 (verification). Read the developer's memory file to see what the code review confirmed.
   - `Sent Back` -> Read the architect's memory file and/or reviewer's memory file to determine which verification failed and what needs fixing. The orchestrator fixes issues in conversation with the user, then returns to Step 5 (code review) or Step 6 (verification) as appropriate.
   - `Requirements Documented` -> Read the documenter's memory file for pending Developer Deliverables (from Part A). If none, proceed to Part B (general documentation, if applicable) or Step 8 (completion).
   - `Documentation Complete` -> Step 8 (completion)
4. Invoke a fresh agent for review/verification steps, providing the todo path, plan path, and agent memory file path. Include relevant context from other agents' memory files in the spawn prompt (the fresh agent must NOT read other agents' memory files directly).

---

## Best Practices

1. **Status accuracy**: Update status fields promptly as workflow progresses.
2. **Progress logging**: Update progress log as work happens, not just at the end.
3. **Link maintenance**: Always update both files when creating links.
4. **Multiple plans OK**: A todo can have multiple plans. One todo per file.
5. **Last Updated**: Always update when modifying any content.
6. **Requirements review before architect**: Never skip the business requirements review (Step 2). The most expensive bugs come from contradicting existing requirements — especially implicit dependencies.
7. **Verification resources**: When the project has verification resources (design projects, sample projects, integration suites), use them. Compilation and test results are the source of truth for scope claims.
8. **Documentation deliverables**: Identify expected documentation deliverables during planning, not as an afterthought.
9. **Code review catches what conversation misses**: The developer code review in Step 5 traces assertions against real code. This is more reliable than reviewing a plan because it verifies what was actually built, not what was intended.
10. **Architect flags issues = design needs work**: If the architect reports that business rules are ambiguous or test scenarios have gaps, the orchestrator addresses this in conversation with the user before re-invoking the architect.
11. **Course-correct in conversation**: The orchestrator implements in conversation specifically so the user can steer. When something feels wrong, change direction immediately rather than completing the wrong approach.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`
- Verification step guide: `references/verification-step-guide.md` — detailed Step 6 agent invocation instructions
- Documentation step guide: `references/documentation-step-guide.md` — detailed Step 7 agent invocation instructions
- Agent migration guide (v4 -> v5): `references/agent-migration-v5.md`
- Agent migration guide (v2 -> v3): `references/agent-migration-v3.md`
- Agent migration guide (v1 -> v2): `references/agent-memory-migration.md`
- Shared agent memory pattern: `~/.claude/skills/shared/references/agent-memory.md` — key rules, base format, orchestrator responsibilities

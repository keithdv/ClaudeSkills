---
name: project-todos
description: This skill should be used when the user asks to "create a todo", "add a plan", "track this work", "document this task", "complete a todo", "verify the implementation", "run architect verification", "hand off to the developer", "update docs for this feature", "what's the next step", "resume the todo", "what's blocked", "pick up where we left off", or mentions managing project todos, plans, and multi-agent workflows. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration (architect, developer, UI, documentation) through the full design-review-implement-verify-document lifecycle.
---

# Project Todos, Plans, and Agent Workflow

Manage significant project work using structured markdown files and coordinate agent collaboration through the full design-review-implement-document lifecycle.

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

1. **Architect agent** - Check `.claude/agents/` for a project-specific architect agent. Use it if found; otherwise use a general-purpose agent for design work.
2. **Developer agent** - Check `.claude/agents/` for a project-specific developer agent. Use it if found; otherwise use a general-purpose agent for review and implementation.
3. **Specialized implementation agents** - Check `.claude/agents/` for specialized implementation agents (e.g., UI agents, integration agents). These handle specific portions of Step 5 implementation work. For example, a Blazor UI agent handles `.razor` and `.razor.css` files while the developer agent handles domain models, repositories, and tests.
4. **Documentation agent** - Check `.claude/agents/` for a documentation-specific agent.
5. **Domain skill** - Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
6. **Design projects** - Check if the project has design/stub projects (e.g., `src/Design/`) used for compilation verification. The architect agent should use these to verify scope claims.
7. **Documentation samples** - Check if the project has documentation sample projects. The documentation agent should use these when updating docs.

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
4. Create a plan in `docs/plans/` using the plan template
5. **If design projects exist**: verify scope claims by writing compilable code. Leave failing code as acceptance criteria for features that need implementation.
6. Link the plan to the todo (update both files)
7. Set plan status to "Draft (Architect)"
8. Hand off to developer review

### Step 3: Developer Review

Invoke the **developer agent** with:
- The plan file path
- The todo file path
- Instruction: "Review this plan for completeness, correctness, and implementability. Raise concerns or approve."

The developer agent should:
1. Read and understand the plan
2. Investigate the codebase to verify plan claims
3. **If the architect provided design project verification**: confirm the evidence exists and makes sense
4. **If the architect did NOT provide design project verification** (and design projects exist): reject the plan back to the architect
5. Check for gaps, ambiguities, edge cases, and risks
6. Render a verdict: **Concerns Raised** or **Approved**

### Step 4: Clarification Loop

If the developer raises concerns:
1. Present concerns to the user
2. Ask the user: "Would you like to clarify these yourself, or should the architect agent address them?"
3. Based on user's choice:
   - **User clarifies**: Update the plan with user's answers, return to Step 3
   - **Architect clarifies**: Invoke architect agent with the concerns, then return to Step 3
4. Repeat until the developer approves

When the developer approves:
- Developer creates an **Implementation Contract** in the plan (scope, out-of-scope, verification gates)
- If design projects have failing acceptance criteria code, list them in the contract
- Set plan status to "Ready for Implementation"

### Step 5: Implementation

Invoke the **developer agent** for implementation with:
- The plan file path (with implementation contract)
- Instruction: "Implement the approved plan following the implementation contract"

**Specialized agent routing**: If the implementation includes work that matches a specialized agent's scope (identified in Prerequisites step 3), split the implementation:
- **Developer agent**: Domain models, repositories, services, tests, backend logic
- **Specialized UI agent** (if found): Blazor pages, components, `.razor` files, CSS, layout
- **Other specialized agents**: Route according to their declared file scope and capabilities

Coordinate by having the developer agent complete backend work first (or in parallel if independent), then invoke the specialized agent for its portion with the same plan file.

**Fresh agent strategy**: Evaluate which implementation portions would benefit from fresh agents. Consider using fresh agents for portions that are:
- Independent of prior implementation context
- Parallelizable with other portions
- Large enough to benefit from a clean context window
- Focused on a single, well-defined deliverable

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

1. Verify architect verification verdict is "VERIFIED"
2. Verify documentation step is complete (plan status is "Documentation Complete") or was marked N/A
3. Update todo status to "Complete" and Last Updated date
3. Fill in the Results/Conclusions section
4. Move todo and associated plans to `completed/` directories
5. Update plan statuses to "Complete"

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

### Filename Convention

Same rules as todos. Be descriptive of the plan's purpose.

Examples: `authentication-fix-design.md`, `dark-mode-implementation.md`

### Write the Plan File

Use the template from `references/plan-template.md`. Fill in:

- **Title**: Descriptive plan title
- **Date**: Today's date
- **Related Todo**: Relative link to parent todo
- **Status**: "Draft" (default)
- **Last Updated**: Same as Date
- Core sections: Overview, Approach, Design, Implementation Steps, Acceptance Criteria, Dependencies, Risks

### Plan Workflow Sections

Plans that go through the agent collaboration workflow should include these additional sections.

> **Sync note**: These sections are also present in `references/plan-template.md` as a clean starting point. If you update one, update the other to match.

```markdown
---

## Architectural Verification

[Architect completes before handoff]

**Scope Table:** [Pattern/feature matrix showing what's affected]

**Design Project Verification:** [If design projects exist]
- [Feature/Pattern]: Verified | Needs Implementation
  - Evidence: [file path or compiler error]

**Breaking Changes:** Yes/No - [Explanation]

**Codebase Analysis:** [Files examined, patterns found]

---

## Developer Review

**Status:** Not Started | Under Review | Concerns Raised | Approved
**Reviewed:** [date]

**Concerns:** [List issues, or "None - ready for implementation"]

---

## Implementation Contract

**Created:** [date]
**Approved by:** [developer agent]

### Acceptance Criteria

[If design projects have failing code, list them here as acceptance criteria]

### In Scope

- [ ] Specific change 1
- [ ] Specific change 2
- [ ] Test to add
- [ ] Checkpoint: Run tests after X

### Out of Scope

- [Feature X - reason]

### Verification Gates

1. After [milestone]: [What must be true]
2. Final: All tests pass, design projects compile

### Stop Conditions

If any occur, STOP and report:
- Out-of-scope test fails
- Architectural contradiction discovered

---

## Implementation Progress

**Started:** [date]

**[Milestone 1]:** [Name]
- [ ] Step 1
- [ ] Step 2
- [ ] **Verification**: [results]

---

## Completion Evidence

- **Tests Passing:** [Output or summary]
- **Design Projects Compile:** [Yes/No/N/A]
- **All Contract Items:** [Confirmed complete]

---

## Documentation

**Agent:** [documentation agent name, or "developer" if no documentation agent]
**Completed:** [date]

### Expected Deliverables

[Architect or developer lists what documentation should be updated — filled during planning or implementation]

- [ ] [File or area 1]
- [ ] [File or area 2]
- [ ] Skill updates: [Yes/No/N/A]
- [ ] Sample updates: [Yes/No/N/A]

### Files Updated

[Documentation agent fills this after completing work]

- [file path]: [what was changed]

---

## Architect Verification

[Architect fills this section after independently verifying the developer's work.]

**Verified:** [date]
**Verdict:** VERIFIED | SENT BACK

**Independent test results:**
[Build and test output]

**Design match:** [Does the implementation match the original plan?]

**Issues found:** [List any issues, or "None"]
```

### Plan Status Values

- `Draft` - Initial creation
- `Draft (Architect)` - Architect working on design
- `Under Review (Developer)` - Developer reviewing
- `Concerns Raised` - Developer found issues
- `Ready for Implementation` - Approved, contract created
- `In Progress` - Implementation underway
- `Awaiting Verification` - Developer reports done, architect must verify
- `Sent Back` - Architect verification failed, developer must fix
- `Documentation Complete` - Documentation step finished
- `Complete` - Architect verified, moved to completed/

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

---

## Best Practices

1. **File naming**: Concise and descriptive. No dates in filenames.
2. **Status accuracy**: Update status fields promptly as workflow progresses.
3. **Progress logging**: Update progress log as work happens, not just at the end.
4. **Link maintenance**: Always update both files when creating links.
5. **One todo per file**: Don't combine multiple todos.
6. **Multiple plans OK**: A todo can have multiple plans.
7. **Last Updated**: Always update when modifying any content.
8. **Agent handoffs**: Each agent transition should reference the file paths being handed off.
9. **Design project verification**: When the project has design/stub projects, the compiler is the source of truth for scope claims. Grepping code is secondary.
10. **Fresh agents**: Evaluate at implementation time whether portions benefit from fresh agent context. Don't force it; let the orchestrator decide based on independence and context size.
11. **Documentation deliverables**: Identify expected documentation deliverables during planning (Step 2) or implementation contract (Step 4), not as an afterthought.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`
- Documentation step guide: `references/documentation-step-guide.md`

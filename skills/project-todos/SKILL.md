---
name: project-todos
description: Use when the user asks to "create a todo", "add a plan", "track this work", "document this task", "complete a todo", or mentions managing project todos and plans. Provides the structured workflow for creating, managing, and linking todo/plan files, and orchestrating agent collaboration (architect, developer, documentation) through the full lifecycle.
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

This is the full lifecycle for significant work. Each phase uses the appropriate agent.

### Prerequisites

Before starting the workflow, check for project-specific resources:

1. **Architect agent** - Check `.claude/agents/` for a project-specific architect agent. Use it if found; otherwise use a general-purpose agent for design work.
2. **Developer agent** - Check `.claude/agents/` for a project-specific developer agent. Use it if found; otherwise use a general-purpose agent for review and implementation.
3. **Documentation agent** - Check `.claude/agents/` for a documentation-specific agent.
4. **Domain skill** - Check if the project has domain-specific skills (in `skills/` or `.claude/skills/`) that provide context about the codebase. Reference these when invoking agents so they have domain knowledge.
5. **Design projects** - Check if the project has design/stub projects (e.g., `src/Design/`) used for compilation verification. The architect agent should use these to verify scope claims.
6. **Documentation samples** - Check if the project has documentation sample projects. The documentation agent should use these when updating docs.

### Phase 1: Create Todo

1. Gather information from the user (title, priority, problem, solution)
2. Create the todo file in `docs/todos/` using the todo template
3. Set status to "In Progress"

### Phase 2: Architect Review & Plan Creation

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

### Phase 3: Developer Review

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

### Phase 4: Clarification Loop

If the developer raises concerns:
1. Present concerns to the user
2. Ask the user: "Would you like to clarify these yourself, or should the architect agent address them?"
3. Based on user's choice:
   - **User clarifies**: Update the plan with user's answers, return to Phase 3
   - **Architect clarifies**: Invoke architect agent with the concerns, then return to Phase 3
4. Repeat until the developer approves

When the developer approves:
- Developer creates an **Implementation Contract** in the plan (scope, out-of-scope, verification gates)
- If design projects have failing acceptance criteria code, list them in the contract
- Set plan status to "Ready for Implementation"

### Phase 5: Implementation

Invoke the **developer agent** for implementation with:
- The plan file path (with implementation contract)
- Instruction: "Implement the approved plan following the implementation contract"

**Fresh agent strategy**: Evaluate which implementation phases would benefit from fresh agents. Consider using fresh agents for phases that are:
- Independent of prior implementation context
- Parallelizable with other phases
- Large enough to benefit from a clean context window
- Focused on a single, well-defined deliverable

The developer agent should:
1. Work through the implementation contract checklist
2. Run tests at each verification gate
3. **STOP and report** if out-of-scope tests fail or architectural contradictions are discovered
4. Collect evidence (test output, generated code samples)

### Phase 6: Documentation

Invoke the **documentation agent** (if one exists) for documentation phases:
- Updated documentation files
- Documentation samples
- Skill updates (if the project has domain skills)

If no documentation agent exists, the developer agent handles documentation.

### Phase 7: Completion

1. Verify all implementation contract items are checked
2. Verify all tests pass
3. If design projects exist, verify they compile
4. Update todo status to "Complete"
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

Plans that go through the agent collaboration workflow should include these additional sections:

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

1. After Phase 1: [What must be true]
2. Final: All tests pass, design projects compile

### Stop Conditions

If any occur, STOP and report:
- Out-of-scope test fails
- Architectural contradiction discovered

---

## Implementation Progress

**Started:** [date]

**Phase 1:** [Name]
- [ ] Step 1
- [ ] Step 2
- [ ] **Verification**: [results]

---

## Completion Evidence

- **Tests Passing:** [Output or summary]
- **Design Projects Compile:** [Yes/No/N/A]
- **All Contract Items:** [Confirmed complete]
```

### Plan Status Values

- `Draft` - Initial creation
- `Draft (Architect)` - Architect working on design
- `Under Review (Developer)` - Developer reviewing
- `Concerns Raised` - Developer found issues
- `Ready for Implementation` - Approved, contract created
- `In Progress` - Implementation underway
- `Complete` - Done, moved to completed/

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

1. Create todo (Phase 1)
2. Invoke architect agent (Phase 2)
3. Developer reviews (Phase 3)
4. Clarification loop if needed (Phase 4)
5. Implementation (Phase 5)
6. Documentation (Phase 6)
7. Completion (Phase 7)

### Adding a Plan to Existing Todo

1. Read existing todo for context
2. Write plan file with template
3. Link plan to todo (both files)
4. Continue with Phase 3 (developer review)

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
10. **Fresh agents**: Evaluate at implementation time whether phases benefit from fresh agent context. Don't force it; let the orchestrator decide based on phase independence and context size.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`

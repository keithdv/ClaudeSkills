# Documentation Step Guide

Every project organizes documentation differently. The documenter agent and the project's CLAUDE.md provide the project-specific knowledge of where requirements live and how they're structured. This guide defines the workflow steps and agent responsibilities, not the project details.

Detailed guidance for Step 7 (Documentation) of the agent collaboration workflow.

## When Documentation Is Required

Documentation is required when the implementation:
- Adds or changes behavior governed by documented business rules
- Introduces new domain concepts or entities
- Changes existing workflows or business processes
- Affects user-facing functionality covered by requirements docs

Documentation may be skipped (mark N/A) for:
- Internal refactoring with no behavior change
- Bug fixes that restore expected behavior
- Test-only changes

## Step 7 Part Structure

Step 7 has two parts with distinct responsibilities:

### Part A: Requirements Documentation (Documenter Agent)

The documenter agent updates the project's business requirements documentation:
- Reads the plan's Business Requirements Context, Business Rules, and the implementation summary (relayed by the orchestrator)
- Adds new rules, updates changed rules, resolves gaps
- If the documenter identifies source code changes needed (e.g., code comments, samples, verification tests), it lists them as **Developer Deliverables** in the documenter's memory file — but does NOT modify source code

The orchestrator handles any Developer Deliverables directly in conversation with the user.

The documenter records all work in the documenter's memory file (files updated, deliverables completed) and sets plan status to "Requirements Documented."

### Part B: General Documentation (Docs Agent or Orchestrator)

Non-requirements documentation — README, architecture docs, migration guides, API docs, getting-started guides.

Only needed if the plan identifies non-requirements documentation deliverables.

Invoke a fresh **documentation agent** (use the project-specific agent from `.claude/agents/` if one exists, otherwise fall back to the general agent at `~/.claude/agents/`, such as `docs-writer`; use the orchestrator as a final fallback if no documentation agent exists) with:
- The plan file path
- The todo file path
- Instruction: "Update non-requirements documentation affected by this implementation."

The documentation agent should:
1. **Read the plan** to understand what was implemented
2. **Identify documentation deliverables** from the plan's Acceptance Criteria or Risks section
3. **Update affected files**, which may include:
   - README or getting-started guides
   - API documentation
   - Architecture documentation
   - Migration guides
4. **Set plan status** to "Documentation Complete"

After all applicable parts complete (Part A + Part B if applicable), the plan status should be "Documentation Complete."

## Quality Criteria

- Documentation matches the implemented behavior (not the plan's design — the actual result)
- New domain concepts or rules are documented with context
- Changed behavior notes what changed and why

## Documentation Does Not Require Separate Verification

Documentation quality is checked during the Completion step (Step 8), not through a separate architect verification cycle. If documentation is materially wrong, the orchestrator can send it back, but this is rare.

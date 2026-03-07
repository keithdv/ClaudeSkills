# Documentation Step Guide

Every project organizes documentation differently. The documenter agent and the project's CLAUDE.md provide the project-specific knowledge of where requirements live and how they're structured. This guide defines the workflow steps and agent responsibilities, not the project details.

Detailed guidance for Step 9 (Documentation) of the agent collaboration workflow.

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

## Invoking the Documentation Agent

Invoke the **documentation agent** with:
- The plan file path
- The todo file path
- Instruction: "Review the completed implementation and update all affected documentation. See the Documentation section of the plan for expected deliverables."

If no documentation agent exists, invoke the **developer agent** with the same instruction.

## Step 9 Part Structure

Step 9 has two parts with distinct responsibilities:

### Part A: Requirements Documentation (Documenter Agent)

The documenter agent updates the project's business requirements documentation:
- Reads the plan's Business Requirements Context, Business Rules, and Completion Evidence
- Adds new rules, updates changed rules, resolves gaps
- If the documenter identifies source code changes needed (e.g., code comments, samples, verification tests), it lists them as **Developer Deliverables** in the plan — but does NOT modify source code

The orchestrator routes any Developer Deliverables to the developer agent as needed.

The documenter records work in the plan's Documentation section and sets plan status to "Requirements Documented."

### Part B: General Documentation (Docs Agent or Developer)

Non-requirements documentation — README, architecture docs, migration guides, API docs, getting-started guides.

Only needed if the plan identifies non-requirements documentation deliverables.

1. **Read the plan** to understand what was implemented
2. **Identify documentation deliverables** from the plan's Documentation section
3. **Update affected files**, which may include:
   - README or getting-started guides
   - API documentation
   - Architecture documentation
   - Migration guides
4. **Record work** in the plan's Documentation section:
   - List each file created or updated
   - Note any documentation deliverables that were N/A and why
5. **Set plan status** to "Documentation Complete"

## Quality Criteria

- Documentation matches the implemented behavior (not the plan's design — the actual result)
- New domain concepts or rules are documented with context
- Changed behavior notes what changed and why

## Documentation Does Not Require Separate Verification

Documentation quality is checked during the Completion step (Step 10), not through a separate architect verification cycle. If documentation is materially wrong, the orchestrator can send it back, but this is rare.

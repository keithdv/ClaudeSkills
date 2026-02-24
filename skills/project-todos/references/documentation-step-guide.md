# Documentation Step Guide

Detailed guidance for Step 7 (Documentation) of the agent collaboration workflow.

## When Documentation Is Required

Documentation is required when the implementation:
- Adds or changes public API surface
- Introduces new patterns or conventions
- Changes existing behavior that other developers rely on
- Affects domain skills (Neatoo, KnockOff, RemoteFactory, etc.)

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

## What the Documentation Agent Should Do

1. **Read the plan** to understand what was implemented
2. **Identify documentation deliverables** from the plan's Documentation section
3. **Update affected files**, which may include:
   - README or getting-started guides
   - API documentation
   - Architecture documentation
   - Domain skill reference files (in `.claude/skills/`)
   - Code comments on public APIs (only where non-obvious)
4. **Update documentation samples** if the project has sample projects
5. **Record work** in the plan's Documentation section:
   - List each file created or updated
   - Note any documentation deliverables that were N/A and why
6. **Set plan status** to "Documentation Complete"

## Quality Criteria

- Documentation matches the implemented behavior (not the plan's design — the actual result)
- New patterns are documented with at least one example
- Changed behavior notes what changed and why
- Skill reference files reflect any new patterns or corrections discovered during implementation

## Documentation Does Not Require Separate Verification

Documentation quality is checked during the Completion step (Step 8), not through a separate architect verification cycle. If documentation is materially wrong, the orchestrator can send it back, but this is rare.

# Documentation Step Guide

Detailed guidance for Step 8 (Documentation) of the agent collaboration workflow.

## When Documentation Is Required

Documentation is required when the implementation:
- Adds or changes public API surface
- Introduces new patterns or conventions
- Changes existing behavior that other developers rely on
- Affects domain skills or framework-specific knowledge bases

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

## Step 8 Part Structure

Step 8 has three parts with distinct responsibilities:

### Part A: Markdown Requirements Documentation (Documenter Agent)

The business-requirements-documenter handles markdown files only:
- User-facing documentation (`docs/`)
- Skill behavioral contract reference files — files encoding what the framework does (e.g., `entities.md`, `collections.md`, `validation.md`, `properties.md`)

The documenter also **identifies** `.cs` changes needed (Design project tests/examples, code comments, samples) and lists them as **Developer Deliverables** in the plan — but does NOT modify `.cs` files.

### Part B: Source Code Requirements Documentation (Developer Agent)

Only if Part A identified Developer Deliverables. The developer agent handles:
- Design project tests and examples (`src/Design/`)
- Framework source code comments (`src/Neatoo/`)
- Documentation samples (`src/samples/`)
- Build and test verification after changes

### Part C: General Documentation (Docs Agent or Developer)

Non-requirements documentation — API docs, README, migration guides, getting-started updates. Also handles **instructional** skill reference files (e.g., `testing.md`, `pitfalls.md`, `blazor.md`) — files that teach how to use the framework rather than encoding behavioral contracts.

### Skill File Boundary

- **Part A** (documenter): Skill reference files encoding **behavioral contracts** — what the framework does, how state properties behave, what factory operations produce, entity lifecycle rules
- **Part C** (docs agent): Skill reference files that are **instructional** — how to test, common pitfalls, integration guides, tutorials

## What the Documentation/Docs Agent Should Do (Part C)

1. **Read the plan** to understand what was implemented
2. **Identify documentation deliverables** from the plan's Documentation section
3. **Update affected files**, which may include:
   - README or getting-started guides
   - API documentation
   - Architecture documentation
   - Instructional skill reference files (`testing.md`, `pitfalls.md`, `blazor.md`)
4. **Update documentation samples** if needed (coordinate with developer if `.cs` samples are involved)
5. **Record work** in the plan's Documentation section:
   - List each file created or updated
   - Note any documentation deliverables that were N/A and why
6. **Set plan status** to "Documentation Complete"

## Quality Criteria

- Documentation matches the implemented behavior (not the plan's design — the actual result)
- New patterns are documented with at least one example
- Changed behavior notes what changed and why
- Behavioral contract skill refs (Part A) encode what the framework does
- Instructional skill refs (Part C) teach how to use the framework

## Documentation Does Not Require Separate Verification

Documentation quality is checked during the Completion step (Step 9), not through a separate architect verification cycle. If documentation is materially wrong, the orchestrator can send it back, but this is rare.

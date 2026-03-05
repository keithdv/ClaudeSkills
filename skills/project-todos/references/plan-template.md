# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft | Draft (Architect) | Under Review (Developer) | Concerns Raised | Ready for Implementation | In Progress | Awaiting Verification | Sent Back | Documentation Complete | Complete
**Last Updated:** YYYY-MM-DD

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

---

## Overview

[Brief description of what this plan addresses]

---

## Business Rules (Testable Assertions)

[Extract ALL business rules as numbered, crisp, unambiguous assertions BEFORE designing the approach. These are the source of truth for the entire plan. Every design decision, implementation step, and test scenario must trace back to one or more assertions here.]

[Format each rule using WHEN/THEN to eliminate ambiguity about what the expected value applies to.]

1. WHEN [conditions], THEN [property/method] RETURNS [expected value]
2. WHEN [conditions], THEN [observable behavior]. Expected: [value]
3. ...

### Test Scenarios

[For each business rule above, provide at least one concrete scenario showing inputs and expected result. These scenarios become acceptance tests.]

| # | Scenario | Inputs / State | Rule(s) | Expected Result |
|---|----------|---------------|---------|-----------------|
| 1 | [Descriptive name] | [Concrete values] | Rule 1 | [Expected value — with brief explanation] |
| 2 | [Descriptive name] | [Concrete values] | Rule 2 | [Expected value — with brief explanation] |
| 3 | ... | ... | ... | ... |

---

## Approach

[How will we solve this? High-level strategy]

---

## Design

[Detailed design - architecture, file structure, data flow, etc.]

---

## Implementation Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

---

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Dependencies

[Any prerequisites, tools, or external factors]

---

## Risks / Considerations

[Things to watch out for, trade-offs, known issues]

---

## Architectural Verification

[Architect completes this section before handoff to developer]

**Scope Table:**
[Pattern/feature matrix showing what is affected and current support status]

**Design Project Verification:**
[If the project has design/stub projects, list verification results here]

- [Feature/Pattern]: Verified | Needs Implementation
  - Evidence: [file path and line, or compiler error]

**Breaking Changes:** Yes/No - [Explanation]

**Codebase Analysis:**
[Files examined and key findings]

---

## Agent Phasing

[Architect identifies which implementation phases benefit from fresh agents. Each phase is a unit of work that can be handed to an agent with clear inputs and expected outputs.]

| Phase | Agent Type | Fresh Agent? | Rationale | Dependencies |
|-------|-----------|-------------|-----------|--------------|
| [Phase 1 name] | [developer/UI/specialized] | [Yes/No] | [Why fresh or continuing] | [Prior phases needed] |
| [Phase 2 name] | [developer/UI/specialized] | [Yes/No] | [Why fresh or continuing] | [Prior phases needed] |

**Parallelizable phases:** [List phases that can run concurrently, if any]

**Notes:** [Any special coordination needed between phases]

---

## Developer Review

**Status:** Not Started
**Reviewed:** [date]

### Assertion Trace Verification

[For EACH business rule assertion in the "Business Rules" section above, trace through the proposed implementation and verify the expected result matches. This is NOT optional — every assertion must have a trace entry. Each Implementation Path entry must cite a specific method name and condition expression. Entries that say "handled correctly" or "matches design" without specifics are insufficient — send back to the architect for detail.]

| Rule # | Implementation Path (method/condition) | Expected Result | Matches Rule? | Notes |
|--------|---------------------------------------|-----------------|---------------|-------|
| 1 | [e.g., `CanAdvanceStep()` line 42: checks `HasSigns && IsConsultation`] | [value] | [YES/NO] | |
| 2 | ... | ... | ... | |

### Concerns

[Developer adds concerns/questions here during review — but ONLY after completing the assertion trace above]

---

## Implementation Contract

[Developer fills this section after approving the plan]

**Created:** [date]
**Approved by:** [developer agent name]

### Design Project Acceptance Criteria

[If design projects have failing code left by the architect, list them here. Implementation is done when they all compile.]

- [ ] `path/to/file:line` - [Description]: [Compiler error] -> Must compile after implementation

### Test Scenario Mapping

[Map each scenario from the Business Rules section to a test method. Every scenario must have a corresponding test.]

| Scenario # | Test Method | Notes |
|------------|-------------|-------|
| 1 | [e.g., `OrderTests.IsSavable_WhenChildEntity_ReturnsFalse()`] | |
| 2 | ... | |

### In Scope

- [ ] File 1: Specific changes
- [ ] File 2: Specific changes
- [ ] Test cases to add (see Test Scenario Mapping above)
- [ ] Checkpoint: Run tests after [milestone]

### Out of Scope

[Explicitly list what will NOT be changed]

### Verification Gates

1. After [milestone]: [What must be true]
2. Final: All tests pass, design projects compile (if applicable)

### Stop Conditions

If any occur, STOP and report:
- Out-of-scope test failure
- Architectural contradiction discovered

---

## Implementation Progress

**Started:** [date]
**Developer:** [agent name]

**[Milestone 1]:** [Name]
- [ ] Step 1
- [ ] Step 2
- [ ] **Verification**: [test results, evidence]

**[Milestone 2]:** [Name]
- [ ] Step 1
- [ ] **Verification**: [test results, evidence]

---

## Completion Evidence

[Developer fills this section, then sets status to "Awaiting Verification" and STOPS.]

**Reported:** [date]

- **Tests Passing:** [Output or summary — report ALL failures, do not classify any as "pre-existing"]
- **Design Projects Compile:** [Yes/No/N/A]
- **All Contract Items:** [Confirmed 100% complete]

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
- [Project/module 1]: [Build result]
- [Project/module 2]: [Build result]
- All tests: [X passed, Y failed]

**Design match:** [Does the implementation match the original plan?]

**Issues found:** [List any issues, or "None"]

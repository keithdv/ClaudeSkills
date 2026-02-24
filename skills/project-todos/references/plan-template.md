# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft | Draft (Architect) | Under Review (Developer) | Concerns Raised | Ready for Implementation | In Progress | Awaiting Verification | Sent Back | Documentation Complete | Complete
**Last Updated:** YYYY-MM-DD

---

## Overview

[Brief description of what this plan addresses]

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

## Developer Review

**Status:** Not Started
**Reviewed:** [date]

**Concerns:**
[Developer adds concerns/questions here during review]

---

## Implementation Contract

[Developer fills this section after approving the plan]

**Created:** [date]
**Approved by:** [developer agent name]

### Design Project Acceptance Criteria

[If design projects have failing code left by the architect, list them here. Implementation is done when they all compile.]

- [ ] `path/to/file.cs:line` - [Description]: [Compiler error] -> Must compile after implementation

### In Scope

- [ ] File 1: Specific changes
- [ ] File 2: Specific changes
- [ ] Test cases to add
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
- Design.Stubs: [Build result]
- Design.Tests: [X passed, Y failed]
- Production code: [Build result]
- Documentation.Samples: [Build result]
- All tests: [X passed, Y failed]

**Design match:** [Does the implementation match the original plan?]

**Issues found:** [List any issues, or "None"]

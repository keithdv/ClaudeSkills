# Verification Step Guide

Detailed guidance for Step 6 (Verification) of the agent collaboration workflow. This step has two parts: technical verification (architect) and requirements verification (reviewer). Both must pass before documentation or completion.

## Part A: Architect Verification

Invoke the **architect agent** with:
- The plan file path
- The todo file path
- The architect's memory file path: `docs/plans/{plan-name}.memory/architect.md`
- A summary of what was implemented: files changed, tests written, build/test results
- The developer code review verdict (relayed by the orchestrator from `docs/plans/{plan-name}.memory/developer.md` — the architect does NOT read `developer.md` directly)
- Instruction: "Perform post-implementation verification. The implementation summary and code review verdict are included below. Independently verify all builds and tests. Cross-check every test scenario. Write your verification verdict to your agent memory file at [path]."

### Architect Verification Process

The architect agent should:

1. Review the implementation summary and code review verdict (relayed in the spawn prompt) to understand what was built and what the code review confirmed
2. **Independently run all builds and tests** — do NOT trust previously reported results
3. **Check EVERY test result** — zero failures allowed. If any test fails, the work is NOT complete, even if failures were classified as "pre-existing"
4. Verify the implementation matches the original design (compare generated code against the plan's expected patterns)
5. **Cross-check test scenarios against actual tests** — For EACH numbered test scenario in the plan's "Test Scenarios" table (or Business Rules section), verify that a corresponding test method exists in the test projects and passes. Specifically:
   - Review the Code Review Trace from the developer's code review (relayed by orchestrator)
   - For each scenario, confirm the mapped test method exists in the codebase (read the file, find the method)
   - Confirm the test passes in the test run output
   - If any scenario has no corresponding test, or the mapped test doesn't exist, this is a **SENT BACK** issue
   - Report coverage: "N of M test scenarios verified with passing tests"
6. If verification resources exist, verify they still pass
7. **Write verification verdict and evidence** to the architect's memory file

### Architect Verdicts

- **VERIFIED**: All builds pass, all tests pass, all test scenarios have corresponding passing tests, implementation matches design -> proceed to Part B
- **SENT BACK**: Failures found OR test scenarios missing coverage -> write issues to architect's memory file, set plan status to "Sent Back", report to orchestrator for fixes

**Critical rule**: Any test failure — even one classified as "pre-existing" — must be reported. Only the user can decide whether a failure is acceptable.

---

## Part B: Requirements Verification

**Only if Part A passes (VERIFIED).** The orchestrator reads the architect's memory file to confirm the verdict before proceeding.

Invoke the **business-requirements-reviewer** agent (same agent resolution as Step 2 — project-specific first, user-level fallback) with:
- The plan file path
- The reviewer's memory file path: `docs/plans/{plan-name}.memory/requirements-reviewer.md`
- A summary of what was implemented (relayed by the orchestrator)
- Instruction: "Perform post-implementation requirements verification. Confirm the implementation satisfies the documented business requirements identified in the Business Requirements Context section. Check for unintended side effects. Write your verification verdict to your agent memory file at [path]."

### Requirements Verification Process

The reviewer agent should:

1. Read the plan's Business Requirements Context section
2. Review the implementation summary (relayed in the spawn prompt)
3. For each requirement identified as relevant, trace through the implementation to verify compliance
4. Check for unintended side effects — changes that technically work but alter behavior governed by other business rules
5. **Write verification findings** to the reviewer's memory file (requirements compliance table, unintended side effects, issues found)

### Requirements Verdicts

- **REQUIREMENTS SATISFIED**: Implementation respects all documented requirements -> proceed to Step 7
- **REQUIREMENTS VIOLATION**: Implementation violates documented requirements -> write violations to memory file, set plan status to "Sent Back", report to orchestrator

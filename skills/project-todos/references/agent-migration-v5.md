# Agent Migration Guide: v4.x to v5.0

**Skill version:** 5.0.0
**Breaking change from 4.x:** Yes — agents shift from semi-autonomous collaborators to read-only reviewers that report back. The orchestrator owns all plan/todo writing, status changes, and implementation.

## What Changed in v5.0

Three fundamental shifts:

1. **Orchestrator writes everything.** The orchestrator (conversation) creates all plan sections — business rules, test scenarios, domain model design — and is the only writer of plan files, todo files, and status fields.

2. **Agents report back, never write to shared files.** Agents write to their own memory files and return findings to the orchestrator. They never write to the plan, never write to the todo, never set status.

3. **No agent-to-agent communication via shared files.** The Business Requirements Context section is removed from the plan. Agent findings stay in memory files. The orchestrator reads memory files and passes relevant context to other agents via spawn prompts.

| Before (v4) | After (v5) |
|-------------|------------|
| Orchestrator creates plan structure, architect fills in Business Rules, Test Scenarios, Domain Model Design | Orchestrator creates the complete plan with the user — ALL sections |
| Architect is "reviewer and enhancer" who writes to the plan | Architect is a validator who reads the plan and reports back |
| Reviewer writes findings into the todo's Requirements Review section | Reviewer writes findings to memory file, orchestrator records verdict + one-liner in todo |
| Plan has Business Requirements Context section (copied from reviewer findings) | Removed — findings stay in reviewer's memory file, read on demand |
| Agents set plan status (e.g., architect sets "Under Review (Developer)") | Only the orchestrator sets plan/todo status |
| Documenter sets plan status to "Requirements Documented" | Documenter reports back, orchestrator sets status |
| short-todo: agents implement code | short-todo: orchestrator implements in conversation |

### Step Changes (project-todos)

| v4 Step | v5 Step | What Changed |
|---------|---------|-------------|
| Step 1: Create Todo + Draft Plan | Step 1: Create Todo + **Complete** Plan | Orchestrator fills ALL sections including Business Rules, Test Scenarios, Domain Model Design |
| Step 2: Requirements Review | Step 2: Requirements Review | Reviewer writes to memory file instead of todo. Orchestrator records verdict. |
| Step 3: Architect Review | Step 3: Architect **Validation** | Architect validates (doesn't write to plan). Reports back. Orchestrator sets status. |
| Step 4: Implementation | Step 4: Implementation | Unchanged — orchestrator implements |
| Step 5: Developer Code Review | Step 5: Developer Code Review | Developer reports back. Orchestrator sets status. |
| Step 6: Verification | Step 6: Verification | Agents report back. Orchestrator sets status. |
| Step 7: Documentation | Step 7: Documentation | Documenter reports back. Orchestrator sets status. |
| Step 8: Completion | Step 8: Completion | Unchanged |

### Step Changes (short-todo)

| v4 Step | v5 Step | What Changed |
|---------|---------|-------------|
| Step 1: Create Todo | Step 1: Create Todo | Unchanged |
| Step 2: Architect Questions | Step 2: Draft Plan (orchestrator + user) | Orchestrator creates the complete plan |
| Step 3: Architect Plan | Step 3: Architect Validation | Architect validates, doesn't create |
| Step 4: Developer Review | Step 4: Implementation (orchestrator) | Orchestrator implements in conversation |
| Step 5: Implementation (developer agent) | Step 5: Developer Code Review | Agent reviews, doesn't implement |
| Step 6: Verification | Step 6: Verification | Agent reports back |
| Step 7: Documentation | Step 7: Documentation | Agent reports back |
| Step 8: Completion | Step 8: Completion | Unchanged |

---

## Template Changes

### Plan Template

- **Removed:** Entire Business Requirements Context section (was ~40 lines of subsections)
- **Changed:** All "Architect fills this section" annotations → "Orchestrator writes this section during Step 1"
- **Changed:** "Recommendations for Architect" → "Recommendations" (in Business Requirements Context, now removed)

### Todo Template

- **Slimmed:** Requirements Review section reduced from detailed subsections to:
  ```
  **Verdict:** Pending | SKIPPED | APPROVED | VETOED
  **Reviewed:** [date]
  **Summary:** [One-line summary. Full details in reviewer's memory file.]
  ```

---

## Agent Migration Checklists

### All Agents

- [ ] Remove any code that writes to plan files or todo files
- [ ] Remove any code that sets plan/todo status
- [ ] Add "Report back to orchestrator" as the final step
- [ ] Add "Do NOT write to the plan file or set plan status" to file scope
- [ ] Remove references to "Business Requirements Context" in the plan
- [ ] Update references to read from memory files instead of plan sections

### Architect Agent

- [ ] Rename Mode 1 from "Plan Review" to "Plan Validation"
- [ ] Remove "What You Fill In" section → replace with "What You Validate"
- [ ] Remove all plan-writing instructions (Business Rules, Test Scenarios, Domain Model Design, Business Requirements Context)
- [ ] Remove "Handoff to developer" section — orchestrator handles routing
- [ ] Remove plan status setting — report verdict to orchestrator
- [ ] Add "Do NOT write to the plan file" prominently
- [ ] Update post-implementation verification to report verdict, not set status

### Developer Agent

- [ ] Remove plan status changes
- [ ] Clarify: reports findings to orchestrator via memory file
- [ ] Add "Do NOT write to the plan file or set plan status"

### Business Requirements Reviewer

- [ ] Mode 1: Write findings to memory file, NOT the todo
- [ ] Mode 2: Read own memory file for prior findings, NOT plan's Business Requirements Context
- [ ] Mode 2: Write verification to memory file, NOT the plan
- [ ] Update file scope: memory file only, no todo/plan writes
- [ ] Remove "Recommendations for Architect" → "Recommendations"
- [ ] Update examples in description that reference plan's Business Requirements Context

### Business Requirements Documenter

- [ ] Read reviewer's memory file for requirements context (path in spawn prompt), NOT plan's Business Requirements Context
- [ ] Write tracking to memory file, NOT the plan's Documentation section
- [ ] Remove plan status setting
- [ ] Update file scope: docs/ files + memory file only, no plan writes
- [ ] Update description/examples that reference plan's Business Requirements Context

---

## Compatibility

### Existing Plans (v4)

Plans with a Business Requirements Context section still work — agents just won't read that section anymore. The data becomes inert. No need to migrate existing plans.

### New Plans (v5)

New plans won't have Business Requirements Context. All agent findings live in memory files.

### Mixed Agent Versions

If some agents are v5 and others are v4, the v4 agents will try to write to the plan/todo and the v5 orchestrator won't expect it. **Update all agents at once.**

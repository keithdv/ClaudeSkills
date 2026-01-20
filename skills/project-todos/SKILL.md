---
name: project-todos
description: Use when the user asks to "create a todo", "add a plan", "track this work", "document this task", "complete a todo", or mentions managing project todos and plans. Provides the structured workflow for creating, managing, linking, and completing todo and plan markdown files in the docs/todos/ and docs/plans/ directories.
---

# Project Todos and Plans Workflow

Manage significant project work using structured markdown files for todos and plans. This skill provides the complete workflow for creating, linking, and completing project documentation.

## When to Use This Workflow

Create a todo when:
- The user explicitly requests it ("create a todo", "track this work")
- Starting significant work that requires tracking across sessions
- Work involves multiple steps or spans multiple days
- The task needs design/planning before implementation

Do NOT create a todo for:
- Trivial tasks or quick fixes
- Work already tracked in session-level TodoWrite (the in-conversation task list)
- Simple documentation updates

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

**Important**: All paths in this skill are relative to the project root.

## Creating a Todo

### Step 1: Gather Information

When the user requests a todo, gather:
- **Title**: Clear, concise description of the work
- **Priority**: High, Medium, or Low
- **Problem**: What problem are we solving?
- **Solution**: High-level approach (can be refined later)

You can ask the user directly or interpret from their description.

### Step 2: Generate Filename

Create a filename from the title:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Keep it concise (2-5 words)
- **No dates** in filename

**Examples:**
- "Fix Authentication Bug" → `fix-authentication.md`
- "Add Dark Mode Support" → `add-dark-mode.md`
- "Refactor API Layer" → `refactor-api-layer.md`

### Step 3: Create Directory if Needed

Before creating the todo, ensure the directory exists:

```bash
mkdir -p docs/todos
```

### Step 4: Write the Todo File

Use the template from `references/todo-template.md`. Fill in:

- **Title**: The work title
- **Status**: "In Progress" (default for new todos)
- **Priority**: High, Medium, or Low
- **Created**: Today's date (YYYY-MM-DD)
- **Last Updated**: Same as Created initially
- **Problem**: The problem statement
- **Solution**: The high-level approach
- **Plans**: Leave empty initially (will be populated when plans are created)
- **Tasks**: Initial task list if known, or placeholder
- **Progress Log**: Empty initially
- **Results / Conclusions**: Empty initially

**File location**: `docs/todos/{filename}.md`

### Example

```markdown
# Fix Authentication Bug

**Status:** In Progress
**Priority:** High
**Created:** 2026-01-18
**Last Updated:** 2026-01-18

---

## Problem

Users are being logged out randomly during active sessions. Session tokens appear to expire prematurely.

## Solution

Investigate session management logic, verify token expiration settings, and implement proper token refresh mechanism.

---

## Plans

---

## Tasks

- [ ] Reproduce the issue
- [ ] Review session management code
- [ ] Check token expiration configuration
- [ ] Implement token refresh
- [ ] Test fix

---

## Progress Log

---

## Results / Conclusions
```

## Creating a Plan

Plans are created when working on a todo requires design or detailed implementation planning. This typically happens when using skills like `/brainstorm` or `/write-plan`, or when starting complex implementation work.

### Step 1: Determine Plan Purpose

Identify what the plan will cover:
- Design document (architecture, approach, trade-offs)
- Implementation plan (steps, file changes, testing strategy)
- Investigation findings (root cause analysis, research results)

### Step 2: Generate Filename

Create a filename that describes the plan:
- Convert to lowercase
- Replace spaces with hyphens
- Be descriptive but concise
- **No dates** in filename

**Examples:**
- "Authentication Fix Design" → `authentication-fix-design.md`
- "Dark Mode Implementation Plan" → `dark-mode-implementation.md`
- "API Refactoring Strategy" → `api-refactoring-strategy.md`

### Step 3: Create Directory if Needed

```bash
mkdir -p docs/plans
```

### Step 4: Write the Plan File

Use the template from `references/plan-template.md`. Fill in:

- **Title**: Descriptive plan title
- **Date**: Today's date (YYYY-MM-DD)
- **Related Todo**: Relative link to the parent todo file
- **Status**: "Draft" (default for new plans)
- **Last Updated**: Same as Date initially
- **Overview**: Brief description
- **Approach**: High-level strategy
- **Design**: Detailed design (architecture, patterns, etc.)
- **Implementation Steps**: Specific steps to execute
- **Acceptance Criteria**: How to know when it's complete
- **Dependencies**: Prerequisites or external factors
- **Risks / Considerations**: Trade-offs and potential issues

**New Template Sections (for workflow integration):**

Plans created by knockoff-architect should include these additional sections:

```markdown
## Architectural Verification
[Architect completes this checklist before handoff]

**Three Patterns Analysis:**
- Standalone: [How this applies or N/A]
- Inline Interface: [How this applies or N/A]
- Inline Class: [How this applies or N/A]

**Breaking Changes:** Yes/No - [Explanation]

**Pattern Consistency:** [How design follows existing patterns or intentional deviation]

**Codebase Analysis:** [Files examined, patterns found]

---

## Developer Review
[Developer adds concerns/questions here during review phase]

**Status:** [Not Started / Under Review / Concerns Raised / Approved]

**Concerns:** [List any issues found, or "None - ready for implementation"]

---

## Implementation Contract
[Developer fills before starting implementation]

**In Scope:**
- [ ] File 1: Specific changes
- [ ] File 2: Specific changes
- [ ] Test cases to add

**Out of Scope:**
[Explicitly list what will NOT be changed]

---

## Implementation Progress

**Phase 1:** [Name]
- [ ] Step 1
- [ ] Step 2
- [ ] **Verification**: [Test results, evidence]

[Continue for each phase]

---

## Completion Evidence
[Required before marking complete]

- **Tests Passing:** [Output or screenshot]
- **Generated Code Sample:** [Snippet showing feature works]
- **All Checklist Items:** [Confirmed 100% complete]
```

**Plan Status Values:**

Use these status values to track workflow progress:
- `Draft` - Initial plan creation (default)
- `Draft (Architect)` - Architect working on design
- `Under Review (Developer)` - Developer reviewing architect's design
- `Concerns Raised` - Developer found issues, awaiting user decision
- `Ready for Implementation` - Approved, implementation contract created
- `In Progress` - Developer implementing
- `Complete` - All evidence provided, moved to completed/

**Status field location:** In the YAML-style header at the top of plan files.

**File location**: `docs/plans/{filename}.md`

### Step 5: Link Plan to Todo

**Critical**: When creating a plan, you must update BOTH files:

1. **In the plan file**: Add relative link to todo in "Related Todo" field
   ```markdown
   **Related Todo:** [Fix Authentication Bug](../todos/fix-authentication.md)
   ```

2. **In the todo file**: Add plan link to "Plans" section
   ```markdown
   ## Plans

   - [Authentication Fix Design](../plans/authentication-fix-design.md)
   ```

3. **Update todo's Last Updated date** to today

### Link Format

**Always use relative paths:**
- From plan to todo: `../todos/{todo-filename}.md`
- From todo to plan: `../plans/{plan-filename}.md`

**Never use:**
- Absolute paths
- URLs
- Full file system paths

### Example Plan

```markdown
# Authentication Fix Design

**Date:** 2026-01-18
**Related Todo:** [Fix Authentication Bug](../todos/fix-authentication.md)
**Status:** Draft
**Last Updated:** 2026-01-18

---

## Overview

Design for fixing premature session expiration by implementing JWT token refresh mechanism.

---

## Approach

Implement sliding expiration with short-lived access tokens and longer-lived refresh tokens. Client automatically refreshes tokens before expiration.

---

## Design

**Token Structure:**
- Access token: 15 minutes expiration
- Refresh token: 7 days expiration
- Both stored as httpOnly cookies

**Refresh Flow:**
1. Client detects access token near expiration
2. Sends refresh request with refresh token
3. Server validates refresh token
4. Issues new access token and refresh token pair
5. Client continues with new tokens

**File Changes:**
- `auth/tokens.js`: Add refresh token generation
- `middleware/auth.js`: Add token validation with refresh check
- `api/auth/refresh.js`: New endpoint for token refresh

---

## Implementation Steps

1. Create refresh token model and database schema
2. Update login endpoint to issue both tokens
3. Implement /auth/refresh endpoint
4. Add client-side token expiration detection
5. Add automatic refresh logic to API client
6. Update logout to clear both tokens
7. Add tests for refresh flow

---

## Acceptance Criteria

- [ ] Users stay logged in during active sessions
- [ ] Tokens refresh automatically before expiration
- [ ] Logout clears all tokens
- [ ] All tests pass

---

## Dependencies

- JWT library (already installed)
- Database migration for refresh_tokens table

---

## Risks / Considerations

- Refresh token storage security (using httpOnly cookies)
- Token rotation to prevent replay attacks
- Handling clock skew between client and server
```

## Updating Last Updated Dates

**Always update the Last Updated field when:**
- Modifying any content in a todo or plan
- Adding a new plan link to a todo
- Updating status
- Adding progress log entries

**How to update:**
1. Find the "Last Updated" field in the YAML header
2. Replace with today's date (YYYY-MM-DD)

**Example:**
```markdown
**Last Updated:** 2026-01-18
```

## Completing Todos

When work on a todo is complete:

### Step 1: Update Todo Status

Change the todo's status to "Complete" and update Last Updated date.

### Step 2: Fill Results Section

Complete the "Results / Conclusions" section with:
- What was accomplished
- Key decisions made
- Lessons learned
- Final outcomes

### Step 3: Find Associated Plans

Search all plan files in `docs/plans/` for links to this todo. Look for the todo filename in the "Related Todo" field.

**How to find plans:**
```bash
grep -l "todos/{todo-filename}.md" docs/plans/*.md
```

### Step 4: Move Todo to Completed

```bash
mkdir -p docs/todos/completed
mv docs/todos/{todo-filename}.md docs/todos/completed/
```

### Step 5: Move Plans to Completed

For each associated plan:
```bash
mkdir -p docs/plans/completed
mv docs/plans/{plan-filename}.md docs/plans/completed/
```

### Step 6: Update Plan Statuses

Update each moved plan's status to "Complete" and Last Updated date.

**Important**: When you move files to completed/, the relative links still work because both todos and plans move the same depth level.

## Common Workflows

### Creating a Todo Only

User says: "Create a todo to fix the authentication bug"

1. Gather information (or interpret from description)
2. Generate filename: `fix-authentication.md`
3. Create `docs/todos/` if needed
4. Write todo file with template
5. Inform user: "Created todo at docs/todos/fix-authentication.md"

### Creating a Todo with Initial Plan

User says: "Create a todo and plan for adding dark mode"

1. Create the todo first (as above)
2. Generate plan filename: `dark-mode-implementation.md`
3. Create `docs/plans/` if needed
4. Write plan file with template
5. Link plan to todo (update both files)
6. Update todo's Last Updated date
7. Inform user: "Created todo and plan at docs/todos/add-dark-mode.md and docs/plans/dark-mode-implementation.md"

### Adding a Plan to Existing Todo

User is working on a todo and creates a plan (e.g., via `/write-plan`):

1. Read the existing todo file to get context
2. Generate plan filename from plan purpose
3. Write plan file with template
4. Add relative link to todo in plan's "Related Todo" field
5. Add plan link to todo's "Plans" section
6. Update todo's Last Updated date
7. Inform user of both file locations

### Completing a Todo

User says: "Complete the fix-authentication todo"

1. Read the todo file
2. Update Status to "Complete"
3. Update Last Updated date
4. Ask user for Results/Conclusions (or summarize from progress log)
5. Search for associated plans by grepping for the todo filename
6. Move todo to `docs/todos/completed/`
7. Move each associated plan to `docs/plans/completed/`
8. Update each plan's Status to "Complete" and Last Updated date
9. Inform user of completion and what was moved

## Best Practices

1. **File naming**: Keep filenames concise and descriptive. No dates.

2. **Status accuracy**: Update status fields promptly:
   - "In Progress" for active work
   - "Blocked" when waiting on external factors
   - "Complete" when fully done

3. **Progress logging**: Update progress log as work happens, not just at the end. Helps resume context in new sessions.

4. **Link maintenance**: Always update both files when creating links. Check that relative paths are correct.

5. **One todo per file**: Don't combine multiple todos in one file.

6. **Multiple plans OK**: A todo can have multiple plans (design, implementation, investigation, etc.)

7. **Plan evolution**: It's normal to update plans as work progresses. Keep the Last Updated field current.

8. **Completed directory**: Only move to completed/ when truly done. In-progress work stays in the main directory.

## Reference Files

- Todo template: `references/todo-template.md`
- Plan template: `references/plan-template.md`

Use these templates as the source of truth for file structure.

## Summary

**Key points:**
- Todos track significant work in `docs/todos/`
- Plans provide detailed designs in `docs/plans/`
- Link plans to todos using relative paths (update both files)
- Update "Last Updated" dates when modifying files
- Move completed work to `/completed` subdirectories
- Use Write tool to create files, Edit tool to update them
- No dates in filenames, only in YAML headers
- Auto-generate filenames from titles using kebab-case

---

## For Architects (knockoff-architect agent)

When creating or enhancing a plan, you must:

1. **Complete the Architectural Verification Checklist** (see below)
2. **Use project-todos skill for structure** - templates, file paths, linking
3. **Apply your architectural expertise for content** - design decisions, trade-offs
4. **Document codebase analysis** - which files you examined, patterns found

### Architectural Verification Checklist

Before handing off to developer, verify:
- [ ] All three patterns analyzed (Standalone, Inline Interface, Inline Class)
- [ ] Breaking changes assessment completed
- [ ] Pattern consistency check (follows or intentionally deviates)
- [ ] Diagnostic requirements identified
- [ ] Test strategy defined
- [ ] Edge cases documented
- [ ] Codebase deep-dive completed (document files examined)

## For Developers (knockoff-developer agent)

When reviewing and implementing a plan, you must:

1. **Review Phase**: Analyze architect's design for completeness
2. **Concern Documentation**: If issues found, document in "Developer Review" section
3. **Implementation Contract**: Before coding, list exactly what will be implemented
4. **Checklist-Driven**: Every file change and test is a checklist item
5. **Milestone Verification**: Run tests and verify after each phase
6. **Evidence-Based Completion**: Provide proof (test output, code snippets)

### When to STOP and Ask User

- **ALWAYS STOP**: Out-of-scope test failures
- **ALWAYS STOP**: Architectural discoveries that contradict the design
- **Document and continue**: Minor implementation adjustments (note in progress log)

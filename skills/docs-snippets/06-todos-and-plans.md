# 06 - Todos and Plans

How to track work using markdown plans in `docs/todos/`.

---

## Overview

Work is tracked in markdown files, not issue trackers. Each significant task gets a markdown file that contains:
- The plan
- Progress (checkboxes)
- Results and conclusions

When complete, the file moves to `docs/todos/completed/` and is referenced from release notes.

---

## Directory Structure

```
docs/
├── todos/
│   ├── feature-x.md              # Active work
│   ├── bug-fix-y.md              # In progress
│   └── completed/
│       ├── documentation-samples-project.md   # Done, referenced in release notes
│       └── save-reassignment-pattern.md
│
└── release-notes/
    ├── v10.6.0.md                # References completed todos
    └── v10.5.0.md
```

---

## Todo File Structure

Each todo file should contain enough context to resume work without prior conversation history.

### Required Sections

```markdown
# [Title of Work]

**Status:** In Progress | Complete | Blocked
**Priority:** High | Medium | Low
**Created:** YYYY-MM-DD

---

## Problem

[What problem are we solving? Why does this matter?]

## Solution

[High-level approach]

---

## Tasks

- [ ] First task
- [ ] Second task
  - [ ] Subtask
- [x] Completed task

---

## Progress Log

### YYYY-MM-DD
- Did X
- Discovered Y
- Next: Z

---

## Results / Conclusions

[What was learned? What decisions were made? Any gotchas for future reference?]
```

---

## Example: Complete Todo

```markdown
# Documentation Samples Project

**Status:** Complete
**Priority:** High
**Created:** 2026-01-02

---

## Problem

Documentation code snippets are incorrect - bad syntax, outdated APIs. Developers
encounter compilation errors when following the docs.

## Solution

Create a `Neatoo.Samples.DomainModel` project where every code snippet is:
1. Compiled (syntax verified)
2. Tested (behavior verified)
3. Extracted into docs via region markers

---

## Tasks

- [x] Create project structure
- [x] Set up test base class
- [x] Migrate validation-and-rules.md snippets (21)
- [x] Migrate aggregates-and-entities.md snippets (11)
- [x] Migrate factory-operations.md snippets (10)
- [x] Add CI verification step
- [x] Add snippet markers to documentation

---

## Results

- 62 snippets migrated
- 122 tests passing
- CI now fails if docs drift from samples
- Pattern documented in docs-snippets skill
```

---

## When to Create a Todo

Create a todo file for:

| Scenario | Example |
|----------|---------|
| Multi-step features | "Add CancellationToken support" |
| Breaking changes | "Migrate to new serialization format" |
| Refactoring | "Consolidate base classes" |
| Investigation | "Analyze lazy loading options" |
| Documentation work | "Migrate code examples to samples project" |

**Don't create todos for:**
- Simple bug fixes (just fix and note in release notes)
- Trivial changes (typos, formatting)

---

## Workflow

### Starting Work

1. Create `docs/todos/{descriptive-name}.md`
2. Fill in Problem, Solution, Tasks
3. Work through tasks, updating checkboxes
4. Add to Progress Log as you go

### Completing Work

1. Mark all tasks complete
2. Fill in Results/Conclusions section
3. Change Status to "Complete"
4. Move file to `docs/todos/completed/`
5. Reference in release notes

### Referencing in Release Notes

```markdown
# v10.6.0 - 2026-01-05

## Added
- CancellationToken support in factory operations
  - See: [todos/completed/cancellation-token-support.md](../todos/completed/cancellation-token-support.md)

## Changed
- Documentation samples now in `docs/samples/`
  - See: [todos/completed/documentation-samples-project.md](../todos/completed/documentation-samples-project.md)
```

---

## Progress Log Format

The progress log helps resume work in a new session:

```markdown
## Progress Log

### 2026-01-05
- Completed migration of validation-and-rules.md (21 snippets)
- Found API mismatch: RuleBase<T> signature changed
- Fixed by updating samples to use new Execute signature
- Next: Migrate aggregates-and-entities.md

### 2026-01-04
- Created project structure
- Set up test base class
- Verified samples build against Neatoo 10.6.0
```

**Key elements:**
- Date header
- What was done
- What was discovered/decided
- What's next

---

## Resuming Work

When resuming a conversation about existing work:

1. Read the todo file to understand current state
2. Check the Progress Log for where we left off
3. Continue from the "Next:" note
4. Update Progress Log with new session's work

---

## Keywords

When asking Claude to work on something:

| You Say | Claude Understands |
|---------|-------------------|
| "Create a todo for X" | Create `docs/todos/x.md` with full structure |
| "Update the todo" | Update checkboxes and progress log |
| "What's the plan?" | Read and summarize the todo file |
| "Mark it complete" | Move to completed/, update status |
| "Check the todos" | List active todos and their status |

---

## Integration with Ready-to-Commit

When checking "Are we ready to commit?", verify:

- [ ] Active todo files updated with progress
- [ ] Completed work moved to `docs/todos/completed/`
- [ ] Release notes reference completed todos (if releasing)

See [05-ready-to-commit.md](05-ready-to-commit.md) for full checklist.

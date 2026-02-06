---
name: docs-review
description: Review documentation for accuracy and completeness using the docs-writer agent
argument-hint: "[filepath|all] - review one file or all docs"
allowed-tools: ["Glob", "Grep", "Read", "Task", "Bash", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

Review documentation for accuracy, completeness, and API synchronization.

## Instructions

1. **Determine scope**: If argument is a specific file, review that file. If argument is "all" or empty, review all documentation files.

2. **Find files to review** (if reviewing all):
   - `Glob("docs/**/*.md")` -- user-facing docs
   - `Glob("skills/neatoo/**/*.md")` -- Claude-facing skills
   - Exclude: `docs/todos/`, `docs/plans/`, `docs/release-notes/`

3. **For each file, launch docs-writer agent in Review mode**:

Use Task tool with `subagent_type: "docs-writer"` and this prompt:

```
Review mode: Audit {filepath} for accuracy and completeness.

Steps:
1. Read the markdown file
2. Read actual framework code (src/Design/, source files, generated .g.cs files)
3. Compare documented behavior against actual behavior
4. Check all snippet placeholders have matching #region code in src/samples/
5. Report issues with specific file:line references
6. Apply straightforward fixes directly
7. Flag complex issues for user review
8. Run the mandatory verification protocol:
   - dotnet build src/samples/
   - dotnet test src/samples/
   - dotnet mdsnippets

CRITICAL: Verify against actual code, not comments or release notes.
```

4. **Generate summary report**: Total files reviewed, issues found per file, changes applied, build/test status.

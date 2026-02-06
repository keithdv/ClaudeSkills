---
name: docs-update
description: Update existing documentation to match current API using the docs-writer agent
argument-hint: "<filepath> - e.g., docs/guides/validation.md"
allowed-tools: ["Glob", "Grep", "Read", "Task", "Bash", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

Update existing documentation to match the current API.

## Instructions

1. **Determine the target file**: Use the argument provided. If no argument, ask the user which file to update.

2. **Launch docs-writer agent in Update mode**:

Use Task tool with `subagent_type: "docs-writer"` and this prompt:

```
Update mode: Update {filepath} to match the current API.

Steps:
1. Read the existing markdown file
2. Read actual framework code (src/Design/, source files, generated .g.cs files)
3. Compare documented behavior against actual behavior
4. Fix markdown text and snippet placeholders as needed
5. Fix C# sample code in src/samples/ to match current API
6. Run the mandatory verification protocol:
   - dotnet build src/samples/
   - dotnet test src/samples/
   - dotnet mdsnippets
7. Verify no duplicate or missing snippets

CRITICAL: Verify against actual code, not comments or release notes.
```

3. **Report results**: Show the user what changed (files modified, issues found, build/test status).

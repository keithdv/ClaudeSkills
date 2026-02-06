---
name: docs-create
description: Create new documentation for a feature or topic using the docs-writer agent
argument-hint: "<filepath> - e.g., docs/guides/validation.md"
allowed-tools: ["Glob", "Grep", "Read", "Task", "Bash", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion"]
---

Create documentation for a specific file or topic.

## Instructions

1. **Determine the target file**: Use the argument provided (e.g., `docs/guides/validation.md`). If no argument, ask the user what to document.

2. **Launch docs-writer agent in Create mode**:

Use Task tool with `subagent_type: "docs-writer"` and this prompt:

```
Create mode: Create documentation for {filepath}.

Steps:
1. Read CLAUDE.md and src/Design/ to understand the feature
2. Read existing docs to avoid duplication
3. Write the markdown file with <!-- snippet: name --> placeholders
4. Write C# sample code in src/samples/ with #region markers
5. Run the mandatory verification protocol:
   - dotnet build src/samples/
   - dotnet test src/samples/
   - dotnet mdsnippets
6. Verify no duplicate or missing snippets

Target audience: expert .NET/C# developers familiar with DDD.
```

3. **Report results**: Show the user what was created (files, snippet count, build/test status).

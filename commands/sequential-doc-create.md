---
name: sequential-doc-create
description: Create comprehensive C# documentation structure with architect-led planning, sample code generation, and sequential file-by-file creation
argument-hint: ""
allowed-tools: ["Glob", "Grep", "Read", "Task", "Bash", "TaskCreate", "TaskUpdate", "TaskList", "AskUserQuestion", "Skill"]
---

Create a complete C# documentation structure by analyzing the codebase, creating a todo with documentation plan, and sequentially generating each markdown file with corresponding code samples.

## Process Overview

This command orchestrates multiple agents with fresh contexts to create comprehensive documentation:

1. **Architect Analysis** - Analyze codebase and existing docs to identify gaps
2. **Todo Creation** - Create project todo listing all documentation files to create
3. **Samples Planning** - Update todo with required sample project structure
4. **Sequential Creation** - For each file: architect creates markdown → samples creates code → tests pass
5. **Final Sync** - Run mdsnippets to inject code into all markdown files
6. **User Completion** - Ask user if todo should be marked complete

**Important**: All documentation files are created with `**UPDATED:** {date}` footers per the csharp-docs skill. This date tracks API synchronization verification.

## Step-by-Step Instructions

### Step 1: Load Required Skills

Load the csharp-docs and project-todos skills to access their guidance:

```
Use Skill tool to invoke:
- skill: "csharp-docs"
- skill: "project-todos"
```

This loads the documentation patterns and todo/plan workflow knowledge.

### Step 2: Architect Analysis and Todo Creation

Launch docs-architect agent to analyze codebase and create todo:

**Prompt:**
```
Analyze the codebase and existing documentation to identify documentation gaps.

FIND ALL MARKDOWN FILES:
Use Glob to find ALL markdown files recursively:
- Pattern: **/*.md
- This will find every .md file in the repository

EXCLUDE HISTORICAL FILES:
Filter out files that should NOT be part of documentation workflow:
- Exclude: docs/todos/**/*.md (project todo tracking)
- Exclude: docs/plans/**/*.md (implementation plans)
- Exclude: docs/release-notes/**/*.md (release notes)
- Keep everything else for review

EXISTING DOCUMENTATION CHECK:
After filtering, if you find existing documentation files, STOP and list what exists.
- ASK the user: "Found existing documentation: [list files]. Should I:
  1. Analyze gaps and only create missing documentation
  2. Stop - user will delete existing docs first
  3. Other approach"
- Wait for user response before proceeding

CODEBASE ANALYSIS:
- Examine the main project files to understand the framework/library
- Identify public APIs, features, and key concepts that need documentation
- Check for recent changes (new APIs, features since last doc update)
- Review existing docs for completeness and gaps
- Compare existing doc files against APIs/features to find gaps

TODO CREATION:
Use the project-todos skill to create a todo file in docs/todos/ with:
- Title: "Create C# Framework Documentation"
- Priority: Medium (or as appropriate)
- Problem: Describe what documentation is missing or incomplete
- Solution: High-level approach for documentation structure

TASK LIST IN TODO:
Create individual tasks for EACH markdown file that needs to be created or has gaps:
- [ ] README.md
- [ ] docs/getting-started.md
- [ ] docs/guides/feature-a.md
- [ ] docs/guides/feature-b.md
- [ ] docs/reference/api.md
(etc. - based on what you discover in codebase)

Be specific about which files need creation vs. updates.

IMPORTANT: Do NOT delete any existing documentation. Only identify gaps.
```

Use Task tool with:
- `subagent_type: "docs-architect"`
- `description: "Analyze codebase and create documentation todo"`
- Wait for completion

**Critical**: If the architect reports existing documentation, use AskUserQuestion to confirm approach before proceeding.

### Step 3: Samples Planning

Launch docs-code-samples agent to update todo with sample structure:

**Prompt:**
```
Read the documentation todo file created by the architect (check docs/todos/ for the latest file).

Review the task list of markdown files to be created.

UPDATE THE TODO:
Add a new section called "## Sample Project Structure" after the "Solution" section with:

```
## Sample Project Structure

The following sample files will be created in src/docs/samples/:

- **Samples.csproj** - Main xUnit test project
- **ReadmeSamples.cs** - Code samples for README.md
- **GettingStartedSamples.cs** - Code samples for docs/getting-started.md
- **FeatureASamples.cs** - Code samples for docs/guides/feature-a.md
(etc. - list a .cs file for each markdown file)

Platform-specific samples (if needed):
- **Platforms/BlazorSamples/** - Blazor-specific samples
- **Platforms/AspNetCoreSamples/** - ASP.NET Core samples
```

Update the todo's "Last Updated" date to today.

Use the Edit tool to add this section to the todo file.
```

Use Task tool with:
- `subagent_type: "docs-code-samples"`
- `description: "Update todo with sample structure"`
- Wait for completion

### Step 4: Sequential Per-File Documentation Creation

Read the todo file to get the list of markdown files to create.

For EACH markdown file in the todo's task list, execute these steps sequentially:

#### 4A. Create Markdown File (Fresh Architect Agent)

Launch a FRESH docs-architect agent for this specific file:

**Prompt:**
```
Create the markdown file: {filepath}

Review the documentation todo at docs/todos/{todo-filename}.md to understand the overall documentation plan.

CONTEXT:
- This file is part of a larger documentation effort
- Follow the csharp-docs skill patterns for structure and style (including breadcrumbs, index files, and UPDATED footer)
- Target expert .NET developers
- Create MarkdownSnippets placeholders for code samples

CREATE THE FILE:
- Write comprehensive content for this specific document
- Include proper section structure
- Add breadcrumb navigation at the top (if applicable per csharp-docs skill rules)
- Add <!-- snippet: name --> placeholders where code samples are needed
- Provide descriptive text above each placeholder explaining what code should be shown
- Follow naming conventions (e.g., getting-started-basic, feature-a-setup)
- **Add UPDATED footer at bottom**: Per csharp-docs skill, add `---` then `**UPDATED:** {today's date}` at the very bottom

DO NOT:
- Write actual C# code (that's the samples agent's job)
- Create other markdown files (focus only on {filepath})
- Delete or modify existing documentation

Use Write tool to create {filepath}.
```

Use Task tool with:
- `subagent_type: "docs-architect"`
- `description: "Create {filename}"` (e.g., "Create README.md")
- Wait for completion

#### 4B. Create Code Samples for File (Fresh Samples Agent)

Launch a FRESH docs-code-samples agent for this specific file:

**Prompt:**
```
Create code samples for the markdown file: {filepath}

READ THE MARKDOWN:
- Find all <!-- snippet: name --> placeholders
- Read the descriptive text above each placeholder to understand what code to create

CREATE SAMPLE FILE:
- Create or update the appropriate .cs file in src/docs/samples/
  (e.g., README.md → ReadmeSamples.cs, docs/getting-started.md → GettingStartedSamples.cs)
- For each snippet placeholder, create a #region wrapped xUnit test method
- Region name MUST match the snippet name exactly
- All code must compile and tests must pass

VERIFY:
- Run: dotnet build src/docs/samples/
- Run: dotnet test src/docs/samples/
- All tests must pass before completing

IMPORTANT:
- Focus each snippet on the document's instructional point
- Keep #region markers wrapping ONLY the code demonstrating the concept
- Setup/boilerplate can be outside the region markers
- Make each snippet clear and understandable in context

Use Write/Edit tools to create sample code files.
Use Bash tool to run build and test commands.
```

Use Task tool with:
- `subagent_type: "docs-code-samples"`
- `description: "Create samples for {filename}"` (e.g., "Create samples for README.md")
- Wait for completion

#### 4C. Track Progress

After both agents complete for a file:
- Note the completion in a running summary
- Continue to next file in the task list

**Important**: Each markdown file gets TWO fresh agents (architect + samples). Do NOT reuse agents across files.

### Step 5: Final Markdown Snippets Sync

After ALL files have been created and their samples verified, run mdsnippets:

```bash
mdsnippets
```

This syncs all code from #region markers in sample projects into the markdown documentation files.

Verify the command completes successfully. If errors occur, report them to the user.

### Step 6: Generate Summary Report

Create a summary showing:
- Total markdown files created
- Total sample files created
- Build status (all samples compiled successfully)
- Test status (all tests passed)
- MarkdownSnippets sync status
- Location of the todo file

Display summary to user.

### Step 7: Ask About Todo Completion

Use AskUserQuestion to ask:

```
Documentation creation complete. Would you like to mark the todo as complete?
```

Options:
1. Yes - Mark complete and move to docs/todos/completed/
2. No - Leave in docs/todos/ for further work
3. Review first - Show me the summary again

If user selects "Yes":
- Update todo Status to "Complete"
- Fill in "Results / Conclusions" section with summary
- Move todo to docs/todos/completed/
- Update "Last Updated" date

## Example Workflow

```
Step 1: Loading skills...
  ✓ csharp-docs skill loaded
  ✓ project-todos skill loaded

Step 2: Architect analyzing codebase...
  ✓ Created todo: docs/todos/create-framework-documentation.md
  ✓ Identified 5 markdown files to create

Step 3: Samples agent planning...
  ✓ Updated todo with sample project structure
  ✓ Listed 5 sample files to create

Step 4: Sequential creation...

  File 1/5: README.md
    ✓ Architect created README.md with 4 snippet placeholders
    ✓ Samples created ReadmeSamples.cs with 4 regions
    ✓ Build successful, tests passed (4/4)

  File 2/5: docs/getting-started.md
    ✓ Architect created getting-started.md with 3 snippet placeholders
    ✓ Samples created GettingStartedSamples.cs with 3 regions
    ✓ Build successful, tests passed (7/7)

  File 3/5: docs/guides/interceptors.md
    ✓ Architect created interceptors.md with 6 snippet placeholders
    ✓ Samples created InterceptorsSamples.cs with 6 regions
    ✓ Build successful, tests passed (13/13)

  [... continue for remaining files ...]

Step 5: Running mdsnippets...
  ✓ Updated 5 markdown files with code samples

Summary:
- Markdown files created: 5
- Sample files created: 5
- Total snippets: 20
- Build status: ✓ All samples compiled
- Test status: ✓ All tests passed (20/20)
- Todo location: docs/todos/create-framework-documentation.md

Would you like to mark the todo as complete?
```

## Tips

- Process files in logical order (README first, then getting-started, then guides)
- Each file gets independent agents with fresh context
- If any build or test fails, STOP and report to user
- Track progress with running summary for visibility
- Agents apply changes directly, not just planning
- All existing documentation is preserved unless user explicitly requests deletion

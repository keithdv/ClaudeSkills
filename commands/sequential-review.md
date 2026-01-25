---
name: sequential-review
description: Sequentially review all documentation files using docs-architect and docs-code-samples agents, then update markdown snippets
argument-hint: ""
allowed-tools: ["Glob", "Grep", "Read", "Task", "Bash", "TaskCreate", "TaskUpdate", "TaskList"]
---

Perform a comprehensive sequential review of all C# documentation files.

## Critical Directive

**YOU CANNOT TRUST:**
- Comments in source code (they may be outdated)
- Release notes (they show historical "before/after" examples, not current API)
- Your own knowledge or memory

**YOU MUST VERIFY AGAINST:**
- Actual generated .g.cs files in test projects
- Current test usage patterns
- What the renderer actually generates NOW

When reviewing for accuracy, verify against **reality** (generated code, compiled samples), not **descriptions** (comments, docs, release notes).

## Process Overview

Review documentation files in this order:
1. Recursively find all documentation markdown files in the repository
2. Exclude historical/planning files (todos/, plans/, release-notes/)
3. For each file sequentially:
   - Launch fresh docs-architect agent to review structure, content, and completeness
   - Launch fresh docs-code-samples agent to review/update code samples
4. After all files reviewed, run `mdsnippets` to sync code samples to markdown

**Important**: This command performs API synchronization review. Both agents MUST update the `**UPDATED:** {date}` footer per the csharp-docs skill requirements, as they are verifying the documentation matches the current API.

## Step-by-Step Instructions

### Step 1: Find Documentation Files

Use Glob to find all markdown files:
- README.md in repository root
- All .md files in docs/ directory
- All .md files in skills/ directory
- Exclude: docs/todos/, docs/plans/, docs/release-notes/

Create a sorted list of files to process.

### Step 2: Review Each File Sequentially

For each file in the list:

**A. Launch docs-code-samples agent (Sync Snippets)**
- Use Task tool with subagent_type="docs-code-samples"
- Provide clear prompt: "Run mdsnippets to sync code samples for {filepath}. Fix any errors or warnings that occur. Ensure all snippet placeholders can be resolved from #region markers in sample projects."
- Wait for agent to complete
- Note findings in running summary

**B. Launch docs-architect agent (API Changes Pass)**
- Use Task tool with subagent_type="docs-architect"
- Provide clear prompt: "Review {filepath} for outdated content and new API changes. Check the UPDATED date at the bottom of the document (if present) and focus on any API updates since that date. Apply fixes directly.

CRITICAL: You cannot trust comments, release notes, or your own knowledge. Verify against actual generated .g.cs files and current test usage.

Per the csharp-docs skill requirements, update the footer at the bottom to `---` then `**UPDATED:** {today's date}` to signify this API synchronization review was completed."
- Wait for agent to complete
- Note findings in running summary

**C. Launch docs-architect agent (Structure Pass - Fresh Context)**
- Use Task tool with subagent_type="docs-architect"
- Provide clear prompt: "Review {filepath} for structure, completeness, and MarkdownSnippets placeholders. Check for: missing sections, unclear explanations, missing code sample placeholders, proper breadcrumb navigation, and UPDATED footer per csharp-docs skill. Apply fixes directly.

Ensure the UPDATED footer is present at the bottom (format: `---` then `**UPDATED:** {today's date}`)."
- Wait for agent to complete
- Note findings in running summary

**D. Launch docs-code-samples agent (Review & Update)**
- Use Task tool with subagent_type="docs-code-samples"
- Provide clear prompt: "Review and update code samples for {filepath}. Ensure all snippet placeholders have corresponding #region code in sample projects. Verify all samples compile and tests pass. Apply fixes directly.

CRITICAL: You cannot trust comments, release notes, or your own knowledge. Verify code samples work with the CURRENT API by examining generated .g.cs files and compiling the samples.

IMPORTANT: Focus each snippet on the document's instructional point. The #region markers should wrap ONLY the code that demonstrates the specific concept being taught. The full test method can contain whatever setup, boilerplate, or context is needed to compile and run - but keep that code OUTSIDE the #region markers so it doesn't appear in the documentation. Each snippet doesn't need to show the complete beginning-to-end flow, just the relevant part that illustrates the point being made. Make each snippet as clear and understandable as possible within the context of where it appears in the document.

After verifying all code samples work with the current API, update the markdown file's UPDATED footer to today's date (per csharp-docs skill requirements for API synchronization verification)."
- Wait for agent to complete
- Note findings in running summary

**Important**: Launch a fresh agent for EACH file. Do not reuse agents across files.

### Step 3: Update Markdown Snippets

After all files reviewed, run MarkdownSnippets:

```bash
mdsnippets
```

This syncs all code from #region markers in sample projects into the markdown documentation.

### Step 4: Generate Summary Report

Create a summary showing:
- Total files reviewed
- Issues found per file (architecture issues, missing samples, etc.)
- Changes applied
- MarkdownSnippets sync status

Display summary to user.

## Example Workflow

```
Found 7 files to review:
1. README.md
2. docs/getting-started.md
3. docs/guides/interceptors.md
4. docs/guides/validation.md
5. docs/reference/api.md
6. skills/csharp-docs/SKILL.md
7. skills/csharp-docs/references/documentation-patterns.md

Reviewing README.md...
  - docs-architect: Found 2 missing placeholders, added them
  - docs-code-samples: Created 3 new sample regions, all tests pass

Reviewing docs/getting-started.md...
  - docs-architect: Updated intro section for clarity
  - docs-code-samples: All samples up to date

[... continue for each file ...]

Running mdsnippets...
✓ Updated 12 markdown files with latest code samples

Summary:
- Files reviewed: 7
- Architecture improvements: 10
- Code samples created: 9
- Code samples updated: 5
- All tests passing: ✓
```

## Tips

- Process files in logical order (README first, then getting-started, then guides)
- Each agent runs independently with fresh context
- Agents should apply fixes directly, not just report issues
- If mdsnippets fails, report the error to user
- Track progress with TaskCreate/TaskUpdate for visibility

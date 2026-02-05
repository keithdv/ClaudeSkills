---
name: sequential-review
description: Review all C# documentation files using docs-architect and docs-code-samples agents to verify API accuracy, then update markdown snippets
argument-hint: ""
allowed-tools: ["Glob", "Grep", "Read", "Task", "Bash", "TaskCreate", "TaskUpdate", "TaskList"]
---

Perform a comprehensive review of all C# documentation files with parallel architect passes and sequential code sample updates.

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

This command performs API synchronization review in phases:

1. **Initial Sync**: Run `mdsnippets` to establish baseline (code → markdown)
2. **Find Files**: Recursively locate all documentation markdown files, excluding historical files (todos/, plans/, release-notes/)
3. **Parallel Architect Review**: Launch docs-architect agents in parallel across all files
   - API Changes Pass: Verify current API accuracy (parallel across all files)
   - Structure Pass: Review completeness and organization (parallel across all files)
4. **Sequential Code Sample Review**: Launch docs-code-samples agents one file at a time (shared samples directory requires sequential execution)
5. **Final Sync**: Run `mdsnippets` again to capture all code sample updates (code → markdown)

**Important**: All agents MUST update the `**UPDATED:** {date}` footer per the csharp-docs skill requirements, as they are verifying the documentation matches the current API.

**Parallelization Strategy**: Architect agents can run concurrently because they edit different markdown files. Code sample agents must run sequentially because they share the same `src/docs/samples/` directory and would conflict if run simultaneously.

## Step-by-Step Instructions

### Step 1: Initial Snippet Sync

Run mdsnippets to establish baseline before review:

- Use Task tool with subagent_type="docs-code-samples"
- Provide clear prompt: "Run mdsnippets to sync code samples. Fix any errors or warnings that occur. Ensure all snippet placeholders can be resolved from #region markers in sample projects."
- Wait for agent to complete
- Note findings in running summary

This ensures documentation reflects current code samples before review begins.

### Step 2: Find Documentation Files

Use Glob to find all markdown files:
- README.md in repository root
- All .md files in docs/ directory
- All .md files in skills/ directory
- Exclude: docs/todos/, docs/plans/, docs/release-notes/

Create a sorted list of files to process.

### Step 3: Parallel Architect Review (All Files)

Launch docs-architect agents in parallel for all files. Each file gets TWO architect passes:

#### A. API Changes Pass (Parallel Across All Files)

For each file, launch docs-architect agent:
- Use Task tool with subagent_type="docs-architect"
- Provide clear prompt: "Review {filepath} for outdated content and new API changes. Check the UPDATED date at the bottom of the document (if present) and focus on any API updates since that date. Apply fixes directly.

CRITICAL: You cannot trust comments, release notes, or your own knowledge. Verify against actual generated .g.cs files and current test usage.

Per the csharp-docs skill requirements, update the footer at the bottom to `---` then `**UPDATED:** {today's date}` to signify this API synchronization review was completed."

**Implementation**: Launch all API pass agents simultaneously using multiple Task tool calls. Do not wait for completion yet.

#### B. Structure Pass (Parallel Across All Files)

For each file, launch docs-architect agent:
- Use Task tool with subagent_type="docs-architect"
- Provide clear prompt: "Review {filepath} for structure, completeness, and MarkdownSnippets placeholders. Check for: missing sections, unclear explanations, missing code sample placeholders, proper breadcrumb navigation, and UPDATED footer per csharp-docs skill. Apply fixes directly.

CRITICAL: You cannot trust comments, release notes, or your own knowledge. Verify against actual generated .g.cs files and current test usage.

Ensure the UPDATED footer is present at the bottom (format: `---` then `**UPDATED:** {today's date}`)."

**Implementation**: Launch all Structure pass agents simultaneously using multiple Task tool calls. Do not wait for completion yet.

#### Wait for All Architect Agents

After launching all API and Structure passes, wait for ALL architect agents to complete before proceeding to code samples.

Track progress and note findings from each agent in running summary.

**Important**: Each file gets fresh agent instances. Do not reuse agents across files.

### Step 4: Sequential Code Sample Review (One File at a Time)

Process code samples sequentially because agents share the `src/docs/samples/` directory:

For each file in the list (one at a time):

- Use Task tool with subagent_type="docs-code-samples"
- Provide clear prompt: "Review and update code samples for {filepath}. Ensure all snippet placeholders have corresponding #region code in sample projects. Verify all samples compile and tests pass. Apply fixes directly.

CRITICAL: You cannot trust comments, release notes, or your own knowledge. Verify code samples work with the CURRENT API by examining generated .g.cs files and compiling the samples.

IMPORTANT: Focus each snippet on the document's instructional point. The #region markers should wrap ONLY the code that demonstrates the specific concept being taught. The full test method can contain whatever setup, boilerplate, or context is needed to compile and run - but keep that code OUTSIDE the #region markers so it doesn't appear in the documentation. Each snippet doesn't need to show the complete beginning-to-end flow, just the relevant part that illustrates the point being made. Make each snippet as clear and understandable as possible within the context of where it appears in the document.

After verifying all code samples work with the current API, update the markdown file's UPDATED footer to today's date (per csharp-docs skill requirements for API synchronization verification)."
- Wait for agent to complete before starting next file
- Note findings in running summary

**Why Sequential**: Code sample agents modify shared sample files in `src/docs/samples/`. Running them in parallel would cause file conflicts and test failures.

### Step 5: Final Snippet Sync

After all files reviewed, run mdsnippets to capture code sample updates:

```bash
mdsnippets
```

This syncs all code from #region markers in sample projects into the markdown documentation, capturing any updates made during the review.

### Step 6: Generate Summary Report

Create a summary showing:
- Total files reviewed
- Initial snippet sync status
- Issues found per file (API changes, structure issues, code sample updates, etc.)
- Changes applied by each agent type
- Final snippet sync status

Display summary to user.

## Example Workflow

```
Step 1: Initial snippet sync...
Running mdsnippets...
✓ Synced 45 code snippets to 12 markdown files

Step 2: Finding documentation files...
Found 7 files to review:
1. README.md
2. docs/getting-started.md
3. docs/guides/interceptors.md
4. docs/guides/validation.md
5. docs/reference/api.md
6. skills/csharp-docs/SKILL.md
7. skills/csharp-docs/references/documentation-patterns.md

Step 3: Launching parallel architect review...

API Changes Pass (parallel):
  - Launching docs-architect for README.md...
  - Launching docs-architect for docs/getting-started.md...
  - Launching docs-architect for docs/guides/interceptors.md...
  - [... all 7 files launched ...]

Structure Pass (parallel):
  - Launching docs-architect for README.md...
  - Launching docs-architect for docs/getting-started.md...
  - [... all 7 files launched ...]

Waiting for all architect agents to complete...
✓ All 14 architect agents completed

Results:
  README.md:
    - API Pass: Updated 2 outdated API references
    - Structure Pass: Added missing section on advanced usage
  docs/getting-started.md:
    - API Pass: No changes needed
    - Structure Pass: Improved intro clarity, added placeholders
  docs/guides/interceptors.md:
    - API Pass: Updated lifecycle hook signatures
    - Structure Pass: Added breadcrumb navigation
  [... continue for each file ...]

Step 4: Sequential code sample review...
  Processing README.md...
    - Created 2 new sample regions, all tests pass
  Processing docs/getting-started.md...
    - All samples up to date
  Processing docs/guides/interceptors.md...
    - Updated 3 samples to use current API, tests pass
  [... continue for each file ...]

Step 5: Final snippet sync...
Running mdsnippets...
✓ Synced 52 code snippets to 12 markdown files (+7 new snippets)

Step 6: Summary Report
=======================
Files reviewed: 7
Initial sync: 45 snippets
Final sync: 52 snippets (+7 new)

Architect Changes:
- API updates: 8 files
- Structure improvements: 12 files
- Total architect agents: 14 (7 API + 7 Structure)

Code Sample Changes:
- New samples created: 5
- Samples updated: 9
- All tests passing: ✓
```

## Tips

- Launch all architect agents in parallel for maximum speed (they edit different files)
- Wait for ALL architect agents to finish before starting code sample agents
- Process code sample agents strictly one at a time to avoid conflicts in shared samples directory
- Each file gets fresh agent instances (never reuse agents across files)
- Agents should apply fixes directly, not just report issues
- If mdsnippets fails at any stage, report the error to user
- Track overall progress with TaskCreate/TaskUpdate for visibility
- The two mdsnippets runs serve different purposes: initial sync establishes baseline, final sync captures review updates

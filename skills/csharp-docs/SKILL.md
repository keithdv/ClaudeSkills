---
name: csharp-docs
description: This skill should be used when the user asks to "create documentation", "write docs", "update documentation", "add code samples", "sync snippets", "create README", "document this framework", or mentions MarkdownSnippets, documentation samples, or keeping docs in sync with code. Provides comprehensive guidance for documenting C# open source frameworks.
version: 0.3.0
---

# C# Framework Documentation

Comprehensive documentation system for C# open source frameworks using MarkdownSnippets for code synchronization.

## Core Workflow

Documentation follows a two-agent pipeline:

1. **docs-architect** - Creates documentation structure with snippet placeholders (does NOT write code)
2. **docs-code-samples** - Creates compilable sample projects that fill the placeholders

Always run docs-architect first, then docs-code-samples.

## Documentation Structure

Standard structure for C# frameworks:

```
README.md                    # Project overview, quick start, evaluation guide
docs/
├── index.md                 # Top-level documentation index (no breadcrumbs)
├── getting-started.md       # Installation, first usage
├── guides/                  # Feature-specific guides
│   ├── index.md             # Guides index
│   ├── feature-a.md
│   └── feature-b.md
├── reference/               # API reference
│   ├── index.md             # Reference index
│   └── api.md
└── migration/               # Migration guides
    ├── index.md             # Migration index
    └── from-other-lib.md
```

**Excluded from MarkdownSnippets scanning:** `docs/todos/`, `docs/plans/`, `docs/release-notes/` (these are project management directories, not technical documentation)

### Index Files

Every folder containing documentation must have an `index.md` file that:

1. **Lists subfolders first** (alphabetically) with manually-written descriptions
2. **Lists markdown files** (alphabetically, excluding index.md) with manually-written descriptions
3. **Uses consistent formatting**:
   ```markdown
   # Folder Name

   Brief overview of this section.

   ## Subfolders

   - **[Subfolder Name](subfolder/)** - Description of subfolder contents

   ## Documentation

   - **[Document Title](document.md)** - Description of document
   ```

**Top-level index (`docs/index.md`)**: Has no breadcrumbs.

**Subfolder indexes**: Include only `[↑ Up](../index.md)` breadcrumb at the very top.

### Breadcrumb Navigation

All documentation files (except `docs/index.md` and index files) must have breadcrumbs at the **very top**:

```markdown
[← Previous](prev.md) | [↑ Up](index.md) | [Next →](next.md)

# Document Title
```

**Breadcrumb Rules:**
- **Previous/Next**: Navigate alphabetically within the current folder only
- **Up**: Links to the local `index.md` in the same folder
- **Index files**: Only have `[↑ Up](../index.md)` (no prev/next)
- **First file**: No previous link: `[↑ Up](index.md) | [Next →](next.md)`
- **Last file**: No next link: `[← Previous](prev.md) | [↑ Up](index.md)`
- **Alphabetical order**: Determines prev/next sequence (exclude index.md from sequence)

### Update Tracking

All technical documentation markdown files (including `index.md` and `README.md`) must have an update timestamp at the **very bottom**:

```markdown
---

**UPDATED:** 2026-01-24
```

**Update Rules:**
- Place after all content, separated by `---` horizontal rule
- Use format: `**UPDATED:** YYYY-MM-DD`
- **Only update the date when verifying the document matches the current API**
- Do NOT update for minor edits, typos, or formatting changes
- The date tracks API synchronization verification, not general modifications
- Update when:
  - Verifying code examples work with current API
  - Checking that described API behavior is still accurate
  - Adding/updating content to reflect API changes
  - Performing documentation review/audit against codebase

## MarkdownSnippets Integration

### Snippet Placeholder Syntax

In markdown documentation, use this syntax for code placeholders:

```markdown
<!-- snippet: snippet-name -->
<!-- endSnippet -->
```

The docs-architect creates descriptive placeholder names. The docs-code-samples agent creates the actual code.

### Sample Code Location

Sample code lives in `src/docs/samples/` with this structure:

```
src/docs/samples/
├── Samples.csproj           # Main xUnit test project
├── GettingStartedSamples.cs # Samples for getting-started.md
├── FeatureASamples.cs       # Samples for guides/feature-a.md
└── Platforms/               # Platform-specific projects when needed
    ├── Blazor/
    └── AspNetCore/
```

### Sample Code Format

Each sample is a region-wrapped test method:

```csharp
#region snippet-name
[Fact]
public void SnippetName()
{
    // Actual compilable code
}
#endregion
```

MarkdownSnippets extracts the code between `#region` and `#endregion` markers.

## Using the Agents

### docs-architect Agent

Invoke when creating or restructuring documentation:

- Creates documentation files with proper structure
- **Creates index.md files** for each folder with manually-written descriptions
- **Adds breadcrumb navigation** to all files (except docs/index.md)
- Writes content targeted at expert .NET developers
- Creates descriptive snippet placeholders
- Does NOT write actual C# code samples

**Critical tasks:**
- Ensure every folder has an `index.md`
- Add breadcrumbs at the very top of each file (except docs/index.md)
- Add `**UPDATED:** YYYY-MM-DD` footer at the bottom of all files
- Order prev/next links alphabetically within folder
- Write clear, concise descriptions for all index entries

### docs-code-samples Agent

Invoke after docs-architect completes:

- Reads documentation to find snippet placeholders
- Creates sample projects in `src/docs/samples/`
- Writes compilable, tested C# code
- Ensures code matches placeholder descriptions

## MarkdownSnippets Setup

For projects without MarkdownSnippets configured (first-time setup), see `references/markdownsnippets-setup.md` for installation and configuration guidance.

## Writing Guidelines

### Target Audience

Documentation targets expert .NET and C# developers:

- No explanations of basic C# concepts
- No hand-holding or verbose tutorials
- Direct, technical language
- Focus on API usage and patterns

### Content Progression

Documentation progresses from introductory to detailed:

1. **README** - Quick evaluation: What does it do? Why use it?
2. **Getting Started** - Minimal setup to first working code
3. **Guides** - Feature deep-dives with examples
4. **Reference** - Complete API documentation

### Snippet Naming

Use descriptive, hierarchical names:

- `getting-started-install` - Installation snippet
- `getting-started-basic-usage` - First usage example
- `feature-a-setup` - Feature A setup code
- `feature-a-advanced` - Advanced Feature A usage

## Complete Example

For a complete walkthrough showing index files, breadcrumbs, and snippet integration, see `references/complete-example.md`.

## Additional Resources

### Reference Files

For detailed guidance, consult:

- **`references/complete-example.md`** - Complete documentation structure example with indexes and breadcrumbs
- **`references/markdownsnippets-setup.md`** - MarkdownSnippets installation and configuration
- **`references/documentation-patterns.md`** - Common documentation patterns and templates

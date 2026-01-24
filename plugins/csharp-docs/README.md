# csharp-docs Plugin

Documentation management for C# open source frameworks with MarkdownSnippets integration.

## Overview

This plugin provides a two-agent pipeline for creating and maintaining C# framework documentation:

1. **docs-architect** (Sonnet) - Creates documentation structure with code placeholders
2. **docs-code-samples** (Opus) - Creates compilable C# sample code

All code samples use MarkdownSnippets for synchronization between markdown and actual compilable tests.

## Components

### Command: sequential-review

Performs comprehensive sequential review of all documentation files.

**Usage:** `/csharp-docs:sequential-review`

**Process:**
1. Finds all documentation files (README.md + docs/ + skills/)
2. Excludes historical files (todos/, plans/, release-notes/)
3. For each file sequentially:
   - Launches fresh docs-architect agent to review structure
   - Launches fresh docs-code-samples agent to review samples
4. Runs `mdsnippets` to sync all code samples
5. Displays summary report of changes

**Use cases:**
- Regular documentation maintenance
- After adding new features
- Before releases to ensure docs are current
- Finding missing or outdated samples

### Skill: C# Framework Documentation

Auto-triggers when discussing documentation, creating docs, or syncing samples.

**Trigger phrases:**
- "create documentation"
- "write docs"
- "update documentation"
- "add code samples"
- "sync snippets"
- "create README"
- "document this framework"

### Agent: docs-architect

Creates documentation structure with MarkdownSnippets placeholders. Does NOT write actual C# code.

**Responsibilities:**
- Analyze codebase for documentable features
- Design documentation hierarchy (README, guides, reference)
- Write documentation for expert .NET developers
- Create descriptive snippet placeholders

**Model:** Sonnet (cost-effective for writing text)

### Agent: docs-code-samples

Creates compilable C# sample projects that integrate with MarkdownSnippets.

**Responsibilities:**
- Read documentation to find snippet placeholders
- Create sample projects in `src/docs/samples/`
- Write tested, compilable C# code
- Ensure all samples pass

**Model:** Opus (higher quality for code generation)

## Workflow

```
1. User requests documentation
2. docs-architect creates docs with placeholders
3. docs-code-samples creates compilable code
4. Run mdsnippets to sync code into docs
```

## Documentation Structure

The plugin targets this structure:

```
README.md                    # Evaluation and quick start
docs/
├── getting-started.md       # First-time setup
├── guides/                  # Feature guides
├── reference/               # API reference
└── migration/               # Migration guides
```

**Excluded:** `docs/todos/`, `docs/plans/`, `docs/release-notes/`

## Sample Code Location

Samples go in `src/docs/samples/`:

```
src/docs/samples/
├── Samples.csproj           # Main xUnit project
├── ReadmeSamples.cs         # README snippets
├── GettingStartedSamples.cs # Getting started snippets
└── Platforms/               # Platform-specific when needed
```

## MarkdownSnippets Integration

**In markdown:**
```markdown
<!-- snippet: snippet-name -->
<!-- endSnippet -->
```

**In C#:**
```csharp
#region snippet-name
[Fact]
public void SnippetName()
{
    // Actual code here
}
#endregion
```

Run `mdsnippets` to sync code into documentation.

## Setup

1. Install MarkdownSnippets: `dotnet tool install -g MarkdownSnippets.Tool`
2. Create `mdsnippets.json` configuration (see skill references)
3. Use docs-architect to create documentation
4. Use docs-code-samples to create samples
5. Run `mdsnippets` to sync

## Reference Files

- `skills/csharp-docs/references/markdownsnippets-setup.md` - Installation and configuration
- `skills/csharp-docs/references/documentation-patterns.md` - Templates and conventions

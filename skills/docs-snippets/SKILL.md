---
name: docs-snippets
description: Documentation snippet synchronization. Load whenever working with markdown documentation files including README.md or docs/*.md. Load before every commit to git.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(pwsh:*, powershell:*, dotnet:*)
---

# Documentation Snippets Skill

Code examples in documentation must be **compiled and tested**. This skill manages the sync between sample projects and documentation using [MarkdownSnippets](https://github.com/SimonCropp/MarkdownSnippets).

## Single Source of Truth

Whether you're updating:
- **README.md** - The project's main documentation (first thing users see)
- **Repository docs** (`{project}/docs/*.md`) - Read by developers
- **Claude skills** (`{project}/.claude/skills/{skill}/`) - Used by Claude

**All code snippets come from the samples project.** MarkdownSnippets processes all these locations identically.

**README.md is not exempt.** Code examples in the README must use snippet markers just like any other documentation file. This ensures the README stays in sync with actual tested code.

Skills live **in the repository** alongside the code they describe, then get copied to the shared location (`~/.claude/skills/`) on commit for use outside the repo.

## When to Use This Skill

- Adding code examples to documentation
- Syncing docs after code changes
- Verifying docs are current
- **"Are we ready to commit?"** - run the checklist
- Preparing a release

## Quick Reference

### Project Structure

```
{Project}/
├── README.md                                   # Main docs (mdsnippets-processed)
├── .claude/
│   └── skills/
│       └── {skill}/                            # Local skill (versioned, mdsnippets-processed)
│           ├── SKILL.md
│           └── *.md
├── docs/
│   ├── *.md                                    # Documentation (mdsnippets-processed)
│   ├── release-notes/                          # Version notes
│   ├── todos/                                  # Active plans
│   │   └── completed/                          # Done plans
│   └── samples/                                # Single source for BOTH docs and skills
│       ├── {Project}.Samples.DomainModel/      # Domain with #region snippets
│       ├── {Project}.Samples.DomainModel.Tests/
│       ├── {Project}.Samples.Server/           # Server Program.cs
│       └── {Project}.Samples.BlazorClient/     # Client Program.cs
├── scripts/
│   └── verify-code-blocks.ps1                  # Verifies pseudo/invalid markers
├── mdsnippets.json                             # MarkdownSnippets config
└── .config/
    └── dotnet-tools.json                       # Tool manifest

~/.claude/skills/{skill}/                       # Shared copy (for use outside repo)
```

**On commit:** Local skill is copied to shared location so it's available when working in other projects.

### Key Commands

```powershell
# Sync documentation AND skills with code snippets
dotnet mdsnippets

# Verify all code blocks have markers (pseudo/invalid)
pwsh scripts/verify-code-blocks.ps1

# Check if docs/skills changed (CI verification)
dotnet mdsnippets && git diff --exit-code docs/ .claude/skills/

# Copy local skill to shared location (on commit)
Copy-Item -Recurse -Force ".claude/skills/{skill}" "$HOME/.claude/skills/"
```

### Snippet Marker Types

**Core principles:**
1. **If it compiles, it should be compiled.**
2. **No commented code in snippets.** Comments like `// await db.SaveChangesAsync();` defeat the purpose.

All C# code blocks must have a marker. Four types are supported:

| Type | Purpose | How It Works |
|------|---------|--------------|
| `snippet: {id}` | Compiled, tested code | MarkdownSnippets extracts from `#region {id}` |
| `<!-- pseudo:{id} -->` | Illustrative code | Manual marker, not processed by mdsnippets |
| `<!-- invalid:{id} -->` | Anti-patterns, wrong examples | Manual marker, not processed by mdsnippets |
| `<!-- generated:{path}#L{start}-L{end} -->` | Source-generated output | Manual marker with line tracking for drift detection |

**Decision flowchart:**
```
Is this code intentionally broken/wrong?     → invalid:
Is this showing source-generated output?     → generated:
Is this compilable C# (even from Moq, etc)?  → snippet: (add to samples, NO commented code)
Is this an API signature/incomplete fragment? → pseudo:
```

**"But the types don't exist!"** — That's not an excuse for `pseudo:`. If the code would compile with supporting types, create placeholder types in the samples project. Stubs, interfaces, simple classes — whatever the snippet needs to compile. The samples project exists to make documentation code real.

See [01-snippet-regions.md](01-snippet-regions.md) for detailed syntax and examples.

### Ready to Commit Checklist

```
[ ] dotnet build                              # Code compiles
[ ] dotnet test                               # Tests pass
[ ] dotnet mdsnippets                         # Snippets extracted to docs AND skills
[ ] git diff --exit-code docs/ .claude/       # No uncommitted changes
[ ] pwsh scripts/verify-code-blocks.ps1       # All code blocks have markers
[ ] Copy skill to shared location             # ~/.claude/skills/{skill}/
[ ] Release notes needed?                     # If features/fixes, add to docs/release-notes/
[ ] If release: version updated, release notes created
```

### Configuration (mdsnippets.json)

```json
{
  "Convention": "InPlaceOverwrite",
  "LinkFormat": "GitHub",
  "OmitSnippetLinks": true
}
```

## Detailed Guides

Load these guides based on what you're doing:

| When | Load | Why |
|------|------|-----|
| Adding code examples to docs | [01-snippet-regions.md](01-snippet-regions.md) | `#region` syntax, naming conventions, partial snippets |
| Running `dotnet mdsnippets` fails | [02-documentation-sync.md](02-documentation-sync.md) | Troubleshooting sync errors, configuration |
| Updating skill files | [03-skill-sync.md](03-skill-sync.md) | Local vs shared skills, copy-on-commit workflow |
| CI failures or unmarked blocks | [04-verification.md](04-verification.md) | Verification scripts, CI integration |
| "Are we ready to commit?" | [05-ready-to-commit.md](05-ready-to-commit.md) | Full checklist with commands |
| Creating/updating todo files | [06-todos-and-plans.md](06-todos-and-plans.md) | Todo file format, `docs/todos/` conventions |
| Adding release notes | [07-release-notes.md](07-release-notes.md) | Release note format, versioning |
| Setting up new project | [08-migration-guide.md](08-migration-guide.md) | Initial setup, migrating from custom scripts |
| Choosing snippet vs pseudo vs invalid | [09-marker-types.md](09-marker-types.md) | Detailed marker definitions, common mistakes |


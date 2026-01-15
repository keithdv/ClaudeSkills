---
name: docs-snippets
description: This skill should be used when working with "markdown documentation", "README.md", "docs/*.md", "code examples in documentation", "snippet sync", "dotnet mdsnippets", "MarkdownSnippets", "code block markers", "pseudo code blocks", "ready to commit", or preparing documentation for commit. Provides workflow for keeping code examples compiled and tested via MarkdownSnippets.
---

# Documentation Snippets

Code examples in documentation must be **compiled and tested**. This skill manages synchronization between sample projects and documentation using [MarkdownSnippets](https://github.com/SimonCropp/MarkdownSnippets).

## Core Principle

**If it compiles, it should be compiled.** Every code example that could run should exist in a samples project with `#region` markers, not as hand-written markdown that drifts from reality.

## Quick Reference

### Marker Types

All C# code blocks require a marker:

| Marker | Purpose | Source |
|--------|---------|--------|
| `snippet: {id}` | Compiled, tested code | Extracted from `#region {id}` in samples |
| `<!-- pseudo:{id} -->` | Illustrative fragments | Manual, not compiled |
| `<!-- invalid:{id} -->` | Anti-patterns, wrong code | Manual, intentionally broken |
| `<!-- generated:{path}#L{n}-L{m} -->` | Source-generator output | Manual, with line tracking |

### Key Commands

```powershell
dotnet mdsnippets                          # Sync snippets to docs
git diff --exit-code docs/                 # Verify no drift
pwsh scripts/verify-code-blocks.ps1       # Check all blocks have markers
```

## Workflow: Adding Code to Documentation

### Step 1: Add Code to Samples Project

Create a region in `docs/samples/`:

```csharp
#region user-validation
public class UserValidation
{
    public bool IsValid(string email) => email.Contains("@");
}
#endregion
```

### Step 2: Reference in Documentation

Add a single line where the code should appear:

```markdown
## Email Validation

snippet: user-validation

This validates email format.
```

### Step 3: Run MarkdownSnippets

```powershell
dotnet mdsnippets
```

The tool injects the compiled code into the markdown, wrapped in `<!-- snippet: -->` and `<!-- endSnippet -->` markers.

### Step 4: Commit Both

Always commit code changes and documentation changes together.

## Choosing the Right Marker

```
Is this code intentionally broken?        → invalid:
Is this source-generator output?          → generated:
Could this compile with proper types?     → snippet: (add to samples)
Is this just a signature/fragment?        → pseudo:
```

**"But the types don't exist!"** — Create placeholder types in the samples project. The samples project exists to make documentation code real.

See [references/marker-types.md](references/marker-types.md) for detailed guidance.

## Ready to Commit Checklist

Before committing changes to documentation or code:

```
[ ] dotnet build                           # Code compiles
[ ] dotnet test                            # Tests pass
[ ] dotnet mdsnippets                      # Sync snippets
[ ] git diff --exit-code docs/             # No uncommitted changes
[ ] pwsh scripts/verify-code-blocks.ps1   # All blocks marked
```

If docs changed after `dotnet mdsnippets`, stage them:

```powershell
git add docs/
```

## Project Structure

```
{Project}/
├── README.md                              # mdsnippets-processed
├── docs/
│   ├── *.md                               # mdsnippets-processed
│   └── samples/                           # Code with #region markers
│       ├── {Project}.Samples/
│       └── {Project}.Samples.Tests/
├── scripts/
│   └── verify-code-blocks.ps1
├── mdsnippets.json                        # Configuration
└── .config/
    └── dotnet-tools.json                  # Tool manifest
```

## Configuration

Standard `mdsnippets.json`:

```json
{
  "Convention": "InPlaceOverwrite",
  "LinkFormat": "GitHub",
  "OmitSnippetLinks": true,
  "ExcludeDirectories": ["node_modules", "bin", "obj", ".git"]
}
```

## Snippet Naming Conventions

IDs must be globally unique across the project:

| Pattern | Example |
|---------|---------|
| feature-concept | `validation-email-rule` |
| entity-operation | `user-create-factory` |
| context-pattern | `server-di-setup` |

Avoid generic names like `example`, `usage`, or `pattern`.

## Non-Compiled Code Blocks

### Pseudo-code

For API signatures or incomplete fragments:

```markdown
<!-- pseudo:save-signature -->
```csharp
Task<T> Save<T>(T entity);
```
<!-- /snippet -->
```

### Invalid Examples

For anti-patterns or intentionally wrong code:

```markdown
<!-- invalid:wrong-pattern -->
```csharp
// WRONG - don't do this
await factory.Save(entity);  // Discards result
```
<!-- /snippet -->
```

### Generated Output

For source-generator output with drift detection:

```markdown
<!-- generated:Generated/Factory.g.cs#L15-L22 -->
```csharp
public interface IUserFactory { }
```
<!-- /snippet -->
```

## Additional Resources

### Reference Files

- **[references/marker-types.md](references/marker-types.md)** - Detailed marker decisions, common mistakes
- **[references/setup.md](references/setup.md)** - New project setup, tool installation
- **[references/verification.md](references/verification.md)** - Verification scripts, CI integration

### Scripts

- **[scripts/verify-code-blocks.ps1](scripts/verify-code-blocks.ps1)** - Verification script for pseudo/invalid markers

## Troubleshooting

### "Snippet not found"

The `snippet: {id}` has no matching `#region {id}` in code:
1. Check spelling
2. Run `grep -r "region {id}" docs/samples/`
3. Verify file isn't in ExcludeDirectories

### Unmarked Code Blocks

The verify script found ```` ```csharp ```` without a marker:
1. If compilable → Add to samples with `#region`, use `snippet:`
2. If illustrative → Add `<!-- pseudo:{id} -->` wrapper
3. If anti-pattern → Add `<!-- invalid:{id} -->` wrapper

### Docs Out of Sync

`dotnet mdsnippets` changed files:
1. Review changes with `git diff docs/`
2. Stage: `git add docs/`
3. Commit with code changes

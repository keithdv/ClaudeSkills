# 03 - Skill Sync

How to keep Claude skills in sync with documentation and source code using local-first skills.

---

## Architecture Overview

Skills live **in the repository** and are processed by MarkdownSnippets alongside documentation:

```
{Project}/
├── .claude/
│   └── skills/
│       └── {skill}/                    # Local skill (versioned with code)
│           ├── SKILL.md
│           └── *.md
├── docs/
│   ├── *.md                            # Documentation
│   └── samples/                        # Single source for BOTH
└── mdsnippets.json

~/.claude/skills/{skill}/               # Shared copy (for use outside repo)
```

**Key insight:** Both docs and skills use `snippet: {id}` markers. MarkdownSnippets processes them identically.

---

## Why Local-First?

| Aspect | Old (Shared Only) | New (Local-First) |
|--------|-------------------|-------------------|
| Location | `~/.claude/skills/` only | `.claude/skills/` in repo |
| Versioning | Manual sync table | Git-versioned with code |
| Snippet sync | Manual or custom script | MarkdownSnippets (same as docs) |
| CI verification | Manual check | `git diff --exit-code .claude/` |
| When in repo | Load shared (may be stale) | Load local (always current) |

---

## How It Works

### 1. Skills in Repository

Create skills in `.claude/skills/{skill}/`:

```
{Project}/.claude/skills/neatoo/
├── SKILL.md              # Overview, quick reference
├── entities.md           # EntityBase, ValidateBase details
├── factories.md          # Factory operations
└── ...
```

### 2. MarkdownSnippets Processes Skills

MarkdownSnippets scans ALL `.md` files not in excluded directories. Since `.claude/` isn't excluded, skills get processed:

```bash
dotnet mdsnippets
# Output includes:
# Processing: .claude/skills/neatoo/entities.md
#   Snippet: person-entity
#   Snippet: age-validation-rule
```

### 3. Claude Loads Local Skills

When working in the repo, Claude loads `./.claude/skills/` (local) rather than `~/.claude/skills/` (shared). Local takes precedence.

### 4. Copy to Shared on Commit

After committing, copy to shared location so the skill is available when working in other projects:

```powershell
Copy-Item -Recurse -Force ".claude/skills/{skill}" "$HOME/.claude/skills/"
```

### When Is the Shared Copy Used?

The shared copy (`~/.claude/skills/`) is loaded when you're **not** inside the skill's repository:

| You're working in... | Claude loads skill from... |
|---------------------|---------------------------|
| `~/repos/Neatoo/` | `.claude/skills/neatoo/` (local - always current) |
| `~/repos/KnockOff/` | `.claude/skills/knockoff/` (local) + `~/.claude/skills/neatoo/` (shared) |
| `~/repos/MyClientApp/` | `~/.claude/skills/neatoo/` (shared) |
| `~/repos/AnyOtherProject/` | `~/.claude/skills/*` (shared) |

**Concrete scenario:** You're building a client application that uses the Neatoo library. You want Claude to understand Neatoo patterns (EntityBase, factories, validation rules) while helping you write domain code. Claude loads `~/.claude/skills/neatoo/` because you're not in the Neatoo repo itself.

**Why both?**
- **Local** ensures skill content matches the exact version of code you're editing
- **Shared** makes skills available everywhere, even in projects that just *use* the library

If you only develop within Neatoo/KnockOff repos, the shared copy matters less. But if you (or others) build applications using these libraries, the shared skills provide framework guidance.

---

## Skill vs Documentation

| Aspect | Documentation | Claude Skill |
|--------|---------------|--------------|
| Audience | Developers reading docs | Claude assisting with code |
| Detail level | Comprehensive tutorials | Condensed quick reference |
| Code examples | Full context, step-by-step | Key patterns only |
| Location | `{project}/docs/` | `{project}/.claude/skills/{skill}/` |
| Snippet source | `docs/samples/` | `docs/samples/` (same!) |

**Key principle:** The skill is a **condensed summary** of documentation, not a duplicate. Both pull from the same compiled samples.

---

## Adding Snippets to Skills

Use the same `snippet: {id}` syntax as documentation:

**In `.claude/skills/neatoo/entities.md`:**
```markdown
## Basic Entity Pattern

snippet: person-entity

The entity uses `[Factory]` attribute for source generation.
```

**In `docs/samples/Entities/Person.cs`:**
```csharp
#region person-entity
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    public Person(IEntityBaseServices<Person> services) : base(services) { }

    [Required]
    public partial string? Name { get; set; }
}
#endregion
```

After `dotnet mdsnippets`, the skill file contains the actual compiled code.

---

## Workflow: Updating Skills

### When Code Changes

1. Edit code in `docs/samples/`
2. Run `dotnet build docs/samples/` - verify it compiles
3. Run `dotnet test docs/samples/` - verify tests pass
4. Run `dotnet mdsnippets` - syncs BOTH docs AND skills
5. Review changes: `git diff docs/ .claude/`
6. Commit everything together
7. Copy to shared: `Copy-Item -Recurse -Force ".claude/skills/{skill}" "$HOME/.claude/skills/"`

### When Adding New Skill Content

1. Add the content to skill file with `snippet: {id}` references
2. Ensure corresponding `#region {id}` exists in samples
3. Run `dotnet mdsnippets`
4. Commit and copy to shared

---

## Copy-on-Commit Options

### Option 1: Manual (Simplest)

Add to your commit workflow:

```powershell
# After git commit
Copy-Item -Recurse -Force ".claude/skills/neatoo" "$HOME/.claude/skills/"
```

### Option 2: Git Hook

Create `.git/hooks/post-commit`:

```bash
#!/bin/bash
# Copy local skills to shared location

SKILL_DIR=".claude/skills"
SHARED_DIR="$HOME/.claude/skills"

if [ -d "$SKILL_DIR" ]; then
    for skill in "$SKILL_DIR"/*; do
        if [ -d "$skill" ]; then
            skill_name=$(basename "$skill")
            echo "Copying skill: $skill_name"
            cp -r "$skill" "$SHARED_DIR/"
        fi
    done
fi
```

Make executable: `chmod +x .git/hooks/post-commit`

### Option 3: PowerShell Post-Commit Hook

For Windows, create a PowerShell script and call it from your workflow:

```powershell
# scripts/copy-skills-to-shared.ps1
$localSkills = ".claude/skills"
$sharedSkills = "$HOME/.claude/skills"

if (Test-Path $localSkills) {
    Get-ChildItem -Path $localSkills -Directory | ForEach-Object {
        $dest = Join-Path $sharedSkills $_.Name
        Write-Host "Copying skill: $($_.Name)" -ForegroundColor Cyan
        Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
    }
}
```

---

## CI Integration

### Verify Skills Are In Sync

```yaml
# .github/workflows/build.yml

- name: Run MarkdownSnippets
  run: dotnet mdsnippets

- name: Verify docs and skills unchanged
  run: |
    if [ -n "$(git status --porcelain docs/ .claude/)" ]; then
      echo "Documentation or skills out of sync"
      git diff docs/ .claude/
      exit 1
    fi
```

### Note on Shared Skills in CI

CI environments don't have `~/.claude/skills/`. This is fine - the local skills in the repo are what get verified. The shared copy is only for local development convenience.

---

## Skill Structure Recommendations

### SKILL.md (Entry Point)

```markdown
---
name: {skill-name}
description: Brief description for skill selection
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(...)
---

# {Skill Name}

Brief overview.

## Quick Reference

Key patterns with `snippet:` references.

## Detailed Guides

Links to other skill files.
```

### Topic Files

Keep focused on specific areas:
- `entities.md` - Entity patterns
- `factories.md` - Factory operations
- `validation.md` - Rule patterns
- etc.

Each can use `snippet: {id}` to pull from compiled samples.

---

## Skill Code Guidelines

### Do: Use Condensed Examples

Skills are for **quick reference**, not tutorials. Show the pattern, link to docs for details:

```markdown
### Save Pattern

snippet: save-pattern-correct

**Important:** Always reassign - `Save()` returns a new instance.

For complete examples, see `docs/factory-operations.md`.
```

### Don't: Duplicate Full Documentation

If you need 50 lines of explanation, it belongs in docs, not the skill. Skills should be scannable.

### Do: Use the Same Snippets as Docs

The same `#region` can appear in both:
- `docs/factory-operations.md` - Full context
- `.claude/skills/neatoo/factories.md` - Quick reference

MarkdownSnippets keeps both in sync automatically.

---

## Migration from Shared-Only Skills

If you have existing skills in `~/.claude/skills/{skill}/`:

1. **Copy to repo:**
   ```bash
   cp -r ~/.claude/skills/neatoo .claude/skills/
   ```

2. **Convert to snippet references:**
   Replace hardcoded code blocks with `snippet: {id}` where corresponding regions exist

3. **Run MarkdownSnippets:**
   ```bash
   dotnet mdsnippets
   ```

4. **Commit the local skill:**
   ```bash
   git add .claude/skills/
   git commit -m "feat: add neatoo skill to repository"
   ```

5. **Update shared on commit** (ongoing)

---

## Troubleshooting

### MarkdownSnippets Not Processing Skills

**Check:** Is `.claude` in `ExcludeDirectories`?

```json
// mdsnippets.json - ensure .claude is NOT listed
{
  "ExcludeDirectories": [
    "node_modules",
    "bin",
    "obj",
    ".git"
  ]
}
```

### Skill Shows Stale Content

**Cause:** Forgot to run `dotnet mdsnippets` or copy to shared.

**Fix:**
```bash
dotnet mdsnippets
Copy-Item -Recurse -Force ".claude/skills/{skill}" "$HOME/.claude/skills/"
```

### Snippet Not Found in Skill

**Cause:** The `snippet: {id}` references a region that doesn't exist.

**Fix:** Same as docs - ensure `#region {id}` exists in `docs/samples/`.

---

## Summary

| Step | Command |
|------|---------|
| Sync snippets | `dotnet mdsnippets` |
| Check changes | `git diff docs/ .claude/` |
| Commit | `git add -A && git commit` |
| Copy to shared | `Copy-Item -Recurse -Force ".claude/skills/{skill}" "$HOME/.claude/skills/"` |

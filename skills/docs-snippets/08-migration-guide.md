# 08 - Migration Guide

How to migrate from the custom `extract-snippets.ps1` implementation to MarkdownSnippets.

---

## Overview

This guide covers migrating from:
- **Old:** Custom `extract-snippets.ps1` with `#region docs:{file}:{id}` markers
- **New:** MarkdownSnippets tool with `#region {id}` markers + `pseudo:`/`invalid:` verification layer

---

## Why Migrate?

| Aspect | Custom Script | MarkdownSnippets |
|--------|---------------|------------------|
| Maintenance | You maintain it | Community maintained |
| Downloads | - | 317K+ |
| Verification | Custom | Built-in |
| Source links | None | Auto-generated |
| IDE support | None | JetBrains templates |
| Documentation | Your skill | Official docs |

---

## Prerequisites

Before starting migration, verify your repository has:

### Required

| Item | Check | If Missing |
|------|-------|------------|
| `docs/samples/` folder | Sample projects exist | See "Starting from Scratch" below |
| Existing `#region` markers | Code has `#region docs:{file}:{id}` | See "Starting from Scratch" below |
| Documentation folder | `docs/*.md` files exist | Create `docs/` and add markdown files |

### Recommended

| Item | Check | If Missing |
|------|-------|------------|
| Sample tests | `docs/samples/*.Tests/` project | Create test project for samples |
| CI pipeline | GitHub Actions workflow | Add after migration |

### Starting from Scratch?

If your repository doesn't have `docs/samples/` or existing snippet markers, you're not migrating - you're setting up fresh. Skip to [01-snippet-regions.md](01-snippet-regions.md) and [02-documentation-sync.md](02-documentation-sync.md) instead.

This migration guide is for repositories that already use the custom `extract-snippets.ps1` script with `#region docs:{file}:{id}` markers.

---

## Migration Checklist

```
[ ] Phase 1: Setup MarkdownSnippets
    [ ] Install dotnet tool
    [ ] Create mdsnippets.json config
    [ ] Create .gitattributes for generated files

[ ] Phase 2: Migrate C# Region Markers
    [ ] Convert #region docs:{file}:{id} to #region {id}
    [ ] Verify all regions have unique IDs across project
    [ ] Update file headers listing snippets

[ ] Phase 3: Migrate Markdown Placeholders
    [ ] Convert <!-- snippet: docs:{file}:{id} --> to snippet: {id}
    [ ] Remove <!-- /snippet --> closing tags
    [ ] Add pseudo:/invalid: markers to non-compiled blocks

[ ] Phase 4: Verification
    [ ] Run MarkdownSnippets to generate
    [ ] Create verify-code-blocks.ps1 for pseudo/invalid
    [ ] Update CI/CD pipeline
    [ ] Remove old extract-snippets.ps1

[ ] Phase 5: Cleanup
    [ ] Update skill documentation
    [ ] Update CLAUDE.md references
    [ ] Archive old script
```

---

## Phase 1: Setup MarkdownSnippets

### Step 1.1: Install the Tool

```bash
cd /path/to/your/project

# Create tool manifest if it doesn't exist
dotnet new tool-manifest

# Install MarkdownSnippets
dotnet tool install MarkdownSnippets.Tool

# Verify installation
dotnet mdsnippets --help
```

### Step 1.2: Create Configuration

Create `mdsnippets.json` in project root:

```json
{
  "Convention": "InPlaceOverwrite",
  "LinkFormat": "GitHub",
  "UrlPrefix": "",
  "ReadOnly": false,
  "OmitSnippetLinks": true,
  "ExcludeDirectories": [
    "node_modules",
    "bin",
    "obj",
    ".git"
  ],
  "ExcludeMarkdownDirectories": [],
  "DocumentExtensions": [
    "md"
  ]
}
```

**Configuration explained:**

| Setting | Value | Why |
|---------|-------|-----|
| `Convention` | `InPlaceOverwrite` | Modifies existing .md files directly |
| `LinkFormat` | `GitHub` | Generates GitHub-compatible source links |
| `OmitSnippetLinks` | `true` | Cleaner output (set `false` if you want source links) |
| `ReadOnly` | `false` | Allow editing generated sections |

### Step 1.3: Create .gitattributes (Optional)

If you want to mark generated content:

```gitattributes
# Mark snippet-generated content
**/docs/*.md linguist-generated=false
```

---

## Phase 2: Migrate C# Region Markers

### Step 2.1: Understand the Format Change

**Old format:**
```csharp
#region docs:validation-and-rules:age-validation-rule
public class AgeValidationRule : RuleBase<IPerson>
{
    // ...
}
#endregion
```

**New format:**
```csharp
#region age-validation-rule
public class AgeValidationRule : RuleBase<IPerson>
{
    // ...
}
#endregion
```

The `docs:{file}:` prefix is removed. MarkdownSnippets scans ALL code files and ALL markdown files, matching by snippet ID alone.

### Step 2.2: Migration Script for C# Files

Run this PowerShell script to convert all region markers:

```powershell
# migrate-regions.ps1
param(
    [string]$Path = "docs/samples",
    [switch]$WhatIf
)

$files = Get-ChildItem -Path $Path -Recurse -Include "*.cs"
$converted = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $original = $content

    # Convert: #region docs:{anything}:{id} -> #region {id}
    $content = $content -replace '#region docs:[^:]+:([^\r\n]+)', '#region $1'

    if ($content -ne $original) {
        $converted++
        Write-Host "Converting: $($file.FullName)" -ForegroundColor Yellow

        # Show what changed
        $oldRegions = [regex]::Matches($original, '#region docs:[^:]+:([^\r\n]+)')
        $newRegions = [regex]::Matches($content, '#region ([^\r\n]+)')

        for ($i = 0; $i -lt $oldRegions.Count; $i++) {
            Write-Host "  $($oldRegions[$i].Value) -> #region $($oldRegions[$i].Groups[1].Value)" -ForegroundColor Gray
        }

        if (-not $WhatIf) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
        }
    }
}

Write-Host "`nConverted $converted files" -ForegroundColor Cyan
if ($WhatIf) {
    Write-Host "(WhatIf mode - no files were modified)" -ForegroundColor Yellow
}
```

**Usage:**

```powershell
# Preview changes (no modifications)
.\migrate-regions.ps1 -Path "docs/samples" -WhatIf

# Apply changes
.\migrate-regions.ps1 -Path "docs/samples"
```

### Step 2.3: Verify Unique IDs

MarkdownSnippets requires globally unique snippet IDs. Check for duplicates:

```powershell
# check-duplicate-ids.ps1
param([string]$Path = "docs/samples")

$snippets = @{}
$duplicates = @()

Get-ChildItem -Path $Path -Recurse -Include "*.cs" | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw

    # Find all #region {name} patterns
    $regions = [regex]::Matches($content, '#region\s+([^\r\n]+)')

    foreach ($match in $regions) {
        $id = $match.Groups[1].Value.Trim()

        # Skip non-snippet regions (like standard Visual Studio regions)
        if ($id -match '^(Fields|Properties|Methods|Constructor|Private|Public)$') {
            continue
        }

        if ($snippets.ContainsKey($id)) {
            $duplicates += [PSCustomObject]@{
                Id = $id
                File1 = $snippets[$id]
                File2 = $file
            }
        } else {
            $snippets[$id] = $file
        }
    }
}

if ($duplicates) {
    Write-Host "DUPLICATE SNIPPET IDs FOUND:" -ForegroundColor Red
    $duplicates | Format-Table -AutoSize
    exit 1
} else {
    Write-Host "All $($snippets.Count) snippet IDs are unique" -ForegroundColor Green
}
```

### Step 2.4: Resolve Duplicates

If duplicates are found, rename them to be unique. Common strategies:

```csharp
// Before: Both files had #region save-pattern
// File1: factories/PersonFactory.cs
// File2: factories/OrderFactory.cs

// After: Add prefix for context
// File1: #region person-save-pattern
// File2: #region order-save-pattern
```

### Step 2.5: Update File Headers

Update the snippet listing in file headers:

**Old:**
```csharp
/// <summary>
/// Code samples for docs/validation-and-rules.md
///
/// Snippets in this file:
/// - docs:validation-and-rules:required-attribute
/// - docs:validation-and-rules:age-validation-rule
/// </summary>
```

**New:**
```csharp
/// <summary>
/// Code samples for validation documentation.
///
/// Snippets in this file:
/// - required-attribute
/// - age-validation-rule
/// </summary>
```

---

## Phase 3: Migrate Markdown Placeholders

### Step 3.1: Understand the Format Change

**Old format:**
```markdown
Here's how to define an age validation rule:

<!-- snippet: docs:validation-and-rules:age-validation-rule -->
```csharp
// placeholder content
```
<!-- /snippet -->

Next, let's look at...
```

**New format:**
```markdown
Here's how to define an age validation rule:

snippet: age-validation-rule

Next, let's look at...
```

The `snippet:` line stands alone - no HTML comments, no code fence, no closing tag.

### Step 3.2: Migration Script for Markdown Files

```powershell
# migrate-markdown.ps1
param(
    [string]$Path = "docs",
    [switch]$WhatIf
)

$files = Get-ChildItem -Path $Path -Recurse -Include "*.md" -Exclude "*.source.md"
$converted = 0
$snippetsConverted = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $original = $content

    # Pattern to match old snippet blocks:
    # <!-- snippet: docs:{file}:{id} -->
    # ```csharp
    # ... any content ...
    # ```
    # <!-- /snippet -->

    $pattern = '(?s)<!-- snippet: docs:[^:]+:([^\s]+)\s*-->\r?\n```(?:csharp|razor)\r?\n.*?```\r?\n<!-- /snippet -->'

    $matches = [regex]::Matches($content, $pattern)
    $snippetsConverted += $matches.Count

    # Replace with new format
    $content = [regex]::Replace($content, $pattern, 'snippet: $1')

    if ($content -ne $original) {
        $converted++
        Write-Host "Converting: $($file.FullName) ($($matches.Count) snippets)" -ForegroundColor Yellow

        if (-not $WhatIf) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
        }
    }
}

Write-Host "`nConverted $snippetsConverted snippets in $converted files" -ForegroundColor Cyan
if ($WhatIf) {
    Write-Host "(WhatIf mode - no files were modified)" -ForegroundColor Yellow
}
```

**Usage:**

```powershell
# Preview changes
.\migrate-markdown.ps1 -Path "docs" -WhatIf

# Apply changes
.\migrate-markdown.ps1 -Path "docs"
```

### Step 3.3: Add Markers to Non-Compiled Code Blocks

After migration, you'll have:
1. **Compiled snippets:** `snippet: {id}` - handled by MarkdownSnippets
2. **Pseudo-code:** Needs `<!-- snippet: pseudo:{id} -->` markers
3. **Invalid examples:** Needs `<!-- snippet: invalid:{id} -->` markers

Find unmarked code blocks:

```powershell
# find-unmarked-blocks.ps1
param([string]$Path = "docs")

Get-ChildItem -Path $Path -Recurse -Include "*.md" | ForEach-Object {
    $file = $_.Name
    $lines = Get-Content $_.FullName
    $inSnippet = $false
    $lineNum = 0

    foreach ($line in $lines) {
        $lineNum++

        # Track MarkdownSnippets output blocks
        if ($line -match '^<!-- snippet:' -or $line -match '^snippet:') {
            $inSnippet = $true
        }
        if ($line -match '^<!-- endSnippet -->' -or $line -match '^<!-- /snippet -->') {
            $inSnippet = $false
        }

        # Find code blocks not preceded by a marker
        if ($line -match '^```csharp' -and -not $inSnippet) {
            # Check previous line for marker
            $prevLine = if ($lineNum -gt 1) { $lines[$lineNum - 2] } else { "" }
            if ($prevLine -notmatch 'snippet:') {
                Write-Warning "${file}:${lineNum} - Unmarked code block"
            }
        }
    }
}
```

### Step 3.4: Add pseudo:/invalid: Markers

For each unmarked block, determine its type and add the appropriate marker:

**Pseudo-code (illustrative, not compiled):**
```markdown
<!-- snippet: pseudo:db-save-concept -->
```csharp
// In a real implementation:
// await db.SaveChangesAsync();
```
<!-- /snippet -->
```

**Invalid example (anti-pattern):**
```markdown
<!-- snippet: invalid:wrong-save-pattern -->
```csharp
// WRONG - discards the updated entity
await factory.Save(person);
```
<!-- /snippet -->
```

---

## Phase 4: Verification

### Step 4.1: Run MarkdownSnippets

```bash
# Generate/update all documentation
dotnet mdsnippets

# Check output
git diff docs/
```

**Expected output:**
```
Processing directory: /path/to/project
Processing: docs/validation-and-rules.md
  Snippet: age-validation-rule
  Snippet: required-attribute
Processing: docs/factories.md
  Snippet: create-pattern
  Snippet: save-pattern
Processed 4 snippets in 2 files
```

### Step 4.2: Create Verification Script for pseudo:/invalid:

Create `scripts/verify-code-blocks.ps1`:

```powershell
# verify-code-blocks.ps1
# Verifies all C# code blocks have appropriate markers
param(
    [string]$DocsPath = "docs",
    [switch]$Verbose
)

$errors = @()
$stats = @{
    Files = 0
    CompiledSnippets = 0
    PseudoSnippets = 0
    InvalidSnippets = 0
    Unmarked = 0
}

Get-ChildItem -Path $DocsPath -Recurse -Include "*.md" | ForEach-Object {
    $file = $_
    $stats.Files++
    $content = Get-Content $file.FullName -Raw
    $lines = Get-Content $file.FullName

    # Count snippet types
    $stats.CompiledSnippets += ([regex]'(?m)^snippet:\s+\S+').Matches($content).Count
    $stats.CompiledSnippets += ([regex]'<!-- snippet: docs:').Matches($content).Count
    $stats.PseudoSnippets += ([regex]'<!-- snippet: pseudo:').Matches($content).Count
    $stats.InvalidSnippets += ([regex]'<!-- snippet: invalid:').Matches($content).Count

    # Check for unclosed pseudo/invalid snippets
    $pseudoOpens = ([regex]'<!-- snippet: pseudo:').Matches($content).Count
    $invalidOpens = ([regex]'<!-- snippet: invalid:').Matches($content).Count
    $manualCloses = ([regex]'<!-- /snippet -->').Matches($content).Count

    if (($pseudoOpens + $invalidOpens) -ne $manualCloses) {
        $errors += "$($file.Name): Unclosed snippet (pseudo:$pseudoOpens + invalid:$invalidOpens opens, $manualCloses closes)"
    }

    # Find unmarked code blocks
    $lineNum = 0
    $inManagedSnippet = $false

    foreach ($line in $lines) {
        $lineNum++

        # Track managed snippets (MarkdownSnippets output or manual pseudo/invalid)
        if ($line -match '^snippet:\s+\S+' -or $line -match '<!-- snippet:') {
            $inManagedSnippet = $true
        }
        if ($line -match '<!-- endSnippet -->' -or $line -match '<!-- /snippet -->') {
            $inManagedSnippet = $false
        }

        # Find ```csharp blocks
        if ($line -match '^```csharp') {
            if (-not $inManagedSnippet) {
                # Check if previous line has any snippet marker
                $prevLine = if ($lineNum -gt 1) { $lines[$lineNum - 2] } else { "" }
                if ($prevLine -notmatch 'snippet:') {
                    $stats.Unmarked++
                    $errors += "$($file.Name):$lineNum - Unmarked C# code block"
                }
            }
        }
    }
}

# Output results
Write-Host "`n=== Code Block Verification ===" -ForegroundColor Cyan
Write-Host "Files scanned: $($stats.Files)"
Write-Host "Compiled snippets (MarkdownSnippets): $($stats.CompiledSnippets)" -ForegroundColor Green
Write-Host "Pseudo-code blocks: $($stats.PseudoSnippets)" -ForegroundColor Yellow
Write-Host "Invalid/anti-pattern blocks: $($stats.InvalidSnippets)" -ForegroundColor Yellow
Write-Host "Unmarked blocks: $($stats.Unmarked)" -ForegroundColor $(if ($stats.Unmarked -gt 0) { 'Red' } else { 'Green' })

if ($errors) {
    Write-Host "`nErrors found:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
} else {
    Write-Host "`nAll code blocks are properly marked" -ForegroundColor Green
    exit 0
}
```

### Step 4.3: Update CI/CD Pipeline

```yaml
# .github/workflows/build.yml

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - name: Restore tools
        run: dotnet tool restore

      - name: Build samples
        run: dotnet build docs/samples/

      - name: Test samples
        run: dotnet test docs/samples/

      - name: Run MarkdownSnippets
        run: dotnet mdsnippets

      - name: Verify docs unchanged
        run: |
          if [ -n "$(git status --porcelain docs/)" ]; then
            echo "Documentation out of sync with code snippets"
            git diff docs/
            exit 1
          fi

      - name: Verify code block coverage
        run: pwsh -File scripts/verify-code-blocks.ps1
```

### Step 4.4: Remove Old Script

Once everything is working:

```bash
# Archive the old script
mkdir -p scripts/archive
mv scripts/extract-snippets.ps1 scripts/archive/

# Or just delete it
rm scripts/extract-snippets.ps1
```

---

## Phase 5: Cleanup

### Step 5.1: Update Tool Manifest

Ensure `.config/dotnet-tools.json` includes MarkdownSnippets:

```json
{
  "version": 1,
  "isRoot": true,
  "tools": {
    "markdownsnippets.tool": {
      "version": "27.0.2",
      "commands": [
        "mdsnippets"
      ]
    }
  }
}
```

### Step 5.2: Update README/Contributing Docs

Add to project README or CONTRIBUTING.md:

```markdown
## Documentation

Code examples in documentation are extracted from compiled sample projects.

### Updating Documentation

1. Edit code in `docs/samples/`
2. Run `dotnet mdsnippets` to sync
3. Commit both code and documentation changes

### Verification

```bash
dotnet build docs/samples/
dotnet test docs/samples/
dotnet mdsnippets
pwsh scripts/verify-code-blocks.ps1
```
```

### Step 5.3: Update CLAUDE.md

If your CLAUDE.md references the old system, update it:

**Old:**
```markdown
- Run `.\scripts\extract-snippets.ps1 -Update` to sync to docs
```

**New:**
```markdown
- Run `dotnet mdsnippets` to sync snippets to docs
- Run `pwsh scripts/verify-code-blocks.ps1` to verify all code blocks have markers
```

---

## Quick Reference: Before & After

### C# Region Markers

| Before | After |
|--------|-------|
| `#region docs:validation:age-rule` | `#region age-rule` |
| `#region docs:factories:save-pattern` | `#region save-pattern` |
| `#region docs:entities:person-class` | `#region person-class` |

### Markdown Placeholders

| Before | After |
|--------|-------|
| `<!-- snippet: docs:validation:age-rule -->` | `snippet: age-rule` |
| ` ```csharp ` | (removed - auto-generated) |
| `// placeholder` | (removed - auto-generated) |
| ` ``` ` | (removed - auto-generated) |
| `<!-- /snippet -->` | (removed - auto-generated) |

### Commands

| Before | After |
|--------|-------|
| `.\scripts\extract-snippets.ps1 -Update` | `dotnet mdsnippets` |
| `.\scripts\extract-snippets.ps1 -Verify` | `dotnet mdsnippets` + `git diff --exit-code` |
| (none) | `pwsh scripts/verify-code-blocks.ps1` |

### Non-Compiled Code Markers

| Type | Format (unchanged) |
|------|-------------------|
| Pseudo-code | `<!-- snippet: pseudo:{id} -->` ... `<!-- /snippet -->` |
| Invalid/anti-pattern | `<!-- snippet: invalid:{id} -->` ... `<!-- /snippet -->` |

---

## Troubleshooting

### "Snippet not found" Error

**Symptom:** MarkdownSnippets reports missing snippet

**Cause:** The `snippet: {id}` in markdown doesn't match any `#region {id}` in code

**Fix:**
1. Check spelling of snippet ID
2. Verify region exists in code: `grep -r "region {id}" docs/samples/`
3. Ensure region is not inside a comment or #if false block

### Duplicate Snippet IDs

**Symptom:** MarkdownSnippets uses wrong code or reports duplicate

**Cause:** Same `#region {id}` in multiple files

**Fix:** Rename regions to be unique (add prefix like `person-save-pattern` vs `order-save-pattern`)

### Code Block Not Updating

**Symptom:** Markdown still shows old code after running mdsnippets

**Cause:** Using `SourceTransform` convention with `.source.md` files

**Fix:** Either:
- Switch to `InPlaceOverwrite` in mdsnippets.json
- Or edit the `.source.md` file, not the generated `.md` file

### Unmarked Blocks After Migration

**Symptom:** verify-code-blocks.ps1 reports unmarked blocks

**Cause:** Code blocks that weren't using the old snippet system

**Fix:** Add appropriate marker:
- If it should be compiled: Add to samples project with `#region`, then add `snippet:` line
- If it's illustrative: Add `<!-- snippet: pseudo:{id} -->` wrapper
- If it's an anti-pattern: Add `<!-- snippet: invalid:{id} -->` wrapper

---

## Rollback Plan

If migration fails, you can rollback:

```bash
# Restore old script from archive
mv scripts/archive/extract-snippets.ps1 scripts/

# Revert markdown changes
git checkout docs/*.md

# Revert C# region changes
git checkout docs/samples/

# Remove MarkdownSnippets
dotnet tool uninstall MarkdownSnippets.Tool
rm mdsnippets.json
```

---

## Post-Migration Verification

After completing migration, verify everything works:

```bash
# 1. Build samples
dotnet build docs/samples/

# 2. Test samples
dotnet test docs/samples/

# 3. Generate snippets
dotnet mdsnippets

# 4. Verify no uncommitted changes (CI check)
git diff --exit-code docs/

# 5. Verify all code blocks have markers
pwsh scripts/verify-code-blocks.ps1

# 6. Manual review: spot-check a few markdown files
```

If all checks pass, commit the migration:

```bash
git add .
git commit -m "chore: migrate to MarkdownSnippets for documentation snippets

- Replace custom extract-snippets.ps1 with MarkdownSnippets dotnet tool
- Convert #region docs:{file}:{id} to #region {id} format
- Convert <!-- snippet: --> placeholders to snippet: format
- Add verify-code-blocks.ps1 for pseudo:/invalid: marker verification
- Update CI pipeline"
```

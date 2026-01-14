# 04 - Verification

How to verify that documentation and skills are in sync with compiled code.

---

## Verification Layers

Documentation has four types of C# code blocks:

| Type | Verified By | Why Separate? |
|------|-------------|---------------|
| **Compiled snippets** | MarkdownSnippets | Tool extracts from `#region` - fails if missing |
| **Pseudo-code** (`<!-- pseudo: -->`) | verify-code-blocks.ps1 | MarkdownSnippets ignores these (just HTML comments) |
| **Invalid examples** (`<!-- invalid: -->`) | verify-code-blocks.ps1 | MarkdownSnippets ignores these too |
| **Generated output** (`<!-- generated: -->`) | verify-generated-snippets.ps1 | Tracks source-generated code with line number drift detection |

**Why multiple verification systems?** MarkdownSnippets only knows about compiled snippets (those with matching `#region` markers in code). It has no awareness of `pseudo:`, `invalid:`, or `generated:` blocks - those are just HTML comments to MarkdownSnippets. The verification scripts fill the gap by ensuring every C# code block has *some* marker and that generated snippets haven't drifted.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Code Compiles                                      │
│ dotnet build docs/samples/                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Tests Pass                                         │
│ dotnet test docs/samples/                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: MarkdownSnippets Sync (Docs AND Skills)            │
│ dotnet mdsnippets && git diff --exit-code docs/ .claude/    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Code Block Coverage                                │
│ pwsh scripts/verify-code-blocks.ps1                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Copy Skill to Shared                               │
│ Copy-Item -Recurse -Force ".claude/skills/*" "~/.claude/skills/" │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Code Compiles

**What it verifies:** Syntax is correct, APIs exist, types resolve

```powershell
dotnet build docs/samples/
```

**Common failures:**
- Removed/renamed API in main project
- Missing using statements
- Type mismatches

**Fix:** Update sample code to match current API

---

## Layer 2: Tests Pass

**What it verifies:** Code examples actually work as documented

```powershell
dotnet test docs/samples/
```

**Common failures:**
- Behavior changed in main project
- Sample code doesn't demonstrate correct usage
- Missing setup in test

**Fix:** Update sample code and/or tests to reflect current behavior

---

## Layer 3: MarkdownSnippets Sync

**What it verifies:** Documentation AND skill files contain current compiled code

```powershell
# Update snippets in docs AND skills
dotnet mdsnippets

# Check if anything changed (CI verification)
git diff --exit-code docs/ .claude/
```

**If nothing changed:** Documentation and skills are in sync.

**If changes detected:** Snippets were out of date. Either:
- Commit the changes: `git add docs/ .claude/ && git commit -m "docs: sync snippets"`
- Or investigate why they drifted

**Note:** MarkdownSnippets processes ALL `.md` files not in excluded directories, including `.claude/skills/`.

### MarkdownSnippets Built-in Verification

MarkdownSnippets itself verifies:
- Every `snippet: {id}` has a matching `#region {id}` in code
- No duplicate snippet IDs exist
- Regions are properly closed

If a snippet reference can't be resolved, MarkdownSnippets **fails with an error**.

---

## Layer 4: Code Block Coverage

**What it verifies:** Every C# code block has a marker

MarkdownSnippets handles compiled snippets. But pseudo-code and invalid examples use manual markers that MarkdownSnippets ignores. This layer verifies those.

### The verify-code-blocks.ps1 Script

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
    GeneratedSnippets = 0
    Unmarked = 0
}

Get-ChildItem -Path $DocsPath -Recurse -Include "*.md" | ForEach-Object {
    $file = $_
    $stats.Files++
    $content = Get-Content $file.FullName -Raw
    $lines = Get-Content $file.FullName

    # Count MarkdownSnippets-managed blocks (look for endSnippet marker)
    $stats.CompiledSnippets += ([regex]'<!-- endSnippet -->').Matches($content).Count

    # Count manual pseudo/invalid/generated blocks
    $stats.PseudoSnippets += ([regex]'<!-- pseudo:').Matches($content).Count
    $stats.InvalidSnippets += ([regex]'<!-- invalid:').Matches($content).Count
    $stats.GeneratedSnippets += ([regex]'<!-- generated:').Matches($content).Count

    # Check for unclosed manual snippets
    $pseudoOpens = ([regex]'<!-- pseudo:').Matches($content).Count
    $invalidOpens = ([regex]'<!-- invalid:').Matches($content).Count
    $generatedOpens = ([regex]'<!-- generated:').Matches($content).Count
    $manualCloses = ([regex]'<!-- /snippet -->').Matches($content).Count

    if (($pseudoOpens + $invalidOpens + $generatedOpens) -ne $manualCloses) {
        $errors += "$($file.Name): Unclosed manual snippet (pseudo:$pseudoOpens + invalid:$invalidOpens + generated:$generatedOpens opens, $manualCloses closes)"
    }

    # Find unmarked code blocks
    $lineNum = 0
    $inManagedSnippet = $false

    foreach ($line in $lines) {
        $lineNum++

        # Track MarkdownSnippets-managed blocks
        if ($line -match '<!-- snippet:' -or $line -match '^snippet:\s+\S+') {
            $inManagedSnippet = $true
        }
        if ($line -match '<!-- endSnippet -->' -or $line -match '<!-- /snippet -->') {
            $inManagedSnippet = $false
        }

        # Find ```csharp blocks
        if ($line -match '^```csharp') {
            if (-not $inManagedSnippet) {
                $stats.Unmarked++
                $errors += "$($file.Name):$lineNum - Unmarked C# code block"
                if ($Verbose) {
                    # Show context
                    $contextStart = [Math]::Max(0, $lineNum - 3)
                    $contextEnd = [Math]::Min($lines.Count - 1, $lineNum + 2)
                    Write-Host "  Context:" -ForegroundColor Gray
                    for ($i = $contextStart; $i -le $contextEnd; $i++) {
                        $prefix = if ($i -eq $lineNum - 1) { ">>> " } else { "    " }
                        Write-Host "$prefix$($lines[$i])" -ForegroundColor Gray
                    }
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
Write-Host "Generated output blocks: $($stats.GeneratedSnippets)" -ForegroundColor Cyan
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

### Running the Script

```powershell
# Basic check
pwsh scripts/verify-code-blocks.ps1

# With context for unmarked blocks
pwsh scripts/verify-code-blocks.ps1 -Verbose
```

### What It Checks

1. **Compiled snippets** - Blocks with `<!-- endSnippet -->` (MarkdownSnippets output)
2. **Pseudo-code** - Blocks with `<!-- pseudo:{id} -->` and `<!-- /snippet -->`
3. **Invalid examples** - Blocks with `<!-- invalid:{id} -->` and `<!-- /snippet -->`
4. **Generated output** - Blocks with `<!-- generated:{path}#L{start}-L{end} -->` and `<!-- /snippet -->`
5. **Unmarked blocks** - Any ` ```csharp ` not inside a managed snippet

---

## Layer 4b: Generated Snippet Drift Detection

**What it verifies:** Source-generated code snippets match current generator output

Generated snippets show output from Roslyn source generators (e.g., factory interfaces, property implementations). These change when the generator evolves. The `generated:` marker includes a file path and line range to detect drift.

### Format

```markdown
<!-- generated:Samples.DomainModel/Generated/Neatoo.Factory/PersonFactory.g.cs#L15-L22 -->
```csharp
public interface IPersonFactory
{
    IPerson Create();
    Task<IPerson> Fetch(int id);
}
```
<!-- /snippet -->
```

### Format Requirements

Generated snippets must follow these constraints:

| Requirement | Correct | Incorrect |
|-------------|---------|-----------|
| Language specifier required | ` ```csharp ` | ` ``` ` (bare) |
| No ` ``` ` in snippet content | Clean C# code | Code containing markdown examples |

### Path Resolution

The path in `generated:{path}#L{start}-L{end}` is **relative to the samples folder**:

| Marker Path | Base Path (default) | Resolved Path |
|-------------|---------------------|---------------|
| `Samples.DomainModel/Generated/...` | `docs/samples` | `docs/samples/Samples.DomainModel/Generated/...` |

The verification script joins `$BasePath` + marker path:
```powershell
$sourcePath = Join-Path $BasePath $match.Groups[1].Value
# Example: Join-Path "docs/samples" "Samples.DomainModel/Generated/PersonFactory.g.cs"
# Result:  "docs/samples/Samples.DomainModel/Generated/PersonFactory.g.cs"
```

**Important:** Don't include `docs/samples/` in the marker path - that's handled by the base path parameter.

### The verify-generated-snippets.ps1 Script

```powershell
# verify-generated-snippets.ps1
# Verifies generated snippets match their source files
param(
    [string]$DocsPath = "docs",
    [string]$BasePath = "docs/samples"
)

$errors = @()
$checked = 0

Get-ChildItem -Path $DocsPath -Recurse -Include "*.md" | ForEach-Object {
    $file = $_
    $content = Get-Content $file.FullName -Raw

    # Find all generated snippet markers
    # Note: This pattern requires:
    #   - A language specifier after ``` (e.g., ```csharp, not bare ```)
    #   - No ``` sequences inside the snippet content itself
    $pattern = '<!-- generated:([^#]+)#L(\d+)-L(\d+)\s*-->\s*```\w+\s*([\s\S]*?)```\s*<!-- /snippet -->'
    $matches = [regex]::Matches($content, $pattern)

    foreach ($match in $matches) {
        $checked++
        $sourcePath = Join-Path $BasePath $match.Groups[1].Value
        $startLine = [int]$match.Groups[2].Value
        $endLine = [int]$match.Groups[3].Value
        $snippetContent = $match.Groups[4].Value.Trim()

        if (-not (Test-Path $sourcePath)) {
            $errors += "$($file.Name): generated:$($match.Groups[1].Value) - File not found"
            continue
        }

        $sourceLines = Get-Content $sourcePath
        $actualContent = ($sourceLines[($startLine-1)..($endLine-1)] -join "`n").Trim()

        if ($snippetContent -ne $actualContent) {
            $errors += "$($file.Name): generated:$($match.Groups[1].Value)#L$startLine-L$endLine - MISMATCH"
            $errors += "  Expected (from file):"
            $errors += "    $($actualContent.Substring(0, [Math]::Min(100, $actualContent.Length)))..."
            $errors += "  Found (in doc):"
            $errors += "    $($snippetContent.Substring(0, [Math]::Min(100, $snippetContent.Length)))..."
        }
    }
}

Write-Host "`n=== Generated Snippet Verification ===" -ForegroundColor Cyan
Write-Host "Checked: $checked generated snippets"

if ($errors) {
    Write-Host "`nDrift detected:" -ForegroundColor Yellow
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host "`nReview these snippets - generator output may have changed" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "All generated snippets match source files" -ForegroundColor Green
    exit 0
}
```

### When Drift Is Detected

A mismatch means the source generator output changed. This is a **signal to review**, not necessarily an error:

1. **Build the project** to regenerate `.g.cs` files
2. **Compare** the new output with the documented snippet
3. **Update the snippet** if the change is intentional
4. **Update line numbers** in the marker to match new location
5. **Investigate** if the change was unexpected

### Why Line Numbers?

Line numbers serve as a canary:
- Generator refactoring shifts line numbers → drift detected
- New code inserted above → line numbers shift → drift detected
- Content at those lines changes → content mismatch → drift detected

Even if content happens to match at wrong lines, the line number drift signals review is needed.

---

## Layer 5: Copy Skill to Shared

**What it does:** Copies local skill to shared location for use outside the repo

Skills live in the repository at `.claude/skills/{skill}/` and are processed by MarkdownSnippets (Layer 3). After committing, copy to `~/.claude/skills/` so the skill is available when working in other projects.

### Copy Command

```powershell
# Copy all skills to shared location
Copy-Item -Recurse -Force ".claude/skills/*" "$HOME/.claude/skills/"

# Or copy a specific skill
Copy-Item -Recurse -Force ".claude/skills/neatoo" "$HOME/.claude/skills/"
```

### When to Copy

- **Every commit** that changes skill files
- **After pulling** changes that update skills
- **After cloning** a repo with local skills

### Automation Options

See [03-skill-sync.md](03-skill-sync.md) for git hook options to automate this step.

### Why Copy?

| Context | What Claude Loads |
|---------|-------------------|
| Working in Neatoo repo | `./.claude/skills/neatoo/` (local, current) |
| Working elsewhere | `~/.claude/skills/neatoo/` (shared copy) |

The copy ensures the shared version stays current with the repo.

---

## Full Verification Sequence

Run all layers in order:

```powershell
# 1. Build samples
Write-Host "`n[1/6] Building samples..." -ForegroundColor Cyan
dotnet build docs/samples/
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }

# 2. Run tests
Write-Host "`n[2/6] Running tests..." -ForegroundColor Cyan
dotnet test docs/samples/
if ($LASTEXITCODE -ne 0) { Write-Error "Tests failed"; exit 1 }

# 3. Sync snippets (docs AND skills)
Write-Host "`n[3/6] Running MarkdownSnippets..." -ForegroundColor Cyan
dotnet mdsnippets
if ($LASTEXITCODE -ne 0) { Write-Error "MarkdownSnippets failed"; exit 1 }

# Check for uncommitted changes in docs and skills
$changes = git status --porcelain docs/ .claude/
if ($changes) {
    Write-Warning "Documentation or skills were out of sync. Changes:"
    git diff docs/ .claude/
    Write-Host "`nRun 'git add docs/ .claude/' to stage the updates" -ForegroundColor Yellow
}

# 4a. Verify code block coverage
Write-Host "`n[4/6] Verifying code block coverage..." -ForegroundColor Cyan
pwsh scripts/verify-code-blocks.ps1
if ($LASTEXITCODE -ne 0) { Write-Error "Unmarked code blocks found"; exit 1 }

# 4b. Verify generated snippets (if script exists)
Write-Host "`n[5/6] Verifying generated snippets..." -ForegroundColor Cyan
if (Test-Path "scripts/verify-generated-snippets.ps1") {
    pwsh scripts/verify-generated-snippets.ps1
    if ($LASTEXITCODE -ne 0) { Write-Warning "Generated snippet drift detected - review needed" }
} else {
    Write-Host "No verify-generated-snippets.ps1 found, skipping" -ForegroundColor Yellow
}

# 5. Copy skills to shared location
Write-Host "`n[6/6] Copying skills to shared location..." -ForegroundColor Cyan
if (Test-Path ".claude/skills") {
    Copy-Item -Recurse -Force ".claude/skills/*" "$HOME/.claude/skills/"
    Write-Host "Skills copied to ~/.claude/skills/" -ForegroundColor Green
} else {
    Write-Host "No local skills found" -ForegroundColor Yellow
}

Write-Host "`n=== Verification Complete ===" -ForegroundColor Green
```

---

## CI Integration

### GitHub Actions

```yaml
# .github/workflows/build.yml

name: Build and Verify

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

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

      - name: Verify docs and skills unchanged
        run: |
          if [ -n "$(git status --porcelain docs/ .claude/)" ]; then
            echo "::error::Documentation or skills out of sync with code snippets"
            git diff docs/ .claude/
            exit 1
          fi

      - name: Verify code block coverage
        run: pwsh scripts/verify-code-blocks.ps1

      - name: Verify generated snippets
        run: |
          if [ -f "scripts/verify-generated-snippets.ps1" ]; then
            pwsh scripts/verify-generated-snippets.ps1
          fi
```

**This ensures:**
- PRs can't merge with broken code examples
- Documentation AND skills stay in sync with code
- All code blocks have appropriate markers
- Generated snippet drift is detected for review
- API changes require documentation and skill updates

**Note:** CI doesn't copy to `~/.claude/skills/` - that's a local development convenience. CI verifies the local skills are in sync.

---

## Verification Checklist

### Before Committing Code Changes

- [ ] `dotnet build docs/samples/` passes
- [ ] `dotnet test docs/samples/` passes
- [ ] `dotnet mdsnippets` runs without error
- [ ] `git diff docs/ .claude/` shows expected changes only
- [ ] `pwsh scripts/verify-code-blocks.ps1` passes
- [ ] Skills copied to shared: `Copy-Item -Recurse -Force ".claude/skills/*" "$HOME/.claude/skills/"`

### Before Releasing

- [ ] All above checks pass
- [ ] Release notes updated
- [ ] Version number updated

---

## Common Issues

### "Snippet not found" from MarkdownSnippets

A `snippet: {id}` reference has no matching `#region {id}` in code.

**Fix:**
1. Check spelling
2. `grep -r "region {id}" docs/samples/`
3. Ensure file is not in ExcludeDirectories

### Unmarked Code Blocks

The verify-code-blocks.ps1 script found a ` ```csharp ` block without a marker.

**Fix:** Add the appropriate marker:

```markdown
<!-- For compiled code (add to samples first) -->
snippet: my-snippet-id

<!-- For pseudo-code -->
<!-- pseudo:concept-name -->
```csharp
// illustrative code
```
<!-- /snippet -->

<!-- For anti-patterns -->
<!-- invalid:bad-example -->
```csharp
// WRONG - don't do this
```
<!-- /snippet -->

<!-- For source-generated output -->
<!-- generated:Path/To/Generated/File.g.cs#L15-L22 -->
```csharp
// code from source generator
```
<!-- /snippet -->
```

### Generated Snippet Drift

The verify-generated-snippets.ps1 script reports a mismatch between the documented snippet and the actual generated file.

**This is a signal to review, not necessarily an error.** The source generator output changed.

**Fix:**
1. Build the project to regenerate `.g.cs` files
2. Review the new output vs documented snippet
3. Update the snippet content if the change is intentional
4. Update the line numbers in the marker: `#L{new-start}-L{new-end}`

### Documentation Changed After mdsnippets

This is expected when code was updated but docs weren't synced.

**Fix:**
```bash
dotnet mdsnippets
git add docs/
git commit -m "docs: sync snippets with code"
```

### Unclosed Manual Snippet

A `<!-- pseudo: -->`, `<!-- invalid: -->`, or `<!-- generated: -->` is missing its `<!-- /snippet -->`.

**Fix:** Add the closing tag after the code block.

---

## Fixing Out-of-Sync Documentation

When verification fails:

### Option 1: Update Samples (Code Changed Correctly)

If the main project API changed and samples are outdated:

1. Update sample code to use new API
2. Update tests
3. Run `dotnet mdsnippets`
4. Commit all changes

### Option 2: Revert Code Change (Documentation Was Correct)

If samples had the right pattern and main code regressed:

1. Fix the main project code
2. Verify samples still pass
3. No doc changes needed

### Option 3: Update Both

If both code and documentation need updates:

1. Update main project
2. Update samples
3. Update tests
4. Run `dotnet mdsnippets`
5. Update skill if needed
6. Commit everything together

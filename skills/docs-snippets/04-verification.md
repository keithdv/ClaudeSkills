# 04 - Verification

How to verify that documentation and skills are in sync with compiled code.

---

## Verification Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Code Compiles                                      │
│ dotnet build docs/samples/{Project}.Samples.DomainModel/    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Tests Pass                                         │
│ dotnet test docs/samples/{Project}.Samples.DomainModel.Tests│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Documentation In Sync                              │
│ .\scripts\extract-snippets.ps1 -Verify                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Skill In Sync (Manual)                             │
│ Compare skill sync table to current version                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Code Compiles

**What it verifies:** Syntax is correct, APIs exist, types resolve

```powershell
# Run from project root
dotnet build docs/samples/{Project}.Samples.DomainModel/
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
# Run from project root
dotnet test docs/samples/{Project}.Samples.DomainModel.Tests/
```

**Common failures:**
- Behavior changed in main project
- Sample code doesn't demonstrate correct usage
- Missing setup in test

**Fix:** Update sample code and/or tests to reflect current behavior

---

## Layer 3: Documentation In Sync

**What it verifies:** Markdown files contain current compiled code

```powershell
# Run from project root
.\scripts\extract-snippets.ps1 -Verify
```

**Output when in sync:**
```
Verification complete. 56 snippets verified, 6 orphan snippets.
```

**Output when out of sync:**
```
Documentation out of sync with samples:
  - validation-and-rules.md: age-validation-rule
  - collections.md: list-cascade-delete

Run '.\scripts\extract-snippets.ps1 -Update' to sync documentation.
```

**Fix:**
```powershell
.\scripts\extract-snippets.ps1 -Update
git add docs/
git commit -m "docs: sync snippets from samples"
```

---

## Layer 4: Skill In Sync

**What it verifies:** Claude skill reflects current documentation

This is currently a **manual check**:

### Step 1: Check Sync Table

Read the skill's sync tracking table:
```markdown
## Skill Sync Status

| Repository | Last Synced Commit | Date |
|------------|-------------------|------|
| Neatoo | v10.5.0 | 2025-12-15 |
```

### Step 2: Compare to Current Version

```bash
# In project repo
git describe --tags --abbrev=0
# Output: v10.6.0

# Or check Directory.Build.props
```

### Step 3: Review Changes Since Last Sync

```bash
git log --oneline v10.5.0..v10.6.0
```

Look for:
- API changes
- New features
- Breaking changes
- Documentation updates

### Step 4: Update Skill If Needed

If changes affect skill content:
1. Update relevant skill files
2. Update sync tracking table
3. Commit skill changes

---

## Full Verification Sequence

Run all layers in order:

```powershell
# 1. Build samples
dotnet build docs/samples/{Project}.Samples.DomainModel/
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }

# 2. Run tests
dotnet test docs/samples/{Project}.Samples.DomainModel.Tests/
if ($LASTEXITCODE -ne 0) { Write-Error "Tests failed"; exit 1 }

# 3. Verify documentation
.\scripts\extract-snippets.ps1 -Verify
if ($LASTEXITCODE -ne 0) { Write-Error "Docs out of sync"; exit 1 }

# 4. Manual: Check skill sync table
Write-Host "Manual check: Verify skill sync table is current"
```

---

## CI Integration

Add to GitHub Actions workflow:

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

      - name: Build samples
        run: dotnet build docs/samples/{Project}.Samples.DomainModel/

      - name: Test samples
        run: dotnet test docs/samples/{Project}.Samples.DomainModel.Tests/

      - name: Verify documentation snippets
        run: pwsh -File scripts/extract-snippets.ps1 -Verify
```

**This ensures:**
- PRs can't merge with broken code examples
- Documentation stays in sync with code
- API changes require documentation updates

---

## Verification Checklist

### Before Committing Code Changes

- [ ] `dotnet build` passes on samples project
- [ ] `dotnet test` passes on samples tests
- [ ] `extract-snippets.ps1 -Verify` passes
- [ ] If breaking change: skill updated

### Before Releasing

- [ ] All above checks pass
- [ ] Release notes updated
- [ ] Version number updated
- [ ] Skill sync table updated

---

## Common Issues

### "Orphan snippets" Warning

Orphan snippets exist in samples but not in docs. This is okay:
- Code compiles (good)
- No placeholder in docs yet (intentional or todo)

### "Doc file not found" Warning

The script can't find `{doc-file}.md`. Check:
- Filename matches region marker
- File is in `docs/` directory

### Verification Passes But Docs Look Wrong

The script only checks snippets with markers. Unmigrated code blocks are not verified:

```markdown
<!-- This IS verified -->
<!-- snippet: docs:example:code -->
```csharp
...
```
<!-- /snippet -->

<!-- This is NOT verified (no marker) -->
```csharp
// Old, potentially stale code
```
```

**Solution:** Migrate all code blocks to use snippet markers.

---

## Verification for Multiple Projects

When working across Neatoo, RemoteFactory, and KnockOff:

```powershell
# Verify all three projects
$projects = @(
    "C:\src\neatoodotnet\Neatoo",
    "C:\src\neatoodotnet\RemoteFactory",
    "C:\src\neatoodotnet\KnockOff"
)

foreach ($project in $projects) {
    Push-Location $project
    Write-Host "`n=== Verifying $project ===" -ForegroundColor Cyan

    dotnet build docs/samples/*.Samples.DomainModel/ 2>$null
    if (Test-Path "scripts/extract-snippets.ps1") {
        .\scripts\extract-snippets.ps1 -Verify
    }

    Pop-Location
}
```

---

## Fixing Out-of-Sync Documentation

When verification fails:

### Option 1: Update Samples (Code Changed Correctly)

If the main project API changed and samples are outdated:

1. Update sample code to use new API
2. Update tests
3. Run `-Update` to sync docs
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
4. Run `-Update`
5. Update skill if needed
6. Commit everything together

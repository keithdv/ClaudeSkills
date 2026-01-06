# 05 - Ready to Commit Checklist

What to verify before committing changes to Neatoo, RemoteFactory, or KnockOff.

---

## When User Asks "Are We Ready to Commit?"

Run through this checklist before confirming readiness.

---

## The Checklist

### 1. Code Quality

```
[ ] All changes compile without errors
[ ] No new compiler warnings introduced
[ ] Unit tests pass
```

**How to verify:**
```powershell
dotnet build
dotnet test
```

---

### 2. Documentation Samples Sync

```
[ ] Samples project builds
[ ] Samples tests pass
[ ] Documentation is in sync with samples
```

**How to verify:**
```powershell
# Build samples
dotnet build docs/samples/{Project}.Samples.DomainModel/

# Test samples
dotnet test docs/samples/{Project}.Samples.DomainModel.Tests/

# Verify docs in sync
.\scripts\extract-snippets.ps1 -Verify
```

**If out of sync:**
```powershell
.\scripts\extract-snippets.ps1 -Update
git add docs/
```

---

### 3. Skill Sync (For Breaking Changes or New Features)

```
[ ] Skill reflects current API
[ ] Code examples in skill are correct
[ ] Sync tracking table is current
```

**How to verify:**
1. Check skill sync table date vs current version
2. If significant changes, review affected skill files
3. Compare skill code examples against documentation

**Skill locations:**
- Neatoo: `~/.claude/skills/neatoo/`
- KnockOff: `~/.claude/skills/knockoff/`
- RemoteFactory: (part of Neatoo skill)

---

### 4. Release Notes (For Releases Only)

```
[ ] CHANGELOG.md has entry for this version
[ ] Breaking changes clearly marked
[ ] New features documented
```

**CHANGELOG.md format:**
```markdown
## [10.6.0] - 2026-01-05

### Added
- CancellationToken support in factory operations

### Changed
- RemoteFactory upgraded to 10.5.0

### Breaking
- Save() now returns new instance, must reassign

### Fixed
- Serialization issue with nested aggregates
```

---

### 5. Version Number (For Releases Only)

```
[ ] Version in Directory.Build.props is correct
[ ] Version follows semver based on changes:
    - MAJOR: Breaking changes
    - MINOR: New features, non-breaking
    - PATCH: Bug fixes only
```

**Check version:**
```powershell
Get-Content Directory.Build.props | Select-String "Version"
```

---

## Quick Decision Tree

```
Making code changes?
├── Yes → Check items 1-2
│   └── Breaking change or new feature?
│       ├── Yes → Also check item 3 (skill)
│       └── No → Done with 1-2
└── No (docs only) → Check item 2 only

Preparing a release?
├── Yes → Check ALL items (1-5)
└── No → Skip items 4-5
```

---

## Project-Specific Paths

### Neatoo

| Item | Location |
|------|----------|
| Build | `dotnet build Neatoo.sln` |
| Test | `dotnet test` |
| Samples | `docs/samples/Neatoo.Samples.DomainModel/` |
| Samples Tests | `docs/samples/Neatoo.Samples.DomainModel.Tests/` |
| Docs | `docs/` |
| Sync Script | `scripts/extract-snippets.ps1` |
| Skill | `~/.claude/skills/neatoo/` |
| Version | `Directory.Build.props` |
| Changelog | `docs/release-notes/` |

### KnockOff

| Item | Location |
|------|----------|
| Build | `dotnet build KnockOff.sln` |
| Test | `dotnet test` |
| Samples | `docs/samples/KnockOff.Samples.DomainModel/` |
| Samples Tests | `docs/samples/KnockOff.Samples.DomainModel.Tests/` |
| Docs | `docs/` |
| Sync Script | `scripts/extract-snippets.ps1` |
| Skill | `~/.claude/skills/knockoff/` |
| Version | `Directory.Build.props` |
| Changelog | `docs/release-notes/` |

### RemoteFactory

| Item | Location |
|------|----------|
| Build | `dotnet build RemoteFactory.sln` |
| Test | `dotnet test` |
| Samples | `docs/samples/RemoteFactory.Samples.DomainModel/` |
| Samples Tests | `docs/samples/RemoteFactory.Samples.DomainModel.Tests/` |
| Docs | `docs/` |
| Skill | (part of Neatoo skill) |
| Version | `Directory.Build.props` |
| Changelog | `docs/release-notes/` |

---

## Example Responses

### "Yes, Ready to Commit"

> All checks pass:
> - ✅ Build and tests pass
> - ✅ Documentation samples verified (56 snippets in sync)
> - ✅ Skill sync table current (v10.6.0)
>
> Ready to commit. Suggested commit message:
> ```
> feat: add CancellationToken support to factory operations
> ```

### "Not Ready - Issues Found"

> Found issues:
> - ❌ Documentation out of sync:
>   - `validation-and-rules.md`: `age-validation-rule`
>   - `factory-operations.md`: `save-pattern`
>
> Run `.\scripts\extract-snippets.ps1 -Update` to sync, then commit.

### "Not Ready - Skill Needs Update"

> Found issues:
> - ⚠️ Skill sync table shows v10.5.0, current version is v10.6.0
> - Breaking change detected: Save() reassignment pattern
>
> Skill files that may need updates:
> - `~/.claude/skills/neatoo/factories.md` - Save patterns
> - `~/.claude/skills/neatoo/SKILL.md` - Quick reference
>
> Review these files and update skill sync table after confirming.

---

## Full Verification Script

For comprehensive verification:

```powershell
param(
    [string]$ProjectRoot = ".",
    [switch]$IncludeSkill
)

Write-Host "=== Pre-Commit Verification ===" -ForegroundColor Cyan
Push-Location $ProjectRoot

# 1. Build
Write-Host "`n[1/4] Building..." -ForegroundColor Yellow
dotnet build --nologo -v q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build passed" -ForegroundColor Green

# 2. Test
Write-Host "`n[2/4] Testing..." -ForegroundColor Yellow
dotnet test --nologo -v q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Tests passed" -ForegroundColor Green

# 3. Documentation sync
Write-Host "`n[3/4] Verifying documentation..." -ForegroundColor Yellow
if (Test-Path "scripts/extract-snippets.ps1") {
    .\scripts\extract-snippets.ps1 -Verify
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Documentation out of sync" -ForegroundColor Red
        Write-Host "Run: .\scripts\extract-snippets.ps1 -Update" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Documentation in sync" -ForegroundColor Green
} else {
    Write-Host "⚠️ No extract-snippets.ps1 found" -ForegroundColor Yellow
}

# 4. Skill check (manual reminder)
if ($IncludeSkill) {
    Write-Host "`n[4/4] Skill sync..." -ForegroundColor Yellow
    Write-Host "⚠️ Manual check required:" -ForegroundColor Yellow
    Write-Host "   - Review skill sync table in SKILL.md"
    Write-Host "   - Compare to current version"
    Write-Host "   - Update skill if breaking changes"
}

Write-Host "`n=== Verification Complete ===" -ForegroundColor Cyan
Pop-Location
```

---

## After Committing

Don't forget to:
- Push to remote (if ready for PR)
- Tag release (if releasing): `git tag v10.6.0 && git push origin v10.6.0`
- Update GitHub release notes (auto-generated from commits)

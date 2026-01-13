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

### 2. Documentation AND Skills Sync

```
[ ] Samples project builds
[ ] Samples tests pass
[ ] MarkdownSnippets runs without error
[ ] No uncommitted doc/skill changes after sync
[ ] All code blocks have markers (pseudo/invalid verified)
```

**How to verify:**
```powershell
# Build samples
dotnet build docs/samples/

# Test samples
dotnet test docs/samples/

# Sync snippets (docs AND skills)
dotnet mdsnippets

# Check if docs or skills changed
git diff --exit-code docs/ .claude/

# Verify code block coverage
pwsh scripts/verify-code-blocks.ps1
```

**If out of sync:**
```powershell
dotnet mdsnippets
git add docs/ .claude/
```

---

### 3. Copy Skills to Shared Location

```
[ ] Skills copied to ~/.claude/skills/
```

**How to copy:**
```powershell
# Copy all local skills to shared location
Copy-Item -Recurse -Force ".claude/skills/*" "$HOME/.claude/skills/"
```

**Why:** When working in the repo, Claude loads local skills (`./.claude/skills/`). When working elsewhere, Claude loads shared skills (`~/.claude/skills/`). The copy keeps shared current.

**Local skill locations (in repo):**
- Neatoo: `.claude/skills/neatoo/`
- KnockOff: `.claude/skills/knockoff/`
- RemoteFactory: (part of Neatoo skill)

---

### 4. Release Notes Needed?

```
[ ] If adding features or fixing bugs, entry added to docs/release-notes/
```

Check if this commit includes:
- New features → Add to release notes
- Bug fixes → Add to release notes
- Refactoring only → Skip
- Documentation only → Skip

**Release notes location:** `docs/release-notes/`

---

### 5. Release Notes Format (For Releases Only)

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

### 6. Version Number (For Releases Only)

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
Making any changes (code, docs, or skills)?
├── Yes → Check items 1-2 (build, test, mdsnippets)
│   └── Has local skills (.claude/skills/)?
│       ├── Yes → Also do item 3 (copy to shared)
│       └── No → Done with 1-2
│   └── Adding features or fixing bugs?
│       ├── Yes → Also do item 4 (release notes entry)
│       └── No → Skip item 4
└── No changes → Nothing to commit

Preparing a release?
├── Yes → Check ALL items (1-6)
└── No → Skip items 5-6
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
| Sync Command | `dotnet mdsnippets` |
| Coverage Script | `scripts/verify-code-blocks.ps1` |
| Config | `mdsnippets.json` |
| Local Skill | `.claude/skills/neatoo/` |
| Shared Skill | `~/.claude/skills/neatoo/` |
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
| Sync Command | `dotnet mdsnippets` |
| Coverage Script | `scripts/verify-code-blocks.ps1` |
| Config | `mdsnippets.json` |
| Local Skill | `.claude/skills/knockoff/` |
| Shared Skill | `~/.claude/skills/knockoff/` |
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
| Sync Command | `dotnet mdsnippets` |
| Coverage Script | `scripts/verify-code-blocks.ps1` |
| Config | `mdsnippets.json` |
| Local Skill | (part of Neatoo skill) |
| Shared Skill | (part of Neatoo skill) |
| Version | `Directory.Build.props` |
| Changelog | `docs/release-notes/` |

---

## Example Responses

### "Yes, Ready to Commit"

> All checks pass:
> - ✅ Build and tests pass
> - ✅ Documentation and skills in sync (56 snippets)
> - ✅ Skills copied to shared location
>
> Ready to commit. Suggested commit message:
> ```
> feat: add CancellationToken support to factory operations
> ```

### "Not Ready - Issues Found"

> Found issues:
> - ❌ Documentation or skills out of sync:
>   - `docs/validation-and-rules.md`: `age-validation-rule`
>   - `.claude/skills/neatoo/factories.md`: `save-pattern`
>
> Run `dotnet mdsnippets` to sync, then commit.

### "Not Ready - Skills Not Copied"

> Found issues:
> - ⚠️ Local skills updated but not copied to shared location
>
> Run:
> ```powershell
> Copy-Item -Recurse -Force ".claude/skills/*" "$HOME/.claude/skills/"
> ```

---

## Full Verification Script

For comprehensive verification:

```powershell
param(
    [string]$ProjectRoot = "."
)

Write-Host "=== Pre-Commit Verification ===" -ForegroundColor Cyan
Push-Location $ProjectRoot

# 1. Build
Write-Host "`n[1/5] Building..." -ForegroundColor Yellow
dotnet build --nologo -v q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build passed" -ForegroundColor Green

# 2. Test
Write-Host "`n[2/5] Testing..." -ForegroundColor Yellow
dotnet test --nologo -v q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Tests passed" -ForegroundColor Green

# 3. MarkdownSnippets sync (docs AND skills)
Write-Host "`n[3/5] Syncing documentation and skill snippets..." -ForegroundColor Yellow
dotnet mdsnippets
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ MarkdownSnippets failed" -ForegroundColor Red
    exit 1
}

# Check for uncommitted changes in docs and skills
$changes = git status --porcelain docs/ .claude/
if ($changes) {
    Write-Host "⚠️ Documentation or skills were out of sync" -ForegroundColor Yellow
    Write-Host "Run 'git add docs/ .claude/' to stage updates" -ForegroundColor Yellow
} else {
    Write-Host "✅ Documentation and skills in sync" -ForegroundColor Green
}

# 4. Code block coverage
Write-Host "`n[4/5] Verifying code block coverage..." -ForegroundColor Yellow
if (Test-Path "scripts/verify-code-blocks.ps1") {
    pwsh scripts/verify-code-blocks.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Unmarked code blocks found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️ No verify-code-blocks.ps1 found" -ForegroundColor Yellow
}

# 5. Copy skills to shared location
Write-Host "`n[5/5] Copying skills to shared location..." -ForegroundColor Yellow
if (Test-Path ".claude/skills") {
    Copy-Item -Recurse -Force ".claude/skills/*" "$HOME/.claude/skills/"
    Write-Host "✅ Skills copied to ~/.claude/skills/" -ForegroundColor Green
} else {
    Write-Host "⚠️ No local skills found (.claude/skills/)" -ForegroundColor Yellow
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

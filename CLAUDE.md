## Core Rules

- **STOP and ask** when you hit an obstacle - don't push through with workarounds
- **STOP and ask** before reverting, undoing, or changing direction
- **STOP and ask** before modifying out-of-scope tests
- **STOP and ask** before using reflection

##### Folder Structure
- `docs/` - Documentation as markdown files
- `docs/todos/` - Directory of markdown files. Track identified future work and track progress. When I say 'todo' this is what I mean. Linked to plans to implement to work.
- `docs/todos/completed` - Completed work-in-progress markdown files
- `docs/plans` - Directory of markdown files. These are designs created to complete todos.
- `docs/release-notes/` - Release Notes folder
---

#### Existing Tests Are Sacred - Never Gut Them

**Do NOT modify out-of-scope tests to complete your task.**

When working on a task, existing tests may start failing. Before modifying any test that was passing before your changes:

1. **Determine if the test is in-scope** - Does the test directly cover the feature you're implementing?
2. **If out-of-scope, STOP** - Don't modify the test to make it pass
3. **REPORT** - "Test X started failing. It tests [feature], which is outside my current task."
4. **ASK** - "Should I fix the underlying issue, add this to the bug list, or is this expected breakage?"

**What counts as "gutting" a test (NEVER do these to out-of-scope tests):**
- Removing or commenting out assertions
- Removing test cases or edge cases
- Simplifying setup that was exercising real scenarios
- Changing expected values to match broken behavior
- Commenting out the entire test
- Deleting the test

**The rule:** When modifying existing tests, the **original intent must be preserved**. If you can't preserve the intent while completing your task, STOP and ask.

**Why this matters:** Tests exist to catch bugs. Modifying tests to hide failures means bugs ship and resurface later.

**Bad example:** Implementing flat API → `IEnumerator<T>` tests fail → comment out `IEnumerator<T>` tests → mark task complete. *Bug is hidden, not fixed.*

**Good example:** Implementing flat API → `IEnumerator<T>` tests fail → STOP and say: "IEnumerator<T> tests are failing due to duplicate interceptor generation. This appears to be a separate bug. Should I (1) fix it now, (2) add to bug list and continue, or (3) investigate further?"

---

#### No Reflection Without Approval

**Do NOT use reflection in code without reviewing and getting approval first.**

The goal is to have no reflection, even in tests.

Before writing any code that uses `System.Reflection`, `Type.GetMethod()`, `MethodInfo.Invoke()`, or similar:
1. **STOP** - Consider if there's a non-reflection alternative
2. **REPORT** - Explain why reflection seems necessary
3. **ASK** - Get approval before proceeding

---

#### DDD Documentation Guidelines

For all neatoodotnet/**/* repositories:

- **Use DDD terminology freely.** Terms like aggregate root, entity, value object, domain event, repository, bounded context, etc. are Neatoo's vocabulary. Use them in comments and documentation.
- **Do not explain or define DDD concepts.** Assume the reader is a DDD expert. Never include tutorial-style explanations of what DDD patterns mean.
- **Focus on what the specific code does**, not what DDD pattern it implements.
- Emphasize Neatoo-specific patterns: RemoteFactory, source generation, validation rules, and client-server state transfer.

##### Examples

| Context | Good | Bad |
|---------|------|-----|
| Class comment | `/// Repository for Employee aggregates.` | `/// Repositories abstract persistence for aggregates. Aggregates are consistency boundaries that...` |
| Class comment | `/// Employee aggregate root.` | `/// An aggregate root is the entry point to an aggregate. This class represents...` |
| Class comment | `/// Value object for phone numbers.` | `/// Value objects are immutable and compared by structural equality. This represents...` |
| Inline comment | `// Owned: BusinessId` | `// Value objects should be configured as owned types in EF Core because...` |
| Documentation | "The Employee aggregate validates BR-EMP-001" | "Aggregates maintain invariants. An invariant is a business rule that must always be true..."

---

##### Release Notes

Release notes live in `docs/release-notes/` with individual version files.

**Structure:**
```
docs/release-notes/
├── index.md          # Version index
├── v10.6.0.md
└── v10.5.0.md
```

**Version file template:**

```markdown
# {Project} {Version}

**Release Date:** YYYY-MM-DD
**Breaking Changes:** Yes | No

---

## Summary

[1-2 sentence overview]

---

## What's New

### [Feature Name]

[Description with code example]

---

## Migration Guide

[Required if breaking changes - show Before/After code]

---

## Related

- [Completed Todo](../todos/completed/feature-name.md)
```

**Version naming:**
- Breaking changes → Major (10.x → 11.0)
- New features → Minor (10.1 → 10.2)
- Bug fixes → Patch (10.1.0 → 10.1.1)

---

#### CI/CD Standards (.NET Libraries)

##### Workflow Structure
- Single workflow file: `.github/workflows/build.yml`
- Name: "Build, Test & Publish"
- Triggers:
  - `push` to main branch (build/test only)
  - `push` of `v*` tags (build/test/publish)
  - `pull_request` to main (build/test only)
  - `workflow_dispatch` with inputs:
    - `publish_nuget` (boolean) - manual publish trigger
    - `nuget_version_suffix` (string) - e.g., "beta1", "rc1"

##### Versioning
- Version stored in `Directory.Build.props` (`<Version>` or `<PackageVersion>`)
- Manual version bumps (no MinVer/GitVersion)
- Multi-targeting: `net8.0;net9.0;net10.0`
- Prerelease versions via suffix input (e.g., `10.2.0-beta1`)

##### Build Job
```yaml
env:
  DOTNET_SKIP_FIRST_TIME_EXPERIENCE: true
  DOTNET_CLI_TELEMETRY_OPTOUT: true
  DOTNET_NOLOGO: true
```
- Checkout with `fetch-depth: 0` (full history)
- NuGet package caching via `actions/cache@v4`
- Build with `-p:ContinuousIntegrationBuild=true`
- Test with trx logging, upload results as artifacts
- Pack and upload .nupkg as artifacts

##### Publish Job
- Condition: tag push (`v*`) OR manual with `publish_nuget=true`
- Environment: `nuget` (for secrets)
- Push to NuGet.org with `--skip-duplicate`
- Create GitHub Release via `softprops/action-gh-release@v2`:
  - `generate_release_notes: true` (auto-generated from commits)
  - `prerelease: ${{ contains(github.ref, '-') }}`
  - Attach .nupkg files

##### Release Process
1. Update version in `Directory.Build.props`
2. Commit: `chore: bump version to X.Y.Z`
3. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
4. Workflow auto-publishes to NuGet and creates GitHub Release

##### Project Standards
- `TreatWarningsAsErrors`: true
- `ManagePackageVersionsCentrally`: true (Directory.Packages.props)
- `NuGetAudit`: true (security scanning)
- `LangVersion`: preview

---

#### Source-Generated Files

**Include source-generated files in git** so changes can be tracked and compared.

- Output generated files to a `Generated/` folder within each project
- Do NOT gitignore these files—commit them to the repository
- This allows reviewing generator output changes in diffs and PRs
- If file paths become too long (Windows path limit issues), ask for guidance
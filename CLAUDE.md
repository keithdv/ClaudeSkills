## Core Rules

- **STOP and ask** when you hit an obstacle - don't push through with workarounds
- **STOP and ask** before reverting, undoing, or changing direction
- **STOP and ask** before modifying out-of-scope tests
- **STOP and ask** before using reflection
- **Never commit** unless explicitly asked
- **Broken code is OK** - leave it broken and review with me before fixing
- **MARKDOWN FILES** always load the docs-snippet skill when working with any markdown files

##### Folder Structure
- `docs/` - Documentation as markdown files
- `docs/todos/` - Plans and work-in-progress as markdown files
- `docs/todos/completed` - Completed work-in-progress markdown files
- `docs/realies-notes` - Release Notes folder
---

#### When You Hit an Obstacle - STOP

**Do NOT work around obstacles with solutions that defeat the original purpose.**

When something doesn't work as expected (code isn't testable, API doesn't exist, pattern doesn't fit):
1. **STOP** - Don't push through with a creative workaround
2. **REPORT** - Explain what the obstacle is and why it blocks progress
3. **ASK** - Let me decide how to proceed

**Bad example:** Asked to test production code → code isn't testable → recreate code in test project → test the copy. *This completely defeats the purpose of testing.*

**Good example:** Asked to test production code → code isn't testable → STOP and say: "This code can't be tested as-is because [specific reason]. Options: (1) refactor production code for testability, (2) integration test instead, (3) skip this test. Which approach?"

**The goal is collaboration, not completion at any cost.**

---

#### DO NOT REVERT OR REVERSE COURSE WITHOUT STOPPING TO REVIEW!!!!!

**Never undo work, reverse direction, or roll back changes without explicit approval.**

This applies to ALL reversals:
- Git operations (`git checkout`, `git revert`, `git reset`)
- Re-editing files to remove changes you just made
- Deleting code you just wrote
- Changing approach mid-task
- "Fixing" something by undoing it

When something isn't working or you think you need to change direction:
1. **STOP** - Do not start undoing anything
2. **REPORT** - Explain what's broken and what you're considering
3. **ASK** - "Should I revert X, try Y, or take a different approach?"

**Why this matters:** The user may prefer to leave code broken temporarily while fixing the root cause elsewhere. Undoing work without asking destroys progress and wastes time.

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

#### Git Commits - Only When Asked

**Do NOT commit or push unless explicitly requested.**

- Each "commit and push" request is a **one-time action**, not a mode change
- After committing, return to normal behavior: make changes, let me review
- Never auto-commit subsequent changes just because I asked for a commit earlier
- Always give me a chance to review changes before they're committed

---

#### No Reflection Without Approval

**Do NOT use reflection in code without reviewing and getting approval first.**

The goal is to have no reflection, even in tests.

Before writing any code that uses `System.Reflection`, `Type.GetMethod()`, `MethodInfo.Invoke()`, or similar:
1. **STOP** - Consider if there's a non-reflection alternative
2. **REPORT** - Explain why reflection seems necessary
3. **ASK** - Get approval before proceeding

---

#### Documentation Code Examples

When working with `docs/` or Claude skills that contain code examples:

1. **Always run `/docs-snippets`** to load the documentation sync skill


#### DDD Documentation Guidelines

For all Neatoo repositories:

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

#### Project Conventions


##### Todo Files
Todo files in `docs/todos/` must:
- Include a **task list** with checkboxes (`- [ ]` / `- [x]`)
- Be **updated as work progresses** to reflect completed items
- Contain enough context to **resume work without prior conversation history**

The goal is continuity: any todo file should allow picking up exactly where we left off in a new session.

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
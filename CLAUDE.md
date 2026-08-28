---

## Core Rules

- **STOP and ask** when you hit an obstacle - don't push through with workarounds
- **STOP and ask** before reverting, undoing, or changing direction
- **STOP and ask** before modifying out-of-scope tests
- **STOP and ask** before using reflection
- **STOP and ask** when a required agent (e.g., `crm-architect`) is not available as a Task subagent — do NOT substitute a general-purpose agent or work around it
- **NEVER take over for an agent.** If an agent appears stuck, slow, or unresponsive — STOP and ask for direction. Do NOT kill the agent and do the work yourself. Do NOT read source files "to take over." The orchestrator never modifies source code. Always wait for the user, even if they are away.

---

## ALWAYS Capture Build and Test Output to a File

**Builds and tests produce large output that gets truncated when piped through `tail`, `grep`, or the harness's task-output buffer.** Re-running a build or test because you couldn't find the failure in truncated output is the single most expensive mistake you can make — it wastes minutes per cycle and trains the user to distrust you.

**The rule:**

```bash
dotnet build > /tmp/build.log 2>&1
dotnet test --no-build > /tmp/test.log 2>&1
```

Then `grep` the file for what you need:

- Build errors: `grep -E "error CS|Build FAILED|Build succeeded|Error\(s\)" /tmp/build.log`
- Test failures: `grep -E "\[FAIL\]|Failed " /tmp/test.log`
- Failed test names with full message: `grep -B 1 -A 10 "\[FAIL\]" /tmp/test.log`
- Summary footer: `tail -3 /tmp/test.log`

**Why this matters:**

- The harness's `task-output` file truncates to ~30 KB. A test run with hundreds of passing tests pushes the failure detail (which appears earlier) past the truncation point. By the time you `tail -N` the file, only the trailing stack trace and the summary footer remain.
- Once the output is gone, the next instinct is to re-run the command. **Don't.** The output you need is still in the log file you redirected to — go grep it again with different patterns.
- Test runs are slow (minutes per cycle). Re-running because of a tooling-truncation problem is pure waste.

**This applies to:**

- `dotnet build` — always `> /tmp/build.log 2>&1`
- `dotnet test` — always `> /tmp/test.log 2>&1`
- `mvn`, `gradle`, `npm test`, any other build/test command with verbose output

Use unique filenames per invocation if you'll need to compare runs (`/tmp/test-before.log`, `/tmp/test-after.log`).

**If a test/build is running in the background:** the harness writes its full output to a task-output file (whose path it tells you). That file *also* gets truncated to ~30 KB. Treat it the same as direct stdout — if the failure detail is past the truncation point, redirect to your own file on the next run; do NOT re-run just because the task-output was short.

---

#### A Windowed Read Proves Presence, Never Absence

**`head`, `tail`, `sed -n '1,120p'`, `grep -A 20` and friends answer "is this here?" — they cannot answer "is this all of it?" or "does this file say anything about X?"** The window you chose is not evidence about what lies outside it, and once the output is on screen a partial read looks exactly like a complete one.

**The rule:** before writing *entire*, *only*, *never*, *both*, *no way to*, or any other closed-world claim — read the whole file, or grep for the specific thing being denied.

**What it looks like when it goes wrong.** Two from one session, hours apart:

- `grep -A 40 "enum LaserFault"` stopped before the last two members. Reported as "the **entire** fault vocabulary is three values." It was five, and the two that fell outside the window were the two the reader needed.
- `sed -n '1,70p'` of a 210-line README. Reported as that component's architecture. The section refuting it sat 85 lines further down, under a heading named for the exact question being answered.

Both were stated confidently, both were wrong the same way, and in both cases the text outside the window *was* the correction.

**Presence claims are fine from a window** — "the service logs `Laser State:`" needs one matching line and nothing more. It is absence and completeness claims, the ones that sound most authoritative, that a window can never support.

---

#### NuGet Package Lookups

- **ONLY use the listed/registration endpoints on `nuget.org`** (e.g., `https://api.nuget.org/v3/registration5-gz-semver2/...` or the package page at `https://www.nuget.org/packages/<id>`).
- **DO NOT use `flatcontainer`** (`https://api.nuget.org/v3-flatcontainer/...`) for version lookups or anything else.
- If a dependency is a **NuGet package, get versions from NuGet only**. Do NOT infer versions from local builds, local `bin/` output, sibling repository clones, or `Directory.Packages.props` in another repo.
- Local source checkouts of a NuGet-published library are NOT a source of truth for "latest version" — always query NuGet.

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

#### Never Work Around Production Bugs in Tests

**Tests must expose bugs, not hide them.**

When you discover a bug in the production code (generator, library, etc.) while writing tests:

1. **Write the test the natural way** - Use the API as a user would. If the natural usage triggers a bug, that's the test doing its job.
2. **Do NOT rewrite the test to avoid the broken code path** - If `Return("value").ThenReturn("value")` is the natural API but it throws, the test should demonstrate that failure.
3. **REPORT** - "This test exposes a bug in [component]: [description]."
4. **ASK** - "Should I (1) mark it as a known-bug regression test, (2) fix the bug now, or (3) file a todo?"

**What counts as "working around" (NEVER do this):**
- Using a different API overload because the natural one is broken
- Adding extra setup steps that users wouldn't need if the bug were fixed
- Avoiding a feature combination because it has a known issue
- Using callback form when value form is the natural choice, just because value form has a bug

**Why this matters:** Working around bugs in tests means the bug has zero test coverage. When someone later tries to fix the bug, there's no failing test to verify the fix. The bug stays invisible.

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

> **Scope: neatoodotnet repos only.** Skip for application repositories.

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

**Template:** Include release date, breaking changes flag, summary, what's new, migration guide (if breaking), and link to completed todo.

**Version naming:**
- Breaking changes → Major (10.x → 11.0)
- New features → Minor (10.1 → 10.2)
- Bug fixes → Patch (10.1.0 → 10.1.1)

---

#### CI/CD Standards (.NET Libraries)

> **Scope: neatoodotnet library repos only.** Not applicable to application repositories like zTreatment.

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

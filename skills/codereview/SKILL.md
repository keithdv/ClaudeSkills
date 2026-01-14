---
name: codereview
description: Comprehensive code review checklist for verifying changes before commit. Run after completing a task to catch issues before they're committed.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*, pwsh:*, dotnet:*)
---

# Code Review Skill

Perform a comprehensive code review of recent changes. This is a systematic second look as a professional senior software engineer before committing.

## Review Process

Work through each section in order. Report findings for each section before moving to the next. **STOP and discuss any issues found** - do not auto-fix.

---

## 1. Code Quality Review

Review all changed files (`git diff --name-only` and `git diff`):

- [ ] **Style consistency** - Does new code match the style of surrounding code?
- [ ] **Variable/method names** - Are they clear and understandable?
- [ ] **Comments** - Are complex sections explained? Are there confusing parts without comments?
- [ ] **Refactoring opportunities** - Now that it's complete, any obvious improvements?
- [ ] **Over-engineering** - Did we add unnecessary abstraction, features, or complexity?

```bash
git diff --cached --name-only  # Staged files
git diff --name-only           # Unstaged changes
git diff                       # Full diff
```

---

## 2. Todo/Plan Verification

If a todo file was being implemented:

- [ ] **Completeness** - Was the todo fully implemented or were there obstacles?
- [ ] **Plan adherence** - If the plan changed during implementation, WHY?
- [ ] **Plan drift** - Did we change the plan just to "complete" it? That's a red flag.
- [ ] **Obstacle handling** - Were obstacles properly reported, or worked around?

**Critical:** We've made the mistake of changing plans mid-implementation to declare victory. If the plan changed, that needs explicit review.

---

## 3. Test Coverage

### New Code Must Have Tests

- [ ] **Unit tests** - All new production features/functionality have unit tests
- [ ] **Integration tests** - If an integration test approach exists, were integration tests added?

### Test Regression Check (CRITICAL)

Review ANY existing tests that were modified:

```bash
git diff --name-only | grep -E "\.Tests?\."
git diff -- "*Tests*" "*Test*"
```

For each modified test file, check for:

- [ ] **Removed assertions** - Were asserts removed to stop failures?
- [ ] **Deleted tests** - Were test methods removed entirely?
- [ ] **Weakened tests** - Were expected values changed to match broken behavior?
- [ ] **Commented code** - Were test sections commented out?

**If any test was "gutted" to pass, STOP.** This is a serious issue that has caused bugs before. Report the specific test and what was removed.

---

## 4. Documentation Check

If any markdown files were modified:

### 4.1 Skill & Sync Verification

- [ ] **docs-snippets skill loaded?** - Was `/docs-snippets` run before making changes?
- [ ] **Sync executed?** - Was `dotnet mdsnippets` run after all changes?
- [ ] **Verification script?** - Was `pwsh scripts/verify-code-blocks.ps1` run?

### 4.2 C# Code Block Review (CRITICAL)

For EVERY `csharp` or `cs` code block added or modified in markdown:

```bash
# Find all changed markdown files
git diff --name-only | grep -E "\.md$"

# Show the diff for markdown files
git diff -- "*.md"
```

Review each code block and check:

- [ ] **Has a marker?** - Every C# block must have `snippet:`, `pseudo:`, `invalid:`, or `generated:`
- [ ] **Correct marker type?** Use the decision flowchart:
  ```
  Is code intentionally broken/wrong?     → <!-- invalid:{id} -->
  Is it source-generated output?          → <!-- generated:{path}#L{start}-L{end} -->
  Is it compilable C# (complete code)?    → snippet: {id}
  Is it just API signature/fragment?      → <!-- pseudo:{description} -->
  ```

**Common mistakes to catch:**

| Check | Issue | Fix |
|-------|-------|-----|
| **Compiled code marked pseudo?** | Code that WOULD compile is marked `<!-- pseudo: -->` | Change to `snippet:`, add to samples |
| **Missing snippet in samples?** | `snippet: xyz` but no `#region xyz` in samples | Add region to samples project |
| **Snippet accidentally deleted?** | A `#region` was removed from samples | Restore or update docs to match |
| **Moq/library code as pseudo?** | Other library examples marked as pseudo | Add package ref to samples, use `snippet:` |
| **Complete statements as pseudo?** | Full C# statements marked pseudo because "types don't exist" | Create placeholder types in samples |
| **Commented code in snippet?** | `// db.SaveChangesAsync();` in compiled snippet | Remove comments or use `pseudo:` |

### 4.3 Samples Project Check

If new code examples were added to documentation:

- [ ] **Samples created?** - Were corresponding `#region` blocks added to `docs/samples/`?
- [ ] **Samples compile?** - Does `dotnet build` pass on the samples project?
- [ ] **Samples tested?** - If the snippet shows behavior, is there a test verifying it?

```bash
# Check for new regions in samples
git diff -- "*/docs/samples/*" | grep -E "^[+-]\s*#region"

# Verify samples build
dotnet build docs/samples/
```

### 4.4 Snippet Drift Check

For existing documentation:

- [ ] **Deleted snippets?** - Were any `#region` blocks removed from samples that docs still reference?
- [ ] **Changed snippets?** - Did snippet content change in ways that break documentation context?

```bash
# Find all snippet references in changed docs
grep -h "snippet:" $(git diff --name-only -- "*.md") 2>/dev/null | sort -u

# Check if those regions exist in samples
# For each snippet ID, verify it exists in samples
```

### 4.5 Documentation Updates Needed?

Check for docs that SHOULD be updated:

- [ ] **README.md** - If public API or usage changed, does README need updates?
- [ ] **docs/ folder** - Do any docs need updates based on changes?
- [ ] **Skills** - Do local skills (`.claude/skills/`) need updates?

---

## 5. Skill Sync Check

If the project has a local skill (`.claude/skills/{project}/`):

- [ ] **Local skill updated?** - Does the local skill reflect current changes?
- [ ] **Shared skill sync** - Does `~/.claude/skills/{project}/` need to be updated from local?

Check for matching skills:
```bash
ls -la .claude/skills/ 2>/dev/null
ls -la ~/.claude/skills/ 2>/dev/null
```

---

## 6. Version & Release Notes

If production code was modified:

- [ ] **Version bump** - Was the version number updated in `Directory.Build.props`?
- [ ] **Release notes** - Was a release note created in `docs/release-notes/`?

Check version file:
```bash
cat Directory.Build.props 2>/dev/null | grep -E "<Version>|<PackageVersion>"
```

### Critical: Verify Changes Are Actually Uncommitted

When you find production code in `git diff`, **do not assume** they're "from a previous session." Verify:

```bash
# Check if the file changes are already committed
git log --oneline -1 -- src/path/to/file.cs

# Compare: does the latest commit match what's in the diff?
# If git diff shows changes but git log shows an old commit,
# those changes are UNCOMMITTED and need release notes.
```

**Common mistake:** Seeing production files in `git diff`, assuming "those were committed earlier," then running `git add -A` which includes them in your commit WITHOUT release notes.

**Rule:** If production code appears in `git diff --name-only`, it needs release notes - verify it's not just sitting uncommitted from previous work.

---

## Summary Report

After completing all sections, provide a summary:

```
## Code Review Summary

### Findings
- [List any issues found]

### Blockers (must fix before commit)
- [Critical issues]

### Recommendations (optional improvements)
- [Nice-to-haves]

### Ready to Commit?
[YES/NO with explanation]
```

---

## Remember

- **Report issues, don't auto-fix** - Let the user decide how to proceed
- **Test regression is critical** - We've been burned by gutted tests before
- **Plan changes need review** - Changing the plan to complete it is a red flag

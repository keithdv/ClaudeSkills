# 07 - Release Notes

How to create and maintain release notes in `docs/release-notes/`.

---

## Directory Structure

```
docs/release-notes/
├── index.md          # Version index with highlights table
├── v10.6.0.md        # Individual version notes
├── v10.5.0.md
├── v10.4.0.md
└── ...
```

---

## Index File (index.md)

The index provides a quick overview of all releases:

```markdown
# Release Notes

## Current Version

**Neatoo 10.6.0** (2026-01-05)

---

## Highlights

| Version | Date | Type | Summary |
|---------|------|------|---------|
| [10.6.0](v10.6.0.md) | 2026-01-05 | Feature | CancellationToken support |
| [10.5.0](v10.5.0.md) | 2026-01-04 | Feature | Ordinal serialization |
| [10.4.0](v10.4.0.md) | 2026-01-03 | Breaking | Simplified inheritance |

---

## Version Naming

| Change Type | Version Bump |
|-------------|--------------|
| Breaking changes | Major (10.x → 11.0) |
| New features | Minor (10.1 → 10.2) |
| Bug fixes | Patch (10.1.0 → 10.1.1) |
```

---

## Individual Version File (v10.6.0.md)

Each version gets its own file with this structure:

```markdown
# {Project} {Version}

**Release Date:** YYYY-MM-DD
**Type:** Feature Release | Bug Fix | Breaking Change
**Breaking Changes:** Yes | No

---

## Summary

[1-2 sentence overview of what this release does]

---

## What's New

### [Feature Name]

[Description with code example if applicable]

```csharp
// Example usage
```

---

## Migration Guide

[Required if breaking changes exist]

### [Change Description]

**Before:**
```csharp
// Old code
```

**After:**
```csharp
// New code
```

---

## Dependency Updates

| Package | Previous | New |
|---------|----------|-----|
| SomePackage | 1.0.0 | 2.0.0 |

---

## Related

- [Completed Todo](../todos/completed/feature-name.md)
- [Documentation](../feature.md)
```

---

## Release Note Sections

### Required Sections

| Section | When to Include |
|---------|-----------------|
| Summary | Always |
| What's New | Features and changes |
| Migration Guide | Breaking changes |
| API Changes | Interface/signature changes |

### Optional Sections

| Section | When to Include |
|---------|-----------------|
| Dependency Updates | Package version changes |
| Test Results | After major changes |
| Related Documentation | Links to updated docs |
| Completed Todos | Complex features with plans |

---

## Linking to Completed Todos

When a release includes work tracked in a todo, reference it:

```markdown
## What's New

### Documentation Samples Infrastructure

Code examples in documentation are now compiled and tested. This ensures all
examples work with the current API.

**Related:** [todos/completed/documentation-samples-project.md](../todos/completed/documentation-samples-project.md)
```

This provides:
- Traceability from release to the planning/implementation work
- Context for why changes were made
- Detailed implementation notes beyond what's in release notes

---

## Version Types

### Feature Release (Minor)

```markdown
**Type:** Feature Release
**Breaking Changes:** No
```

Includes:
- New features
- Enhancements to existing features
- Non-breaking API additions

### Bug Fix Release (Patch)

```markdown
**Type:** Bug Fix
**Breaking Changes:** No
```

Includes:
- Bug fixes only
- No new features
- No API changes

### Breaking Change Release (Major or Minor with Breaking)

```markdown
**Type:** Feature Release
**Breaking Changes:** Yes (for X implementations)
```

Must include:
- Migration Guide section
- Clear before/after code examples
- Explanation of why the break was necessary

---

## Workflow: Creating Release Notes

### 1. Before Releasing

Check completed todos since last release:
```bash
git log --oneline {last-tag}..HEAD -- docs/todos/completed/
```

### 2. Create Version File

```bash
# Create new release notes file
touch docs/release-notes/v10.7.0.md
```

### 3. Fill In Sections

1. Write Summary
2. Document What's New
3. Add Migration Guide if breaking
4. Link to completed todos
5. List dependency updates

### 4. Update Index

Add new version to:
- "Current Version" at top
- Highlights table
- All Releases table

### 5. Update Version Number

```bash
# Update Directory.Build.props
# Then commit and tag
git tag v10.7.0
git push origin v10.7.0
```

---

## Code Examples in Release Notes

Release notes often include code examples. These should:

1. **Come from samples projects** when possible (use `#region` markers)
2. **Be minimal** - just enough to show the change
3. **Show before/after** for migrations

If the example is release-note specific and not reusable in docs:
```markdown
```csharp
// This example is specific to the migration and not extracted from samples
var oldWay = DoThingOldWay();

// New approach
var newWay = DoThingNewWay();
```
```

---

## GitHub Integration

Release notes in `docs/release-notes/` complement GitHub releases:

| Content | docs/release-notes/ | GitHub Release |
|---------|---------------------|----------------|
| Detailed migration guide | ✓ | Link to docs |
| Code examples | ✓ | Brief summary |
| Completed todo links | ✓ | - |
| Auto-generated from commits | - | ✓ |
| NuGet package attached | - | ✓ |

**GitHub release body:**
```markdown
## Neatoo 10.6.0

CancellationToken support for factory methods.

**Full release notes:** [docs/release-notes/v10.6.0.md](link)

### Changelog
(auto-generated from commits)
```

---

## Integration with Ready-to-Commit

When releasing, verify:

- [ ] Version file created: `docs/release-notes/v{version}.md`
- [ ] Index updated with new version
- [ ] Completed todos referenced where applicable
- [ ] Migration guide included (if breaking)
- [ ] Version in `Directory.Build.props` matches

See [05-ready-to-commit.md](05-ready-to-commit.md) for full checklist.

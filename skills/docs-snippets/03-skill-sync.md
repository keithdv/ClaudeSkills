# 03 - Skill Sync

How to keep Claude skills in sync with documentation and source code.

---

## Skill vs Documentation

| Aspect | Documentation | Claude Skill |
|--------|---------------|--------------|
| Audience | Developers reading docs | Claude assisting with code |
| Detail level | Comprehensive tutorials | Condensed quick reference |
| Code examples | Full context, step-by-step | Key patterns only |
| Format | Jekyll/Markdown site | Skill markdown files |
| Location | `{project}/docs/` or GitHub Pages | `~/.claude/skills/{skill}/` |

**Key principle:** The skill is a **condensed summary** of documentation, not a duplicate.

---

## Skill Structure

Each skill follows this structure:

```
~/.claude/skills/{skill}/
├── SKILL.md              # Main entry point (required)
├── {topic}.md            # Sub-documents for specific topics
├── {topic}.md
└── ...
```

Example for Neatoo:

```
~/.claude/skills/neatoo/
├── SKILL.md              # Overview, quick reference, when to use
├── entities.md           # EntityBase, ValidateBase details
├── rules.md              # Validation rules reference
├── factories.md          # Factory operations
├── client-server.md      # RemoteFactory setup
├── blazor-integration.md # MudBlazor, binding patterns
└── ...
```

---

## Sync Tracking Table

Every skill SKILL.md should have a sync tracking table:

```markdown
## Skill Sync Status

| Repository | Last Synced Commit | Date |
|------------|-------------------|------|
| Neatoo | v10.6.0 | 2026-01-05 |
| RemoteFactory | v10.5.0 | 2026-01-05 |
```

**Update this table** after reviewing changes and updating the skill.

---

## Workflow: Syncing Skill After Code Changes

### Step 1: Identify What Changed

Check commits since last sync:

```bash
# In the project repository
git log --oneline {last-synced-commit}..HEAD
```

Or check release notes:
- `docs/release-notes/` in the project
- `CHANGELOG.md`

### Step 2: Identify Skill-Relevant Changes

Not all changes need skill updates. Focus on:

| Change Type | Skill Update? |
|-------------|---------------|
| New public API | Yes |
| Breaking changes | Yes (high priority) |
| New patterns/best practices | Yes |
| Bug fixes | Usually no |
| Internal refactoring | No |
| Performance improvements | No |

### Step 3: Update Relevant Skill Files

1. Read the updated documentation
2. Condense key points into skill format
3. Update code examples (from compiled samples)
4. Update the sync tracking table

### Step 4: Verify Skill Code Examples

**Critical:** Skill code examples should come from the same compiled sources as documentation.

**Preferred: Use snippet markers (automated)**
```markdown
<!-- snippet: docs:validation-and-rules:age-validation-rule -->
```csharp
// Replaced automatically by extract-snippets.ps1
```
<!-- /snippet -->
```

Then run:
```powershell
.\scripts\extract-snippets.ps1 -Update -SkillPath "$env:USERPROFILE\.claude\skills\neatoo"
```

**Alternative: Reference documentation**
```markdown
For full example, see docs/validation-and-rules.md#age-validation
```

**Never write code directly in skills** - always pull from compiled sources.

---

## Skill Code Example Guidelines

### Do: Use Condensed Examples

```markdown
### Basic Entity Pattern

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    public Person(IEntityBaseServices<Person> services) : base(services) { }

    [Required]
    public partial string? Name { get; set; }

    [Create]
    public void Create() { }
}
```

Focus on the pattern, not comprehensive coverage.
```

### Don't: Duplicate Full Documentation

Skills are for **quick reference**, not tutorials. Link to docs for full explanations:

```markdown
### Async Rules

Async rules validate against external resources (database, API).

```csharp
public class UniqueEmailRule : AsyncRuleBase<IPerson>
{
    // Condensed example
}
```

For complete async rule patterns including cancellation, see:
- `docs/validation-and-rules.md` - Async Rules section
- `docs/database-dependent-validation.md`
```

---

## When to Update Skills

### Trigger: New Release

After every release that includes user-facing changes:

1. Review release notes
2. Update affected skill files
3. Update sync tracking table
4. Test that Claude gives correct guidance

### Trigger: Documentation Update

After significant documentation updates:

1. Review what changed in docs
2. Determine if skill summary needs update
3. Update relevant skill sections

### Trigger: User Reports Issue

If a user reports Claude giving incorrect guidance:

1. Identify the skill section with wrong info
2. Verify against current documentation
3. Update skill from compiled sources
4. Note the fix in skill commit message

---

## Skill Review Checklist

When updating a skill, verify:

- [ ] Code examples compile (match documentation/samples)
- [ ] API references are current (class names, method signatures)
- [ ] Patterns shown are current best practices
- [ ] Breaking changes from recent versions are reflected
- [ ] Sync tracking table is updated

---

## Example: Syncing After API Change

**Scenario:** Neatoo 10.5.0 changed `Save()` to require reassignment.

### 1. Identify the Change

From release notes:
> **Breaking:** `Save()` now returns a new deserialized instance. Must capture: `person = await personFactory.Save(person);`

### 2. Find Affected Skill Sections

Search skill files for `Save(`:
```
~/.claude/skills/neatoo/factories.md - Factory Usage section
~/.claude/skills/neatoo/SKILL.md - Quick Reference section
```

### 3. Update Skill Content

Before:
```csharp
await personFactory.Save(person);
```

After:
```csharp
person = await personFactory.Save(person);  // ALWAYS reassign!
```

### 4. Update Sync Table

```markdown
| Neatoo | v10.5.0 | 2026-01-05 |
```

---

## Skill Files for Neatoo Project

| Skill File | Corresponding Docs | Topics Covered |
|------------|-------------------|----------------|
| SKILL.md | docs/index.md, docs/quick-start.md | Overview, quick reference |
| entities.md | docs/aggregates-and-entities.md | EntityBase, ValidateBase, Value Objects |
| rules.md | docs/validation-and-rules.md | Rules engine, validation |
| factories.md | docs/factory-operations.md | CRUD, Commands & Queries |
| client-server.md | docs/remote-factory.md | RemoteFactory setup |
| properties.md | docs/property-system.md | Meta-properties |
| blazor-integration.md | docs/blazor-binding.md | MudNeatoo, binding |
| data-mapping.md | docs/mapper-methods.md | MapFrom, MapTo |
| authorization.md | - | AuthorizeFactory |
| testing.md | docs/testing.md | Test patterns |
| source-generators.md | - | Generator output |
| migration.md | docs/release-notes/ | Version migration |

---

## Automated Skill Sync

The `extract-snippets.ps1` script now supports skill files via the `-SkillPath` parameter.

### How It Works

1. Skills use the **same** `<!-- snippet: docs:{docfile}:{snippetid} -->` markers as documentation
2. The script scans skill files for these markers
3. Code is injected from the same compiled samples that feed documentation

### Usage

```powershell
# Update both docs and skills
.\scripts\extract-snippets.ps1 -Update -SkillPath "$env:USERPROFILE\.claude\skills\neatoo"

# Verify both are in sync
.\scripts\extract-snippets.ps1 -Verify -SkillPath "$env:USERPROFILE\.claude\skills\neatoo"
```

### Adding a Snippet Marker to a Skill File

```markdown
## Value Objects

<!-- snippet: docs:aggregates-and-entities:value-object -->
```csharp
// This will be replaced by extract-snippets.ps1
```
<!-- /snippet -->
```

The snippet ID (`docs:aggregates-and-entities:value-object`) must match a `#region docs:*` marker in the samples.

### Key Points

- Skills can use **any** snippet from samples, not just ones matching the skill filename
- The same snippet can appear in both documentation and skills
- Run `-Verify -SkillPath` before committing to ensure skills are in sync

---

## Future Improvements

1. **Diff detection** - Script to compare skill code blocks against documentation
2. **Staleness alerts** - Warn when skill hasn't been synced after N commits

# 02 - Documentation Sync

How to sync code snippets from sample projects into documentation using MarkdownSnippets.

---

## Overview

[MarkdownSnippets](https://github.com/SimonCropp/MarkdownSnippets) is a dotnet tool that:
1. Scans code files for `#region {id}` markers
2. Scans markdown files for `snippet: {id}` references
3. Injects the code content into the markdown

---

## Setup

### Install MarkdownSnippets

```bash
# Create tool manifest (if not exists)
dotnet new tool-manifest

# Install the tool
dotnet tool install MarkdownSnippets.Tool

# Verify installation
dotnet mdsnippets --help
```

### Create Configuration

Create `mdsnippets.json` in project root:

```json
{
  "Convention": "InPlaceOverwrite",
  "LinkFormat": "GitHub",
  "UrlPrefix": "",
  "OmitSnippetLinks": true,
  "ReadOnly": false,
  "ExcludeDirectories": [
    "node_modules",
    "bin",
    "obj",
    ".git"
  ]
}
```

**Configuration options:**

| Setting | Values | Description |
|---------|--------|-------------|
| `Convention` | `InPlaceOverwrite` | Modifies `.md` files directly |
| | `SourceTransform` | Converts `.source.md` to `.md` |
| `LinkFormat` | `GitHub`, `GitLab`, `None` | Format for source links |
| `OmitSnippetLinks` | `true/false` | Hide/show "snippet source" links |
| `ReadOnly` | `true/false` | Mark generated content read-only |

---

## Markdown Placeholder Syntax

Add references in documentation where you want compiled code injected:

```markdown
## Age Validation Example

snippet: age-validation-rule

This rule validates that age is not negative.
```

That's it - just `snippet: {id}` on its own line. No HTML comments, no code fences, no closing tags.

---

## Running MarkdownSnippets

### Basic Usage

```bash
# From project root
dotnet mdsnippets
```

**Output:**
```
Processing directory: /path/to/project
  docs/validation-and-rules.md
    age-validation-rule
    required-attribute
  docs/factories.md
    create-pattern
    save-pattern
Processed 4 snippets in 2 files
```

### What It Generates

The markdown is transformed to include the code:

**Before (what you write):**
```markdown
snippet: age-validation-rule
```

**After (what mdsnippets generates):**
```markdown
<!-- snippet: age-validation-rule -->
<a id='snippet-age-validation-rule'></a>
```csharp
public class AgeValidationRule : RuleBase<IPerson>
{
    // code from the #region
}
```
<sup><a href='/path/to/file.cs#L5-L16' title='Snippet source file'>snippet source</a></sup>
<!-- endSnippet -->
```

If `OmitSnippetLinks: true`, the `<sup>` source link is omitted.

---

## Workflow: Adding a New Snippet

### Step 1: Add Code to Samples Project

```csharp
// docs/samples/Neatoo.Samples.DomainModel/Rules/EmailValidationRule.cs

namespace Neatoo.Samples.DomainModel.Rules;

#region email-validation-rule
public class EmailValidationRule : RuleBase<IPerson>
{
    public EmailValidationRule() : base(p => p.Email) { }

    protected override IRuleMessages Execute(IPerson target)
    {
        if (!target.Email?.Contains("@") ?? true)
            return (nameof(target.Email), "Invalid email format").AsRuleMessages();
        return None;
    }
}
#endregion
```

### Step 2: Build to Verify Compilation

```bash
dotnet build docs/samples/
```

### Step 3: Add Test Coverage

```csharp
// docs/samples/Neatoo.Samples.DomainModel.Tests/Rules/EmailValidationRuleTests.cs

public class EmailValidationRuleTests : SamplesTestBase
{
    [Fact]
    public async Task InvalidEmail_ReturnsError()
    {
        var person = CreatePerson();
        person.Email = "not-an-email";

        await person.WaitForTasks();

        Assert.False(person[nameof(person.Email)].IsValid);
    }
}
```

### Step 4: Add Reference to Documentation

```markdown
<!-- In docs/validation-and-rules.md -->

### Email Validation

snippet: email-validation-rule
```

### Step 5: Run MarkdownSnippets

```bash
dotnet mdsnippets
```

### Step 6: Verify Result

Check that `docs/validation-and-rules.md` now contains the actual compiled code.

---

## Workflow: Updating Existing Snippets

When you modify code in a `#region`:

1. Edit the code in the samples project
2. Build and test to verify it works
3. Run `dotnet mdsnippets` to update docs
4. Commit both code and doc changes together

```bash
# After editing code
dotnet build docs/samples/
dotnet test docs/samples/
dotnet mdsnippets
git add docs/
git commit -m "feat: update validation rule behavior"
```

---

## Workflow: Adding Non-Compiled Code Blocks

For pseudo-code or anti-patterns that shouldn't be compiled:

### Pseudo-code

```markdown
Here's the conceptual pattern:

<!-- snippet: pseudo:save-concept -->
```csharp
// In a real implementation:
// await db.SaveChangesAsync();
```
<!-- /snippet -->
```

### Anti-patterns

```markdown
<!-- snippet: invalid:wrong-approach -->
```csharp
// WRONG - don't do this
await factory.Save(entity);
```
<!-- /snippet -->
```

**Note:** MarkdownSnippets ignores these - they're just HTML comments. Your `verify-code-blocks.ps1` script validates them.

---

## Error Handling

### "Snippet not found"

**Cause:** `snippet: {id}` references a snippet that doesn't exist in code.

**Fix:**
1. Check spelling of the snippet ID
2. Verify `#region {id}` exists in code: `grep -r "region {id}" docs/samples/`
3. Ensure the region is in a scanned directory

### "Duplicate snippet"

**Cause:** Same `#region {id}` exists in multiple files.

**Fix:** Rename one of the regions to be unique.

### Snippet Not Updating

**Cause:** MarkdownSnippets only updates content it generated.

**Check:**
- Look for `<!-- snippet: {id} -->` and `<!-- endSnippet -->`
- If these don't exist, add `snippet: {id}` reference first

---

## Handling Different Code Languages

MarkdownSnippets auto-detects language from file extension:

| Extension | Language |
|-----------|----------|
| `.cs` | `csharp` |
| `.razor` | `razor` |
| `.fs` | `fsharp` |
| `.vb` | `vb` |
| `.xml` | `xml` |
| `.json` | `json` |

### Razor Example

```razor
@* In docs/samples/Components/PersonForm.razor *@

@#region person-form-binding
<EditForm Model="@Person" OnValidSubmit="@HandleSubmit">
    <MudTextField @bind-Value="Person.Name" Label="Name" />
    <MudButton ButtonType="ButtonType.Submit">Save</MudButton>
</EditForm>
@#endregion
```

```markdown
snippet: person-form-binding
```

---

## Advanced: Include Full Files

If no matching snippet region is found, MarkdownSnippets searches for a file with that name:

```markdown
snippet: LICENSE.txt
```

This includes the entire `LICENSE.txt` file.

---

## Advanced: Remote Snippets

Include content from URLs:

```markdown
snippet: https://raw.githubusercontent.com/owner/repo/main/example.cs
```

Or reference a specific snippet in a remote file:

```markdown
web-snippet: https://url/to/file.cs#snippet-name
```

---

## CI Integration

Verify documentation stays in sync:

```yaml
# .github/workflows/build.yml

- name: Restore tools
  run: dotnet tool restore

- name: Build samples
  run: dotnet build docs/samples/

- name: Test samples
  run: dotnet test docs/samples/

- name: Run MarkdownSnippets
  run: dotnet mdsnippets

- name: Verify no changes
  run: |
    if [ -n "$(git status --porcelain docs/)" ]; then
      echo "Documentation out of sync"
      git diff docs/
      exit 1
    fi
```

---

## Comparison: Old vs New

| Aspect | Old (extract-snippets.ps1) | New (MarkdownSnippets) |
|--------|---------------------------|------------------------|
| Region format | `#region docs:{file}:{id}` | `#region {id}` |
| Markdown placeholder | `<!-- snippet: docs:{file}:{id} -->` + code fence + `<!-- /snippet -->` | `snippet: {id}` |
| Source links | None | Auto-generated |
| Verification | Custom script | Built-in (fails on missing) |
| Language detection | Manual | Automatic |

---

## Troubleshooting

### mdsnippets Not Finding Regions

Check:
1. File is in a scanned directory (not in `ExcludeDirectories`)
2. Region uses correct syntax: `#region name` or `// begin-snippet: name`
3. No typos in region name

### Generated Content Looks Wrong

If you edited the generated section manually:
1. Delete everything between `<!-- snippet: -->` and `<!-- endSnippet -->`
2. Replace with just `snippet: {id}`
3. Re-run `dotnet mdsnippets`

### Line Endings Issues

MarkdownSnippets normalizes line endings. If git shows changes:

```bash
# Configure git to handle line endings
git config core.autocrlf input
```

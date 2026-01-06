# 02 - Documentation Sync

How to sync code snippets from sample projects into documentation markdown files.

---

## Overview

The sync process:
1. Scans sample files for `#region docs:*` markers
2. Extracts code content
3. Injects into documentation at `<!-- snippet: ... -->` placeholders

---

## Markdown Placeholder Syntax

Add placeholders in documentation where you want compiled code injected:

```markdown
## Age Validation Example

<!-- snippet: docs:validation-and-rules:age-validation-rule -->
```csharp
// This content will be replaced by extract-snippets.ps1
```
<!-- /snippet -->
```

**Format:**
```markdown
<!-- snippet: docs:{doc-file}:{snippet-id} -->
```csharp
placeholder content (will be replaced)
```
<!-- /snippet -->
```

**Important:**
- The placeholder must exist BEFORE running the script
- The `{doc-file}` and `{snippet-id}` must match a region in the samples project
- Use `csharp` or `razor` for the code fence language

---

## The Extraction Script

Each project has `scripts/extract-snippets.ps1`:

### List Snippets (Default)

```powershell
# Just scan and list all snippets (no modifications)
.\scripts\extract-snippets.ps1
```

Output:
```
Neatoo Documentation Snippet Extractor
=======================================
Samples Path: C:\src\...\docs\samples
Docs Path: C:\src\...\docs

Scanning source files...

Found 62 snippets:
  validation-and-rules.md:
    - required-attribute (DataAnnotationSamples.cs)
    - age-validation-rule (RuleBaseSamples.cs)
    - async-database-rule (AsyncRuleSamples.cs)
  aggregates-and-entities.md:
    - entity-base-class (EntityBaseSamples.cs)
    ...
```

### Verify Mode (CI)

```powershell
# Check if docs are in sync with samples (exits with error if not)
.\scripts\extract-snippets.ps1 -Verify
```

Output when in sync:
```
Verification complete. 56 snippets verified, 6 orphan snippets.
```

Output when out of sync:
```
Documentation out of sync with samples:
  - validation-and-rules.md: age-validation-rule
  - collections.md: list-cascade-delete

Run '.\scripts\extract-snippets.ps1 -Update' to sync documentation.
```

### Update Mode (Local)

```powershell
# Extract snippets and update documentation files
.\scripts\extract-snippets.ps1 -Update
```

Output:
```
Updating documentation files...
  Updated: validation-and-rules.md
  Updated: aggregates-and-entities.md
  Updated: factory-operations.md

Update complete. 3 files updated, 56 snippets processed.
```

---

## Workflow: Adding a New Snippet

### Step 1: Add Code to Samples Project

Create or edit a file in `docs/samples/`:

```csharp
// docs/samples/Neatoo.Samples.DomainModel/ValidationAndRules/NewRuleSamples.cs

namespace Neatoo.Samples.DomainModel.ValidationAndRules;

#region docs:validation-and-rules:email-validation-rule
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
dotnet build docs/samples/Neatoo.Samples.DomainModel/
```

### Step 3: Add Test Coverage

```csharp
// docs/samples/Neatoo.Samples.DomainModel.Tests/ValidationAndRules/NewRuleSamplesTests.cs

public class NewRuleSamplesTests : SamplesTestBase
{
    [Fact]
    public void EmailValidationRule_InvalidEmail_ReturnsError()
    {
        var person = CreatePerson();
        person.Email = "not-an-email";

        await person.WaitForTasks();

        Assert.False(person[nameof(person.Email)].IsValid);
    }
}
```

### Step 4: Add Placeholder to Documentation

```markdown
<!-- In docs/validation-and-rules.md -->

### Email Validation

<!-- snippet: docs:validation-and-rules:email-validation-rule -->
```csharp
// Placeholder - will be replaced
```
<!-- /snippet -->
```

### Step 5: Run Update

```powershell
.\scripts\extract-snippets.ps1 -Update
```

### Step 6: Verify Result

Check that `docs/validation-and-rules.md` now contains the actual compiled code.

---

## Workflow: Adding Infrastructure Snippets (Program.cs)

Infrastructure code (server setup, client setup) must live in runnable projects.

### Step 1: Add Regions to Server Program.cs

```csharp
// docs/samples/Neatoo.Samples.Server/Program.cs

var builder = WebApplication.CreateBuilder(args);

#region docs:remote-factory:server-di-setup
builder.Services.AddNeatooServices(NeatooFactory.Server, typeof(IPerson).Assembly);
#endregion

// Other app-specific setup...

var app = builder.Build();

#region docs:remote-factory:server-endpoint
app.MapPost("/api/neatoo", (HttpContext ctx, RemoteRequestDto request, CancellationToken ct) =>
{
    var handler = ctx.RequestServices.GetRequiredService<HandleRemoteDelegateRequest>();
    return handler(request, ct);
});
#endregion

await app.RunAsync();
```

### Step 2: Verify Server Runs

```bash
# Server must actually start without errors
dotnet run --project docs/samples/Neatoo.Samples.Server/
```

### Step 3: Add Placeholders to Documentation

```markdown
<!-- In docs/remote-factory.md -->

### Server Setup

<!-- snippet: docs:remote-factory:server-di-setup -->
```csharp
// Will be replaced
```
<!-- /snippet -->

### Endpoint Configuration

<!-- snippet: docs:remote-factory:server-endpoint -->
```csharp
// Will be replaced
```
<!-- /snippet -->
```

### Step 4: Sync and Verify

```powershell
.\scripts\extract-snippets.ps1 -Update
```

**Why runnable projects matter:** If the service registration is wrong, it compiles but fails at runtime. By having actual runnable Server/BlazorClient projects, you catch these errors before they reach documentation.

---

## Orphan Snippets

**Orphan snippets** exist in samples but have no corresponding marker in docs.

```
Orphan snippets (in samples but not in docs):
  - validation-and-rules.md: experimental-rule
  - collections.md: future-feature
```

This is a **warning**, not an error. Orphans are useful for:
- Code that compiles but isn't yet documented
- Alternative examples kept for reference
- Future documentation planned

---

## Script Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-Verify` | Check sync status, exit 1 if out of sync | - |
| `-Update` | Inject snippets into documentation | - |
| `-SamplesPath` | Path to samples projects | `docs/samples/` |
| `-DocsPath` | Path to docs directory | `docs/` |

---

## Handling Different Code Languages

The script supports both C# and Razor:

```markdown
<!-- For C# -->
<!-- snippet: docs:validation-and-rules:rule-example -->
```csharp
...
```
<!-- /snippet -->

<!-- For Razor -->
<!-- snippet: docs:blazor-binding:edit-form -->
```razor
...
```
<!-- /snippet -->
```

The script detects `.razor` files and uses the appropriate language fence.

---

## Script Location

Each project should have the script at:

```
{project}/
├── scripts/
│   └── extract-snippets.ps1
├── src/
│   └── {Project}/
└── docs/
    ├── *.md
    └── samples/
        ├── {Project}.Samples.DomainModel/
        ├── {Project}.Samples.DomainModel.Tests/
        ├── {Project}.Samples.Server/
        └── {Project}.Samples.BlazorClient/
```

**The Neatoo script can be copied to other projects** - it's parameterized to work with any project structure following this convention.

---

## Troubleshooting

### "Doc file not found: xyz.md"

The script looks for `{doc-file}.md` in the docs directory. Check:
- The doc-file part of the region matches the actual filename
- The file exists in `docs/` or adjust `DocsPath`

### Snippet Not Updating

The script only updates content between existing markers. If the marker doesn't exist in the markdown, nothing happens.

1. Add the placeholder first:
   ```markdown
   <!-- snippet: docs:file:id -->
   ```csharp
   placeholder
   ```
   <!-- /snippet -->
   ```
2. Then run `-Update`

### Line Ending Issues

The script normalizes line endings for comparison. If verification still fails:
- Check for mixed line endings in source files
- Ensure Git isn't auto-converting on checkout

---

## Projects Using This Pattern

| Project | Script Location | Docs Location |
|---------|----------------|---------------|
| Neatoo | `scripts/extract-snippets.ps1` | `docs/` |
| KnockOff | `scripts/extract-snippets.ps1` | `docs/` |
| RemoteFactory | TBD | TBD |
| neatoodotnet.github.io | `scripts/inject-code-blocks.ps1` | `_pages/` |

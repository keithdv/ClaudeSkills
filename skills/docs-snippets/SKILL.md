---
name: docs-snippets
description: Documentation snippet synchronization. Use when adding code examples to documentation, syncing snippets from samples to docs, verifying docs are in sync with code, or working with the #region docs:* pattern. Ensures code in documentation is compiled and tested.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(pwsh:*, powershell:*, dotnet:*)
---

# Documentation Snippets

## Overview

This skill manages documentation code snippets using a **single source of truth** pattern:

1. **Code lives in a `Documentation.Samples` project** with `#region docs:*` markers
2. **Markdown files reference snippets** with `<!-- snippet: docs:* -->` markers
3. **A PowerShell script syncs** extracted code into documentation

Benefits:
- Code in docs is always **compiled and tested**
- No drift between docs and actual API
- Snippets are **validated by the compiler**

## Project Structure

```
{Project}/
├── src/
│   └── Tests/
│       ├── {Project}.Documentation.Samples/       # Samples project
│       │   ├── GettingStarted/
│       │   │   └── GettingStartedSamples.cs       # Contains #region markers
│       │   └── Guides/
│       │       └── MethodsSamples.cs
│       └── {Project}.Documentation.Samples.Tests/ # Tests for samples
├── docs/
│   ├── getting-started.md                         # Contains <!-- snippet: --> markers
│   └── guides/
│       └── methods.md
└── scripts/
    └── extract-snippets.ps1                       # Sync script
```

## Region Marker Convention

### In C# Sample Files

```csharp
/// <summary>
/// Code samples for docs/getting-started.md
/// </summary>
namespace KnockOff.Documentation.Samples.GettingStarted;

#region docs:getting-started:interface-definition
public interface IEmailService
{
    void SendEmail(string to, string subject, string body);
    bool IsConnected { get; }
}
#endregion

#region docs:getting-started:stub-class
[KnockOff]
public partial class EmailServiceKnockOff : IEmailService
{
    // That's it! The generator creates the implementation.
}
#endregion
```

**Format**: `#region docs:{doc-file-name}:{snippet-id}`

- `{doc-file-name}` - Markdown filename without extension (e.g., `getting-started`)
- `{snippet-id}` - Unique identifier within that doc (e.g., `interface-definition`)

### In Markdown Documentation

```markdown
### Step 1: Define an Interface

<!-- snippet: docs:getting-started:interface-definition -->
```csharp
public interface IEmailService
{
    void SendEmail(string to, string subject, string body);
    bool IsConnected { get; }
}
```
<!-- /snippet -->

### Step 2: Create a KnockOff Stub

<!-- snippet: docs:getting-started:stub-class -->
```csharp
[KnockOff]
public partial class EmailServiceKnockOff : IEmailService
{
    // That's it! The generator creates the implementation.
}
```
<!-- /snippet -->
```

**Format**:
```markdown
<!-- snippet: docs:{doc-file}:{snippet-id} -->
```csharp
... code here (will be replaced on sync) ...
```
<!-- /snippet -->
```

## PowerShell Script Usage

### Verify (CI-friendly)

```powershell
# Check if docs are in sync with samples (exits with error if not)
.\scripts\extract-snippets.ps1 -Verify
```

Output:
```
KnockOff Documentation Snippet Extractor
=========================================
Samples Path: C:\src\...\KnockOff.Documentation.Samples
Docs Path: C:\src\...\docs

Scanning source files...

Found 15 snippets:
  getting-started.md:
    - interface-definition (GettingStartedSamples.cs)
    - stub-class (GettingStartedSamples.cs)
  methods.md:
    - void-no-params (MethodsSamples.cs)
    ...

Verification complete. 12 snippets verified, 3 orphan snippets.
```

### Update (Sync docs)

```powershell
# Update documentation files with latest snippet content
.\scripts\extract-snippets.ps1 -Update
```

### List (No flags)

```powershell
# Just scan and list all snippets (doesn't modify or verify)
.\scripts\extract-snippets.ps1
```

## Workflow: Adding a New Snippet

### Step 1: Add Code to Samples Project

Create or edit a file in `Documentation.Samples`:

```csharp
// src/Tests/KnockOff.Documentation.Samples/Guides/AsyncMethodsSamples.cs

namespace KnockOff.Documentation.Samples.Guides;

#region docs:async-methods:basic-interface
public interface IAsyncRepository
{
    Task<User?> GetByIdAsync(int id);
    Task SaveAsync(User user);
}
#endregion
```

### Step 2: Add Test Coverage (Optional but Recommended)

```csharp
// src/Tests/KnockOff.Documentation.Samples.Tests/Guides/AsyncMethodsSamplesTests.cs

public class AsyncMethodsSamplesTests
{
    [Fact]
    public async Task GetByIdAsync_ReturnsUser()
    {
        var knockOff = new AsyncRepositoryKnockOff();
        // Test the sample code works
    }
}
```

### Step 3: Add Marker to Documentation

```markdown
<!-- docs/guides/async-methods.md -->

## Basic Async Interface

<!-- snippet: docs:async-methods:basic-interface -->
```csharp
// Placeholder - will be replaced by sync
```
<!-- /snippet -->
```

### Step 4: Sync

```powershell
.\scripts\extract-snippets.ps1 -Update
```

## Best Practices

### Snippet Size

| Lines | Status | Recommendation |
|-------|--------|----------------|
| 1-15 | Good | Focused, easy to understand |
| 16-30 | Acceptable | Consider splitting if possible |
| 30+ | Too large | Use nested micro-snippets |

### Nested Regions (Micro-Snippets)

For large examples, use nested regions to extract focused parts:

```csharp
// Full compilable class
[Factory]
internal partial class OrderSamples : EntityBase<OrderSamples>
{
    #region docs:aggregates:state-tracking-properties
    public partial string? Status { get; set; }     // IsModified tracked
    public partial decimal Total { get; set; }      // IsSavable updated
    #endregion

    #region docs:aggregates:inline-validation
    RuleManager.AddValidation(
        t => t.Total <= 0 ? "Total must be positive" : "",
        t => t.Total);
    #endregion
}
```

Documentation can reference either the full class OR the micro-snippets.

### File Organization

```
Documentation.Samples/
├── GettingStarted/           # Matches docs/getting-started.md
│   └── GettingStartedSamples.cs
├── Concepts/                 # Matches docs/concepts/*.md
│   └── CustomizationPatternsSamples.cs
├── Guides/                   # Matches docs/guides/*.md
│   ├── MethodsSamples.cs
│   ├── PropertiesSamples.cs
│   └── AsyncMethodsSamples.cs
└── Reference/                # Matches docs/reference/*.md
    └── HandlerApiSamples.cs
```

### Sample File Header

Include a header listing all snippets for discoverability:

```csharp
/// <summary>
/// Code samples for docs/getting-started.md
///
/// Snippets in this file:
/// - docs:getting-started:interface-definition
/// - docs:getting-started:stub-class
/// - docs:getting-started:user-method
///
/// Corresponding tests: GettingStartedSamplesTests.cs
/// </summary>

namespace KnockOff.Documentation.Samples.GettingStarted;
```

## Orphan Snippets

**Orphan snippets** exist in samples but have no corresponding marker in docs.

```
Orphan snippets (in samples but not in docs):
  - methods.md: sequential-returns
  - properties.md: readonly-backing
```

This is a **warning**, not an error. Orphans are useful for:
- Code that compiles but isn't yet documented
- Alternative examples kept for reference
- Future documentation planned

## CI Integration

Add verification to your build workflow:

```yaml
# .github/workflows/build.yml
- name: Verify documentation snippets
  run: pwsh -File scripts/extract-snippets.ps1 -Verify
```

This ensures documentation stays in sync with compiled code.

## Troubleshooting

### "Doc file not found: xyz.md"

The script looks for `{snippet-id}.md` in the docs directory. Check:
- The doc-file part of the region matches the actual filename
- The file exists in `docs/` or a subdirectory

### "Missing #endregion"

Every `#region docs:*` needs a matching `#endregion`:

```csharp
#region docs:example:snippet-id
// code
#endregion  // <- Don't forget this
```

### "Duplicate snippet key"

Each `docs:{file}:{id}` combination must be unique across all sample files:

```csharp
// BAD - same key in two files
// File1.cs: #region docs:methods:basic-example
// File2.cs: #region docs:methods:basic-example

// GOOD - unique keys
// File1.cs: #region docs:methods:void-method
// File2.cs: #region docs:methods:return-method
```

### Snippet Not Updating

The script only updates content between existing markers. If the marker doesn't exist in the markdown, nothing happens. Add the marker first:

```markdown
<!-- snippet: docs:file:id -->
```csharp
placeholder
```
<!-- /snippet -->
```

Then run `-Update`.

## Projects Using This Pattern

- **KnockOff**: `src/Tests/KnockOff.Documentation.Samples`
- **Neatoo**: `src/Neatoo.Documentation.Samples`

Both use identical conventions and script structure.

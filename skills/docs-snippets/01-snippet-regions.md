# 01 - Snippet Regions

How to mark code in source files for extraction into documentation.

---

## Inline Code vs Snippets

Documentation contains two types of code:

| Term | Format | Sourced from samples? |
|------|--------|----------------------|
| **Inline code** | Mid-sentence backticks like `EntityBase<T>` | No - out of scope |
| **Snippet** | Fenced code block showing working code | Yes - always |
| **Illustration** | Fenced code block showing non-executable content | No - intentionally unsourced |

**Inline code** names things within sentences - class names, method names, property names. These are not tracked.

**Snippets** are fenced code blocks that demonstrate working behavior. Whether 1 line or 100 lines, if it's meant to work, it must be sourced from compiled sample code.

**Illustrations** are fenced code blocks that intentionally show non-executable content:
- **Anti-patterns** - WRONG/CORRECT comparisons showing what NOT to do
- **Pseudocode** - Conceptual logic, not real syntax
- **Hypothetical examples** - Code that doesn't exist in the project
- **Partial fragments** - Incomplete code used to highlight a concept

Illustrations should be clearly marked with comments like `// WRONG` or `// Pseudocode` so readers understand they're not working examples.

```markdown
Use `EntityBase<T>` as your base class.     <!-- inline code - OK -->

<!-- snippet: docs:entities:base-class -->  <!-- snippet - sourced from samples -->
```csharp
public class Person : EntityBase<Person> { }
```
<!-- /snippet -->

```csharp
// WRONG - don't do this                    <!-- illustration - intentionally unsourced -->
await personFactory.Save(person);

// CORRECT
person = await personFactory.Save(person);
```
```

---

## The Problem

Fenced code blocks written directly in documentation:
- Have **syntax errors** (never compiled)
- Use **outdated API** (code drifted from implementation)
- Make **false assertions** (claims behavior that doesn't exist)

## The Solution

All fenced code blocks live in **compiled, tested projects**. Documentation **pulls from** these sources via `#region` markers.

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCE OF TRUTH                          │
│  Sample projects with #region docs:* markers                │
│  - Compiled by dotnet build                                 │
│  - Verified by dotnet test                                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Documentation │    │ Claude Skill  │    │    README     │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## Code Sources

Documentation snippets come from two types of projects:

| Project Type | Purpose | Examples |
|--------------|---------|----------|
| **Snippet libraries** | Testable domain code | Entities, rules, factories, validation |
| **Runnable apps** | Infrastructure code | Program.cs, DI setup, Razor components |

**Why both?** Test projects can't validate infrastructure code. A `Program.cs` with incorrect service registration will compile but fail at runtime. Only a real runnable application catches these errors.

---

## Project Structure

All documentation-related content lives under `docs/`:

```
{Project}/
├── src/
│   └── {Project}/                              # Main library
│
├── docs/
│   ├── *.md                                    # Documentation markdown
│   ├── release-notes/                          # Version release notes
│   │
│   ├── todos/                                  # Active markdown plans
│   │   └── completed/                          # Completed plans
│   │
│   └── samples/                                # All code for documentation
│       ├── {Project}.Samples.DomainModel/      # Domain with #region snippets
│       │   ├── Entities/
│       │   │   ├── IPerson.cs
│       │   │   └── Person.cs
│       │   ├── Rules/
│       │   │   └── AgeValidationRule.cs
│       │   └── ...
│       ├── {Project}.Samples.DomainModel.Tests/# Tests (proves snippets work)
│       ├── {Project}.Samples.BlazorClient/     # Program.cs client snippets
│       ├── {Project}.Samples.Server/           # Program.cs server snippets
│       └── {Project}.Samples.Ef/               # EF Core (optional)
│
└── scripts/
    └── extract-snippets.ps1                    # Scans docs/samples/
```

**Key insight:** The domain model IS the snippets. Entities, rules, and factories contain `#region` markers - no separate snippet library needed.

---

## Region Naming Convention

```
#region docs:{doc-file}:{snippet-id}
```

| Part | Description | Example |
|------|-------------|---------|
| `docs:` | Required prefix (identifies extractable snippets) | `docs:` |
| `{doc-file}` | Markdown filename **without extension** | `remote-factory` |
| `{snippet-id}` | Unique identifier within that doc | `server-program-cs` |

**Full example:** `#region docs:remote-factory:server-program-cs`

---

## Basic Pattern

```csharp
// In ValidationAndRules/RuleBaseSamples.cs

#region docs:validation-and-rules:age-validation-rule
public class AgeValidationRule : RuleBase<IPerson>
{
    public AgeValidationRule() : base(p => p.Age) { }

    protected override IRuleMessages Execute(IPerson target)
    {
        if (target.Age < 0)
            return (nameof(target.Age), "Age cannot be negative").AsRuleMessages();
        return None;
    }
}
#endregion
```

**Rules:**
- Every `#region docs:*` **must** have a matching `#endregion`
- Each `docs:{file}:{id}` combination **must** be unique across all sample files
- Content between markers is extracted with leading/trailing blank lines trimmed

---

## Infrastructure Snippets (Program.cs)

Infrastructure code lives in runnable projects. Use regions to mark the Neatoo-specific parts:

### Server Program.cs

```csharp
// In docs/samples/{Project}.Samples.Server/Program.cs

var builder = WebApplication.CreateBuilder(args);

#region docs:remote-factory:server-di-setup
// Neatoo server setup
builder.Services.AddNeatooServices(NeatooFactory.Server, typeof(IPerson).Assembly);
#endregion

// App-specific services...
builder.Services.AddScoped<IPersonDbContext, PersonDbContext>();

var app = builder.Build();

#region docs:remote-factory:server-endpoint
// Neatoo endpoint with cancellation support
app.MapPost("/api/neatoo", (HttpContext ctx, RemoteRequestDto request, CancellationToken ct) =>
{
    var handler = ctx.RequestServices.GetRequiredService<HandleRemoteDelegateRequest>();
    return handler(request, ct);
});
#endregion

await app.RunAsync();
```

### Blazor Client Program.cs

```csharp
// In docs/samples/{Project}.Samples.BlazorClient/Program.cs

var builder = WebAssemblyHostBuilder.CreateDefault(args);

#region docs:remote-factory:client-di-setup
// Neatoo client setup
builder.Services.AddNeatooServices(NeatooFactory.Remote, typeof(IPerson).Assembly);
builder.Services.AddKeyedScoped(RemoteFactoryServices.HttpClientKey, (sp, key) =>
    new HttpClient { BaseAddress = new Uri("http://localhost:5183/") });
#endregion

await builder.Build().RunAsync();
```

---

## File Organization

Organize samples like a real domain project. The `#region` markers handle mapping to docs:

```
docs/samples/
  {Project}.Samples.DomainModel/        # Domain entities WITH snippet regions
    {Project}.Samples.DomainModel.csproj
    Entities/
      IPerson.cs                        # #region docs:entities:person-interface
      Person.cs                         # #region docs:entities:person-class
    Rules/
      AgeValidationRule.cs              # #region docs:validation:age-rule
    Factories/
      PersonFactory.cs                  # #region docs:factories:create-pattern

  {Project}.Samples.DomainModel.Tests/  # Tests (proves snippets work)
  {Project}.Samples.BlazorClient/       # Program.cs client snippets
  {Project}.Samples.Server/             # Program.cs server snippets
  {Project}.Samples.Ef/                 # EF Core (optional)
```

**Key insight:** A file in `Entities/` can have snippets for any doc file. The folder structure shows users what a real project looks like; the region markers handle documentation mapping.

---

## File Header Convention

Include a header listing all snippets for discoverability:

```csharp
/// <summary>
/// Code samples for docs/validation-and-rules.md
///
/// Snippets in this file:
/// - docs:validation-and-rules:required-attribute
/// - docs:validation-and-rules:age-validation-rule
/// - docs:validation-and-rules:async-database-rule
///
/// Corresponding tests: RuleBaseSamplesTests.cs
/// </summary>

namespace Neatoo.Samples.DomainModel.Rules;
```

---

## Nested Regions (Micro-Snippets)

For large examples, use nested regions to extract focused parts:

```csharp
[Factory]
internal partial class OrderSamples : EntityBase<OrderSamples>
{
    // Full class context for compilation...

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

Documentation can reference either the full class OR the micro-snippets independently.

---

## Snippet Size Guidelines

| Lines | Status | Recommendation |
|-------|--------|----------------|
| 1-15 | Good | Focused, easy to understand |
| 16-30 | Acceptable | Consider splitting if possible |
| 30+ | Too large | Use nested micro-snippets |

---

## Sample Project Setup

### Domain Model Project (Contains Snippets)

```xml
<!-- docs/samples/{Project}.Samples.DomainModel/{Project}.Samples.DomainModel.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Reference the main library -->
    <ProjectReference Include="..\..\..\src\{Project}\{Project}.csproj" />
  </ItemGroup>
</Project>
```

### Test Project

```xml
<!-- docs/samples/{Project}.Samples.DomainModel.Tests/{Project}.Samples.DomainModel.Tests.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\{Project}.Samples.DomainModel\{Project}.Samples.DomainModel.csproj" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
    <PackageReference Include="xunit" Version="2.*" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
  </ItemGroup>
</Project>
```

### Server Project

```xml
<!-- docs/samples/{Project}.Samples.Server/{Project}.Samples.Server.csproj -->
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\{Project}.Samples.DomainModel\{Project}.Samples.DomainModel.csproj" />
    <ProjectReference Include="..\{Project}.Samples.Ef\{Project}.Samples.Ef.csproj" />
  </ItemGroup>
</Project>
```

### Blazor Client Project

```xml
<!-- docs/samples/{Project}.Samples.BlazorClient/{Project}.Samples.BlazorClient.csproj -->
<Project Sdk="Microsoft.NET.Sdk.BlazorWebAssembly">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\{Project}.Samples.DomainModel\{Project}.Samples.DomainModel.csproj" />
  </ItemGroup>
</Project>
```

---

## Testing Snippets

Every snippet should have corresponding test coverage:

```csharp
// In Tests/ValidationAndRules/RuleBaseSamplesTests.cs

public class RuleBaseSamplesTests : SamplesTestBase
{
    [Fact]
    public void AgeValidationRule_NegativeAge_ReturnsError()
    {
        // Test that the documented rule actually works
        var person = CreatePerson();
        person.Age = -5;

        await person.WaitForTasks();

        Assert.False(person.IsValid);
        Assert.Contains("Age cannot be negative", person.PropertyMessages);
    }
}
```

**Benefits:**
- Proves the documented code actually works
- Catches API changes that break examples
- Documents expected behavior

---

## Common Mistakes

### Missing #endregion

```csharp
// BAD - script will fail
#region docs:example:snippet-id
// code
// forgot #endregion
```

### Duplicate Keys

```csharp
// BAD - same key in two files
// File1.cs: #region docs:methods:basic-example
// File2.cs: #region docs:methods:basic-example

// GOOD - unique keys
// File1.cs: #region docs:methods:void-method
// File2.cs: #region docs:methods:return-method
```

### Doc File Mismatch

```csharp
// BAD - doc file doesn't exist
#region docs:nonexistent-page:snippet

// GOOD - matches actual file docs/validation-and-rules.md
#region docs:validation-and-rules:snippet
```

---

## Projects Using This Pattern

| Project | Samples Location | Status |
|---------|-----------------|--------|
| Neatoo | `docs/samples/` | Migration needed |
| KnockOff | `docs/samples/` | Migration needed |
| RemoteFactory | `docs/samples/` | Not started |

**Migration note:** Existing sample projects should be moved to `docs/samples/` with the structure: DomainModel (with snippets), DomainModel.Tests, Server, BlazorClient, and optionally Ef.
